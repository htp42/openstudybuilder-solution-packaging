<template>
  <div class="pa-4 bg-white">
    <v-row>
      <v-col cols="4"> </v-col>
      <v-col cols="8" class="d-flex align-center">
        <v-spacer />
        <v-switch
          v-show="switchIsEnabled(['protocol'])"
          v-model="showSplitMenu"
          :label="$t('ProtocolFlowchart.show_split_menu')"
          hide-details
          class="mr-4"
          color="primary"
          :readonly="soaContentLoadingStore.loading || toggle.length !== 0"
          :disabled="toggle.length !== 0"
          :loading="soaContentLoadingStore.loading ? 'warning' : null"
        />
        <v-switch
          v-show="switchIsEnabled(['protocol'])"
          v-model="studiesGeneralStore.soaPreferences.show_epochs"
          :label="$t('ProtocolFlowchart.show_epochs')"
          hide-details
          class="mr-4"
          color="primary"
          :readonly="soaContentLoadingStore.loading"
          :loading="soaContentLoadingStore.loading ? 'warning' : null"
          @update:model-value="updateSoaPreferences('show_epochs')"
        />
        <v-switch
          v-show="switchIsEnabled(['protocol'])"
          v-model="studiesGeneralStore.soaPreferences.show_milestones"
          :label="$t('ProtocolFlowchart.show_milestones')"
          hide-details
          class="mr-4"
          color="primary"
          :readonly="soaContentLoadingStore.loading"
          :loading="soaContentLoadingStore.loading ? 'warning' : null"
          @update:model-value="updateSoaPreferences('show_milestones')"
        />
        <v-menu rounded location="bottom">
          <template #activator="{ props }">
            <v-btn
              class="ml-2"
              size="small"
              variant="outlined"
              color="nnBaseBlue"
              v-bind="props"
              :title="$t('DataTableExportButton.export')"
              icon="mdi-download-outline"
              :loading="soaContentLoadingStore.loading"
            />
          </template>
          <v-list>
            <v-list-item link @click="downloadCSV">
              <v-list-item-title>CSV</v-list-item-title>
            </v-list-item>
            <v-list-item link @click="downloadEXCEL">
              <v-list-item-title>EXCEL</v-list-item-title>
            </v-list-item>
            <v-list-item link @click="downloadDocx">
              <v-list-item-title>DOCX</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-col>
    </v-row>
    <div v-if="layout === 'protocol' && showSplitMenu">
      <div class="text-center">
        {{ $t('ProtocolFlowchart.split_info_1') }}
      </div>
      <div class="text-center">
        {{ $t('ProtocolFlowchart.split_info_2') }}
      </div>
      <div class="d-flex flex-column align-center pa-6">
        <v-btn-toggle
          v-model="toggle"
          style="overflow-x: auto"
          variant="outlined"
          divided
          multiple
        >
          <v-slide-group show-arrows>
            <v-btn
              v-for="visit in groupedVisits"
              :key="visit.uid"
              selected-class="split-class"
              variant="outlined"
              rounded="0"
              elevation="0"
              :value="visit.uid"
              :disabled="!switchIsEnabled(['protocol'])"
              @click="splitSoA(visit.uid)"
            >
              <template #prepend>
                <v-icon
                  v-if="toggle.includes(visit.uid)"
                  icon="mdi-content-cut"
                  class="horizontal-flip"
                />
              </template>
              {{ visit.group || visit.name }}
            </v-btn>
          </v-slide-group>
        </v-btn-toggle>
      </div>
    </div>
    <div
      id="protocolFlowchart"
      class="mt-4"
      v-html="sanitizeHTMLHandler(protocolFlowchart)"
    />
  </div>
</template>

<script setup>
import { inject, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import study from '@/api/study'
import soaDownloads from '@/utils/soaDownloads'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useSoaContentLoadingStore } from '@/stores/soa-content-loading'
import unitConstants from '@/constants/units'
import units from '@/api/units'
import { useAccessGuard } from '@/composables/accessGuard'
import { sanitizeHTML } from '@/utils/sanitize'
import studyEpochsApi from '@/api/studyEpochs'

const props = defineProps({
  update: {
    type: Number,
    default: 0,
  },
  layout: {
    type: String,
    default: 'protocol',
  },
})

const studiesGeneralStore = useStudiesGeneralStore()
const soaContentLoadingStore = useSoaContentLoadingStore()
const accessGuard = useAccessGuard()
const { t } = useI18n()
const roles = inject('roles')

const protocolFlowchart = ref('')
const loadingMessage = ref('')
const preferredTimeUnits = ref([])
const toggle = ref([])
const groupedVisits = ref([])
const showSplitMenu = ref(false)

watch(
  () => props.layout,
  (newVal, oldVal) => {
    if (newVal !== oldVal) updateFlowchart()
  }
)
watch(
  () => props.update,
  (newVal, oldVal) => {
    if (newVal !== oldVal) updateFlowchart()
  }
)

