<template>
  <SimpleFormDialog
    ref="dialog"
    content-class="h-100"
    :title="title"
    :open="props.open"
    @close="close"
    @submit="submit"
  >
    <template #body>
      <v-row class="mb-6 align-center">
        <v-col cols="6">
          <v-text-field
            v-model="codelistSearch"
            clearable
            clear-icon="mdi-close"
            prepend-inner-icon="mdi-magnify"
            :label="$t('TermsSelectionForm.search_for_codelists')"
            color="nnBaseBlue"
            hide-details
            @update:model-value="fetchCodelists"
          />
          <v-radio-group v-model="searchMode" inline>
            <v-radio
              value="name"
              :label="$t('TermsSelectionForm.search_by_codelist')"
            />
            <v-radio
              value="term"
              :label="$t('TermsSelectionForm.search_by_term')"
            />
          </v-radio-group>
        </v-col>
        <v-col cols="6" class="pl-8">
          <v-switch
            v-model="searchParams.only_ordinal_codelists"
            :label="$t('TermsSelectionForm.ordinal_codelists')"
            class="mr-4"
            hide-details
            @update:model-value="_fetchCodelists"
          />
          <v-switch
            v-model="searchParams.only_response_codelists"
            :label="$t('TermsSelectionForm.response_codelists')"
            class="mr-4"
            hide-details
            @update:model-value="_fetchCodelists"
          />
          <v-switch
            v-model="searchParams.match_whole_words"
            :label="$t('TermsSelectionForm.whole_word_match')"
            hide-details
          />
        </v-col>
      </v-row>
      <div class="d-flex">
        <div class="w-50">
          <v-sheet border="thin" rounded="lg">
            <div class="dialog-sub-title px-2 pb-2">
              {{ $t('TermsSelectionForm.select_codelist') }}
            </div>
            <v-data-iterator
              :items="codelists"
              :page="codelistPage"
              :items-per-page="10"
            >
              <template #default="{ items }">
                <div
                  v-for="item in items"
                  :key="item.raw.uid"
                  class="pa-2 border-t-thin codelist"
                  :class="{
                    'bg-primary': selectedCodelist?.uid === item.raw.uid,
                  }"
                  @click="selectCodelist(item.raw)"
                >
                  {{ item.raw.submission_value }} ({{ item.raw.library_name
                  }}<template v-if="item.raw.is_ordinal">
                    <strong>{{ $gettext('_global.ordinal') }}</strong></template
                  >)
                  <div class="text-grey">
                    {{ truncate(item.raw.sponsor_preferred_name) }}
                  </div>
                </div>
              </template>
              <template #footer>
                <v-pagination
                  v-model="codelistPage"
                  class="border-t-thin px-2"
                  size="small"
                  :length="codelistPages"
                  :total-visible="5"
                  @update:model-value="_fetchCodelists()"
                />
              </template>
            </v-data-iterator>
          </v-sheet>
        </div>
        <div v-if="selectedCodelist" class="ml-4 w-50">
          <v-sheet border="thin" rounded="lg">
            <div class="dialog-sub-title px-2 pb-2">
              {{ $t('TermsSelectionForm.select_terms') }}
            </div>
            <v-data-iterator
              :items="terms"
              :page="termPage"
              :items-per-page="10"
            >
              <template #default="{ items }">
                <div
                  v-for="item in items"
                  :key="item.raw.term_uid"
                  class="pa-2 border-t-thin codelist d-flex items-center"
                >
                  <v-checkbox
                    v-model="selectedTerms"
                    :value="item.raw.term_uid"
                    hide-details
                    class="mr-2"
                  />
                  <div>
                    {{ item.raw.submission_value }}
                    <div class="text-grey">
                      {{ truncate(item.raw.sponsor_preferred_name) }}
                    </div>
                  </div>
                </div>
              </template>
              <template #footer>
                <v-pagination
                  v-model="termPage"
                  class="border-t-thin px-2"
                  size="small"
                  :length="termPages"
                  :total-visible="5"
                  @update:model-value="_fetchTerms()"
                />
              </template>
            </v-data-iterator>
          </v-sheet>
        </div>
      </div>
    </template>
  </SimpleFormDialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import _debounce from 'lodash/debounce'
import codelistApi from '@/api/controlledTerminology/codelists'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog.vue'

const pageSize = 10

const props = defineProps({
  open: Boolean,
})
const emit = defineEmits(['close', 'selected'])

const codelist = defineModel('codelist', { type: String })
const termSelection = defineModel('termSelection', { type: Array })

const { t } = useI18n()

const codelistPages = computed(() => {
  return totalCodelists.value > pageSize
    ? Math.floor(totalCodelists.value / pageSize)
    : 1
})
const termPages = computed(() => {
  return totalTerms.value > pageSize
    ? Math.floor(totalTerms.value / pageSize)
    : 1
})
const title = computed(() => {
  return t('TermsSelectionForm.title')
})

const codelists = ref([])
const dialog = ref()
const codelistPage = ref(1)
const codelistSearch = ref('')
const loadingCodelists = ref(false)
const loadingTerms = ref(false)
const searchMode = ref('name')
const searchParams = ref({
  only_response_codelists: true,
})
const selectedCodelist = ref(null)
const selectedTerms = ref([])
const termPage = ref(1)
const termSearch = ref([])
const terms = ref([])
const totalCodelists = ref(0)
const totalTerms = ref(0)

async function _fetchCodelists() {
  if (!codelistSearch.value || codelistSearch.value === '') {
    reset()
    return
  }
  loadingCodelists.value = true
  selectedCodelist.value = null
  selectedTerms.value = []
  try {
    const params = {
      ...searchParams.value,
      page_number: codelistPage.value,
      search_string: codelistSearch.value,
    }
    let resp
    if (searchMode.value === 'name') {
      resp = await codelistApi.search(params)
    } else {
      resp = await codelistApi.searchByTerm(params)
    }
    codelists.value = resp.data.items
    totalCodelists.value = resp.data.total
  } finally {
    loadingCodelists.value = false
  }
}
const fetchCodelists = _debounce(_fetchCodelists, 300)

async function _fetchTerms() {
  loadingTerms.value = true
  try {
    const params = {
      page_number: termPage.value,
      total_count: true,
    }
    if (termSearch.value && termSearch.value.length) {
      params.filters = { '*': { v: [termSearch.value] } }
    }
    const resp = await codelistApi.getCodelistTerms(
      selectedCodelist.value.uid,
      params
    )
    terms.value = resp.data.items
    totalTerms.value = resp.data.total
  } finally {
    loadingTerms.value = false
  }
}

function truncate(name) {
  const limit = 50
  return name.length < limit ? name : `${name.substr(0, limit)}...`
}

function reset() {
  codelists.value = []
  totalCodelists.value = 0
  codelistPage.value = 1
  terms.value = []
  totalTerms.value = 0
  termPage.value = 1
  selectedTerms.value = []
  selectedCodelist.value = null
  codelistSearch.value = ''
  termSearch.value = []
}

function close() {
  reset()
  emit('close')
}

function selectCodelist(codelist) {
  selectedCodelist.value = codelist
}

function submit() {
  codelist.value = selectedCodelist.value.uid
  termSelection.value = [...selectedTerms.value]
  emit('selected')
  close()
}

watch(selectedCodelist, () => {
  if (selectedCodelist.value) {
    _fetchTerms()
  }
})
</script>

<style lang="scss" scoped>
.codelist {
  cursor: pointer;
}
</style>
