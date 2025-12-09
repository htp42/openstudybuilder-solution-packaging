<template>
  <td :colspan="columns.length" class="pa-0">
    <v-data-table
      id="items"
      :initial-sort-by="[{ key: 'order_number', order: 'asc' }]"
      :headers="columns"
      :items="items"
      item-value="name"
      light
      :loading="loading"
      :items-per-page="-1"
    >
      <template #headers="{ columns }">
        <tr>
          <template v-for="column in columns" :key="column.key">
            <td>
              <span>{{ column.title }}</span>
            </td>
          </template>
        </tr>
      </template>
      <template #bottom />
      <template #item="{ item, index }">
        <tr style="background-color: var(--v-dfltBackground-base)">
          <td width="45%" :class="'font-weight-bold'">
            <v-row class="align-center">
              <v-btn variant="text" icon class="ml-12 hide" />
              <CrfTreeReorderButtons
                :sort-mode="sortMode"
                :is-parent-draft="parentItemGroup.status === statuses.DRAFT"
                :sibling-length="parentItemGroup.items.length"
                :item="item"
                :index="index"
                @order-up="orderUp"
                @order-down="orderDown"
              />
              <ActionsMenu :actions="actions" :item="item" />
              <span class="ml-2">
                <v-icon color="crfItem"> mdi-alpha-i-circle </v-icon>
                <v-tooltip
                  v-if="item.name.length > 60"
                  location="top"
                  max-width="300"
                  :text="item.name"
                  interactive
                >
                  <template #activator="{ props }">
                    <span v-bind="props">{{
                      item.name.substring(0, 60) + '...'
                    }}</span>
                  </template>
                </v-tooltip>
                <span v-else>{{ item.name }}</span>
              </span>
            </v-row>
          </td>
          <td width="10%">
            <CrfTreeTooltipsHandler :item="item" value="mandatory" />
            <CrfTreeTooltipsHandler :item="item" value="locked" />
            <CrfTreeTooltipsHandler :item="item" value="refAttrs" />
          </td>
          <td width="10%">
            <CrfTreeTooltipsHandler :item="item" value="dataType" />
            <CrfTreeTooltipsHandler :item="item" value="vendor" />
          </td>
          <td width="10%">
            <StatusChip :status="item.status" />
          </td>
          <td width="10%">
            {{ item.version }}
          </td>
          <td width="15%">
            <v-btn width="150px" rounded size="small" class="hide" />
          </td>
        </tr>
      </template>
    </v-data-table>
  </td>
  <v-dialog v-model="showItemForm" persistent content-class="fullscreen-dialog">
    <CrfItemForm
      :selected-item="selectedItem"
      :read-only-prop="selectedItem && selectedItem.status === statuses.FINAL"
      class="fullscreen-dialog"
      @close="closeDefinition"
      @update-item="updateItem"
      @link-item="linkItem"
    />
  </v-dialog>
  <v-dialog
    v-model="showExportForm"
    max-width="800px"
    persistent
    @keydown.esc="closeExportForm"
  >
    <CrfExportForm :item="selectedItem" type="item" @close="closeExportForm" />
  </v-dialog>
  <CrfReferencesForm
    :open="showAttributesForm"
    :parent="parentItemGroup"
    :element="selectedItem"
    :read-only="selectedItem.status === statuses.FINAL"
    @close="closeAttributesForm"
  />
  <CrfNewVersionSummaryConfirmDialog ref="confirmNewVersion" />
</template>

<script>
import crfs from '@/api/crfs'
import CrfTreeTooltipsHandler from '@/components/library/crfs/CrfTreeTooltipsHandler.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import statuses from '@/constants/statuses'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import CrfItemForm from '@/components/library/crfs/CrfItemForm.vue'
import CrfExportForm from '@/components/library/crfs/CrfExportForm.vue'
import CrfReferencesForm from '@/components/library/crfs/CrfReferencesForm.vue'
import CrfTreeReorderButtons from '@/components/library/crfs/CrfTreeReorderButtons.vue'
import crfTypes from '@/constants/crfTypes'
import CrfNewVersionSummaryConfirmDialog from '@/components/library/crfs/CrfNewVersionSummaryConfirmDialog.vue'

