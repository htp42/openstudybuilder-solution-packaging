<template>
  <v-select
    v-model="model"
    :items="terms"
    item-value="term_uid"
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
          @update:model-value="fetchTerms()"
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
</template>

<script setup>
import { ref } from 'vue'
import _debounce from 'lodash/debounce'
import termsApi from '@/api/controlledTerminology/terms'

const props = defineProps({
  codelist: {
    type: String,
    default: null,
  },
})
const model = defineModel({ type: String })

const loading = ref(false)
const search = ref('')
const terms = ref([])

const fetchTerms = _debounce(function () {
  loading.value = true
  const params = {
    page_size: 50,
    sort_by: JSON.stringify({ sponsor_preferred_name: true }),
  }
  if (search.value) {
    params.filters = { '*': { v: [search.value] } }
  }
  termsApi.getTermsByCodelist(props.codelist, params).then((resp) => {
    terms.value = []
    const present = resp.data.items.find(
      (item) => item.term_uid === model.value
    )
    if (model.value && !present) {
      model.value = null
    }
    terms.value = resp.data.items
    loading.value = false
  })
}, 800)

const reset = () => {
  if (search.value && search.value !== '') {
    model.value = null
    terms.value = []
    search.value = ''
  }
}

fetchTerms()
</script>
