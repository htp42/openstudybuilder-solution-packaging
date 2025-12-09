<template>
  <NNTable
    key="studyActivityInstancesTable"
    ref="tableRef"
    export-object-label="ActivityInstances"
    :headers="headers"
    :items="studyActivitiesInstances"
    :items-length="total"
    item-value="activity_instance.uid"
    :export-data-url="exportDataUrl"
    :column-data-resource="`studies/${studiesGeneralStore.selectedStudy.uid}/study-activity-instances`"
    :history-data-fetcher="fetchStudyActivityInstancesHistory"
    :history-title="$t('StudyActivityTable.global_history_title')"
    :filters-modify-function="modifyFilters"
    :default-filters="defaultFilters"
    @filter="getStudyActivityInstances"
  >
    <template #headerCenter="">
      <v-btn-toggle
        v-model="selectedStatusTab"
        mandatory
        density="compact"
        color="nnBaseBlue"
        divided
        variant="outlined"
        class="layoutSelector"
        @update:model-value="onStatusTabChange"
      >
        <v-btn v-for="tab in statusTabs" :key="tab.value" :value="tab.value">
          <v-icon v-if="tab.icon" :color="tab.color">{{ tab.icon }}</v-icon>
          {{ tab.label }}
        </v-btn>
      </v-btn-toggle>
    </template>
    <template #actions="">
      <v-btn
        variant="outlined"
        color="nnBaseBlue"
        :disabled="
          !accessGuard.checkPermission($roles.STUDY_WRITE) ||
          studiesGeneralStore.selectedStudyVersion !== null
        "
        rounded="xl"
        prepend-icon="mdi-exclamation"
        @click="openBatchUpdateForm()"
      >
        {{ $t('StudyActivityTable.review_instances') }}
      </v-btn>
    </template>
    <template #[`item.actions`]="{ item }">
      <ActionsMenu
        :actions="actions"
        :item="item"
        :badge="actionsMenuBadge(item)"
      />
    </template>
    <template #[`item.activity_instance.name`]="{ item }">
      <template v-if="item.activity_instance">
        <router-link
          :to="{
            name: 'ActivityInstanceOverview',
            params: { id: item.activity_instance.uid },
          }"
        >
          {{ item.activity_instance?.name }}
        </router-link>
      </template>
    </template>
    <template #[`item.activity.is_data_collected`]="{ item }">
      {{ $filters.yesno(item.activity.is_data_collected) }}
    </template>
    <template #[`item.state`]="{ item }">
      <div
        :class="getInstanceCssClass(item)"
        @click="
          [instancesActions.REVIEW_NEEDED, instancesActions.ADD].indexOf(
            item.state
          ) !== -1
            ? editRelationship(item)
            : ''
        "
      >
        {{ item.state }}
      </div>
    </template>
    <template #[`item.is_reviewed`]="{ item }">
      <v-checkbox
        v-model="item.is_reviewed"
        class="mt-2 mb-n4"
        :disabled="
          [
            instancesActions.ADD,
            instancesActions.NA,
            instancesActions.REMOVE,
          ].indexOf(item.state) !== -1 ||
          (item.is_activity_instance_updated && !item.keep_old_version)
        "
        @update:model-value="updateReviewedState(item)"
      />
    </template>
    <template #[`item.is_important`]="{ item }">
      {{ item.is_important ? $t('_global.yes') : '' }}
    </template>
    <template #[`item.baseline_visits`]="{ item }">
      {{ displayVisits(item.baseline_visits) }}
    </template>
  </NNTable>
  <StudyActivityInstancesEditForm
    :open="showEditForm"
    :edited-activity="activeActivity"
    @close="closeEditForm"
  />
  <v-dialog
    v-model="showHistory"
    persistent
    :fullscreen="$globals.historyDialogFullscreen"
    @keydown.esc="closeHistory"
  >
    <HistoryTable
      :title="activityInstanceHistoryTitle"
      :headers="headers"
      :items="activityInstanceHistoryItems"
      @close="closeHistory"
    />
  </v-dialog>
  <UpdateActivityInstanceForm
    :activity="activeActivity"
    :open="showUpdateForm"
    @close="closeUpdateForm"
  />
  <v-dialog v-model="showBatchUpdateForm">
    <BatchUpdateActivityInstanceForm @close="closeBatchUpdateForm" />
  </v-dialog>
  <ConfirmDialog ref="confirmRef" :text-cols="6" :action-cols="5" />
