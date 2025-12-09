<template>
  <div>
    <NNTable
      ref="table"
      :headers="headers"
      :items="itemGroups"
      item-value="uid"
      :items-length="total"
      column-data-resource="concepts/odms/item-groups"
      export-data-url="concepts/odms/item-groups"
      export-object-label="CRFItemGroups"
      @filter="getItemGroups"
    >
      <template #actions="">
        <v-btn
          class="ml-2"
          size="small"
          variant="outlined"
          color="nnBaseBlue"
          :title="$t('CRFItemGroups.add_group')"
          data-cy="add-crf-item-group"
          :disabled="!checkPermission($roles.LIBRARY_WRITE)"
          icon="mdi-plus"
          @click.stop="openForm"
        />
      </template>
      <template #[`item.name`]="{ item }">
        <v-tooltip bottom>
          <template #activator="{ props }">
            <div v-bind="props">
              {{
                item.name.length > 40
                  ? item.name.substring(0, 40) + '...'
                  : item.name
              }}
            </div>
          </template>
          <span>{{ item.name }}</span>
        </v-tooltip>
      </template>
      <template #[`item.repeating`]="{ item }">
        {{ item.repeating }}
      </template>
      <template #[`item.description`]="{ item }">
        <v-tooltip bottom>
          <template #activator="{ props }">
            <div
              v-bind="props"
              v-html="
                sanitizeHTMLHandler(
                  getDescriptionAttribute(item, 'description', true)
                )
              "
            />
          </template>
          <span>{{ getDescriptionAttribute(item, 'description', false) }}</span>
        </v-tooltip>
      </template>
      <template #[`item.sponsor_instruction`]="{ item }">
        <v-tooltip bottom>
          <template #activator="{ props }">
            <div
              v-bind="props"
              v-html="
                sanitizeHTMLHandler(
                  getDescriptionAttribute(item, 'sponsor_instruction', true)
                )
              "
            />
          </template>
          <span>{{
            getDescriptionAttribute(item, 'sponsor_instruction', false)
          }}</span>
        </v-tooltip>
      </template>
      <template #[`item.instruction`]="{ item }">
        <v-tooltip bottom>
          <template #activator="{ props }">
            <div
              v-bind="props"
              v-html="
                sanitizeHTMLHandler(
                  getDescriptionAttribute(item, 'instruction', true)
                )
              "
            />
          </template>
          <span>{{ getDescriptionAttribute(item, 'instruction', false) }}</span>
        </v-tooltip>
      </template>
      <template #[`item.status`]="{ item }">
        <StatusChip :status="item.status" />
      </template>
      <template #[`item.actions`]="{ item }">
        <ActionsMenu :actions="actions" :item="item" />
      </template>
    </NNTable>
    <v-dialog
      v-model="showForm"
      persistent
      fullscreen
      content-class="fullscreen-dialog"
    >
      <CrfItemGroupForm
        :selected-group="selectedGroup"
        :read-only-prop="
          selectedGroup && selectedGroup.status === constants.FINAL
        "
        @close="closeForm"
      />
    </v-dialog>
    <v-dialog
      v-model="showGroupHistory"
      persistent
      :fullscreen="$globals.historyDialogFullscreen"
      @keydown.esc="closeGroupHistory"
    >
      <HistoryTable
        :title="groupHistoryTitle"
        :headers="headers"
        :items="groupHistoryItems"
        @close="closeGroupHistory"
      />
    </v-dialog>
    <CrfActivitiesModelsLinkForm
      :open="linkForm"
      :item-to-link="selectedGroup"
      item-type="itemGroup"
      @close="closeLinkForm"
    />
    <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
    <CrfApprovalSummaryConfirmDialog ref="confirmApproval" />
    <CrfNewVersionSummaryConfirmDialog ref="confirmNewVersion" />
  </div>
</template>

