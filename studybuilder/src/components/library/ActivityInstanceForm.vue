<template>
  <HorizontalStepperForm
    ref="stepper"
    :title="title"
    :steps="steps"
    :form-observer-getter="getObserver"
    :extra-step-validation="extraStepValidation"
    :help-items="helpItems"
    @close="close"
    @step-loaded="initStep"
    @save="submit"
  >
    <template #header>
      <v-alert v-if="selectedActivity" type="info" variant="tonal">
        {{ $t('ActivityInstanceForm.selected_activity') }}
        {{ selectedActivityName }}
      </v-alert>
    </template>
    <template #[`step.activities`]>
      <div class="dialog-title">
        {{ $t('ActivityInstanceForm.step1_long_title') }}
      </div>
      <v-alert
        color="nnLightBlue200"
        icon="$info"
        class="my-4 text-nnTrueBlue"
        type="info"
        rounded="lg"
        :text="$t('ActivityInstanceForm.step1_help')"
      />
      <v-form ref="step1FormRef">
        <NNTable
          hide-default-switches
          hide-export-button
          no-padding
          column-data-resource="concepts/activities/activities"
          :item-value="(item) => getFullActivityUid(item)"
          :modifiable-table="false"
          :headers="activitiesHeaders"
          :items="activities"
          :items-length="totalActivities"
          @filter="fetchActivities"
        >
          <template #[`item.selection`]="{ item }">
            <v-radio-group v-model="selectedActivity" hide-details>
              <v-radio
                color="primary"
                :value="getFullActivityUid(item)"
              ></v-radio>
            </v-radio-group>
          </template>
          <template #[`item.activity_instances`]="{ item }">
            <div v-html="sanitizeHTML(showInstances(item))"></div>
          </template>
        </NNTable>
      </v-form>
    </template>
    <template #[`step.required`]>
      <v-form ref="step2FormRef">
        <div class="d-flex w-50">
          <v-select
            v-model="step2Form.activity_instance_class"
            :label="$t('ActivityInstanceForm.activity_instance_class')"
            :items="activityInstanceClasses"
            item-title="name"
            item-value="uid"
            return-object
            variant="outlined"
            density="compact"
            class="w-50"
            :loading="loadingActivityInstances"
            :disabled="activityInstanceUid !== null"
            :rules="[formRules.required]"
            @update:model-value="fetchActivityItemClasses"
          />
          <v-select
            v-model="step2Form.data_domain"
            :label="$t('ActivityInstanceForm.data_domain')"
            :items="dataDomains"
            variant="outlined"
            density="compact"
            class="ml-4 w-50"
            :rules="[formRules.required]"
            @update:model-value="filterActivityInstanceClasses"
          />
        </div>
        <template
          v-if="
            ((testCodeAic && testNameAic) ||
              mandatoryActivityItemClasses.length) &&
            step2Form.data_domain
          "
        >
          <div class="dialog-title mb-4">
            {{ $t('ActivityInstanceForm.step2_long_title') }}
          </div>
          <template v-if="!testCodeAic && !testNameAic">
            <ActivityItemClassField
              v-for="(activityItemClass, index) in mandatoryActivityItemClasses"
              :key="activityItemClass.uid"
              v-model="step2Form.activityItems[index]"
              :all-activity-item-classes="availableActivityItemClasses"
              :compatible-activity-item-classes="[activityItemClass]"
              :unit-dimension="selectedUnitDimension"
              :adam-specific="activityItemClass.is_adam_param_specific_enabled"
              :disabled="
                props.activityInstanceUid !== undefined &&
                props.activityInstanceUid !== null
              "
              :data-domain="step2Form.data_domain"
              select-value-only
              class="mb-4 w-50"
            />
          </template>
          <template v-else>
            <TestActivityItemClassField
              v-model="testValue"
              v-model:code-codelist="testCodeCodelistValue"
              v-model:name-codelist="testNameCodelistValue"
              :test-code-aic="testCodeAic"
              :test-name-aic="testNameAic"
              :data-domain="step2Form.data_domain"
              class="w-50 mb-4"
            />

            <ActivityItemClassField
              v-for="(activityItemClass, index) in mandatoryActivityItemClasses"
              :key="activityItemClass.uid"
              v-model="step2Form.activityItems[index]"
              :all-activity-item-classes="availableActivityItemClasses"
              :compatible-activity-item-classes="[activityItemClass]"
              :unit-dimension="selectedUnitDimension"
              :adam-specific="activityItemClass.is_adam_param_specific_enabled"
              :disabled="
                props.activityInstanceUid !== undefined &&
                props.activityInstanceUid !== null
              "
              :data-domain="step2Form.data_domain"
              select-value-only
              class="mb-4 w-50"
            />
          </template>
        </template>
        <template v-if="showMolecularWeight">
          <div class="dialog-title mb-4">
            {{ $t('ActivityInstanceForm.attributes') }}
          </div>
          <v-text-field
            v-model="step2Form.molecular_weight"
            :label="$t('ActivityInstanceForm.molecular_weight')"
            variant="outlined"
            density="compact"
            class="w-50"
            suffix="g/mol"
          />
        </template>
      </v-form>
    </template>
    <template #[`step.optional`]>
      <div class="dialog-title mb-4">
        {{ $t('ActivityInstanceForm.step3_long_title') }}
      </div>
      <v-form ref="step3FormRef">
        <ActivityItemClassField
          v-for="(activityItemClass, index) in step3Form.activityItems"
          :key="activityItemClass.uid"
          v-model="step3Form.activityItems[index]"
          :all-activity-item-classes="filteredActivityItemClasses"
          :compatible-activity-item-classes="optionalActivityItemClasses"
          :disabled="props.activityInstanceUid !== null"
          :data-domain="step2Form.data_domain"
          adam-specific
          class="mb-4 w-50"
          @update:model-value="updateAIFields"
        >
          <template v-if="!props.activityInstanceUid" #append>
            <v-btn
              color="red"
              variant="flat"
              class="ml-4"
              @click="removeOptionalActivityItemClass(index)"
            >
              {{ $t('_global.remove') }}
            </v-btn>
          </template>
        </ActivityItemClassField>
        <v-btn
          v-if="!props.activityInstanceUid"
          color="secondary"
          variant="outlined"
          rounded="xl"
          prepend-icon="mdi-plus"
          class="mb-4"
          @click="addOptionalActivityItemClass"
        >
          {{ $t('ActivityInstanceForm.add_activity_item_class') }}
        </v-btn>
        <div class="d-flex align-center dialog-title my-4">
          {{ $t('ActivityInstanceForm.step3_second_title') }}
          <v-btn
            icon="mdi-refresh"
            variant="flat"
            :title="$t('ActivityInstanceForm.refresh_title')"
            @click="sendPreviewRequest"
          />

          <v-switch
            v-model="allowManualEdit"
            :label="$t('ActivityInstanceForm.allow_manual_edit')"
            color="primary"
            class="ml-4"
            hide-details
            @update:model-value="onAllowManualEditChange"
          />
        </div>
        <div class="d-flex w-50">
          <v-text-field
            v-model="step3Form.name"
            :label="$t('ActivityInstancePreview.activity_instance_name')"
            variant="outlined"
            density="compact"
            class="mr-4"
            :disabled="!allowManualEdit"
            :loading="loadingPreview"
            :rules="[formRules.required]"
          />
          <v-text-field
            v-model="step3Form.name_sentence_case"
            :label="$t('ActivityInstancePreview.sentence_case_name')"
            variant="outlined"
            density="compact"
            class="mr-4"
            :disabled="!allowManualEdit"
            :loading="loadingPreview"
            :rules="[
              formRules.required,
              (value) => formRules.sameAs(value, step3Form.name),
            ]"
          />
          <v-text-field
            v-model="step3Form.nci_concept_name"
            :label="$t('ActivityInstancePreview.nci_preferred_name')"
            variant="outlined"
            density="compact"
          />
        </div>
        <div class="d-flex w-50">
          <v-text-field
            v-model="step3Form.topic_code"
            :label="$t('ActivityInstancePreview.topic_code')"
            variant="outlined"
            density="compact"
            class="mr-4"
            :disabled="!allowManualEdit"
            :loading="loadingPreview"
            :rules="[formRules.required]"
          />
          <v-text-field
            v-model="step3Form.adam_param_code"
            :label="$t('ActivityInstancePreview.adam_param_code')"
            variant="outlined"
            density="compact"
            class="mr-4"
            :disabled="!allowManualEdit"
            :loading="loadingPreview"
            :rules="[formRules.required]"
          />
          <v-text-field
            v-model="step3Form.nci_concept_id"
            :label="$t('ActivityInstancePreview.nci_code')"
            variant="outlined"
            density="compact"
          />
        </div>
        <div class="d-flex">
          <v-checkbox
            v-model="step3Form.is_research_lab"
            :label="$t('ActivityInstanceForm.data_from_research_lab')"
            color="primary"
          >
            <template #append>
              <v-icon
                icon="$info"
                size="small"
                color="primary"
                :title="$t('ActivityInstanceForm.data_from_research_lab_help')"
              />
            </template>
          </v-checkbox>
        </div>
      </v-form>
    </template>
    <template #[`step.dataspec`]>
      <div class="dialog-title mb-4">
        {{ $t('ActivityInstanceForm.step4_long_title') }}
      </div>
      <v-form ref="step4FormRef">
        <div class="d-flex w-50">
          <SelectCTTermField
            v-model="step4Form.data_category"
            :label="$t('ActivityInstanceForm.data_category')"
            codelist="findingCategoryDefinition"
            item-title="submission_value"
            class="mr-4"
            clearable
          />
          <SelectCTTermField
            v-model="step4Form.data_subcategory"
            :label="$t('ActivityInstanceForm.data_subcategory')"
            codelist="findingSubCategoryDefinition"
            item-title="submission_value"
            clearable
          />
        </div>
        <v-alert
          color="nnLightBlue200"
          icon="$info"
          class="my-4 text-nnTrueBlue"
          type="info"
          rounded="lg"
          width="fit-content"
          :text="$t('ActivityInstanceForm.step4_help')"
        />
        <ActivityItemClassField
          v-for="(activityItemClass, index) in step4Form.activityItems"
          :key="activityItemClass.uid"
          v-model="step4Form.activityItems[index]"
          :all-activity-item-classes="filteredActivityItemClasses"
          :compatible-activity-item-classes="otherAvailableActivityItemClasses"
          :data-domain="step2Form.data_domain"
          class="mb-4 w-50"
          multiple
        >
          <template #append>
            <v-btn
              color="red"
              variant="flat"
              class="ml-4"
              @click="removeDataSpecActivityItemClass(index)"
            >
              {{ $t('_global.remove') }}
            </v-btn>
          </template>
        </ActivityItemClassField>
        <v-btn
          color="secondary"
          variant="outlined"
          rounded="xl"
          prepend-icon="mdi-plus"
          class="mb-4"
          @click="addDataSpecActivityItemClass"
        >
          {{ $t('ActivityInstanceForm.add_activity_item_class') }}
        </v-btn>
        <div class="dialog-title my-4">
          {{ $t('ActivityInstanceForm.step3_second_title') }}
        </div>
        <div class="d-flex">
          <v-checkbox
            v-model="step4Form.is_required_for_activity"
            :label="$t('ActivityInstanceForm.required_for_activity')"
            color="primary"
            class="mr-4"
          >
            <template #append>
              <v-icon
                icon="$info"
                size="small"
                color="primary"
                :title="$t('ActivityInstanceForm.required_for_activity_help')"
              />
            </template>
          </v-checkbox>
          <v-checkbox
            v-model="step4Form.is_data_sharing"
            :label="$t('ActivityInstanceForm.data_sharing')"
            color="primary"
            class="mr-4"
          >
            <template #append>
              <v-icon
                icon="$info"
                size="small"
                color="primary"
                :title="$t('ActivityInstanceForm.data_sharing_help')"
              />
            </template>
          </v-checkbox>
          <v-checkbox
            v-model="step4Form.is_default_selected_for_activity"
            :label="$t('ActivityInstanceForm.default_selected')"
            color="primary"
            class="mr-4"
          >
            <template #append>
              <v-icon
                icon="$info"
                size="small"
                color="primary"
                :title="$t('ActivityInstanceForm.default_selected_help')"
              />
            </template>
          </v-checkbox>
        </div>
      </v-form>
    </template>
  </HorizontalStepperForm>
