<template>
  <td :colspan="columns.length" class="pa-0">
    <v-data-table
      id="itemGroups"
      v-model:expanded="expanded"
      :initial-sort-by="[{ key: 'order_number', order: 'asc' }]"
      :headers="columns"
      :items="itemGroups"
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
      <template #item="{ item, internalItem, toggleExpand, isExpanded, index }">
        <tr style="background-color: lightgrey">
          <td width="45%" :class="'font-weight-bold'">
            <v-row class="align-center">
              <v-btn
                v-if="isExpanded(internalItem)"
                icon="mdi-chevron-down"
                variant="text"
                class="ml-8"
                @click="toggleExpand(internalItem)"
              />
              <v-btn
                v-else-if="item.items && item.items.length > 0"
                icon="mdi-chevron-right"
                variant="text"
                class="ml-8"
                @click="toggleExpand(internalItem)"
              />
              <v-btn v-else variant="text" class="ml-8 hide" icon />
              <CrfTreeReorderButtons
                :sort-mode="sortMode"
                :is-parent-draft="parentForm.status === statuses.DRAFT"
                :sibling-length="parentForm.item_groups.length"
                :item="item"
                :index="index"
                @order-up="orderUp"
                @order-down="orderDown"
              />
              <ActionsMenu :actions="actions" :item="item" />
              <span class="ml-2">
                <v-icon color="crfGroup"> mdi-alpha-g-circle </v-icon>
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
            <CrfTreeTooltipsHandler :item="item" value="repeating" />
            <CrfTreeTooltipsHandler :item="item" value="is_reference_data" />
            <CrfTreeTooltipsHandler :item="item" value="vendor" />
          </td>
          <td width="10%">
            <StatusChip :status="item.status" />
          </td>
          <td width="10%">
            {{ item.version }}
          </td>
          <td width="15%">
            <v-menu v-if="item.status !== statuses.FINAL" offset-y>
              <template #activator="{ props }">
                <div>
                  <v-btn
                    v-show="item.status !== statuses.FINAL"
                    width="150px"
                    size="small"
                    rounded
                    v-bind="props"
                    color="crfItem"
                    :title="$t('CRFTree.link_items')"
                  >
                    <v-icon icon="mdi-plus" />
                    {{ $t('CRFTree.items') }}
                  </v-btn>
                </div>
              </template>
              <v-list>
                <v-list-item @click="openLinkForm(item)">
                  <template #prepend>
                    <v-icon icon="mdi-plus" />
                  </template>
                  <v-list-item-title>
                    {{ $t('CRFTree.link_existing') }}
                  </v-list-item-title>
                </v-list-item>
                <v-list-item @click="openCreateAndAddForm(item)">
                  <template #prepend>
                    <v-icon icon="mdi-pencil-outline" />
                  </template>
                  <v-list-item-title>
                    {{ $t('CRFTree.create_and_link') }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            <v-btn v-else width="150px" rounded size="small" class="hide" />
          </td>
        </tr>
      </template>
      <template #expanded-row="{ columns, item }">
        <CrfTreeItems
          :sort-mode="sortMode"
          :parent-item-group="item"
          :columns="columns"
          @update-parent-item-group-item="updateItemGroupItem"
        />
      </template>
    </v-data-table>
  </td>
  <v-dialog
    v-model="showItemGroupForm"
    persistent
    content-class="fullscreen-dialog"
  >
    <CrfItemGroupForm
      :selected-group="selectedItemGroup"
      :read-only-prop="
        selectedItemGroup && selectedItemGroup.status === statuses.FINAL
      "
      class="fullscreen-dialog"
      @close="closeDefinition"
      @update-item-group="updateItemGroup"
      @link-group="linkGroup"
    />
  </v-dialog>
  <CrfLinkForm
    :open="showLinkForm"
    :item-to-link="selectedItemGroup"
    items-type="items"
    @close="closeLinkForm"
  />
  <v-dialog
    v-model="showExportForm"
    max-width="800px"
    persistent
    @keydown.esc="closeExportForm"
  >
    <CrfExportForm
      :item="selectedItemGroup"
      type="item_group"
      @close="closeExportForm"
    />
  </v-dialog>
  <CrfReferencesForm
    :open="showAttributesForm"
    :parent="parentForm"
    :element="selectedItemGroup"
    :read-only="selectedItemGroup.status === statuses.FINAL"
    @close="closeAttributesForm"
  />
  <v-dialog
    v-model="showCreateForm"
    persistent
    content-class="fullscreen-dialog"
  >
    <CrfItemForm
      class="fullscreen-dialog"
      @close="closeCreateAndAddForm"
      @link-item="linkItem"
    />
  </v-dialog>
  <CrfApprovalSummaryConfirmDialog ref="confirmApproval" />
  <CrfNewVersionSummaryConfirmDialog ref="confirmNewVersion" />
</template>

<script>
import crfs from '@/api/crfs'
import CrfTreeItems from '@/components/library/crfs/crfTreeComponents/CrfTreeItems.vue'
import CrfTreeTooltipsHandler from '@/components/library/crfs/CrfTreeTooltipsHandler.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import statuses from '@/constants/statuses'
import CrfLinkForm from '@/components/library/crfs/CrfLinkForm.vue'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import CrfItemGroupForm from '@/components/library/crfs/CrfItemGroupForm.vue'
import _isEmpty from 'lodash/isEmpty'
import CrfExportForm from '@/components/library/crfs/CrfExportForm.vue'
import CrfReferencesForm from '@/components/library/crfs/CrfReferencesForm.vue'
import crfTypes from '@/constants/crfTypes'
import CrfItemForm from '@/components/library/crfs/CrfItemForm.vue'
import parameters from '@/constants/parameters'
import CrfTreeReorderButtons from '@/components/library/crfs/CrfTreeReorderButtons.vue'
import CrfApprovalSummaryConfirmDialog from '@/components/library/crfs/CrfApprovalSummaryConfirmDialog.vue'
import CrfNewVersionSummaryConfirmDialog from '@/components/library/crfs/CrfNewVersionSummaryConfirmDialog.vue'

export default {
  components: {
    CrfTreeItems,
    CrfTreeTooltipsHandler,
    StatusChip,
    CrfLinkForm,
    ActionsMenu,
    CrfItemGroupForm,
    CrfExportForm,
    CrfReferencesForm,
    CrfItemForm,
    CrfTreeReorderButtons,
    CrfApprovalSummaryConfirmDialog,
    CrfNewVersionSummaryConfirmDialog,
  },
  inject: ['eventBusEmit'],
  props: {
    parentForm: {
      type: Object,
      default: null,
    },
    columns: {
      type: Array,
      default: null,
    },
    refreshItemGroups: {
      type: Number,
      default: null,
    },
    expandGroupsForForm: {
      type: Array,
      default: null,
    },
    sortMode: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['updateParentFormItemGroup'],
  data() {
    return {
      itemGroups: [],
      loading: false,
      selectedItemGroup: {},
      showItemGroupForm: false,
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
      expanded: [],
      showExportForm: false,
      showAttributesForm: false,
      showCreateForm: false,
      showLinkForm: false,
    }
  },
  watch: {
    refreshItemGroups() {
      this.fetchItemGroups()
    },
    expandGroupsForForm(value) {
      if (!_isEmpty(value) && value.indexOf(this.parentForm.uid) > -1) {
        this.expanded = this.itemGroups
          .map((group) => (group.items.length > 0 ? group.name : null))
          .filter(function (val) {
            return val !== null
          })
      }
    },
  },
  created() {
    this.statuses = statuses
  },
  mounted() {
    this.fetchItemGroups()
  },
  methods: {
    async newVersion(item) {
      this.expanded = this.expanded.filter((e) => e !== item.name)

      if (
        await this.$refs.confirmNewVersion.open({
          agreeLabel: this.$t('CRFItemGroups.create_new_version'),
          itemGroup: item,
        })
      ) {
        this.loading = true

        crfs.newVersion('item-groups', item.uid).then((resp) => {
          if (this.parentForm.status === statuses.DRAFT) {
            this.updateItemGroup(resp.data)
          }

          this.expandAll(item)
          this.loading = false
          this.eventBusEmit('notification', {
            msg: this.$t('_global.new_version_success'),
          })
        })
      }
    },
    async approve(item) {
      this.expanded = this.expanded.filter((e) => e !== item.name)

      if (
        await this.$refs.confirmApproval.open({
          agreeLabel: this.$t('CRFItemGroups.approve_group'),
          itemGroup: item,
        })
      ) {
        this.loading = true

        crfs.approve('item-groups', item.uid).then((resp) => {
          this.updateItemGroup(resp.data)

          this.expandAll(item)
          this.loading = false
          this.eventBusEmit('notification', {
            msg: this.$t('CRFItemGroups.approved'),
          })
        })
      }
    },
    updateItemGroupItem(affectedItemGroup, updatedItem) {
      if (affectedItemGroup.status == statuses.DRAFT) {
        const itemGroup = this.itemGroups.find(
          (ig) => ig.uid === affectedItemGroup.uid
        )
        if (itemGroup) {
          itemGroup.items = itemGroup.items.map((i) =>
            i.uid === updatedItem.uid ? { ...i, ...updatedItem } : i
          )
        }
      }
    },
    openCreateAndAddForm(item) {
      this.selectedItemGroup = item
      this.showCreateForm = true
    },
    closeCreateAndAddForm() {
      this.showCreateForm = false
      this.selectedItemGroup = {}
    },
    linkItem(item) {
      const payload = [
        {
          uid: item.data.uid,
          order_number: this.selectedItemGroup.items.length,
          mandatory: 'No',
          collection_exception_condition_oid: null,
          key_sequence: parameters.NULL,
          methodOid: parameters.NULL,
          imputation_method_oid: parameters.NULL,
          role: parameters.NULL,
          role_codelist_oid: parameters.NULL,
          data_entry_required: 'No',
          sdv: 'No',
          vendor: { attributes: [] },
        },
      ]
      crfs
        .addItemsToItemGroup(payload, this.selectedItemGroup.uid, false)
        .then(() => {
          this.fetchItemGroups()
        })
    },
    async fetchItemGroups() {
      this.loading = true
      this.itemGroups = []
      for (const itemGroup of this.parentForm.item_groups) {
        let rs = await crfs.get(`item-groups/${itemGroup.uid}`, {
          params: { version: itemGroup.version },
        })
        this.itemGroups.push({ ...itemGroup, ...rs.data })
      }

      this.refreshItems += 1
      this.loading = false
      if (
        !_isEmpty(this.expandGroupsForForm) &&
        this.expandGroupsForForm.indexOf(this.parentForm.uid) > -1
      ) {
        this.expanded = this.itemGroups
          .map((group) => (group.items.length > 0 ? group.name : null))
          .filter(function (val) {
            return val !== null
          })
      }
    },
    updateItemGroup(itemGroup) {
      this.itemGroups = this.itemGroups.map((ig) =>
        ig.uid === itemGroup.uid ? { ...ig, ...itemGroup } : ig
      )
      this.$emit('updateParentFormItemGroup', this.parentForm, itemGroup)
    },
    openDefinition(item) {
      this.selectedItemGroup = item
      this.showItemGroupForm = true
    },
    closeDefinition() {
      this.selectedItemGroup = {}
      this.showItemGroupForm = false
      this.fetchItemGroups()
    },
    openLinkForm(item) {
      this.selectedItemGroup = item
      this.showLinkForm = true
    },
    closeLinkForm() {
      this.showLinkForm = false
      this.selectedItemGroup = {}
      this.fetchItemGroups()
    },
    async expandAll(item) {
      await this.expanded.push(item.name)
    },
    openExportForm(item) {
      this.selectedItemGroup = item
      this.showExportForm = true
    },
    closeExportForm() {
      this.selectedItemGroup = {}
      this.showExportForm = false
    },
    editAttributes(item) {
      this.selectedItemGroup = item
      this.showAttributesForm = true
    },
    closeAttributesForm() {
      this.selectedItemGroup = {}
      this.showAttributesForm = false
    },
    previewODM(item) {
      this.$router.push({
        name: 'CrfBuilder',
        params: {
          tab: 'odm-viewer',
          uid: item.uid,
          type: crfTypes.ITEM_GROUP,
        },
      })
    },
    orderUp(item, index) {
      if (index === 0) {
        return
      } else {
        this.itemGroups[index].order_number--
        this.itemGroups[index - 1].order_number++
        this.itemGroups.sort((a, b) => {
          return a.order_number - b.order_number
        })
        crfs.addItemGroupsToForm(this.itemGroups, this.parentForm.uid, true)
      }
    },
    orderDown(item, index) {
      if (index === this.itemGroups.length - 1) {
        return
      } else {
        this.itemGroups[index].order_number++
        this.itemGroups[index + 1].order_number--
        this.itemGroups.sort((a, b) => {
          return a.order_number - b.order_number
        })
        crfs.addItemGroupsToForm(this.itemGroups, this.parentForm.uid, true)
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
