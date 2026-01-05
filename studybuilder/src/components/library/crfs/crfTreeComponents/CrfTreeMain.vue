<template>
  <v-row>
    <v-col>
      <v-select
        ref="mainSelect"
        v-model="selectCollection"
        :items="availableSelectCollections"
        :item-title="(item) => item?.name || $t('CRFTree.show_all')"
        :item-value="(item) => item?.uid || null"
        class="ms-4 mt-4"
        variant="outlined"
        density="compact"
        prepend-inner-icon="mdi-filter"
        hide-details
      >
        <template #prepend-item>
          <v-list-item style="cursor: pointer" @click="selectAll">
            <v-list-item-title class="ms-4">{{
              $t('CRFTree.show_all')
            }}</v-list-item-title>
          </v-list-item>
          <v-divider />
        </template>
      </v-select>
    </v-col>
    <v-spacer />
    <v-col class="d-flex justify-end me-4">
      <v-switch
        v-model="sortMode"
        class="ml-6 mt-4"
        color="primary"
        :label="$t('CRFTree.reorder')"
        :disabled="expanded.length === 0"
      />
    </v-col>
  </v-row>
  <v-data-table-server
    ref="mainTable"
    v-model:expanded="expanded"
    :headers="headers"
    item-value="name"
    :items-length="totalCollections"
    :items="collections"
    :loading="loading"
    @update:options="getCollections"
  >
    <template #headers="{ columns }">
      <tr class="header">
        <template v-for="column in columns" :key="column.key">
          <td>
            <span>{{ column.title }}</span>
          </td>
        </template>
      </tr>
    </template>
    <template #item="{ item, internalItem, toggleExpand, isExpanded }">
      <tr style="background-color: rgb(var(--v-theme-dfltBackgroundLight1))">
        <td width="45%" :class="'font-weight-bold'">
          <v-row class="align-center">
            <v-btn
              v-if="isExpanded(internalItem)"
              icon="mdi-chevron-down"
              variant="text"
              @click="doubleClick(toggleExpand, internalItem)"
            />
            <v-tooltip
              v-else-if="item.forms.length > 0"
              location="top left"
              :text="$t('CRFTree.double_click_expand')"
            >
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-chevron-right"
                  variant="text"
                  @click="doubleClick(toggleExpand, internalItem)"
                />
              </template>
            </v-tooltip>
            <v-btn v-else variant="text" class="hide" icon />
            <ActionsMenu :actions="actions" :item="item" />
            <span class="ml-2">
              <v-icon color="crfCollection">mdi-alpha-c-circle</v-icon>
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
        <td width="10%" />
        <td width="10%" />
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
                  color="crfForm"
                  :title="$t('CRFTree.link_forms')"
                >
                  <v-icon icon="mdi-plus" />
                  {{ $t('CRFTree.forms') }}
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
      <CrfTreeForms
        :sort-mode="sortMode"
        :parent-collection="item"
        :columns="columns"
        :refresh-forms="refreshForms"
        :expand-forms-for-collection="expandFormsForCollection"
        @update-parent-collection-form="updateCollectionForm"
      />
    </template>
  </v-data-table-server>
  <CrfCollectionForm
    :open="showCollectionForm"
    :selected-collection="selectedCollection"
    :read-only-prop="
      selectedCollection && selectedCollection.status === statuses.FINAL
    "
    @close="closeDefinition"
    @update-collection="updateCollection"
  />
  <CrfLinkForm
    :open="showLinkForm"
    :item-to-link="selectedCollection"
    items-type="forms"
    @close="closeLinkForm"
  />
  <v-dialog
    v-model="showExportForm"
    max-width="800px"
    persistent
    @keydown.esc="closeExportForm"
  >
    <CrfExportForm
      :item="selectedCollection"
      type="study_event"
      @close="closeExportForm"
    />
  </v-dialog>
  <v-dialog
    v-model="showCreateForm"
    persistent
    content-class="fullscreen-dialog"
  >
    <CrfFormForm
      class="fullscreen-dialog"
      @close="closeCreateAndAddForm"
      @link-form="linkForm"
    />
  </v-dialog>
  <CrfApprovalSummaryConfirmDialog ref="confirmApproval" />
  <ConfirmDialog ref="confirmNewVersion" />
</template>

