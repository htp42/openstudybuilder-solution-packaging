<template>
  <div>
    <NNTable
      ref="table"
      :headers="headers"
      :items="forms"
      item-value="uid"
      :items-length="total"
      column-data-resource="concepts/odms/forms"
      export-data-url="concepts/odms/forms"
      export-object-label="CRFForms"
      @filter="getForms"
    >
      <template #actions="">
        <v-btn
          class="ml-2"
          size="small"
          variant="outlined"
          color="nnBaseBlue"
          :title="$t('CRFForms.add_form')"
          data-cy="add-crf-form"
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
      <template #[`item.repeating`]="{ item }">
        {{ item.repeating }}
      </template>
      <template #[`item.status`]="{ item }">
        <StatusChip :status="item.status" />
      </template>
      <template #[`item.actions`]="{ item }">
        <ActionsMenu :actions="actions" :item="item" />
      </template>
    </NNTable>
    <v-dialog v-model="showForm" persistent content-class="fullscreen-dialog">
      <CrfFormForm
        :selected-form="selectedForm"
        :read-only-prop="selectedForm && selectedForm.status === statuses.FINAL"
        @close="closeForm"
      />
    </v-dialog>
    <v-dialog
      v-model="showFormHistory"
      persistent
      :fullscreen="$globals.historyDialogFullscreen"
      @keydown.esc="closeFormHistory"
    >
      <HistoryTable
        :title="formHistoryTitle"
        :headers="headers"
        :items="formHistoryItems"
        @close="closeFormHistory"
      />
    </v-dialog>
    <CrfActivitiesModelsLinkForm
      :open="linkForm"
      :item-to-link="selectedForm"
      item-type="form"
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
import CrfFormForm from '@/components/library/crfs/CrfFormForm.vue'
import HistoryTable from '@/components/tools/HistoryTable.vue'
import CrfActivitiesModelsLinkForm from '@/components/library/crfs/CrfActivitiesModelsLinkForm.vue'
import statuses from '@/constants/statuses'
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
    CrfFormForm,
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
      fetchForms: crfsStore.fetchForms,
      total: computed(() => crfsStore.totalForms),
      forms: computed(() => crfsStore.forms),
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
          condition: (item) => item.status === statuses.FINAL,
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
          click: this.openFormHistory,
        },
      ],
      headers: [
        { title: '', key: 'actions', width: '1%' },
        { title: this.$t('CRFForms.oid'), key: 'oid' },
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
          title: this.$t('CRFFormTable.repeating'),
          key: 'repeating',
          width: '1%',
        },
        { title: this.$t('_global.version'), key: 'version', width: '1%' },
        { title: this.$t('_global.status'), key: 'status', width: '1%' },
      ],
      showForm: false,
      showHistory: false,
      selectedForm: null,
      filters: '',
      showFormHistory: false,
      linkForm: false,
      formHistoryItems: [],
    }
  },
  computed: {
    formHistoryTitle() {
      if (this.selectedForm) {
        return this.$t('CRFFormTable.form_history_title', {
          formUid: this.selectedForm.uid,
        })
      }
      return ''
    },
  },
  watch: {
    elementProp(value) {
      if (value.tab === 'forms' && value.type === crfTypes.FORM && value.uid) {
        this.edit({ uid: value.uid })
      }
    },
  },
  mounted() {
    if (
      this.elementProp.tab === 'forms' &&
      this.elementProp.type === crfTypes.FORM &&
      this.elementProp.uid
    ) {
      this.edit({ uid: this.elementProp.uid })
    }
  },
  created() {
    this.statuses = statuses
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
      await crfs.getRelationships(item.uid, 'forms').then((resp) => {
        if (resp.data.OdmStudyEvent && resp.data.OdmStudyEvent.length > 0) {
          relationships = resp.data.OdmStudyEvent.length
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
          `${this.$t('CRFForms.delete_warning', { count: relationships })}`,
          options
        ))
      ) {
        crfs.delete('forms', item.uid).then(() => {
          this.$refs.table.filterTable()

          this.notificationHub.add({
            msg: this.$t('CRFForms.deleted'),
          })
        })
      }
    },
    async approve(item) {
      if (
        await this.$refs.confirmApproval.open({
          agreeLabel: this.$t('CRFForms.approve_form'),
          form: item,
        })
      ) {
        crfs.approve('forms', item.uid).then(() => {
          this.$refs.table.filterTable()

          this.notificationHub.add({
            msg: this.$t('CRFForms.approved'),
          })
        })
      }
    },
    inactivate(item) {
      crfs.inactivate('forms', item.uid).then(() => {
        this.$refs.table.filterTable()

        this.notificationHub.add({
          msg: this.$t('CRFForms.inactivated'),
        })
      })
    },
    reactivate(item) {
      crfs.reactivate('forms', item.uid).then(() => {
        this.$refs.table.filterTable()

        this.notificationHub.add({
          msg: this.$t('CRFForms.reactivated'),
        })
      })
    },
    async newVersion(item) {
      if (
        await this.$refs.confirmNewVersion.open({
          agreeLabel: this.$t('CRFForms.create_new_version'),
          form: item,
        })
      ) {
        crfs.newVersion('forms', item.uid).then(() => {
          this.$refs.table.filterTable()

          this.notificationHub.add({
            msg: this.$t('_global.new_version_success'),
          })
        })
      }
    },
    edit(item) {
      crfs.getForm(item.uid).then((resp) => {
        this.selectedForm = resp.data
        this.showForm = true
      })
    },
    view(item) {
      crfs.getForm(item.uid).then((resp) => {
        this.selectedForm = resp.data
        this.showForm = true
      })
    },
    openForm() {
      this.selectedForm = null
      this.showForm = true
    },
    async closeForm() {
      this.showForm = false
      this.selectedForm = null
      this.$refs.table.filterTable()
    },
    async openFormHistory(form) {
      this.selectedForm = form
      const resp = await crfs.getFormAuditTrail(form.uid)
      this.formHistoryItems = resp.data
      this.showFormHistory = true
    },
    closeFormHistory() {
      this.selectedForm = null
      this.showFormHistory = false
    },
    openLinkForm(item) {
      this.selectedForm = item
      this.linkForm = true
    },
    closeLinkForm() {
      this.linkForm = false
      this.selectedForm = null
      this.$refs.table.filterTable()
    },
    async getForms(filters, options, filtersUpdated) {
      if (filters) {
        this.filters = filters
      }
      const params = filteringParameters.prepareParameters(
        options,
        filters,
        filtersUpdated
      )
      this.fetchForms(params)
    },
  },
}
</script>