</template>
<script setup>
import { computed, inject, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useStudyActivitiesStore } from '@/stores/studies-activities'
import study from '@/api/study'
import filteringParameters from '@/utils/filteringParameters'
import NNTable from '@/components/tools/NNTable.vue'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import StudyActivityInstancesEditForm from './StudyActivityInstancesEditForm.vue'
import HistoryTable from '@/components/tools/HistoryTable.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import UpdateActivityInstanceForm from './UpdateActivityInstanceForm.vue'
import BatchUpdateActivityInstanceForm from './BatchUpdateActivityInstanceForm.vue'
import instancesActions from '@/constants/instancesActions'
import { useAccessGuard } from '@/composables/accessGuard'
import _isEmpty from 'lodash/isEmpty'

const { t } = useI18n()
const notificationHub = inject('notificationHub')
const studiesGeneralStore = useStudiesGeneralStore()
const activitiesStore = useStudyActivitiesStore()
const accessGuard = useAccessGuard()
const roles = inject('roles')
const tableRef = ref()
const confirmRef = ref()

const headers = [
  { title: '', key: 'actions', width: '1%' },
  { title: t('StudyActivityInstances.state_actions'), key: 'state' },
  { title: t('StudyActivityInstances.reviewed'), key: 'is_reviewed' },
  { title: t('_global.library'), key: 'activity.library_name' },
  {
    title: t('StudyActivity.flowchart_group'),
    key: 'study_soa_group.soa_group_term_name',
  },
  {
    title: t('StudyActivity.activity_group'),
    key: 'study_activity_group.activity_group_name',
  },
  {
    title: t('StudyActivity.activity_sub_group'),
    key: 'study_activity_subgroup.activity_subgroup_name',
  },
  { title: t('StudyActivity.activity'), key: 'activity.name' },
  {
    title: t('StudyActivity.data_collection'),
    key: 'activity.is_data_collected',
  },
  {
    title: t('StudyActivityInstances.activity_instance'),
    key: 'activity_instance.name',
  },
  {
    title: t('StudyActivityInstances.topic_code'),
    key: 'activity_instance.topic_code',
  },
  {
    title: t('StudyActivityInstances.test_name_code'),
    key: 'activity_instance.test_name_code',
  },
  {
    title: t('StudyActivityInstances.specimen'),
    key: 'activity_instance.specimen',
  },
  {
    title: t('StudyActivityInstances.standard_unit'),
    key: 'activity_instance.standard_unit',
  },
  {
    title: t('StudyActivityInstances.adam_code'),
    key: 'activity_instance.adam_param_code',
  },
  {
    title: t('StudyActivityInstances.important'),
    key: 'is_important',
  },
  {
    title: t('StudyActivityInstances.baseline_visits'),
    key: 'baseline_visits',
  },
]
const studyActivitiesInstances = ref([])
const total = ref(0)
const activeActivity = ref({})
const showEditForm = ref(false)
const activityInstanceHistoryItems = ref([])
const showHistory = ref(false)
const showUpdateForm = ref(false)
const showBatchUpdateForm = ref(false)
const actions = [
  {
    label: t('StudyActivityInstances.edit_relationship'),
    icon: 'mdi-pencil-outline',
    iconColor: 'primary',
    condition: () => !studiesGeneralStore.selectedStudyVersion,
    click: editRelationship,
    accessRole: roles.STUDY_WRITE,
  },
  {
    label: t('StudyActivityInstances.delete_relationship'),
    icon: 'mdi-delete-outline',
    iconColor: 'error',
    condition: () => !studiesGeneralStore.selectedStudyVersion,
    click: deleteRelationship,
    accessRole: roles.STUDY_WRITE,
  },
  {
    label: t('StudyActivityInstances.update_to_new_version'),
    icon: 'mdi-update',
    iconColor: 'primary',
    condition: (item) =>
      !studiesGeneralStore.selectedStudyVersion &&
      item.is_activity_instance_updated,
    click: openUpdateForm,
    accessRole: roles.STUDY_WRITE,
  },
  {
    label: (item) =>
      item.is_important
        ? t('StudyActivityInstances.unmark_as_important')
        : t('StudyActivityInstances.mark_as_important'),
    icon: 'mdi-alert-octagon-outline',
    condition: (item) =>
      !studiesGeneralStore.selectedStudyVersion &&
      item.activity_instance &&
      item.activity.is_data_collected,
    click: toggleImportant,
    accessRole: roles.STUDY_WRITE,
  },
  {
    label: t('_global.history'),
    icon: 'mdi-history',
    click: openHistory,
  },
]
const selectedStatusTab = ref('all')
const statusTabs = [
  { value: 'all', label: t('_global.all') },
  { value: 'updated', icon: 'mdi-alert-circle-outline', color: 'error' },
  { value: 'reviewed', icon: 'mdi-alert-outline', color: 'warning' },
]
const defaultFilters = computed(() => {
  return headers
    .filter((a) => a.key !== 'actions')
    .filter((a) => a.key !== 'test_name_code')
    .filter((a) => a.key !== 'specimen')
    .filter((a) => a.key !== 'standard_unit')
})
const exportDataUrl = computed(() => {
  return `studies/${studiesGeneralStore.selectedStudy.uid}/study-activity-instances`
})
const activityInstanceHistoryTitle = computed(() => {
  if (activeActivity.value) {
    return t('StudyActivityInstances.study_activity_instance_history_title', {
      studyActivityInstanceUid:
        activeActivity.value.study_activity_instance_uid,
    })
  }
  return ''
})

