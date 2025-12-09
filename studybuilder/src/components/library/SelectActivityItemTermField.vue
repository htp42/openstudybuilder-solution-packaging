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
        variant="outlined"
        density="compact"
        hide-details
        class="mr-4"
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
      variant="outlined"
      density="compact"
      hide-details
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
})
const codelist = defineModel('codelist', { type: String })
const model = defineModel({ type: String })
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
    const present = resp.data.items.find(
      (item) => item.term_uid === model.value
    )
    if (model.value && !present) {
      model.value = null
    }
    allowedValues.value = resp.data.items
    loading.value = false
  })
}, 800)

const fetchCodelists = async () => {
  loadingCodelists.value = true
  try {
    const resp = await activityItemClassesApi.getDatasetCodelists(
      props.activityItemClass.uid,
      props.dataDomain,
      { page_size: 0 }
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