<script>
import crfs from '@/api/crfs'
import CrfApprovalSummaryConfirmDialog from '@/components/library/crfs/CrfApprovalSummaryConfirmDialog.vue'
import CrfTreeForms from '@/components/library/crfs/crfTreeComponents/CrfTreeForms.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import statuses from '@/constants/statuses'
import CrfLinkForm from '@/components/library/crfs/CrfLinkForm.vue'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import CrfCollectionForm from '@/components/library/crfs/CrfCollectionForm.vue'
import CrfExportForm from '@/components/library/crfs/CrfExportForm.vue'
import crfTypes from '@/constants/crfTypes'
import CrfFormForm from '@/components/library/crfs/CrfFormForm.vue'
import filteringParameters from '@/utils/filteringParameters'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import isEmpty from 'lodash/isEmpty'

export default {
  components: {
    CrfApprovalSummaryConfirmDialog,
    CrfTreeForms,
    StatusChip,
    CrfLinkForm,
    ActionsMenu,
    CrfCollectionForm,
    CrfExportForm,
    CrfFormForm,
    ConfirmDialog,
  },
  inject: ['notificationHub'],
  data() {
    return {
      headers: [
        { title: this.$t('CRFTree.items_for_linking'), key: 'name' },
        { title: this.$t('CRFTree.ref_attr'), key: 'refAttr' },
        { title: this.$t('CRFTree.def_attr'), key: 'defAttr' },
        { title: this.$t('_global.status'), key: 'status' },
        { title: this.$t('_global.version'), key: 'version' },
        { title: this.$t('CRFTree.link'), key: 'link' },
      ],
      actions: [
        {
          label: this.$t('CRFTree.open_def'),
          icon: 'mdi-arrow-left',
          click: this.openDefinition,
        },
        {
          label: this.$t('CRFTree.preview_odm'),
          icon: 'mdi-file-xml-box',
          click: this.previewODM,
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          click: this.newVersion,
          condition: (item) => item.status === statuses.FINAL,
          accessRole: this.$roles.LIBRARY_WRITE,
        },
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          click: this.approve,
          condition: (item) => item.status === statuses.DRAFT,
          accessRole: this.$roles.LIBRARY_WRITE,
        },
        {
          label: this.$t('CRFTree.create_new_version_all'),
          icon: 'mdi-plus-circle-outline',
          click: this.newVersionAll,
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
          condition: (item) => item.forms.length > 0,
          click: this.expandAll,
        },
      ],
      showLinkForm: false,
      showCollectionForm: false,
      selectedCollection: {},
      refreshForms: 0,
      expanded: [],
      expandFormsForCollection: '',
      showExportForm: false,
      showCreateForm: false,
      sortMode: false,
      collections: [],
      filteredOutCollections: [],
      totalCollections: 0,
      loading: false,
      selectCollection: {},
      doubleClickCounter: 0,
      doubleClickTimer: null,
    }
  },
  computed: {
    availableSelectCollections() {
      return [...this.collections, ...this.filteredOutCollections].sort(
        (a, b) => a.name.localeCompare(b.name)
      )
    },
  },
  watch: {
    selectCollection(val) {
      this.updateCollectionView(val)
    },
  },
  created() {
    this.statuses = statuses
  },
  mounted() {
    this.getCollections()
  },
  methods: {
    doubleClick(toggleExpand, item) {
      this.doubleClickCounter++

      if (this.doubleClickCounter === 1) {
        this.doubleClickTimer = setTimeout(() => {
          toggleExpand(item)
          this.doubleClickCounter = 0
          this.expandFormsForCollection = ''
        }, 500)
      } else {
        this.expandAll(item.raw)
        clearTimeout(this.doubleClickTimer)
        this.doubleClickCounter = 0
      }
    },
    updateCollectionView(collection) {
      if (isEmpty(collection)) {
        this.collections = [...this.collections, ...this.filteredOutCollections]
        this.filteredOutCollections = []
        return
      }

      const allCollections = [
        ...this.collections,
        ...this.filteredOutCollections,
      ]
      this.collections = allCollections.filter((c) => c.uid === collection)
      this.filteredOutCollections = allCollections.filter(
        (c) => c.uid !== collection
      )
    },
    async newVersion(item) {
      this.expanded = this.expanded.filter((e) => e !== item.name)

      if (
        await this.$refs.confirmNewVersion.open(
          this.$t('_global.continuation_confirmation'),
          { type: 'warning' }
        )
      ) {
        this.loading = true

        crfs
          .newVersion('study-events', item.uid)
          .then((resp) => {
            this.collections = this.collections.map((c) =>
              c.uid === resp.data.uid ? { ...c, ...resp.data } : c
            )

            this.expandAll(item)
            this.notificationHub.add({
              msg: this.$t('_global.new_version_success'),
            })
          })
          .finally(() => {
            this.loading = false
          })
      }
    },
    updateCollectionForm(affectedCollection, updatedForm) {
      if (affectedCollection.status == statuses.DRAFT) {
        const collection = this.collections.find(
          (c) => c.uid === affectedCollection.uid
        )
        if (collection) {
          collection.forms = collection.forms.map((f) =>
            f.uid === updatedForm.uid ? { ...f, ...updatedForm } : f
          )
        }
      }
    },
    selectAll() {
      this.selectCollection = {}
      this.$refs.mainSelect?.blur()
    },
    async getCollections(options) {
      options = { ...options, sortBy: [{ key: 'name', order: 'asc' }] }
      const params = filteringParameters.prepareParameters(options, null, null)
      if (!params) {
        params.total_count = true
      }
      return crfs.get('study-events', { params }).then((resp) => {
        this.collections = resp.data.items
        this.updateCollectionView(this.selectCollection)
        this.totalCollections = resp.data.total
      })
    },
    openCreateAndAddForm(item) {
      this.selectedCollection = item
      this.showCreateForm = true
    },
    closeCreateAndAddForm() {
      this.showCreateForm = false
      this.selectedCollection = {}
    },
    linkForm(form) {
      const payload = [
        {
          uid: form.data.uid,
          order_number: this.selectedCollection.forms.length,
          mandatory: 'No',
          collection_exception_condition_oid: null,
        },
      ]
      crfs
        .addFormsToCollection(payload, this.selectedCollection.uid, false)
        .then(() => {
          this.getCollections().then(() => {
            this.refreshForms += 1
          })
        })
    },
    updateCollection(collection) {
      this.collections = this.collections.map((c) =>
        c.uid === collection.uid ? { ...c, ...collection } : c
      )
    },
    openDefinition(item) {
      this.selectedCollection = item
      this.showCollectionForm = true
    },
    closeDefinition() {
      this.selectedCollection = {}
      this.showCollectionForm = false
      this.getCollections()
    },
    openLinkForm(item) {
      this.selectedCollection = item
      this.showLinkForm = true
    },
    async closeLinkForm() {
      this.showLinkForm = false
      this.selectedCollection = {}
      await this.getCollections()
      this.refreshForms += 1
    },
    async expandAll(item) {
      await this.expanded.push(item.name)
      this.expandFormsForCollection = item.uid
    },
    openExportForm(item) {
      this.selectedCollection = item
      this.showExportForm = true
    },
    closeExportForm() {
      this.selectedCollection = {}
      this.showExportForm = false
    },
    previewODM(item) {
      this.$router.push({
        name: 'CrfBuilder',
        params: {
          tab: 'odm-viewer',
          uid: item.uid,
          type: crfTypes.STUDY_EVENT,
        },
      })
    },
    async approve(item) {
      this.expanded = this.expanded.filter((e) => e !== item.name)

      if (
        item.status === statuses.DRAFT &&
        (await this.$refs.confirmApproval.open({
          agreeLabel: this.$t('CRFCollections.approve_collection'),
          collection: item,
        }))
      ) {
        this.loading = true

        await crfs
          .approve('study-events', item.uid)
          .then((resp) => {
            this.collections = this.collections.map((collection) => {
              if (collection.uid === resp.data.uid) {
                return { ...collection, ...resp.data }
              }
              return collection
            })

            this.notificationHub.add({
              msg: this.$t('CRFCollections.approved'),
            })
            this.expandAll(item)
          })
          .finally(() => {
            this.loading = false
          })
      }
    },
    async newVersionAll(item) {
      this.expanded = this.expanded.filter((e) => e !== item.name)

      if (
        item.status === statuses.FINAL &&
        (await this.$refs.confirmNewVersion.open(
          this.$t('CRFTree.new_version_affecting_children_warning'),
          {
            agreeLabel: this.$t('CRFTree.create_new_versions'),
            type: 'warning',
          }
        ))
      ) {
        this.loading = true

        await crfs
          .newVersion('study-events', item.uid, {
            params: { cascade_new_version: true },
          })
          .then((resp) => {
            this.collections = this.collections.map((collection) => {
              if (collection.uid === resp.data.uid) {
                return { ...collection, ...resp.data }
              }
              return collection
            })

            this.notificationHub.add({
              msg: this.$t('CRFCollections.new_version_all'),
            })
            this.expandAll(item)
          })
          .finally(() => {
            this.loading = false
          })
      }
    },
  },
}
</script>
<style>
.hide {
  opacity: 0;
  cursor: default;
}
.header {
  background-color: rgb(var(--v-theme-tableGray)) !important;
  color: rgba(26, 26, 26, 0.6) !important;
  text-align: start;
  font-weight: 500;
  font-size: 14px;
}
</style>
