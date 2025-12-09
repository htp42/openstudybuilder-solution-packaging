<template>
  <SimpleFormDialog
    ref="form"
    max-width="1000px"
    :title="$t('StudyActivityInstances.edit_add_instance')"
    :open="open"
    @close="close"
    @submit="submit"
  >
    <template #body>
      <v-card elevation="0">
        <v-card-title>
          {{ $t('StudyActivityInstances.activity_selected') }}
        </v-card-title>
        <v-text-field
          :model-value="getActivityPath"
          density="compact"
          readonly
          disabled
        />
        <v-alert
          v-if="selected.length > 1"
          density="compact"
          type="info"
          rounded="lg"
          class="text-white mb-2 ml-1 mr-1"
          :text="$t('StudyActivityInstances.multiple_select_info')"
        />
        <v-data-table
          v-model="selected"
          :headers="headers"
          :items="instances"
          item-value="uid"
          show-select
          @filter="getAvailableInstances()"
        >
          <template #[`item.details`]="{ item }">
            <div v-html="sanitizeHTML(item.details)" />
          </template>
          <template #[`item.state`]="{ item }">
            <div :class="'px-1 ' + getActivityStateBackground(item)">
              {{ getActivityState(item) }}
            </div>
          </template>
          <template #[`item.important`]="{ item }">
            <v-checkbox
              v-model="importantMap[item.uid]"
              hide-details
              density="compact"
              color="primary"
            >
              <template v-if="importantMap[item.uid]" #label>
                {{ $t('_global.yes') }}
              </template>
            </v-checkbox>
          </template>
          <template #[`item.baseline_visits`]="{ item }">
            <v-select
              v-model="baselineVisitMap[item.uid]"
              :items="availableBaselineVisits"
              item-value="uid"
              item-title="visit_name"
              density="compact"
              variant="outlined"
              multiple
            />
          </template>
        </v-data-table>
      </v-card>
    </template>
    <template #actions>
      <v-btn
        :disabled="
          selected.length === 0 ||
          editedActivity.state === instancesActions.REMOVE
        "
        variant="outlined"
        rounded
        class="mr-2"
        elevation="0"
        color="success"
        @click="setMultipleActivityInstances(true)"
      >
        {{ $t('StudyActivityInstances.save_reviewed') }}
      </v-btn>
    </template>
  </SimpleFormDialog>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useStudyActivitiesStore } from '@/stores/studies-activities'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog.vue'
import statuses from '@/constants/statuses'
import activities from '@/api/activities'
import _isEmpty from 'lodash/isEmpty'
import study from '@/api/study'
import { escapeHTML, sanitizeHTML } from '@/utils/sanitize'
import instancesActions from '@/constants/instancesActions'

const notificationHub = inject('notificationHub')
const { t } = useI18n()
const props = defineProps({
  open: Boolean,
  editedActivity: {
    type: Object,
    default: null,
  },
})
const emit = defineEmits(['close'])
const studiesGeneralStore = useStudiesGeneralStore()
const activitiesStore = useStudyActivitiesStore()

const selectedStudy = computed(() => studiesGeneralStore.selectedStudy)

const headers = [
  { title: t('StudyActivityInstances.instance'), key: 'name' },
  { title: t('StudyActivityInstances.details'), key: 'details' },
  { title: t('StudyActivityInstances.state'), key: 'state' },
  { title: t('StudyActivityInstances.important'), key: 'important' },
  { title: t('StudyActivityInstances.baseline_flags'), key: 'baseline_visits' },
]

const availableBaselineVisits = ref([])
const instances = ref([])
const selected = ref([])
const selectedHolder = ref([])
const importantMap = ref({})
const baselineVisitMap = ref({})
const importantMapHolder = ref({})
const baselineVisitMapHolder = ref({})
const form = ref()

const getActivityPath = computed(() => {
  if (!_isEmpty(props.editedActivity)) {
    return `${props.editedActivity.study_activity_group.activity_group_name}/${props.editedActivity.study_activity_subgroup.activity_subgroup_name}/${props.editedActivity.activity.name}`
  }
  return ''
})

watch(
  () => props.editedActivity,
  () => {
    getAvailableInstances()
  }
)

onMounted(() => {
  getAvailableInstances()
})