export default {
  components: {
    CrfTreeTooltipsHandler,
    StatusChip,
    ActionsMenu,
    CrfItemForm,
    CrfExportForm,
    CrfReferencesForm,
    CrfTreeReorderButtons,
    CrfNewVersionSummaryConfirmDialog,
  },
  inject: ['notificationHub'],
  props: {
    parentItemGroup: {
      type: Object,
      default: null,
    },
    columns: {
      type: Array,
      default: null,
    },
    refreshItems: {
      type: Number,
      default: null,
    },
    sortMode: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['updateParentItemGroupItem'],
  data() {
    return {
      items: [],
      loading: false,
      selectedItem: {},
      showItemForm: false,
      actions: [
        {
          label: this.$t('CRFTree.open_def'),
          icon: 'mdi-arrow-left',
          click: this.openDefinition,
        },
        {
          label: this.$t('CRFTree.edit_reference'),
          icon: 'mdi-pencil-outline',
          click: this.editAttributes,
          condition: (item) => item.status === statuses.DRAFT,
          accessRole: this.$roles.LIBRARY_WRITE,
        },
        {
          label: this.$t('CRFTree.preview_odm'),
          icon: 'mdi-file-xml-box',
          click: this.previewODM,
        },
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          click: this.approve,
          condition: (item) => item.status === statuses.DRAFT,
          accessRole: this.$roles.LIBRARY_WRITE,
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          click: this.newVersion,
          condition: (item) => item.status === statuses.FINAL,
          accessRole: this.$roles.LIBRARY_WRITE,
        },
        {
          label: this.$t('_global.export'),
          icon: 'mdi-download-outline',
          click: this.openExportForm,
        },
      ],
      showExportForm: false,
      showAttributesForm: false,
    }
  },
  watch: {
    refreshItems() {
      this.fetchItems()
    },
  },
  created() {
    this.statuses = statuses
  },
  mounted() {
    this.fetchItems()
  },
  methods: {
    async newVersion(item) {
      if (
        await this.$refs.confirmNewVersion.open({
          agreeLabel: this.$t('CRFItems.create_new_version'),
          item: item,
        })
      ) {
        this.loading = true

        crfs
          .newVersion('items', item.uid)
          .then((resp) => {
            if (this.parentItemGroup.status === statuses.DRAFT) {
              this.updateItem(resp.data)
            }

            this.notificationHub.add({
              msg: this.$t('_global.new_version_success'),
            })
          })
          .finally(() => {
            this.loading = false
          })
      }
    },
    async approve(item) {
      this.loading = true

      crfs
        .approve('items', item.uid)
        .then((resp) => {
          this.updateItem(resp.data)

          this.notificationHub.add({
            msg: this.$t('CRFItems.approved'),
          })
        })
        .finally(() => {
          this.loading = false
        })
    },
    async fetchItems() {
      this.loading = true
      this.items = []
      for (const items of this.parentItemGroup.items) {
        let rs = await crfs.get(`items/${items.uid}`, {
          params: { version: items.version },
        })
        this.items.push({ ...items, ...rs.data })
      }
      this.loading = false
    },
    updateItem(item) {
      this.items = this.items.map((i) =>
        i.uid === item.uid ? { ...i, ...item } : i
      )
      this.$emit('updateParentItemGroupItem', this.parentItemGroup, item)
    },
    openDefinition(item) {
      this.selectedItem = item
      this.showItemForm = true
    },
    closeDefinition() {
      this.selectedItem = {}
      this.showItemForm = false
      this.fetchItems()
    },
    openExportForm(item) {
      this.selectedItem = item
      this.showExportForm = true
    },
    closeExportForm() {
      this.selectedItem = {}
      this.showExportForm = false
    },
    editAttributes(item) {
      this.selectedItem = item
      this.showAttributesForm = true
    },
    closeAttributesForm() {
      this.selectedItem = {}
      this.showAttributesForm = false
    },
    previewODM(item) {
      this.$router.push({
        name: 'CrfBuilder',
        params: {
          tab: 'odm-viewer',
          uid: item.uid,
          type: crfTypes.ITEM,
        },
      })
    },
    orderUp(item, index) {
      if (index === 0) {
        return
      } else {
        this.items[index].order_number--
        this.items[index - 1].order_number++
        this.items.sort((a, b) => {
          return a.order_number - b.order_number
        })
        crfs.addItemsToItemGroup(this.items, this.parentItemGroup.uid, true)
      }
    },
    orderDown(item, index) {
      if (index === this.items.length - 1) {
        return
      } else {
        this.items[index].order_number++
        this.items[index + 1].order_number--
        this.items.sort((a, b) => {
          return a.order_number - b.order_number
        })
        crfs.addItemsToItemGroup(this.items, this.parentItemGroup.uid, true)
      }
    },
  },
}
</script>
<style scoped>
#forms .v-table__wrapper > table > thead > tr {
  visibility: collapse;
}
</style>