function getInstanceCssClass(item) {
  if (
    [instancesActions.REVIEWED, instancesActions.REVIEW_NOT_NEEDED].indexOf(
      item.state
    ) !== -1
  )
    return 'reviewed'
  if (item.state === instancesActions.REMOVE) return 'needed'
  if (item.state === instancesActions.REVIEW_NEEDED) return 'needed row-pointer'
  if (item.state === instancesActions.ADD) return 'add row-pointer'
  return 'na'
}

function updateReviewedState(instance) {
  study
    .updateStudyActivityInstance(
      studiesGeneralStore.selectedStudy.uid,
      instance.study_activity_instance_uid,
      { is_reviewed: instance.is_reviewed }
    )
    .then(() => {
      tableRef.value.filterTable()
    })
}

function getStudyActivityInstances(filters, options, filtersUpdated) {
  const params = filteringParameters.prepareParameters(
    options,
    filters,
    filtersUpdated
  )
  if (params.filters) {
    const filtersObj = JSON.parse(params.filters)
    if (filtersObj['activity_group.name']) {
      params.activity_group_names = []
      filtersObj['activity_group.name'].v.forEach((value) => {
        params.activity_group_names.push(value)
      })
      delete filtersObj['activity_group.name']
    }
    if (filtersObj['activity_subgroup.name']) {
      params.activity_subgroup_names = []
      filtersObj['activity_subgroup.name'].v.forEach((value) => {
        params.activity_subgroup_names.push(value)
      })
      delete filtersObj['activity_subgroup.name']
    }
    if (filtersObj['activity.name']) {
      params.activity_names = []
      filtersObj['activity.name'].v.forEach((value) => {
        params.activity_names.push(value)
      })
      delete filtersObj['activity.name']
    }
    if (Object.keys(filtersObj).length !== 0) {
      params.filters = JSON.stringify(filtersObj)
    } else {
      delete params.filters
    }
  }
  let statusFilter = {}
  if (selectedStatusTab.value === 'reviewed') {
    statusFilter = { keep_old_version: { v: [true] } }
  } else if (selectedStatusTab.value === 'updated') {
    statusFilter = {
      is_activity_instance_updated: { v: [true] },
      keep_old_version: { v: [false] },
    }
  }

  if (selectedStatusTab.value !== 'all') {
    if (_isEmpty(params.filters)) {
      params.filters = statusFilter
    } else {
      const filtersObj =
        typeof params.filters === 'string'
          ? JSON.parse(params.filters)
          : params.filters
      Object.assign(filtersObj, statusFilter)
      params.filters = filtersObj
    }
  }
  params.studyUid = studiesGeneralStore.selectedStudy.uid
  activitiesStore.fetchStudyActivityInstances(params).then((resp) => {
    studyActivitiesInstances.value = resp.data.items
    total.value = resp.data.total
  })
}

function modifyFilters(jsonFilter, params) {
  if (jsonFilter['activity_group.name']) {
    params.activity_group_names = []
    jsonFilter['activity_group.name'].v.forEach((value) => {
      params.activity_group_names.push(value)
    })
    delete jsonFilter['activity_group.name']
  }
  if (jsonFilter.activity_groups) {
    params.activity_group_names = []
    jsonFilter.activity_groups.v.forEach((value) => {
      params.activity_group_names.push(value)
    })
    delete jsonFilter.activity_groups
  }
  if (jsonFilter['activity_subgroup.name']) {
    params.activity_subgroup_names = []
    jsonFilter['activity_subgroup.name'].v.forEach((value) => {
      params.activity_subgroup_names.push(value)
    })
    delete jsonFilter['activity_subgroup.name']
  }
  if (jsonFilter.name) {
    params.activity_names = []
    jsonFilter.name.v.forEach((value) => {
      params.activity_names.push(value)
    })
    delete jsonFilter.name
  }
  if (jsonFilter['activity.name']) {
    params.activity_names = []
    jsonFilter['activity.name'].v.forEach((value) => {
      params.activity_names.push(value)
    })
    delete jsonFilter['activity.name']
  }
  return {
    jsonFilter: jsonFilter,
    params: params,
  }
}