async function getAvailableInstances() {
  if (!_isEmpty(props.editedActivity)) {
    const params = {
      activity_names: [props.editedActivity.activity.name],
      activity_subgroup_names: [
        props.editedActivity.study_activity_subgroup.activity_subgroup_name,
      ],
      activity_group_names: [
        props.editedActivity.study_activity_group.activity_group_name,
      ],
      filters: {
        status: { v: [statuses.FINAL] },
      },
      page_size: 0,
    }
    await activities.get(params, 'activity-instances').then((resp) => {
      instances.value = transformInstances(resp.data.items)
      // Initialize importantMap
      importantMap.value = {}
      instances.value.forEach((instance) => {
        importantMap.value[instance.uid] = false
      })
      // If editing existing activity instance, set its important status
      if (props.editedActivity.activity_instance) {
        const selectedInstance = instances.value.find(
          (instance) =>
            instance.uid === props.editedActivity.activity_instance.uid
        )
        if (selectedInstance) {
          selected.value.push(selectedInstance.uid)
          importantMap.value[selectedInstance.uid] =
            props.editedActivity.is_important || false
          if (props.editedActivity.baseline_visits?.length) {
            baselineVisitMap.value[selectedInstance.uid] =
              props.editedActivity.baseline_visits.map((item) => item.uid)
          }
        }
      }
    })
    selectedHolder.value = JSON.parse(JSON.stringify(selected.value))
    importantMapHolder.value = JSON.parse(JSON.stringify(importantMap.value))
    baselineVisitMapHolder.value = JSON.parse(
      JSON.stringify(baselineVisitMap.value)
    )
    if (instances.value.length > 1) {
      const par = {
        filters: {
          'activity.uid': { v: [props.editedActivity.activity.uid], op: 'co' },
        },
      }
      study
        .getStudyActivityInstances(selectedStudy.value.uid, par)
        .then((resp) => {
          const uidsToRemove = resp.data.items
            .map((el) => el.activity_instance.uid)
            .filter((el) => el !== selected.value[0])
          instances.value = instances.value.filter(
            (instance) => uidsToRemove.indexOf(instance.uid) === -1
          )
        })
    }
    study
      .getBaselineVisitsForStudyActivityInstance(
        props.editedActivity.study_uid,
        props.editedActivity.study_activity_instance_uid
      )
      .then((resp) => {
        availableBaselineVisits.value = resp.data
      })
  }
}
function transformInstances(instances) {
  return instances.map((instance) => {
    const lines = [
      `Class: ${escapeHTML(instance.activity_instance_class.name)}`,
      `Topic code: ${escapeHTML(instance.topic_code)}`,
      `ADaM param: ${escapeHTML(instance.adam_param_code)}`,
    ]

    for (const item of instance.activity_items) {
      const label = escapeHTML(item.activity_item_class.name)
      const values =
        item.ct_terms.length > 0
          ? item.ct_terms.map((term) => escapeHTML(term.name))
          : item.unit_definitions.map((unit) => escapeHTML(unit.name))

      lines.push(`${label}: ${values.join(', ')}`)
    }

    instance.details = lines.join('<br> ')
    return instance
  })
}
function getActivityStateBackground(activity) {
  if (activity.is_required_for_activity) {
    return 'mandatory'
  } else if (activity.is_default_selected_for_activity) {
    return 'defaulted'
  }
  if (instances.value.length === 1) {
    return 'suggestion'
  }
}
function getActivityState(activity) {
  if (activity.is_required_for_activity) {
    return t('StudyActivityInstances.mandatory')
  } else if (activity.is_default_selected_for_activity) {
    return t('StudyActivityInstances.defaulted')
  }
  if (instances.value.length === 1) {
    return t('StudyActivityInstances.suggestion')
  }
}
function submit() {
  try {
    setMultipleActivityInstances()
  } catch (error) {
    console.error(error)
  }
}
function setMultipleActivityInstances(is_reviewed = false) {
  notificationHub.clearErrors()
  const data = []

  if (_isEmpty(selected.value) && !_isEmpty(selectedHolder.value)) {
    data.push({
      method: 'PATCH',
      content: {
        is_reviewed: is_reviewed,
        activity_instance_uid: null,
        study_activity_uid: props.editedActivity.study_activity_uid,
        study_activity_instance_uid:
          props.editedActivity.study_activity_instance_uid,
        is_important: false,
        baseline_visit_uids: [],
      },
    })
  } else if (selected.value.includes(selectedHolder.value[0])) {
    data.push({
      method: 'PATCH',
      content: {
        is_reviewed: is_reviewed,
        activity_instance_uid: selectedHolder.value[0],
        study_activity_uid: props.editedActivity.study_activity_uid,
        study_activity_instance_uid:
          props.editedActivity.study_activity_instance_uid,
        is_important: importantMap.value[selectedHolder.value[0]] || false,
        baseline_visit_uids:
          baselineVisitMap.value[selectedHolder.value[0]] || [],
      },
    })
    selected.value.splice(selected.value.indexOf(selectedHolder.value[0]), 1)
    selected.value.forEach((value) => {
      data.push({
        method: 'POST',
        content: {
          is_reviewed: is_reviewed,
          activity_instance_uid: value,
          study_activity_uid: props.editedActivity.study_activity_uid,
          is_important: importantMap.value[value] || false,
          baseline_visit_uids: baselineVisitMap.value[value] || [],
        },
      })
    })
  } else {
    for (let index = 0; index < selected.value.length; index++) {
      let placeholder = {
        method: index === 0 ? 'PATCH' : 'POST',
        content: {
          is_reviewed: is_reviewed,
          activity_instance_uid: selected.value[index],
          study_activity_uid: props.editedActivity.study_activity_uid,
          is_important: importantMap.value[selected.value[index]] || false,
          baseline_visit_uids:
            baselineVisitMap.value[selected.value[index]] || [],
        },
      }
      if (index === 0) {
        placeholder.content.study_activity_instance_uid =
          props.editedActivity.study_activity_instance_uid
      }
      data.push(placeholder)
    }
  }
  if (_isEmpty(data)) {
    form.value.working = false
    close()
    return
  }
  activitiesStore
    .batchSelectStudyActivityInstances(selectedStudy.value.uid, data)
    .then(
      () => {
        notificationHub.add({
          msg: t('StudyActivityInstances.instance_created'),
          type: 'success',
        })
        close()
      },
      () => {
        form.value.working = false
      }
    )
}
function close() {
  notificationHub.clearErrors()
  instances.value = []
  selected.value = []
  importantMap.value = {}
  importantMapHolder.value = {}
  baselineVisitMap.value = {}
  baselineVisitMapHolder.value = {}
  emit('close')
}
</script>

<style scoped>
.defaulted {
  background-color: darkseagreen;
  border-radius: 5px;
}
.mandatory {
  background-color: rgb(202, 124, 124);
  border-radius: 5px;
}
.suggestion {
  background-color: rgb(217, 201, 106);
  border-radius: 5px;
}
</style>
