<template>
  <v-select
    v-model="model"
    :items="termsStore.terms"
    item-title="sponsor_preferred_name"
    item-value="term_uid"
    return-object
    bg-color="nnWhite"
    clear-icon="mdi-close"
    clearable
    multiple
    :loading="loading"
    clear-on-select
    @update:search="updateTerms"
  >
    <template #item="{ props }">
      <v-list-item v-bind="props" @click="props.onClick">
        <template #prepend="{ isActive }">
          <v-list-item-action start>
            <v-checkbox-btn :model-value="isActive" />
          </v-list-item-action>
        </template>
        <template #title>
          {{ props.title }}
        </template>
      </v-list-item>
    </template>
    <template #selection="{ index }">
      <div v-if="index === 0">
        <span>
          {{ termslabel }}
        </span>
      </div>
      <span v-if="index === 1" class="text-grey text-caption mr-1">
        (+{{ model.length - 1 }})
      </span>
    </template>
    <template #prepend-item>
      <v-row @keydown.stop>
        <v-text-field
          v-model="search"
          class="pl-6"
          :placeholder="$t('_global.search')"
          @update:model-value="updateTerms"
        />
        <v-btn
          variant="text"
          size="small"
          icon="mdi-close"
          class="mr-3 mt-3"
          @click="search = ''"
        />
      </v-row>
    </template>
  </v-select>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useTermsStore } from '@/stores/library-terms'
import _debounce from 'lodash/debounce'

const props = defineProps({
  library: {
    type: String,
    default: null,
  },
})
const model = defineModel({ type: Array })

const termsStore = useTermsStore()

const loading = ref(false)
const search = ref('')

const termslabel = computed(() => {
  let label = ''
  let labelLength = model.value.length === 1 ? 36 : 30
  if (model.value[0].sponsor_preferred_name.length > 30) {
    label =
      model.value[0].sponsor_preferred_name.substring(0, labelLength) + '...'
  } else {
    label = model.value[0].sponsor_preferred_name
  }
  return label
})

const _updateTerms = async () => {
  loading.value = true
  const filters = {}

  if (search.value && search.value !== '') {
    filters['*'] = { v: [search.value] }
  }
  if (props.library) {
    filters['codelists.library_name'] = { v: [props.library] }
  }

  try {
    await termsStore.fetchTerms(filters, true)
  } finally {
    loading.value = false
  }
}
const updateTerms = _debounce(_updateTerms, 800)

await _updateTerms()
</script>
