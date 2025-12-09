<template>
  <div>
    <NNTable
      ref="table"
      :headers="headers"
      :items="collections"
      item-value="uid"
      sort-desc
      :items-length="total"
      column-data-resource="concepts/odms/study-events"
      export-data-url="concepts/odms/study-events"
      export-object-label="CRFCollections"
      @filter="getCollections"
    >
      <template #actions="">
        <v-btn
          class="ml-2"
          size="small"
          variant="outlined"
          color="nnBaseBlue"
          :title="$t('CRFCollections.add_collection')"
          data-cy="add-crf-collection"
          :disabled="!checkPermission($roles.LIBRARY_WRITE)"
          icon="mdi-plus"
          @click.stop="openForm()"
        />
      </template>
      <template #[`item.actions`]="{ item }">
        <ActionsMenu :actions="actions" :item="item" />
      </template>
      <template #[`item.status`]="{ item }">
        <StatusChip :status="item.status" />
      </template>
      <template #[`item.relations`]="{ item }">
        <v-btn
          size="x-small"
          color="primary"
          icon="mdi-family-tree"
          @click="openRelationsTree(item)"
        />
      </template>
    </NNTable>
    <CrfCollectionForm
      :open="showForm"
      :selected-collection="selectedCollection"
      :read-only-prop="
        selectedCollection && selectedCollection.status === statuses.FINAL
      "
      @close="closeForm"
    />
    <v-dialog
      v-model="showCollectionHistory"
      persistent
      :fullscreen="$globals.historyDialogFullscreen"
      @keydown.esc="closeCollectionHistory"
    >
      <HistoryTable
        :title="collectionHistoryTitle"
        :headers="headers"
        :items="collectionHistoryItems"
        @close="closeCollectionHistory"
      />
    </v-dialog>
    <CrfApprovalSummaryConfirmDialog ref="confirmApproval" />
  </div>
</template>

<script>
import NNTable from '@/components/tools/NNTable.vue'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import crfs from '@/api/crfs'
import HistoryTable from '@/components/tools/HistoryTable.vue'
import CrfApprovalSummaryConfirmDialog from '@/components/library/crfs/CrfApprovalSummaryConfirmDialog.vue'
import CrfCollectionForm from '@/components/library/crfs/CrfCollectionForm.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import filteringParameters from '@/utils/filteringParameters'
import crfTypes from '@/constants/crfTypes'
import statuses from '@/constants/statuses'
import { useAccessGuard } from '@/composables/accessGuard'
import { useCrfsStore } from '@/stores/crfs'
import { computed } from 'vue'

export default {
  components: {
    NNTable,
    ActionsMenu,
    HistoryTable,
    CrfApprovalSummaryConfirmDialog,
    CrfCollectionForm,
    StatusChip,
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
      fetchCollections: crfsStore.fetchCollections,
      total: computed(() => crfsStore.totalCollections),
      collections: computed(() => crfsStore.collections),
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
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'delete'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.deleteCollection,
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'new_version'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.newCollectionVersion,
        },
        {
          label: this.$t('_global.inactivate'),
          icon: 'mdi-close-octagon-outline',
          iconColor: 'primary',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'inactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.inactivateCollection,
        },
        {
          label: this.$t('_global.reactivate'),
          icon: 'mdi-undo-variant',
          iconColor: 'primary',
          condition: (item) =>
            item.possible_actions.find((action) => action === 'reactivate'),
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.reactivateCollection,
        },
        {
          label: this.$t('_global.history'),
          icon: 'mdi-history',
          click: this.openCollectionHistory,
        },
      ],
      headers: [
        { title: '', key: 'actions', width: '1%' },
        { title: this.$t('CRFCollections.oid'), key: 'oid' },
        { title: this.$t('_global.name'), key: 'name' },
        {
          title: this.$t('CRFCollections.effective_date'),
          key: 'effective_date',
        },
        { title: this.$t('CRFCollections.retired_date'), key: 'retired_date' },
        { title: this.$t('_global.version'), key: 'version' },
        { title: this.$t('_global.status'), key: 'status' },
      ],
      showForm: false,
      showCollectionHistory: false,
      selectedCollection: null,
      filters: '',
      collectionHistoryItems: [],
    }
  },
  computed: {
    collectionHistoryTitle() {
      if (this.selectedCollection) {
        return this.$t('CRFCollections.collection_history_title', {
          collectionUid: this.selectedCollection.uid,
        })
      }
      return ''
    },
  },
  watch: {
    elementProp(value) {
      if (
        value.tab === 'collections' &&
        value.type === crfTypes.COLLECTION &&
        value.uid
      ) {
        this.edit({ uid: value.uid })
      }
    },
  },
  created() {
    this.statuses = statuses
  },
  mounted() {
    if (
      this.elementProp.tab === 'collections' &&
      this.elementProp.type === crfTypes.COLLECTION &&
      this.elementProp.uid
    ) {
      crfs.getCollection(this.elementProp.uid).then((resp) => {
        this.edit(resp.data)
      })
    }
  },
  methods: {
    async approve(item) {
      if (
        await this.$refs.confirmApproval.open({
          agreeLabel: this.$t('CRFCollections.approve_collection'),
          collection: item,
        })
      ) {
        crfs.approve('study-events', item.uid).then(() => {
          this.$refs.table.filterTable()

          this.notificationHub.add({
            msg: this.$t('CRFCollections.approved'),
          })
        })
      }
    },
    inactivateCollection(item) {
      crfs.inactivate('study-events', item.uid).then(() => {
        this.$refs.table.filterTable()

        this.notificationHub.add({
          msg: this.$t('CRFCollections.inactivated'),
        })
      })
    },
    reactivateCollection(item) {
      crfs.reactivate('study-events', item.uid).then(() => {
        this.$refs.table.filterTable()

        this.notificationHub.add({
          msg: this.$t('CRFCollections.reactivated'),
        })
      })
    },
    newCollectionVersion(item) {
      crfs.newVersion('study-events', item.uid).then(() => {
        this.$refs.table.filterTable()

        this.notificationHub.add({
          msg: this.$t('_global.new_version_success'),
        })
      })
    },
    deleteCollection(item) {
      crfs.delete('study-events', item.uid).then(() => {
        this.$refs.table.filterTable()

        this.notificationHub.add({
          msg: this.$t('CRFCollections.deleted'),
        })
      })
    },
    edit(item) {
      crfs.getCollection(item.uid).then((resp) => {
        this.selectedCollection = resp.data
        this.showForm = true
      })
    },
    async openCollectionHistory(collection) {
      this.selectedCollection = collection
      const resp = await crfs.getCollectionAuditTrail(collection.uid)
      this.collectionHistoryItems = resp.data
      this.showCollectionHistory = true
    },
    closeCollectionHistory() {
      this.showCollectionHistory = false
      this.selectedCollection = null
    },
    openForm() {
      this.selectedCollection = null
      this.showForm = true
    },
    closeForm() {
      this.selectedCollection = null
      this.showForm = false
      this.$refs.table.filterTable()
    },
    getCollections(filters, options, filtersUpdated) {
      if (filters) {
        this.filters = filters
      }
      const params = filteringParameters.prepareParameters(
        options,
        filters,
        filtersUpdated
      )
      this.fetchCollections(params)
    },
  },
}
</script>
