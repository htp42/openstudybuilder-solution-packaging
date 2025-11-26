<template>
  <td :colspan="columns.length" class="pa-0">
    <v-data-table
      id="forms"
      v-model:expanded="expanded"
      :initial-sort-by="[{ key: 'order_number', order: 'asc' }]"
      :headers="columns"
      :items="forms"
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
        <tr style="background-color: rgb(var(--v-theme-dfltBackgroundLight2))">
          <td width="45%" :class="'font-weight-bold'">
            <v-row class="align-center">
              <v-btn
                v-if="isExpanded(internalItem)"
                icon="mdi-chevron-down"
                variant="text"
                class="ml-4"
                @click="toggleExpand(internalItem)"
              />
              <v-btn
                v-else-if="item.item_groups && item.item_groups.length > 0"
                icon="mdi-chevron-right"
                variant="text"
                class="ml-4"
                @click="toggleExpand(internalItem)"
              />
              <v-btn v-else variant="text" class="ml-4 hide" icon />
              <CrfTreeReorderButtons
                :sort-mode="sortMode"
                :is-parent-draft="parentCollection.status === statuses.DRAFT"
                :sibling-length="parentCollection.forms.length"
                :item="item"
                :index="index"
                @order-up="orderUp"
                @order-down="orderDown"
              />
              <ActionsMenu :actions="actions" :item="item" />
              <span class="ml-2">
                <v-icon color="crfForm"> mdi-alpha-f-circle </v-icon>
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
          </td>
          <td width="10%">
            <CrfTreeTooltipsHandler :item="item" value="repeating" />
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
                    color="crfGroup"
                    :title="$t('CRFTree.link_item_groups')"
                  >
                    <v-icon icon="mdi-plus" />
                    {{ $t('CRFTree.item_groups') }}
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
        <CrfTreeItemGroups
          :sort-mode="sortMode"
          :parent-form="item"
          :columns="columns"
          :refresh-item-groups="refreshItemGroups"
          :expand-groups-for-form="expandGroupsForForm"
          @update-parent-form-item-group="updateFormItemGroup"
        />
      </template>
    </v-data-table>
  </td>
  <v-dialog v-model="showFormForm" persistent content-class="fullscreen-dialog">
    <CrfFormForm
      :selected-form="selectedForm"
      :read-only-prop="selectedForm && selectedForm.status === statuses.FINAL"
      class="fullscreen-dialog"
      @close="closeDefinition"
      @link-form="linkForm"
      @update-form="updateForm"
    />
  </v-dialog>
  <CrfLinkForm
    :open="showLinkForm"
    :item-to-link="selectedForm"
    items-type="item-groups"
    @close="closeLinkForm"
  />
  <v-dialog
    v-model="showExportForm"
    max-width="800px"
    persistent
    @keydown.esc="closeExportForm"
  >
    <CrfExportForm :item="selectedForm" type="form" @close="closeExportForm" />
  </v-dialog>
  <CrfReferencesForm
    :open="showAttributesForm"
    :parent="parentCollection"
    :element="selectedForm"
    :read-only="selectedForm.status === statuses.FINAL"
    @close="closeAttributesForm"
  />
  <v-dialog
    v-model="showCreateForm"
    persistent
    content-class="fullscreen-dialog"
  >
    <CrfItemGroupForm
      class="fullscreen-dialog"
      @close="closeCreateAndAddForm"
      @link-group="linkItemGroup"
    />
  </v-dialog>
  <CrfApprovalSummaryConfirmDialog ref="confirmApproval" />
  <CrfNewVersionSummaryConfirmDialog ref="confirmNewVersion" />
</template>

<script>
import crfs from '@/api/crfs'
import CrfTreeItemGroups from '@/components/library/crfs/crfTreeComponents/CrfTreeItemGroups.vue'
import CrfTreeTooltipsHandler from '@/components/library/crfs/CrfTreeTooltipsHandler.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import statuses from '@/constants/statuses'
import CrfLinkForm from '@/components/library/crfs/CrfLinkForm.vue'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import CrfFormForm from '@/components/library/crfs/CrfFormForm.vue'
import _isEmpty from 'lodash/isEmpty'
import CrfExportForm from '@/components/library/crfs/CrfExportForm.vue'
import CrfReferencesForm from '@/components/library/crfs/CrfReferencesForm.vue'
import crfTypes from '@/constants/crfTypes'
import CrfItemGroupForm from '@/components/library/crfs/CrfItemGroupForm.vue'
import CrfTreeReorderButtons from '@/components/library/crfs/CrfTreeReorderButtons.vue'
import CrfApprovalSummaryConfirmDialog from '@/components/library/crfs/CrfApprovalSummaryConfirmDialog.vue'
import CrfNewVersionSummaryConfirmDialog from '@/components/library/crfs/CrfNewVersionSummaryConfirmDialog.vue'

