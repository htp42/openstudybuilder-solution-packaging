<template>
  <div>
    <v-row>
      <v-col>
        <div class="text-h5 mb-4">
          {{ $t('CRFDescriptions.add') }}
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <v-select
          v-model="inputDesc.language"
          :label="t('CRFDescriptions.language')"
          :items="languages"
          item-title="submission_value"
          item-value="submission_value"
          density="compact"
          :disabled="props.disabled"
        />
      </v-col>
      <v-col>
        <v-combobox
          v-model="inputDesc.name"
          :label="t('CRFDescriptions.name')"
          :items="descriptions"
          item-title="name"
          :item-value="
            (item) => [
              item.language,
              item.name,
              item.description,
              item.instruction,
              item.sponsor_instruction,
            ]
          "
          return-object
          density="compact"
          :disabled="props.disabled"
          @update:model-value="autocompleteValues"
        />
      </v-col>
      <v-col>
        <v-btn
          color="secondary"
          class="mr-2"
          block
          :disabled="props.disabled"
          @click="addDescription"
        >
          {{ t('_global.add') }}
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <div>
          <QuillEditor
            v-model:content="inputDesc.description"
            content-type="html"
            :toolbar="customToolbar"
            :read-only="props.disabled"
            :placeholder="
              inputDesc.description ? '' : t('CRFDescriptions.description')
            "
          />
        </div>
      </v-col>
      <v-col>
        <div>
          <QuillEditor
            v-model:content="inputDesc.sponsor_instruction"
            content-type="html"
            :toolbar="customToolbar"
            :read-only="props.disabled"
            :placeholder="
              inputDesc.sponsor_instruction
                ? ''
                : t('CRFDescriptions.sponsor_instruction')
            "
          />
        </div>
      </v-col>
      <v-col>
        <div>
          <QuillEditor
            v-model:content="inputDesc.instruction"
            content-type="html"
            :toolbar="customToolbar"
            :read-only="props.disabled"
            :placeholder="
              inputDesc.instruction ? '' : t('CRFDescriptions.instruction')
            "
          />
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <div class="text-h5 mb-4">
          {{ $t('CRFDescriptions.select') }}
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <NNTable
          v-model="modelValue"
          :headers="headers"
          :items="descriptions"
          hide-default-switches
          hide-export-button
          :show-select="!disabled"
          :hide-default-footer="props.disabled"
          :hide-search-field="props.disabled"
          table-height="400px"
          :items-length="total"
          disable-filtering
          column-data-resource="concepts/odm-metadata/descriptions"
          @filter="getDescriptions"
        >
          <template #[`item.description`]="{ value }">
            <span v-html="sanitizeHTML(value)"></span>
          </template>
          <template #[`item.instruction`]="{ value }">
            <span v-html="sanitizeHTML(value)"></span>
          </template>
          <template #[`item.sponsor_instruction`]="{ value }">
            <span v-html="sanitizeHTML(value)"></span>
          </template>
        </NNTable>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ref, computed, onMounted } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import filteringParameters from '@/utils/filteringParameters'
import NNTable from '@/components/tools/NNTable.vue'
import parameters from '@/constants/parameters'
import crfs from '@/api/crfs'
import terms from '@/api/controlledTerminology/terms'
import regex from '@/utils/regex'
import { sanitizeHTML } from '@/utils/sanitize'

const { t } = useI18n()

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
})

const modelValue = defineModel({
  type: Array,
  default: () => [],
})

const headers = computed(() => [
  { title: t('CRFDescriptions.language'), key: 'language', width: '10%' },
  { title: t('CRFDescriptions.name'), key: 'name' },
  { title: t('CRFDescriptions.description'), key: 'description' },
  {
    title: t('CRFDescriptions.sponsor_instruction'),
    key: 'sponsor_instruction',
  },
  { title: t('CRFDescriptions.instruction'), key: 'instruction' },
])

const customToolbar = ref([
  ['bold', 'italic', 'underline'],
  [{ script: 'sub' }, { script: 'super' }],
  [{ list: 'ordered' }, { list: 'bullet' }],
])

const inputDesc = ref({
  language: '',
  name: '',
  description: '',
  instruction: '',
  sponsor_instruction: '',
})

const languages = ref([])
const descriptions = ref([])
const total = ref(0)

onMounted(() => {
  terms.getTermsByCodelist('language').then((resp) => {
    languages.value = resp.data.items.filter(
      (el) => el.submission_value.toLowerCase() !== parameters.ENG
    )
  })

  getDescriptions()
})

const getDescriptions = (filters, options, filtersUpdated) => {
  if (props.disabled) {
    descriptions.value = [...modelValue.value]
  } else {
    const params = filteringParameters.prepareParameters(
      options,
      null,
      filtersUpdated
    )
    params.search = options.search
    params.exclude_english = true
    crfs.getDescriptions(params).then((resp) => {
      descriptions.value = [
        ...modelValue.value,
        ...resp.data.items.filter((description) => {
          return !modelValue.value.some(
            (d) =>
              d.name === description.name &&
              d.language === description.language &&
              d.description === description.description &&
              d.instruction === description.instruction &&
              d.sponsor_instruction === description.sponsor_instruction
          )
        }),
      ]
      total.value = resp.data.total
    })
  }
}

const addDescription = () => {
  if (inputDesc.value.language && inputDesc.value.name) {
    const desc = {
      language: inputDesc.value.language,
      name: inputDesc.value.name.name || inputDesc.value.name,
      description: regex.clearEmptyHtml(inputDesc.value.description),
      instruction: regex.clearEmptyHtml(inputDesc.value.instruction),
      sponsor_instruction: regex.clearEmptyHtml(
        inputDesc.value.sponsor_instruction
      ),
    }

    const isDuplicate = descriptions.value.some(
      (d) =>
        d.language === desc.language &&
        d.name === desc.name &&
        d.description === desc.description &&
        d.instruction === desc.instruction &&
        d.sponsor_instruction === desc.sponsor_instruction
    )

    if (!isDuplicate) {
      descriptions.value.push({ ...desc })
    }

    modelValue.value.push({ ...desc })
    inputDesc.value = {}
  }
}

const autocompleteValues = (val) => {
  if (val) {
    inputDesc.value.language = val.language || inputDesc.value.language
    inputDesc.value.description =
      val.description || regex.clearEmptyHtml(inputDesc.value.description)
    inputDesc.value.instruction =
      val.instruction || regex.clearEmptyHtml(inputDesc.value.instruction)
    inputDesc.value.sponsor_instruction =
      val.sponsor_instruction ||
      regex.clearEmptyHtml(inputDesc.value.sponsor_instruction)
  }
}
</script>
