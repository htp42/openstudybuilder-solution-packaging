<template>
  <div>
    <v-row v-if="!doc" class="mt-2 ml-2 mr-2">
      <v-col cols="4">
        <v-select
          v-model="data.target_type"
          :items="types"
          :label="$t('OdmViewer.element_type')"
          density="comfortable"
          clearable
          item-title="name"
          item-value="value"
          class="mt-2"
          :class="{ shake: shakeit && !data.target_type }"
          @update:model-value="setElements()"
          @click:clear="data.target_uid = null"
        />
      </v-col>
      <v-col cols="4" @click="() => activateShake(!data.target_type)">
        <v-select
          v-model="data.target_uid"
          :items="elements"
          :label="targetUidLabel"
          density="comfortable"
          clearable
          class="mt-2"
          item-title="name"
          item-value="uid"
          :disabled="!data.target_type"
          :class="{ shake: shakeit && data.target_type && !data.target_uid }"
          @update:model-value="setElementVersions()"
        />
      </v-col>
      <v-col cols="4" @click="() => activateShake(!data.target_uid)">
        <v-select
          ref="versionSelect"
          v-model="elementVersion"
          :items="elementFinalVersions"
          :label="$t('OdmViewer.element_version')"
          density="comfortable"
          class="mt-2"
          :disabled="!data.target_uid"
        >
          <template #prepend-item>
            <v-list-item
              style="cursor: pointer"
              @click="
                () => {
                  elementVersion = $t('OdmViewer.latest_version')
                  $refs.versionSelect.blur()
                }
              "
            >
              <v-list-item-title class="ms-4">
                {{ $t('OdmViewer.latest_version') }}
              </v-list-item-title>
            </v-list-item>
            <v-divider v-if="elementFinalVersions.length > 0" />
          </template>

          <template #no-data />
        </v-select>
      </v-col>
    </v-row>
    <v-row
      v-if="!doc"
      class="mt-2 ml-2 mr-2"
      @click="() => activateShake(!data.target_uid)"
    >
      <v-col cols="4">
        <v-select
          v-model="data.selectedStylesheet"
          :items="data.stylesheet"
          density="comfortable"
          :label="$t('OdmViewer.stylesheet')"
          :disabled="!data.target_uid"
        />
      </v-col>
      <v-col cols="4">
        <v-select
          v-model="selectedNamespaces"
          :items="allowedNamespaces"
          :label="$t('OdmViewer.allowed_namespaces')"
          density="comfortable"
          clearable
          :disabled="!data.target_uid"
          multiple
        >
          <template #prepend-item>
            <v-list-item
              :title="
                allNamespacesSelected
                  ? t('_global.unselect_all')
                  : t('_global.select_all')
              "
              @click="toggleNamespace"
            >
              <template #prepend>
                <v-checkbox-btn
                  :indeterminate="
                    !allNamespacesSelected && someNamespacesSelected
                  "
                  :model-value="allNamespacesSelected"
                ></v-checkbox-btn>
              </template>
            </v-list-item>

            <v-divider class="mt-2"></v-divider>
          </template>

          <template #selection="{ item, index }">
            <v-chip
              v-if="index < 2"
              :text="item.title"
              density="compact"
            ></v-chip>

            <span
              v-if="index === 2"
              class="text-grey text-caption align-self-center"
            >
              (+{{ selectedNamespaces.length - 2 }}
              {{ selectedNamespaces.length - 2 === 1 ? 'other' : 'others' }})
            </span>
          </template>
        </v-select>
      </v-col>
      <v-col cols="4">
        <v-btn
          :disabled="!data.target_uid"
          color="secondary"
          rounded="xl"
          :label="$t('_global.load')"
          size="large"
          block
          @click="loadXml"
        >
          {{ $t('OdmViewer.generate') }}
        </v-btn>
      </v-col>
    </v-row>
    <v-row v-else class="mt-0 ml-2">
      <v-btn
        v-show="doc"
        size="small"
        color="primary"
        class="mr-4 mt-3 white--text"
        icon="mdi-arrow-left"
        :title="$t('_global.back')"
        @click="clearXml"
      />
      <v-btn
        v-show="doc"
        size="small"
        color="nnGreen1"
        class="ml-4 mt-3 white--text"
        :title="$t('DataTableExportButton.export_xml')"
        :loading="xmlDownloadLoading"
        icon="mdi-file-xml-box"
        @click="downloadXml"
      />
      <v-btn
        v-show="doc !== ''"
        size="small"
        color="nnGreen1"
        class="ml-4 mt-3 white--text"
        :title="$t('DataTableExportButton.export_pdf')"
        :loading="pdfDownloadLoading"
        icon="mdi-file-pdf-box"
        @click="downloadPdf"
      />
      <v-btn
        v-show="doc !== ''"
        size="small"
        color="nnGreen1"
        class="ml-4 mt-3 white--text"
        :title="$t('DataTableExportButton.export_html')"
        :loading="htmlDownloadLoading"
        icon="mdi-file-document-outline"
        @click="downloadHtml"
      />
      <v-spacer />
      <v-switch
        v-model="showOdmXml"
        :label="$t('OdmViewer.xml_code')"
        color="primary"
        class="mr-6"
        inset
      ></v-switch>
    </v-row>
    <div v-show="loading">
      <v-row align="center" justify="center" style="text-align: -webkit-center">
        <v-col cols="12" sm="4">
          <div class="text-h5">
            {{ $t('OdmViewer.loading_message') }}
          </div>
          <v-progress-circular
            color="primary"
            indeterminate
            size="128"
            class="ml-4"
          />
        </v-col>
      </v-row>
    </div>
    <div v-show="doc && !showOdmXml" class="mt-4">
      <iframe />
    </div>
    <div v-show="doc && showOdmXml" class="mt-4">
      <v-card color="primary" style="overflow-x: auto">
        <pre v-show="!loading" class="ml-6 mt-6 pre" style="color: #ff0">{{
          xmlString
        }}</pre>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import _isEmpty from 'lodash/isEmpty'
