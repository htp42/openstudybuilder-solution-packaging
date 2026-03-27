<template>
  <div class="d-flex">
    <template
      v-if="
        props.activityItemClass.name !== 'unit_dimension' &&
        codelists.length > 1
      "
    >
      <v-select
        v-model="codelist"
        :label="$t('ActivityInstanceForm.codelist')"
        :items="codelists"
        item-value="codelist_uid"
        item-title="name.name"
        bg-color="white"
        class="mr-4"
        :disabled="props.disabled"
        :loading="loadingCodelists"
        @update:model-value="changeCodelist"
      />
    </template>
    <v-select
      v-model="model"
      :label="props.label"
      :items="allowedValues"
      item-value="term_uid"
      :item-title="props.itemTitle"
      bg-color="white"
      :disabled="props.disabled"
      :rules="props.rules"
      :multiple="props.multiple"
      :loading="loading"
    >
      <template #prepend-item>
        <v-row @keydown.stop>
          <v-text-field
            v-model="search"
            class="pl-6"
            :placeholder="$t('_global.search')"
          />
          <v-btn
            variant="text"
            size="small"
            icon="mdi-close"
            class="mr-3 mt-3"
            @click="reset"
          />
        </v-row>
      </template>
    </v-select>
  </div>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { i18n } from '@/plugins/i18n'
import activityItemClassesApi from '@/api/activityItemClasses'
import codelistsApi from '@/api/controlledTerminology/codelists'
import _debounce from 'lodash/debounce'

const emit = defineEmits(['updatecodelist'])

const props = defineProps({
  activityItemClass: {
    type: Object,
    default: null,
  },
  dataDomain: {
    type: String,
    default: null,
  },
  label: {
    type: String,
    default: () => i18n.t('ActivityInstanceForm.value'),
  },
  itemTitle: {
    type: String,
    default: 'title',
  },
  multiple: {
    type: Boolean,
    default: false,
  },
  rules: {
    type: Array,
    default: () => [],
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})
const codelist = defineModel('codelist', { type: String })
const model = defineModel({ type: [String, Array] })
const search = defineModel('search', { type: String })

const codelists = ref([])
const allowedValues = ref([])
const loading = ref(false)
const loadingCodelists = ref(false)

const changeCodelist = (codelist) => {
  // find the selected codelist object in the codelists array
  const selectedCodelist = codelists.value.find(
    (item) => item.codelist_uid === codelist
  )
  emit('updatecodelist', selectedCodelist)
  fetchTerms(codelist)
}

const fetchTerms = _debounce(function (codelist) {
  loading.value = true
  const params = {
    page_size: 50,
    sort_by: JSON.stringify({ sponsor_preferred_name: true }),
  }
  if (search.value) {
    params.filters = { '*': { v: [search.value] } }
  }
  codelistsApi.getCodelistTerms(codelist, params).then((resp) => {
    allowedValues.value = []
    if (model.value) {
      let present
      if (typeof model.value === 'string') {
        present = resp.data.items.find((item) => item.term_uid === model.value)
      } else {
        for (const item of resp.data.items) {
          if (model.value.includes(item.term_uid)) {
            present = true
            break
          }
        }
      }
      if (!present) {
        model.value = null
      }
    }
    allowedValues.value = resp.data.items
    loading.value = false
  })
}, 800)

const fetchCodelists = async () => {
  loadingCodelists.value = true
  try {
    const params = {
      page_size: 0,
      ct_catalogue_name: 'SDTM CT',
    }
    if (props.activityItemClass.name === 'categoric_finding_original_result') {
      params.valid_codelists_for_item = true
    }
    const resp = await activityItemClassesApi.getDatasetCodelists(
      props.activityItemClass.uid,
      props.dataDomain,
      params
    )
    codelists.value = resp.data.items
    if (codelists.value.length === 1) {
      codelist.value = codelists.value[0].codelist_uid
      nextTick(() => {
        fetchTerms(codelist.value)
      })
    }
  } finally {
    loadingCodelists.value = false
  }
}

const reset = () => {
  if (search.value && search.value !== '') {
    model.value = null
    allowedValues.value = []
    search.value = ''
  }
}

watch(search, () => {
  if (codelist.value) {
    fetchTerms(codelist.value)
  }
})
watch(codelist, () => {
  fetchTerms(codelist.value)
})
watch(
  () => props.activityItemClass,
  async (value) => {
    if (!value) {
      return
    }
    if (value.name !== 'unit_dimension') {
      await fetchCodelists()
    } else {
      const resp = await codelistsApi.getAll({
        filters: {
          'name.name': { v: ['Unit Dimension'] },
        },
      })
      fetchTerms(resp.data.items[0].codelist_uid)
      codelist.value = resp.data.items[0].codelist_uid
    }
  },
  { immediate: true }
)

watch(
  () => props.dataDomain,
  () => {
    codelist.value = null
    fetchCodelists()
  }
)

defineExpose({
  allowedValues,
})
</script>