function editRelationship(item) {
  activeActivity.value = item
  showEditForm.value = true
}

function closeEditForm() {
  activeActivity.value = {}
  showEditForm.value = false
  tableRef.value.filterTable()
}

function displayVisits(visits) {
  if (!visits) {
    return ''
  }
  return visits.map((v) => v.visit_name).join(', ')
}

async function deleteRelationship(item) {
  const options = {
    type: 'warning',
    cancelLabel: t('_global.cancel'),
    agreeLabel: t('_global.delete'),
  }
  if (
    await confirmRef.value.open(
      t('StudyActivityInstances.confirm_delete', {
        instance: item.study_activity_instance_uid,
      }),
      options
    )
  ) {
    activitiesStore
      .deleteStudyActivityInstance(
        studiesGeneralStore.selectedStudy.uid,
        item.study_activity_instance_uid
      )
      .then(() => {
        notificationHub.add({
          msg: t('StudyActivityInstances.instance_deleted'),
          type: 'success',
        })
        tableRef.value.filterTable()
      })
  }
}

async function fetchStudyActivityInstancesHistory() {
  const resp = await study.getStudyActivityInstancesAuditTrail(
    studiesGeneralStore.selectedStudy.uid
  )
  return resp.data
}

async function openHistory(item) {
  activeActivity.value = item
  const resp = await study.getStudyActivityInstanceAuditTrail(
    studiesGeneralStore.selectedStudy.uid,
    item.study_activity_instance_uid
  )
  activityInstanceHistoryItems.value = resp.data
  showHistory.value = true
}

function closeHistory() {
  activeActivity.value = {}
  showHistory.value = false
}

function actionsMenuBadge(item) {
  if (item.is_activity_instance_updated) {
    return {
      color: item.keep_old_version ? 'warning' : 'error',
      icon: item.keep_old_version
        ? 'mdi-alert-outline'
        : 'mdi-alert-circle-outline',
    }
  }
  return undefined
}

function openUpdateForm(item) {
  activeActivity.value = item
  showUpdateForm.value = true
}

function closeUpdateForm() {
  activeActivity.value = null
  showUpdateForm.value = false
  tableRef.value.filterTable()
}

function openBatchUpdateForm() {
  showBatchUpdateForm.value = true
}

function closeBatchUpdateForm() {
  showBatchUpdateForm.value = false
  tableRef.value.filterTable()
}

function onStatusTabChange() {
  if (tableRef.value) {
    tableRef.value.filterTable()
  }
}
async function toggleImportant(item) {
  const newImportantStatus = !item.is_important
  const data = {
    is_important: newImportantStatus,
  }

  try {
    await study.updateStudyActivityInstance(
      studiesGeneralStore.selectedStudy.uid,
      item.study_activity_instance_uid,
      data
    )

    const messageKey = newImportantStatus
      ? 'StudyActivityInstances.instance_marked_important'
      : 'StudyActivityInstances.instance_unmarked_important'

    notificationHub.add({ msg: t(messageKey), type: 'success' })

    // Refresh the table to show updated data
    tableRef.value.filterTable()
  } catch (error) {
    // Error notification is handled by the repository interceptor
    console.error('Failed to toggle important status:', error)
  }
}
</script>
<style scoped>
.reviewed {
  background-color: darkseagreen;
  border-radius: 5px;
  padding-inline: 5px;
  color: black;
}
.add {
  background-color: rgb(202, 124, 124);
  border-radius: 5px;
  padding-inline: 5px;
  color: black;
}
.needed {
  background-color: rgb(217, 201, 106);
  border-radius: 5px;
  padding-inline: 5px;
  color: black;
}
.na {
  background-color: rgb(179, 179, 179);
  border-radius: 5px;
  padding-inline: 5px;
  color: black;
}
.row-pointer {
  cursor: pointer;
}
.layoutSelector {
  border-color: rgb(var(--v-theme-nnBaseBlue));
}
.layoutSelector :deep(.v-btn) {
  text-transform: none;
}
</style>