import crfs from '@/api/crfs'
import exportLoader from '@/utils/exportLoader'
import { DateTime } from 'luxon'
import { ref, watch, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  typeProp: {
    type: String,
    default: null,
  },
  elementProp: {
    type: String,
    default: null,
  },
  refresh: {
    type: String,
    default: null,
  },
})
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const allowedNamespaces = ref([])
const selectedNamespaces = ref([])
const showOdmXml = ref(false)

const elements = ref([])
const elementFinalVersions = ref(new Set())
let xml = ''
const xmlString = ref('')
const doc = ref(null)
const data = ref({
  target_type: 'form',
  target_uid: null,
  version: '',
  stylesheet: [
    {
      title: t('OdmViewer.crf_with_annotations'),
      value: 'with-annotations',
    },
    {
      title: t('OdmViewer.falcon'),
      value: 'falcon',
    },
  ],
  selectedStylesheet: 'with-annotations',
  export_to: 'v1',
})
const loading = ref(false)
const xmlDownloadLoading = ref(false)
const pdfDownloadLoading = ref(false)
const htmlDownloadLoading = ref(false)
const types = [
  { name: t('OdmViewer.collection'), value: 'study_event' },
  { name: t('OdmViewer.form'), value: 'form' },
  { name: t('OdmViewer.item_group'), value: 'item_group' },
  { name: t('OdmViewer.item'), value: 'item' },
]
const elementVersion = ref(t('OdmViewer.latest_version'))
let url = ''

watch(
  () => props.refresh,
  () => {
    if (props.refresh === 'odm-viewer' && url !== '') {
      const stateObj = { id: '100' }
      window.history.replaceState(stateObj, 'Loaded CRF', url)
    }
  }
)

watch(
  () => props.elementProp,
  () => {
    automaticLoad()
  }
)

onMounted(() => {
  automaticLoad()
})

const shakeit = ref(false)

const targetUidLabel = computed(() => {
  switch (data.value.target_type) {
    case 'study_event':
      return t('OdmViewer.collection_name')
    case 'form':
      return t('OdmViewer.form_name')
    case 'item_group':
      return t('OdmViewer.item_group_name')
    case 'item':
      return t('OdmViewer.item_name')
    default:
      return t('OdmViewer.element_name')
  }
})

const allNamespacesSelected = computed(() => {
  return (
    someNamespacesSelected.value &&
    selectedNamespaces.value.length === allowedNamespaces.value.length
  )
})
const someNamespacesSelected = computed(() => {
  return selectedNamespaces.value.length > 0
})

function toggleNamespace() {
  if (allNamespacesSelected.value) {
    selectedNamespaces.value = []
  } else {
    selectedNamespaces.value = [...allowedNamespaces.value]
  }
}

function automaticLoad() {
  data.value.target_type = route.params.type || 'form'
  data.value.target_uid = route.params.uid || null
  setElements()
  if (_isEmpty(allowedNamespaces.value)) {
    crfs.getAllNamespaces({ page_size: 0 }).then((resp) => {
      allowedNamespaces.value = resp.data.items.map((item) => item.prefix)

      selectedNamespaces.value = allowedNamespaces.value
    })
  }
  if (data.value.target_type && data.value.target_uid) {
    loadXml()
  }
}

function setElements() {
  if (data.value.target_type) {
    const params = { page_size: 0 }
    switch (data.value.target_type) {
      case 'study_event':
        crfs.get('study-events', { params }).then((resp) => {
          elements.value = resp.data.items
        })
        return
      case 'form':
        crfs.get('forms', { params }).then((resp) => {
          elements.value = resp.data.items
        })
        return
      case 'item_group':
        crfs.get('item-groups', { params }).then((resp) => {
          elements.value = resp.data.items
        })
        return
      case 'item':
        crfs.get('items', { params }).then((resp) => {
          elements.value = resp.data.items
        })
    }
  }
}