export default {
  components: {
    CrfTreeItemGroups,
    CrfTreeTooltipsHandler,
    StatusChip,
    CrfLinkForm,
    ActionsMenu,
    CrfFormForm,
    CrfExportForm,
    CrfReferencesForm,
    CrfItemGroupForm,
    CrfTreeReorderButtons,
    CrfApprovalSummaryConfirmDialog,
    CrfNewVersionSummaryConfirmDialog,
  },
  inject: ['eventBusEmit'],
  props: {
    parentCollection: {
      type: Object,
      default: null,
    },
    columns: {
      type: Array,
      default: null,
    },
    refreshForms: {
      type: Number,
      default: null,
    },
    expandFormsForCollection: {
      type: String,
      default: null,
    },
    sortMode: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['updateParentCollectionForm'],
  data() {
    return {
      forms: [],
      loading: false,
      showFormForm: false,
      showLinkForm: false,
      selectedForm: {},
      refreshItemGroups: 0,
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
        {
          label: this.$t('CRFTree.expand'),
          icon: 'mdi-arrow-expand-down',
          condition: (item) => item.item_groups.length > 0,
          click: this.expandAll,
        },
      ],
      expanded: [],
      expandGroupsForForm: [],
      showExportForm: false,
      showAttributesForm: false,
      showCreateForm: false,
    }
  },
  watch: {
    refreshForms() {
      this.fetchForms()
    },
    expandFormsForCollection(value) {
      if (!_isEmpty(value) && value === this.parentCollection.uid) {
        this.expanded = this.forms
          .map((form) => (form.item_groups.length > 0 ? form.name : null))
          .filter(function (val) {
            return val !== null
          })
        this.expandGroupsForForm = this.forms
          .map((form) => (form.item_groups.length > 0 ? form.uid : null))
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
    this.fetchForms()
  },
  methods: {
    async newVersion(item) {
      this.expanded = this.expanded.filter((e) => e !== item.name)

      if (
        await this.$refs.confirmNewVersion.open({
          agreeLabel: this.$t('CRFForms.create_new_version'),
          form: item,
        })
      ) {
        this.loading = true

        crfs.newVersion('forms', item.uid).then((resp) => {
          if (this.parentCollection.status === statuses.DRAFT) {
            this.updateForm(resp.data)
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
          agreeLabel: this.$t('CRFForms.approve_form'),
          form: item,
        })
      ) {
        this.loading = true

        crfs.approve('forms', item.uid).then((resp) => {
          this.updateForm(resp.data)

          this.expandAll(item)
          this.loading = false
          this.eventBusEmit('notification', {
            msg: this.$t('CRFForms.approved'),
          })
        })
      }
    },
    updateFormItemGroup(affectedForm, updatedItemGroup) {
      if (affectedForm.status === statuses.DRAFT) {
        const form = this.forms.find((f) => f.uid === affectedForm.uid)

        if (form) {
          form.item_groups = form.item_groups.map((f) =>
            f.uid === updatedItemGroup.uid ? { ...f, ...updatedItemGroup } : f
          )
        }
      }
    },
    openCreateAndAddForm(item) {
      this.selectedForm = item
      this.showCreateForm = true
    },
    closeCreateAndAddForm() {
      this.showCreateForm = false
      this.selectedForm = {}
    },
    linkItemGroup(group) {
      const payload = [
        {
          uid: group.data.uid,
          order_number: this.selectedForm.item_groups.length,
          mandatory: 'No',
          collection_exception_condition_oid: null,
          vendor: { attributes: [] },
        },
      ]
      crfs
        .addItemGroupsToForm(payload, this.selectedForm.uid, false)
        .then(() => {
          this.fetchForms()
        })
    },
    async fetchForms() {
      this.loading = true
      this.forms = []
      for (const form of this.parentCollection.forms) {
        const rs = await crfs.get(`forms/${form.uid}`, {
          params: { version: form.version },
        })
        this.forms.push({ ...form, ...rs.data })
      }

      this.refreshItemGroups += 1
      this.loading = false
      if (
        !_isEmpty(this.expandFormsForCollection) &&
        this.expandFormsForCollection === this.parentCollection.uid
      ) {
        this.expanded = this.forms
          .map((form) => (form.item_groups.length > 0 ? form.name : null))
          .filter(function (val) {
            return val !== null
          })
        this.expandGroupsForForm = this.forms
          .map((form) => (form.item_groups.length > 0 ? form.uid : null))
          .filter(function (val) {
            return val !== null
          })
      }
    },
    updateForm(form) {
      this.forms = this.forms.map((f) =>
        f.uid === form.uid ? { ...f, ...form } : f
      )
      this.$emit('updateParentCollectionForm', this.parentCollection, form)
    },
    openDefinition(item) {
      this.selectedForm = item
      this.showFormForm = true
    },
    closeDefinition() {
      this.selectedForm = {}
      this.showFormForm = false
      this.fetchForms()
    },
    openLinkForm(item) {
      this.selectedForm = item
      this.showLinkForm = true
    },
    closeLinkForm() {
      this.showLinkForm = false
      this.selectedForm = {}
      this.fetchForms()
    },
    async expandAll(item) {
      await this.expanded.push(item.name)
      this.expandGroupsForForm = [item.uid]
    },
    openExportForm(item) {
      this.selectedForm = item
      this.showExportForm = true
    },
    closeExportForm() {
      this.selectedForm = {}
      this.showExportForm = false
    },
    editAttributes(item) {
      this.selectedForm = item
      this.showAttributesForm = true
    },
    closeAttributesForm() {
      this.selectedForm = {}
      this.showAttributesForm = false
    },
    previewODM(item) {
      this.$router.push({
        name: 'CrfBuilder',
        params: {
          tab: 'odm-viewer',
          uid: item.uid,
          type: crfTypes.FORM,
        },
      })
    },
    orderUp(item, index) {
      if (index === 0) {
        return
      } else {
        this.forms[index].order_number--
        this.forms[index - 1].order_number++
        this.forms.sort((a, b) => {
          return a.order_number - b.order_number
        })
        crfs.addFormsToCollection(this.forms, this.parentCollection.uid, true)
      }
    },
    orderDown(item, index) {
      if (index === this.forms.length - 1) {
        return
      } else {
        this.forms[index].order_number++
        this.forms[index + 1].order_number--
        this.forms.sort((a, b) => {
          return a.order_number - b.order_number
        })
        crfs.addFormsToCollection(this.forms, this.parentCollection.uid, true)
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