onMounted(() => {
  updateFlowchart()
  units
    .getBySubset(unitConstants.TIME_UNIT_SUBSET_STUDY_PREFERRED_TIME_UNIT)
    .then((resp) => {
      preferredTimeUnits.value = resp.data.items
    })
  loadVisits()
  getSoASplits()
})

async function loadVisits() {
  try {
    const resp = await studyEpochsApi.getStudyVisits(
      studiesGeneralStore.selectedStudy.uid,
      { page_size: 0 }
    )
    const items = resp.data.items

    const visits = items.map((v) => ({
      name: v.visit_short_name,
      uid: v.uid,
      show_visit: v.show_visit,
      group: v.consecutive_visit_group ?? null,
    }))

    const result = []
    let lastGroup = null

    for (const visit of visits.slice(1)) {
      if (!visit.show_visit) {
        continue
      }
      if (!visit.group) {
        result.push(visit)
        lastGroup = null
      } else {
        if (visit.group !== lastGroup) {
          result.push(visit)
        }
        lastGroup = visit.group
      }
    }
    groupedVisits.value = result
  } catch (error) {
    console.error('Failed to load visits', error)
  }
}
async function splitSoA(visitUid) {
  if (toggle.value.includes(visitUid)) {
    const payload = { uid: visitUid }
    await study.splitSoA(studiesGeneralStore.selectedStudy.uid, payload)
    updateFlowchart()
  } else {
    await study.removeSoASplit(studiesGeneralStore.selectedStudy.uid, visitUid)
    updateFlowchart()
  }
}
async function getSoASplits() {
  const resp = await study.getSoASplits(studiesGeneralStore.selectedStudy.uid)
  toggle.value = resp.data.map((item) => item.uid)
  if (toggle.value.length) {
    showSplitMenu.value = true
  }
}
function sanitizeHTMLHandler(html) {
  return sanitizeHTML(html)
}
function switchIsEnabled(layouts = []) {
  return (
    !studiesGeneralStore.selectedStudyVersion &&
    accessGuard.checkPermission(roles.STUDY_WRITE) &&
    (!layouts || layouts.includes(props.layout))
  )
}
function updateSoaPreferences(key) {
  studiesGeneralStore
    .setSoaPreferences({ [key]: studiesGeneralStore.soaPreferences[key] })
    .then(() => {
      updateFlowchart()
    })
}
function updateFlowchart() {
  loadingMessage.value = t('ProtocolFlowchart.loading')
  soaContentLoadingStore.changeLoadingState()
  study
    .getStudyProtocolFlowchartHtml(studiesGeneralStore.selectedStudy.uid, {
      layout: props.layout,
    })
    .then((resp) => {
      protocolFlowchart.value = resp.data
    })
    .catch(stopLoading())
}
async function downloadDocx() {
  loadingMessage.value = t('ProtocolFlowchart.downloading')
  soaContentLoadingStore.changeLoadingState()
  try {
    await soaDownloads.docxDownload(props.layout)
  } finally {
    stopLoading()
  }
}
async function downloadCSV() {
  soaContentLoadingStore.changeLoadingState()
  try {
    await soaDownloads.csvDownload(props.layout)
  } finally {
    stopLoading()
  }
}
async function downloadEXCEL() {
  soaContentLoadingStore.changeLoadingState()
  try {
    await soaDownloads.excelDownload(props.layout)
  } finally {
    stopLoading()
  }
}
function stopLoading() {
  loadingMessage.value = ''
  soaContentLoadingStore.changeLoadingState()
}
</script>

<style lang="scss">
.split-class {
  color: red;
  border-inline-start-style: solid !important;
  border-left-color: red !important;
  border-left-width: medium !important;
}
.layoutSelect {
  max-width: 200px;
}
.horizontal-flip {
  transform: rotate(180deg);
}
#protocolFlowchart {
  padding-bottom: 1em;

  table {
    width: 100%;
    border-collapse: collapse;
    table-layout: auto;
    resize: both;
    margin-bottom: 1em;

    &:not(:first-child) {
      margin-top: 2em;
    }

    &,
    & th,
    & td {
      border: 1px solid black;
      padding: 1px 3px;
    }

    & thead {
      background-color: rgb(var(--v-theme-tableGray));

      & th {
        border-color: black;
      }

      & .header1:nth-child(n + 2) {
        vertical-align: top;
        text-orientation: mixed;
      }

      & th:first-child {
        text-align: left;
      }
    }

    & tbody {
      & th {
        text-align: left;
        font-weight: normal;
      }

      & tr td:nth-child(n + 2) {
        text-align: center;
        vertical-align: middle;
      }

      & .soaGroup {
        background-color: rgb(var(--v-theme-tableGray));
        font-weight: bold;
      }

      & .group {
        background-color: rgb(var(--v-theme-tableGray));
        font-weight: bold;
      }

      & .subGroup {
        background-color: rgb(var(--v-theme-tableGray));
      }

      & .activity:first-child {
        background-color: rgb(var(--v-theme-tableGray));
        padding-left: 1em;
      }

      & .activityInstance:first-child {
        padding-left: 2em;
        font-style: italic;
      }
    }
  }
}
</style>