function setElementVersions() {
  const isFinalVersion = (version) => version.endsWith('.0')

  switch (data.value.target_type) {
    case 'study_event':
      crfs.getCollectionAuditTrail(data.value.target_uid).then((resp) => {
        elementFinalVersions.value = new Set(
          resp.data
            .filter((item) => isFinalVersion(item.version))
            .map((item) => item.version)
        )
      })
      return
    case 'form':
      crfs.getFormAuditTrail(data.value.target_uid).then((resp) => {
        elementFinalVersions.value = new Set(
          resp.data
            .filter((item) => isFinalVersion(item.version))
            .map((item) => item.version)
        )
      })
      return
    case 'item_group':
      crfs.getGroupAuditTrail(data.value.target_uid).then((resp) => {
        elementFinalVersions.value = new Set(
          resp.data
            .filter((item) => isFinalVersion(item.version))
            .map((item) => item.version)
        )
      })
      return
    case 'item':
      crfs.getItemAuditTrail(data.value.target_uid).then((resp) => {
        elementFinalVersions.value = new Set(
          resp.data
            .filter((item) => isFinalVersion(item.version))
            .map((item) => item.version)
        )
      })
      return
  }
}

function getAllowedNamespaces() {
  if (_isEmpty(selectedNamespaces.value)) {
    return ''
  } else if (
    allowedNamespaces.value.length == selectedNamespaces.value.length
  ) {
    return '&allowed_namespaces=*'
  } else {
    return selectedNamespaces.value
      .map((ns) => `&allowed_namespaces=${encodeURIComponent(ns)}`)
      .join('')
  }
}

async function loadXml() {
  doc.value = ''
  loading.value = true
  data.value.version =
    elementVersion.value == t('OdmViewer.latest_version')
      ? ''
      : elementVersion.value

  data.value.allowed_namespaces = getAllowedNamespaces()
  data.value.target_uids = `target_uids=${data.value.target_uid}&`
  crfs.getXml(data.value).then((resp) => {
    const parser = new DOMParser()
    xmlString.value = resp.data
    xml = parser.parseFromString(resp.data, 'application/xml')
    const xsltProcessor = new XSLTProcessor()
    crfs.getXsl(data.value.selectedStylesheet).then((resp) => {
      const xmlDoc = parser.parseFromString(resp.data, 'text/xml')
      xsltProcessor.importStylesheet(xmlDoc)
      doc.value = new XMLSerializer().serializeToString(
        xsltProcessor.transformToDocument(xml)
      )

      var iframe = document.createElement('iframe')
      iframe.classList.add('frame')
      document.querySelector('iframe').replaceWith(iframe)
      var iframeDoc = iframe.contentDocument
      iframeDoc.write(doc.value)
      iframeDoc.close()

      loading.value = false
    })
  })
  router.push({
    name: 'CrfBuilder',
    params: {
      tab: 'odm-viewer',
      type: data.value.target_type,
      uid: data.value.target_uid,
    },
  })
  url = `${window.location.href}`
}

function getDownloadFileName() {
  let stylesheet = '_with_annotations_crf_'
  if (data.value.selectedStylesheet === 'falcon') {
    stylesheet = '_falcon_crf_'
  }
  const templateName = elements.value.filter(
    (el) => el.uid === data.value.target_uid
  )[0].name
  return `${templateName + stylesheet + DateTime.local().toFormat('yyyy-MM-dd HH:mm')}`
}

function downloadHtml() {
  htmlDownloadLoading.value = true
  exportLoader.downloadFile(
    doc.value,
    'text/html',
    getDownloadFileName() + '.html'
  )
  htmlDownloadLoading.value = false
}

function downloadXml() {
  xmlDownloadLoading.value = true
  data.value.allowed_namespaces = getAllowedNamespaces()
  crfs.getXml(data.value).then((resp) => {
    exportLoader.downloadFile(
      resp.data,
      'text/xml',
      getDownloadFileName() + '.xml'
    )
    xmlDownloadLoading.value = false
  })
}

function downloadPdf() {
  pdfDownloadLoading.value = true
  data.value.allowed_namespaces = getAllowedNamespaces()
  crfs.getPdf(data.value).then((resp) => {
    exportLoader.downloadFile(
      resp.data,
      'application/pdf',
      getDownloadFileName()
    )
    pdfDownloadLoading.value = false
  })
}

function clearXml() {
  doc.value = null
  url = ''
  router.push({ name: 'Crfs', params: { tab: 'odm-viewer' } })
}

function activateShake(condition) {
  if (condition === false) return

  shakeit.value = true
  setTimeout(() => {
    shakeit.value = false
  }, 1000)
}
</script>
<style>
.frame {
  width: 100%;
  min-height: 1000px;
}
</style>
