<template>
  <SimpleFormDialog
    ref="form"
    :title="$t('CRFTree.link') + ' ' + itemsTypeName"
    :help-items="helpItems"
    :open="open"
    max-width="1200px"
    @close="close"
    @submit="submit"
  >
    <template #body>
      <v-col class="pt-0 mt-0">
        <NNTable
          :headers="availableItemsHeaders"
          item-value="uid"
          :items="items"
          hide-export-button
          hide-default-switches
          only-text-search
          column-data-resource="ct/codelists"
          :items-length="total"
          table-height="auto"
          @filter="getItems"
        >
          <template #[`item.desc`]="{ item }">
            <div v-html="sanitizeHTMLHandler(getDescription(item))" />
          </template>
          <template #[`item.notes`]="{ item }">
            <div v-html="sanitizeHTMLHandler(getNotes(item))" />
          </template>
          <template #[`item.add`]="{ item }">
            <v-btn
              v-if="!checkIfLinked(item)"
              icon="mdi-content-copy"
              class="mt-1 rightButtons"
              data-cy="add-item-link"
              variant="text"
              @click="addItem(item)"
            />
            <v-btn
              v-else
              icon="mdi-delete-outline"
              class="mt-1 rightButtons"
              color="error"
              data-cy="remove-item-link"
              variant="text"
              @click="removeItem(item)"
            />
          </template>
        </NNTable>
      </v-col>
    </template>
  </SimpleFormDialog>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog.vue'
import crfs from '@/api/crfs'
import constants from '@/constants/parameters'
import NNTable from '@/components/tools/NNTable.vue'
import filteringParameters from '@/utils/filteringParameters'
import { sanitizeHTML } from '@/utils/sanitize'

const props = defineProps({
  itemToLink: {
    type: Object,
    default: null,
  },
  itemsType: {
    type: String,
    default: null,
  },
  open: Boolean,
})

const emit = defineEmits(['close'])

const { t } = useI18n()

const helpItems = ref([])
const items = ref([])
const chosenItems = ref([])
const total = ref(0)

const availableItemsHeaders = computed(() => [
  { title: '', key: 'add', width: '5%' },
  { title: t('_global.name'), key: 'name', width: '25%' },
  { title: t('_global.description'), key: 'desc', width: '35%' },
  {
    title: t('CRFTree.sponsor_instruction'),
    key: 'notes',
    width: '35%',
  },
])

const itemsTypeName = computed(() => {
  if (props.itemsType === 'forms') {
    return t('CRFTree.forms')
  }
  if (props.itemsType === 'item-groups') {
    return t('CRFTree.item_groups')
  }
  return t('CRFTree.items')
})

watch(
  () => props.itemToLink,
  () => {
    initForm()
  }
)

onMounted(() => {
  initForm()
})

const sanitizeHTMLHandler = (html) => {
  return sanitizeHTML(html)
}

const getDescription = (item) => {
  const engDesc = item.translated_texts.find(
    (el) =>
      [constants.EN, constants.ENG].includes(el.language) &&
      el.text_type == 'Description'
  )
  return engDesc ? engDesc.text : ''
}

const getNotes = (item) => {
  const engDesc = item.translated_texts.find(
    (el) =>
      [constants.EN, constants.ENG].includes(el.language) &&
      el.text_type == 'osb:DesignNotes'
  )
  return engDesc ? engDesc.text : ''
}

const submit = () => {
  const payload = []
  chosenItems.value.forEach((el, index) => {
    payload.push({
      uid: el.uid ? el.uid : el,
      order_number: index + 1,
      mandatory: el.mandatory ? el.mandatory : 'No',
      data_entry_required: el.data_entry_required
        ? el.data_entry_required
        : 'No',
      sdv: el.sdv ? el.sdv : 'No',
      collection_exception_condition_oid: el.collection_exception_condition_oid
        ? el.collection_exception_condition_oid
        : null,
      vendor: { attributes: [] },
    })
  })
  switch (props.itemsType) {
    case 'forms':
      crfs
        .addFormsToCollection(payload, props.itemToLink.uid, true)
        .then(() => {
          emit('close')
        })
      return
    case 'item-groups':
      crfs.addItemGroupsToForm(payload, props.itemToLink.uid, true).then(() => {
        emit('close')
      })
      return
    case 'items':
      payload.forEach((el) => {
        el.key_sequence = el.key_sequence ? el.key_sequence : constants.NULL
        el.method_oid = el.method_oid ? el.method_oid : constants.NULL
        el.imputation_method_oid = el.imputation_method_oid
          ? el.imputation_method_oid
          : constants.NULL
        el.role = el.role ? el.role : constants.NULL
        el.role_codelist_oid = el.role_codelist_oid
          ? el.role_codelist_oid
          : constants.NULL
      })
      crfs.addItemsToItemGroup(payload, props.itemToLink.uid, true).then(() => {
        emit('close')
      })
  }
}

const addItem = (item) => {
  if (!chosenItems.value.some((el) => el.uid === item.uid)) {
    chosenItems.value.push(item)
  }
}

const checkIfLinked = (item) => {
  return chosenItems.value.some((el) => el.uid === item.uid)
}

const removeItem = (item) => {
  chosenItems.value = chosenItems.value.filter((el) => el.uid !== item.uid)
}

const close = () => {
  chosenItems.value = []
  items.value = []
  emit('close')
}

const initForm = () => {
  if (!props.itemToLink) {
    return
  }
  chosenItems.value = Array.from(
    new Set(
      props.itemToLink.forms ||
        props.itemToLink.item_groups ||
        props.itemToLink.items
    )
  )
  getItems()
}

const getItems = (filters, options, filtersUpdated) => {
  if (props.itemsType) {
    const parameters = filteringParameters.prepareParameters(
      options,
      filters,
      filtersUpdated
    )
    if (filters) {
      parameters.filters = JSON.parse(filters)
    }
    const params = {}
    params.params = parameters
    crfs.get(props.itemsType, params).then((resp) => {
      items.value = resp.data.items
      total.value = resp.data.total
    })
  }
}
</script>
<style scoped>
.rightButtons {
  float: right;
}
</style>
