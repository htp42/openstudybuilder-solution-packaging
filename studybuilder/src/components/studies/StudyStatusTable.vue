<template>
  <NNTable
    :headers="headers"
    :items="items"
    column-data-resource="studies"
    hide-default-switches
    hide-export-button
    disable-filtering
    :items-length="total"
    @filter="fetchItems"
  >
    <template #beforeTable="">
      <v-btn
        v-if="
          studiesGeneralStore.selectedStudy.current_metadata.version_metadata
            .study_status === 'DRAFT' &&
          !studiesGeneralStore.selectedStudy.study_parent_part &&
          isLatestStudySelected()
        "
        class="ml-2 expandHoverBtn"
        variant="outlined"
        color="nnBaseBlue"
        data-cy="release-study"
        :disabled="!accessGuard.checkPermission($roles.STUDY_WRITE)"
        :loading="loading"
        @click.stop="releaseStudy"
      >
        <v-icon left>mdi-share-variant</v-icon>
        <span class="label">{{ $t('Study.release') }}</span>
      </v-btn>
      <v-btn
        v-if="
          studiesGeneralStore.selectedStudy.current_metadata.version_metadata
            .study_status === 'DRAFT' &&
          !studiesGeneralStore.selectedStudy.study_parent_part &&
          isLatestStudySelected()
        "
        class="ml-2 expandHoverBtn"
        color="nnBaseBlue"
        data-cy="lock-study"
        :disabled="!accessGuard.checkPermission($roles.STUDY_WRITE)"
        :loading="loading"
        @click.stop="lockStudy"
      >
        <v-icon left>mdi-lock-outline</v-icon>
        <span class="label">{{ $t('Study.lock') }}</span>
      </v-btn>
      <v-btn
        v-if="
          studiesGeneralStore.selectedStudy.current_metadata.version_metadata
            .study_status === 'LOCKED' &&
          !studiesGeneralStore.selectedStudy.study_parent_part &&
          isLatestStudySelected()
        "
        class="ml-2 expandHoverBtn"
        color="nnBaseBlue"
        data-cy="unlock-study"
        :disabled="!accessGuard.checkPermission($roles.STUDY_WRITE)"
        :loading="loading"
        @click.stop="unlockStudy"
      >
        <v-icon left>mdi-lock-open-outline</v-icon>
        <span class="label">{{ $t('Study.unlock') }}</span>
      </v-btn>
    </template>
    <template #[`item.actions`]="{ item }">
      <ActionsMenu
        v-if="checkIfSelectable(item)"
        :actions="actions"
        :item="item"
      />
    </template>
    <template
      #[`item.current_metadata.version_metadata.study_status`]="{ item }"
    >
      <StatusChip
        :status="item.current_metadata.version_metadata.study_status"
        :outlined="false"
      />
    </template>
    <template
      #[`item.current_metadata.version_metadata.version_timestamp`]="{ item }"
    >
      {{
        $filters.date(item.current_metadata.version_metadata.version_timestamp)
      }}
    </template>
  </NNTable>
  <StudyStatusForm
    :action="statusAction"
    :open="showStatusForm"
    @close="closeStatusForm"
    @status-changed="refreshData"
  />
  <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
</template>

<script setup>
import { inject, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/api/study'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import filteringParameters from '@/utils/filteringParameters'
import NNTable from '@/components/tools/NNTable.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import StudyStatusForm from './StudyStatusForm.vue'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import { useAccessGuard } from '@/composables/accessGuard'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import _isEmpty from 'lodash/isEmpty'

const { t } = useI18n()
const notificationHub = inject('notificationHub')
const accessGuard = useAccessGuard()
const studiesGeneralStore = useStudiesGeneralStore()

const headers = [
  { title: '', key: 'actions', width: '1%' },
  {
    title: t('Study.status'),
    key: 'current_metadata.version_metadata.study_status',
  },
  {
    title: t('_global.version'),
    key: 'current_metadata.version_metadata.version_number',
  },
  {
    title: t('Study.release_description'),
    key: 'current_metadata.version_metadata.version_description',
  },
  {
    title: t('_global.modified'),
    key: 'current_metadata.version_metadata.version_timestamp',
  },
  {
    title: t('_global.modified_by'),
    key: 'current_metadata.version_metadata.version_author',
  },
]
const loading = ref(false)
const showStatusForm = ref(false)
const statusAction = ref(null)
const items = ref([])
const total = ref(0)
const actions = [
  {
    label: t('StudyTable.select'),
    icon: 'mdi-check-circle-outline',
    iconColor: 'primary',
    click: selectStudyVersion,
  },
]
const latestStudy = ref({})

function checkIfSelectable(studyVersion) {
  return (
    studyVersion.current_metadata.version_metadata.version_number !==
      studiesGeneralStore.selectedStudyVersion ||
    studyVersion.current_metadata.version_metadata.study_status !==
      studiesGeneralStore.selectedStudy.current_metadata.version_metadata
        .study_status
  )
}
async function selectStudyVersion(studyVersion) {
  await studiesGeneralStore.selectStudy(studyVersion, true)
}
function closeStatusForm() {
  loading.value = false
  showStatusForm.value = false
}
function fetchItems(filters, options, filtersUpdated) {
  const params = filteringParameters.prepareParameters(
    options,
    filters,
    filtersUpdated
  )
  api
    .getStudySnapshotHistory(studiesGeneralStore.selectedStudy.uid, params)
    .then((resp) => {
      items.value = resp.data.items
      total.value = resp.data.total
      if (_isEmpty(params.sort_by) && _isEmpty(params.filters)) {
        latestStudy.value = resp.data.items[0]
      }
    })
}
function isLatestStudySelected() {
  return (
    latestStudy.value.current_metadata.version_metadata.version_number ===
    studiesGeneralStore.selectedStudy.current_metadata.version_metadata
      .version_number
  )
}
function releaseStudy() {
  loading.value = true
  statusAction.value = 'release'
  showStatusForm.value = true
}
function lockStudy() {
  loading.value = true
  statusAction.value = 'lock'
  showStatusForm.value = true
}
async function refreshData() {
  fetchItems()
}
async function unlockStudy() {
  loading.value = true
  const resp = await api.unlockStudy(studiesGeneralStore.selectedStudy.uid)
  await studiesGeneralStore.selectStudy(resp.data)
  notificationHub.add({
    msg: t('StudyStatusTable.unlock_success'),
    type: 'success',
  })
  loading.value = false
  fetchItems()
}
</script>