<script>
import NNTable from '@/components/tools/NNTable.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import crfs from '@/api/crfs'
import CrfItemGroupForm from '@/components/library/crfs/CrfItemGroupForm.vue'
import HistoryTable from '@/components/tools/HistoryTable.vue'
import CrfActivitiesModelsLinkForm from '@/components/library/crfs/CrfActivitiesModelsLinkForm.vue'
import constants from '@/constants/statuses'
import filteringParameters from '@/utils/filteringParameters'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import CrfApprovalSummaryConfirmDialog from '@/components/library/crfs/CrfApprovalSummaryConfirmDialog.vue'
import crfTypes from '@/constants/crfTypes'
import parameters from '@/constants/parameters'
import { useAccessGuard } from '@/composables/accessGuard'
import { useCrfsStore } from '@/stores/crfs'
import { computed } from 'vue'
import { sanitizeHTML } from '@/utils/sanitize'
import CrfNewVersionSummaryConfirmDialog from '@/components/library/crfs/CrfNewVersionSummaryConfirmDialog.vue'

export default {
  components: {
    NNTable,
    StatusChip,
    ActionsMenu,
    CrfItemGroupForm,
    HistoryTable,
    CrfActivitiesModelsLinkForm,
    ConfirmDialog,
    CrfApprovalSummaryConfirmDialog,
    CrfNewVersionSummaryConfirmDialog,
  },
  inject: ['notificationHub'],
  props: {
    elementProp: {
      type: Object,
      default: null,
    },
  },
  setup() {
    const crfsStore = useCrfsStore()

    return {
      fetchItemGroups: crfsStore.fetchItemGroups,
      total: computed(() => crfsStore.totalItemGroups),
      itemGroups: computed(() => crfsStore.itemGroups),
      ...useAccessGuard(),
    }
  },
  data() {
    return {
      actions: [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'approve'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.approve,
        },
        {
          label: this.$t('_global.edit'),
          icon: 'mdi-pencil-outline',
          iconColor: 'primary',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'edit'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.edit,
        },
        {
          label: this.$t('_global.view'),
          icon: 'mdi-eye-outline',
          iconColor: 'primary',
          condition: (item) => item.status === constants.FINAL,
          click: this.view,
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'new_version'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.newVersion,
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'inactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.inactivate,
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'reactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.reactivate,
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'delete'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.delete,
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openGroupHistory,
        },
      ],
      headers: [
        { title: '', key: 'actions', width: '1%' },
        { title: this.$t('CRFItemGroups.oid'), key: 'oid' },
        { title: this.$t('_global.name'), key: 'name' },
        {
          title: this.$t('_global.description'),
          key: 'description',
          filteringName: 'descriptions.description',
        },
        {
          title: this.$t('CRFDescriptions.sponsor_instruction'),
          key: 'sponsor_instruction',
          filteringName: 'descriptions.sponsor_instruction',
        },
        {
          title: this.$t('CRFDescriptions.instruction'),
          key: 'instruction',
          filteringName: 'descriptions.instruction',
        },
        {
          title: this.$t('CRFItemGroups.repeating'),
          key: 'repeating',
          width: '1%',
        },
        { title: this.$t('_global.version'), key: 'version', width: '1%' },
        { title: this.$t('_global.status'), key: 'status', width: '1%' },
      ],
      showForm: false,
      showHistory: false,
      selectedGroup: null,
      filters: '',
      showGroupHistory: false,
      linkForm: false,
      groupHistoryItems: [],
    }
  },
  computed: {
    groupHistoryTitle() {
      if (this.selectedGroup) {
        return this.$t('CRFItemGroups.group_history_title', {
          groupUid: this.selectedGroup.uid,
        })
      }
      return ''
    },
  },
  watch: {
    elementProp(value) {
      if (
        value.tab === 'item-groups' &&
        value.type === crfTypes.ITEM_GROUP &&
        value.uid
      ) {
        this.edit({ uid: value.uid })
      }
    },
  },
  mounted() {
    if (
      this.elementProp.tab === 'item-groups' &&
      this.elementProp.type === crfTypes.ITEM_GROUP &&
      this.elementProp.uid
    ) {
      this.edit({ uid: this.elementProp.uid })
    }
  },
  created() {
    this.constants = constants
  },
  methods: {
    sanitizeHTMLHandler(html) {
      return sanitizeHTML(html)
    },
    getDescriptionAttribute(item, attr, short) {
      const engDesc = item.descriptions.find(
        (el) => el.language === parameters.ENG
      )
      if (engDesc && engDesc[attr]) {
        return short
          ? engDesc[attr].length > 40
            ? engDesc[attr].substring(0, 40) + '...'
            : engDesc[attr]
          : engDesc[attr]
      }
      return ''
    },
    async delete(item) {
      let relationships = 0
      await crfs.getRelationships(item.uid, 'item-groups').then((resp) => {
        if (resp.data.OdmForm && resp.data.OdmForm.length > 0) {
          relationships = resp.data.OdmForm.length
        }
      })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue'),
      }
      if (
        relationships < 1 ||
        (await this.$refs.confirm.open(
          `${this.$t('CRFItemGroups.delete_warning', { count: relationships })}`,
          options
        ))
      ) {
        crfs.delete('item-groups', item.uid).then(() => {
          this.getItemGroups()

          this.notificationHub.add({
            msg: this.$t('CRFItemGroups.deleted'),
          })
        })
      }
    },
    async approve(item) {
      if (
        await this.$refs.confirmApproval.open({
          agreeLabel: this.$t('CRFItemGroups.approve_group'),
          itemGroup: item,
        })
      ) {
        crfs.approve('item-groups', item.uid).then(() => {
          this.$refs.table.filterTable()

          this.notificationHub.add({
            msg: this.$t('CRFItemGroups.approved'),
          })
        })
      }
    },
    inactivate(item) {
      crfs.inactivate('item-groups', item.uid).then(() => {
        this.$refs.table.filterTable()

        this.notificationHub.add({
          msg: this.$t('CRFItemGroups.inactivated'),
        })
      })
    },
    reactivate(item) {
      crfs.reactivate('item-groups', item.uid).then(() => {
        this.$refs.table.filterTable()

        this.notificationHub.add({
          msg: this.$t('CRFItemGroups.reactivated'),
        })
      })
    },
    async newVersion(item) {
      if (
        await this.$refs.confirmNewVersion.open({
          agreeLabel: this.$t('CRFItemGroups.create_new_version'),
          itemGroup: item,
        })
      ) {
        crfs.newVersion('item-groups', item.uid).then(() => {
          this.$refs.table.filterTable()

          this.notificationHub.add({
            msg: this.$t('_global.new_version_success'),
          })
        })
      }
    },
    edit(item) {
      crfs.getItemGroup(item.uid).then((resp) => {
        this.selectedGroup = resp.data
        this.showForm = true
      })
    },
    view(item) {
      crfs.getItemGroup(item.uid).then((resp) => {
        this.selectedGroup = resp.data
        this.showForm = true
      })
    },
    openForm() {
      this.showForm = true
    },
    async openGroupHistory(group) {
      this.selectedGroup = group
      const resp = await crfs.getGroupAuditTrail(group.uid)
      this.groupHistoryItems = resp.data
      this.showGroupHistory = true
    },
    closeGroupHistory() {
      this.selectedGroup = null
      this.showGroupHistory = false
    },
    async closeForm() {
      this.showForm = false
      this.selectedGroup = null
      this.$refs.table.filterTable()
    },
    openLinkForm(item) {
      this.selectedGroup = item
      this.linkForm = true
    },
    closeLinkForm() {
      this.linkForm = false
      this.selectedGroup = null
      this.$refs.table.filterTable()
    },
    getItemGroups(filters, options, filtersUpdated) {
      if (filters) {
        this.filters = filters
      }
      const params = filteringParameters.prepareParameters(
        options,
        filters,
        filtersUpdated
      )
      this.fetchItemGroups(params)
    },
  },
}
</script>
