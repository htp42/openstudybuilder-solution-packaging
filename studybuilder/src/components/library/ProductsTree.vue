<template>
  <div class="pa-4 bg-white d-flex align-center" style="overflow-x: auto">
    <v-spacer />
    <v-btn
      size="small"
      color="nnBaseBlue"
      :title="$t('MedicinalProductForm.add_title')"
      :disabled="!accessGuard.checkPermission($roles.LIBRARY_WRITE)"
      icon="mdi-plus"
      variant="outlined"
      @click.stop="showForm = true"
    />
    <v-btn
      class="ml-2"
      size="small"
      variant="outlined"
      color="nnBaseBlue"
      :title="$t('NNTableTooltips.history')"
      icon="mdi-history"
      @click="openGlobalHistory"
    />
  </div>
  <div class="pa-4 bg-white">
    <MedicinalProductOverview
      v-for="product in medicinalProducts"
      :key="product.uid"
      :product="product"
      class="mb-4"
    >
      <template #prepend>
        <ActionsMenu :actions="actions" :item="product" />
      </template>
    </MedicinalProductOverview>
  </div>
  <v-dialog
    v-model="showForm"
    fullscreen
    persistent
    content-class="fullscreen-dialog"
  >
    <MedicinalProductForm
      :medicinal-product-uid="selectedItem ? selectedItem.uid : null"
      :open="showForm"
      @close="closeForm"
      @created="fetchItems"
      @updated="fetchItems"
    />
  </v-dialog>
  <v-dialog
    v-model="showHistory"
    persistent
    :fullscreen="$globals.historyDialogFullscreen"
    @keydown.esc="showHistory = false"
  >
    <HistoryTable
      :title="historyTitle"
      :headers="historyHeaders"
      :items="historyItems"
      :items-total="historyItems.length"
      change-field="change_description"
      @close="showHistory = false"
    />
  </v-dialog>
  <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAccessGuard } from '@/composables/accessGuard'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import HistoryTable from '@/components/tools/HistoryTable.vue'
import MedicinalProductForm from '@/components/library/MedicinalProductForm.vue'
import MedicinalProductOverview from '@/components/library/MedicinalProductOverview.vue'
import medicinalProductsApi from '@/api/concepts/medicinalProducts'
import filteringParameters from '@/utils/filteringParameters'

const { t } = useI18n()
const eventBusEmit = inject('eventBusEmit')
const roles = inject('roles')
const props = defineProps({
  tabClickedAt: {
    type: Number,
    default: null,
  },
})
const accessGuard = useAccessGuard()

const actions = [
  {
    label: t('_global.edit'),
    icon: 'mdi-pencil-outline',
    iconColor: 'primary',
    condition: (item) =>
      item.possible_actions.find((action) => action === 'edit'),
    accessRole: roles.LIBRARY_WRITE,
    click: editItem,
  },
  {
    label: t('_global.approve'),
    icon: 'mdi-check-decagram',
    iconColor: 'success',
    condition: (item) =>
      item.possible_actions.find((action) => action === 'approve'),
    accessRole: roles.LIBRARY_WRITE,
    click: approveItem,
  },
  {
    label: t('_global.new_version'),
    icon: 'mdi-plus-circle-outline',
    iconColor: 'primary',
    condition: (item) =>
      item.possible_actions.find((action) => action === 'new_version'),
    accessRole: roles.LIBRARY_WRITE,
    click: createNewVersion,
  },
  {
    label: t('_global.inactivate'),
    icon: 'mdi-close-octagon-outline',
    iconColor: 'primary',
    condition: (item) =>
      item.possible_actions.find((action) => action === 'inactivate'),
    accessRole: roles.LIBRARY_WRITE,
    click: inactivateItem,
  },
  {
    label: t('_global.reactivate'),
    icon: 'mdi-undo-variant',
    iconColor: 'primary',
    condition: (item) =>
      item.possible_actions.find((action) => action === 'reactivate'),
    accessRole: roles.LIBRARY_WRITE,
    click: reactivateItem,
  },
  {
    label: t('_global.delete'),
    icon: 'mdi-delete-outline',
    iconColor: 'error',
    condition: (item) =>
      item.possible_actions.find((action) => action === 'delete'),
    accessRole: roles.LIBRARY_WRITE,
    click: deleteItem,
  },
  {
    label: t('_global.history'),
    icon: 'mdi-history',
    click: openHistory,
  },
]
const headers = [
  { title: t('_global.name'), key: 'name' },
  { title: t('MedicinalProduct.compound'), key: 'compound.name' },
]

const medicinalProducts = ref([])

const historyItems = ref([])
const selectedItem = ref(null)
const showForm = ref(false)
const showHistory = ref(false)
const confirm = ref()

const historyTitle = computed(() => {
  if (selectedItem.value) {
    return t('ProductsTree.history_title', { product: selectedItem.value.uid })
  }
  return t('_global.audit_trail')
})

const historyHeaders = computed(() => {
  if (selectedItem.value) {
    return headers
  }
  const result = [...headers]
  result.unshift({
    title: t('_global.uid'),
    key: 'uid',
  })
  return result
})

watch(
  () => props.tabClickedAt,
  () => {
    fetchItems()
  }
)

onMounted(() => {
  fetchItems()
})

function fetchItems(filters, options, filtersUpdated) {
  const params = filteringParameters.prepareParameters(
    options,
    filters,
    filtersUpdated
  )
  medicinalProductsApi.getFiltered(params).then((resp) => {
    medicinalProducts.value = resp.data.items
  })
}

function closeForm() {
  showForm.value = false
  selectedItem.value = null
}

function editItem(item) {
  selectedItem.value = item
  showForm.value = true
}

function approveItem(item) {
  medicinalProductsApi.approve(item.uid).then(() => {
    fetchItems()
    eventBusEmit('notification', {
      msg: t('ProductsTree.approve_success'),
      type: 'success',
    })
  })
}

async function deleteItem(item) {
  const options = { type: 'warning' }
  const product = item.name
  if (
    await confirm.value.open(
      t('ProductsTree.confirm_delete', { product }),
      options
    )
  ) {
    await medicinalProductsApi.deleteObject(item.uid)
    fetchItems()
    eventBusEmit('notification', {
      msg: t('ProductsTree.delete_success'),
      type: 'success',
    })
  }
}

function createNewVersion(item) {
  medicinalProductsApi.newVersion(item.uid).then(() => {
    fetchItems()
    eventBusEmit('notification', {
      msg: t('ProductsTree.new_version_success'),
      type: 'success',
    })
  })
}

function inactivateItem(item) {
  medicinalProductsApi.inactivate(item.uid).then(() => {
    fetchItems()
    eventBusEmit('notification', {
      msg: t('ProductsTree.inactivate_success'),
      type: 'success',
    })
  })
}

function reactivateItem(item) {
  medicinalProductsApi.reactivate(item.uid).then(() => {
    fetchItems()
    eventBusEmit('notification', {
      msg: t('ProductsTree.reactivate_success'),
      type: 'success',
    })
  })
}

async function openHistory(item) {
  selectedItem.value = item
  const resp = await medicinalProductsApi.getVersions(selectedItem.value.uid)
  historyItems.value = resp.data
  showHistory.value = true
}

async function openGlobalHistory() {
  const resp = await medicinalProductsApi.getAllVersions({ page_size: 0 })
  historyItems.value = resp.data.items
  showHistory.value = true
}
</script>