</template>

<script setup>
import { computed, inject, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import _debounce from 'lodash/debounce'
import ActivityItemClassField from './ActivityItemClassField.vue'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm.vue'
import NNTable from '@/components/tools/NNTable.vue'
import SelectCTTermField from '@/components/tools/SelectCTTermField.vue'
import TestActivityItemClassField from './TestActivityItemClassField.vue'
import activitiesApi from '@/api/activities'
import activityInstanceClassesApi from '@/api/activityInstanceClasses'
import codelistsApi from '@/api/controlledTerminology/codelists'
import activityItemClassesConstants from '@/constants/activityItemClasses'
import libraryConstants from '@/constants/libraries.js'
import statuses from '@/constants/statuses.js'
import filteringParameters from '@/utils/filteringParameters'
import { escapeHTML, sanitizeHTML } from '@/utils/sanitize'

const emit = defineEmits(['close'])
const props = defineProps({
  activityInstanceUid: {
    type: String,
    default: null,
  },
})

const router = useRouter()
const { t } = useI18n()
const notificationHub = inject('notificationHub')
const formRules = inject('formRules')

const activityInstanceClasses = ref([])
const activities = ref([])
const activityInstance = ref(null)
const allowManualEdit = ref(false)
const dataDomainCTTermUid = ref(null)
const datasets = ref([])
const loadingActivityInstances = ref(false)
const loadingPreview = ref(false)
const step2Form = ref({})
const step3Form = ref({})
const step4Form = ref({})
const selectedActivity = ref(null)
const stepper = ref()
const totalActivities = ref(0)
const testValue = ref(null)
const testCodeCodelistValue = ref(null)
const testNameCodelistValue = ref(null)

const step1FormRef = ref()
const step2FormRef = ref()
const step3FormRef = ref()
const step4FormRef = ref()

const title = computed(() => {
  return props.activityInstanceUid
    ? t('ActivityInstanceForm.edit_title')
    : t('ActivityInstanceForm.add_title')
})

const allowedInstanceClasses = [
  'CategoricFindings',
  'NumericFindings',
  'TextualFindings',
]

const dataDomains = computed(() => {
  if (!datasets.value.length) {
    return []
  }
  if (datasets.value.length === 1) {
    return datasets.value[0].datasets
  }
  const allValues = new Set()
  for (const item of datasets.value) {
    for (const domain of item.datasets) {
      if (!allValues.has(domain)) {
        allValues.add(domain)
      }
    }
  }
  return Array.from(allValues.values())
})

const selectedActivityName = computed(() => {
  if (!selectedActivity.value) return ''
  const parts = selectedActivity.value.split('|')
  return activities.value.find((item) => item.uid === parts[2]).name
})

const availableActivityItemClasses = ref([])
const filteredActivityItemClasses = ref([])

const mandatoryActivityItemClasses = computed(() => {
  const result = availableActivityItemClasses.value.filter((item) => {
    return item.mandatory && !['test_code', 'test_name'].includes(item.name)
  })
  if (step2Form.value.activity_instance_class?.name === 'NumericFindings') {
    // special sorting for NumericFindings
    return [
      result.find((item) => item.name === 'unit_dimension'),
      result.find((item) => item.name === 'standard_unit'),
    ].filter(Boolean) // Filter out undefined values
  }
  return result
})

// List of activity item classes that should not be proposed to end users
const activityItemClassExceptions = computed(() => {
  const exceptions = ['domain']
  if (categoryAic.value) {
    exceptions.push(categoryAic.value.name)
  }
  if (subcategoryAic.value) {
    exceptions.push(subcategoryAic.value.name)
  }
  return exceptions
})

const optionalActivityItemClasses = computed(() => {
  return filteredActivityItemClasses.value.filter(
    (item) =>
      !item.mandatory &&
      !activityItemClassExceptions.value.includes(item.name) &&
      step3Form.value.activityItems.find(
        (selection) => selection.activity_item_class_uid === item.uid
      ) === undefined
  )
})
const otherAvailableActivityItemClasses = computed(() => {
  return filteredActivityItemClasses.value.filter(
    (item) =>
      !item.mandatory &&
      !activityItemClassExceptions.value.includes(item.name) &&
      step3Form.value.activityItems.find(
        (selection) => selection.activity_item_class_uid === item.uid
      ) === undefined &&
      step4Form.value.activityItems.find(
        (selection) => selection.activity_item_class_uid === item.uid
      ) === undefined
  )
})

const testCodeAic = computed(() => {
  return availableActivityItemClasses.value.find(
    (aic) => aic.name === 'test_code'
  )
})
const testNameAic = computed(() => {
  return availableActivityItemClasses.value.find(
    (aic) => aic.name === 'test_name'
  )
})
const domainAic = computed(() => {
  return availableActivityItemClasses.value.find((aic) => aic.name === 'domain')
})

const selectedUnitDimension = computed(() => {
  let result = null
  mandatoryActivityItemClasses.value.forEach((aic, index) => {
    if (aic?.name === 'unit_dimension') {
      result = step2Form.value.activityItems[index].ct_term_name
    }
  })
  return result
})

const showMolecularWeight = computed(() => {
  if (!selectedUnitDimension.value) {
    return false
  }
  return selectedUnitDimension.value.toLowerCase().includes('concentration')
})

watch(showMolecularWeight, (value) => {
  if (!value) {
    delete step2Form.value.molecular_weight
  }
})

watch(
  () => step3Form.value.is_research_lab,
  () => {
    // Refresh preview when is_research_lab changes, but only if toggle is off
    if (!allowManualEdit.value && !activityInstance.value) {
      sendPreviewRequestDebounced()
    }
  }
)

const categoryAic = computed(() => {
  const aicName = step2Form.value.activity_instance_class?.name
  return filteredActivityItemClasses.value.find(
    (item) =>
      item.name ===
      activityItemClassesConstants.categoryActivityItemClasses[aicName]
  )
})
const subcategoryAic = computed(() => {
  const aicName = step2Form.value.activity_instance_class?.name
  return filteredActivityItemClasses.value.find(
    (item) =>
      item.name ===
      activityItemClassesConstants.subcategoryActivityItemClasses[aicName]
  )
})

const activitiesHeaders = [
  { title: '', key: 'selection', sortable: false, noFilter: true },
  {
    title: t('ActivityInstanceForm.activity_group'),
    key: 'activity_groupings.0.activity_group_name',
    externalFilterSource: 'concepts/activities/activity-groups$name',
  },
  {
    title: t('ActivityInstanceForm.activity_subgroup'),
    key: 'activity_groupings.0.activity_subgroup_name',
    externalFilterSource: 'concepts/activities/activity-sub-groups$name',
  },
  {
    title: t('ActivityInstanceForm.activity_name'),
    key: 'name',
  },
  {
    title: t('ActivityInstanceForm.activity_instances'),
    key: 'activity_instances',
    filteringName: 'activity_instances.name',
    noFilter: true,
  },
]
const steps = [
  { name: 'activities', title: t('ActivityInstanceForm.step1_title') },
  { name: 'required', title: t('ActivityInstanceForm.step2_title') },
  { name: 'optional', title: t('ActivityInstanceForm.step3_title') },
  { name: 'dataspec', title: t('ActivityInstanceForm.step4_title') },
]
const helpItems = [
  'ActivityInstanceForm.general',
  'ActivityInstanceForm.step1_description',
  'ActivityInstanceForm.step2_description',
  'ActivityInstanceForm.step3_description',
  'ActivityInstanceForm.step4_description',
]

function fetchActivities(filters, options, filtersUpdated) {
  const params = filteringParameters.prepareParameters(
    options,
    filters,
    filtersUpdated
  )
  if (options?.sortBy?.length) {
    if (
      [
        'activity_groupings.0.activity_group_name',
        'activity_groupings.0.activity_subgroup_name',
      ].includes(options.sortBy[0].key)
    ) {
      const parts = options.sortBy[0].key.split('.')
      const sortKey = `${parts[0]}[0].${parts[2]}`
      params.sort_by = `{"${sortKey}":${options.sortBy[0].order === 'asc'}}`
    }
  }
  if (!params.filters) {
    params.filters = {}
  } else {
    params.filters = JSON.parse(params.filters)
  }
  params.filters.status = { v: [statuses.FINAL] }
  params.filters.library_name = { v: [libraryConstants.LIBRARY_SPONSOR] }
  params.filters.is_data_collected = { v: [true] }
  if (params.filters['activity_groupings.0.activity_group_name']) {
    params.activity_group_names = []
    params.filters['activity_groupings.0.activity_group_name'].v.forEach(
      (value) => {
        params.activity_group_names.push(value)
      }
    )
    delete params.filters['activity_groupings.0.activity_group_name']
  }
  if (params.filters['activity_groupings.0.activity_subgroup_name']) {
    params.activity_subgroup_names = []
    params.filters['activity_groupings.0.activity_subgroup_name'].v.forEach(
      (value) => {
        params.activity_subgroup_names.push(value)
      }
    )
    delete params.filters['activity_groupings.0.activity_subgroup_name']
  }
  params.group_by_groupings = false
  activitiesApi.get(params, 'activities').then((resp) => {
    activities.value = resp.data.items
    totalActivities.value = resp.data.total
  })
}

async function fetchActivityItemClasses(activityInstanceClass) {
  if (activityInstanceClass) {
    // Call 1: Get ALL items without dataset filter (for mandatory/Step 2)
    const respAll = await activityInstanceClassesApi.getActivityItemClasses(
      activityInstanceClass.uid
    )
    availableActivityItemClasses.value = respAll.data

    // Call 2: Get filtered items with dataset filter (for optional/Step 3 & 4)
    if (step2Form.value.data_domain) {
      const respFiltered =
        await activityInstanceClassesApi.getActivityItemClasses(
          activityInstanceClass.uid,
          {
            dataset_uid: step2Form.value.data_domain,
            ig_uid: 'SDTMIG',
          }
        )
      filteredActivityItemClasses.value = respFiltered.data
    } else {
      // No dataset selected yet, use unfiltered for optional items too
      filteredActivityItemClasses.value = respAll.data
    }

    // Initialize mandatory activity items for Step 2
    step2Form.value.activityItems = []
    mandatoryActivityItemClasses.value.forEach((aic) => {
      if (!aic) return // Skip if undefined
      let activityItem
      if (activityInstance.value) {
        const matched = activityInstance.value.activity_items.find(
          (item) => item.activity_item_class.uid === aic.uid
        )
        if (matched) {
          activityItem = {
            activity_item_class_uid: matched.activity_item_class.uid,
            ct_term_uids: matched.ct_terms.map((ct_term) => ct_term.uid),
          }
        } else {
          activityItem = { activity_item_class_uid: aic.uid }
        }
      } else {
        activityItem = { activity_item_class_uid: aic.uid }
      }
      step2Form.value.activityItems.push(activityItem)
    })
    await fetchDatasets(activityInstanceClass.uid)
  } else {
    step2Form.value.activityItems = []
    availableActivityItemClasses.value = []
    filteredActivityItemClasses.value = []
  }
}

async function fetchDatasets(activityInstanceClassUid) {
  const params = {
    ig_uid: 'SDTMIG',
  }
  if (activityInstanceClassUid) {
    params.activity_instance_class_uid = activityInstanceClassUid
  }
  const resp = await activityInstanceClassesApi.getModelMappingDatasets(params)
  datasets.value = resp.data
}

function filterActivityInstanceClasses(dataDomainUid) {
  const params = {
    filters: {
      submission_value: { v: [dataDomainUid], op: 'eq' },
    },
  }
  codelistsApi
    .getCodelistTerms(
      activityItemClassesConstants.sdtmDomainAbbreviationCodelistUid,
      params
    )
    .then((resp) => {
      if (resp.data.items.length > 0) {
        dataDomainCTTermUid.value = resp.data.items[0].term_uid
      }
    })

  if (step2Form.value.activity_instance_class) {
    // Re-fetch activity item classes with the dataset filter
    fetchActivityItemClasses(step2Form.value.activity_instance_class)
    return
  }
  const uids = datasets.value
    .filter(
      (item) =>
        item.datasets.includes(dataDomainUid) &&
        allowedInstanceClasses.includes(item.name)
    )
    .map((item) => item.uid)
  const filters = {
    uid: { v: uids },
  }
  loadingActivityInstances.value = true
  activityInstanceClassesApi
    .getAll({
      filters,
      page_size: 0,
    })
    .then((resp) => {
      activityInstanceClasses.value = resp.data.items
      loadingActivityInstances.value = false
    })
}

function getFullActivityUid(activity) {
  const grouping = activity.activity_groupings[0]
  return `${grouping.activity_group_uid}|${grouping.activity_subgroup_uid}|${activity.uid}`
}

function addOptionalActivityItemClass() {
  step3Form.value.activityItems.push({})
}

function removeOptionalActivityItemClass(index) {
  step3Form.value.activityItems.splice(index, 1)
  if (!allowManualEdit.value) {
    sendPreviewRequest()
  }
}

function addDataSpecActivityItemClass() {
  step4Form.value.activityItems.push({})
}

function removeDataSpecActivityItemClass(index) {
  step4Form.value.activityItems.splice(index, 1)
}

function resetForms() {
  selectedActivity.value = null
  step2Form.value = {
    activityItems: [],
  }
  step3Form.value = {
    activityItems: [],
  }
  step4Form.value = {
    activityItems: [],
  }
}

function showInstances(item) {
  return item.activity_instances
    .map((instance) => escapeHTML(instance.name))
    .join('<br/>')
}

function close() {
  emit('close')
  notificationHub.clearErrors()
}

function getObserver(step) {
  const observers = {
    1: step1FormRef,
    2: step2FormRef,
    3: step3FormRef,
    4: step4FormRef,
  }
  return observers[step]?.value
}

function extraStepValidation(step) {
  if (step === 1 && !selectedActivity.value) {
    notificationHub.add({
      msg: t('ActivityInstanceForm.activity_not_selected'),
      type: 'error',
    })
    return false
  }
  return true
}

async function prepareCreationPayload(forPreview) {
  const [activityGroupUid, activitySubgroupUid, activityUid] =
    selectedActivity.value.split('|')
  const activityItems = [
    ...step2Form.value.activityItems,
    ...step3Form.value.activityItems,
    ...step4Form.value.activityItems,
  ].filter((item) => item && item.activity_item_class_uid)

  function addActivityItem(uid, codelistUid, term_uids) {
    const ct_terms = term_uids.map((term_uid) => {
      return { codelist_uid: codelistUid, term_uid }
    })
    activityItems.push({
      activity_item_class_uid: uid,
      ct_terms,
      odm_item_uids: [],
      unit_definition_uids: [],
      is_adam_param_specific: false,
    })
  }

  if (testValue.value) {
    addActivityItem(testCodeAic.value.uid, testCodeCodelistValue.value, [
      testValue.value,
    ])
    addActivityItem(testNameAic.value.uid, testNameCodelistValue.value, [
      testValue.value,
    ])
  }

  if (step4Form.value.data_category) {
    const resp = await codelistsApi.getAll({
      filters: { 'attributes.submission_value': { v: ['FINDCAT'] } },
    })
    if (resp.data.items.length) {
      const codelistUid = resp.data.items[0].codelist_uid
      addActivityItem(categoryAic.value.uid, codelistUid, [
        step4Form.value.data_category,
      ])
    }
  }
  if (step4Form.value.data_subcategory) {
    const resp = await codelistsApi.getAll({
      filters: { 'attributes.submission_value': { v: ['FINDSCAT'] } },
    })
    if (resp.data.items.length) {
      const codelistUid = resp.data.items[0].codelist_uid
      addActivityItem(subcategoryAic.value.uid, codelistUid, [
        step4Form.value.data_subcategory,
      ])
    }
  }
  if (domainAic.value && dataDomainCTTermUid.value) {
    // Manually add domain activity item based on selected dataset
    addActivityItem(
      domainAic.value.uid,
      activityItemClassesConstants.sdtmDomainAbbreviationCodelistUid,
      [dataDomainCTTermUid.value]
    )
  }

  const result = {
    library_name: libraryConstants.LIBRARY_SPONSOR,
    nci_concept_name: step3Form.value.nci_concept_name,
    nci_concept_id: step3Form.value.nci_concept_id,
    activity_instance_class_uid: step2Form.value.activity_instance_class.uid,
    activity_items: activityItems,
    is_required_for_activity: step4Form.value.is_required_for_activity,
    is_default_selected_for_activity:
      step4Form.value.is_default_selected_for_activity,
    is_data_sharing: step4Form.value.is_data_sharing,
    is_research_lab: step3Form.value.is_research_lab,
    activity_groupings: [
      {
        activity_group_uid: activityGroupUid,
        activity_subgroup_uid: activitySubgroupUid,
        activity_uid: activityUid,
      },
    ],
  }
  if (step2Form.value.molecular_weight) {
    result.molecular_weight = step2Form.value.molecular_weight
  }
  if (!forPreview) {
    result.name = step3Form.value.name
    result.name_sentence_case = step3Form.value.name_sentence_case
    result.adam_param_code = step3Form.value.adam_param_code
    result.topic_code = step3Form.value.topic_code
  }
  return result
}

async function sendPreviewRequest() {
  if (allowManualEdit.value) {
    return
  }
  loadingPreview.value = true
  const payload = await prepareCreationPayload(true)
  const resp = await activitiesApi.getPreview(payload, 'activity-instances')
  step3Form.value.name = resp.data.name
  step3Form.value.name_sentence_case = resp.data.name_sentence_case
  step3Form.value.topic_code = resp.data.topic_code
  step3Form.value.adam_param_code = resp.data.adam_param_code
  loadingPreview.value = false
}

const sendPreviewRequestDebounced = _debounce(sendPreviewRequest, 300)

function onAllowManualEditChange(value) {
  if (!value) {
    sendPreviewRequest()
  }
}

async function updateAIFields(value) {
  if (value.ct_terms.length || value.unit_definition_uids.length) {
    await sendPreviewRequestDebounced()
  }
}

async function initStep(step) {
  if (step === 3) {
    // Check if required fields have been selected (param/paramcd)
    const hasRequiredFields =
      // Check test value (test_code/test_name)
      testValue.value ||
      // Check activity items with ct_terms, ct_term_uids, or unit_definition_uids
      step2Form.value.activityItems?.some(
        (item) =>
          item &&
          (item.ct_terms?.length > 0 ||
            item.ct_term_uids?.length > 0 ||
            item.unit_definition_uids?.length > 0)
      )

    // Refresh preview if:
    // 1. Toggle is off (allowManualEdit is false)
    // 2. Required fields have been selected
    // 3. if Wizard stepper for creating an instance Form (activityInstance.value is null)
    if (
      !allowManualEdit.value &&
      hasRequiredFields &&
      !activityInstance.value
    ) {
      await sendPreviewRequest()
    } else if (!step3Form.value.name && !activityInstance.value) {
      // Fallback to original behavior if no required fields selected yet
      await sendPreviewRequest()
    }
  }
}

async function submit() {
  notificationHub.clearErrors()

  const payload = await prepareCreationPayload()
  try {
    const resp = await activitiesApi.create(payload, 'activity-instances')
    notificationHub.add({
      msg: t('ActivityInstanceForm.add_success'),
    })
    router.push({
      name: 'ActivityInstanceOverview',
      params: { id: resp.data.uid },
    })
  } finally {
    stepper.value.loading = false
  }
}

resetForms()

activityInstanceClassesApi
  .getAll({
    filters: {
      name: { v: allowedInstanceClasses },
      level: { v: [3] },
    },
    page_size: 0,
  })
  .then((resp) => {
    activityInstanceClasses.value = resp.data.items
  })
fetchDatasets()

if (props.activityInstanceUid) {
  const resp = await activitiesApi.getObject(
    'activity-instances',
    props.activityInstanceUid
  )
  activityInstance.value = resp.data
  // FIXME: Can we have imported activity instances linked to multiple groupings?
  const grouping = activityInstance.value.activity_groupings[0]
  selectedActivity.value = `${grouping.activity_group.uid}|${grouping.activity_subgroup.uid}|${grouping.activity.uid}`
  step2Form.value.activity_instance_class = activityInstanceClasses.value.find(
    (item) => item.uid === activityInstance.value.activity_instance_class.uid
  )
  await fetchActivityItemClasses(step2Form.value.activity_instance_class)
  step3Form.value.name = activityInstance.value.name
  step3Form.value.name_sentence_case = activityInstance.value.name_sentence_case
  step3Form.value.nci_concept_name = activityInstance.value.nci_concept_name
  step3Form.value.topic_code = activityInstance.value.topic_code
  step3Form.value.adam_param_code = activityInstance.value.adam_param_code
  step3Form.value.nci_concept_id = activityInstance.value.nci_concept_id

  for (const activityItem of activityInstance.value.activity_items) {
    let matched = optionalActivityItemClasses.value.find(
      (aic) => aic.uid === activityItem.activity_item_class.uid
    )
    if (matched) {
      step3Form.value.activityItems.push({
        activity_item_class_uid: matched.uid,
        ct_term_uids: activityItem.ct_terms.map((ct_term) => ct_term.uid),
      })
      continue
    }
    matched = otherAvailableActivityItemClasses.value.find(
      (aic) => aic.uid === activityItem.activity_item_class.uid
    )
    if (matched) {
      step4Form.value.activityItems.push({
        activity_item_class_uid: matched.uid,
        ct_term_uids: activityItem.ct_terms.map((ct_term) => ct_term.uid),
      })
    }
  }
}
</script>
