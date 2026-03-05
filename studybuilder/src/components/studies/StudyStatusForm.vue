<template>
  <SimpleFormDialog
    ref="formRef"
    :title="title"
    :help-items="helpItems"
    :open="open"
    max-width="1200px"
    :action-label="title"
    :scrollable="false"
    @close="close"
    @submit="submit"
  >
    <template #body>
      <table
        class="mt-4"
        :aria-label="$t('StudyStructureOverview.table_caption')"
      >
        <thead>
          <tr>
            <th
              v-for="header in headers"
              :key="header.key"
              scope="col"
              style="color: white"
            >
              {{ header.title }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td v-for="(header, index) in headers" :key="header.key">
              <StatusChip
                v-if="index === 0"
                :status="
                  getValueByColumn(
                    studiesGeneralStore.selectedStudy,
                    header.key
                  )
                "
                :outlined="false"
              />
              <div v-else>
                {{
                  getValueByColumn(
                    studiesGeneralStore.selectedStudy,
                    header.key
                  )
                }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <v-form ref="observer">
        <v-row>
          <v-col cols="12">
            <v-textarea
              v-model="form.change_description"
              :label="$t('_global.description')"
              variant="outlined"
              data-cy="release-description"
              :rules="[formRules.required]"
              auto-grow
              persistent-hint
              :placeholder="$t('StudyStatusForm.description_placeholder')"
              rounded
              width="75%"
              class="mt-10"
            />
          </v-col>
        </v-row>
      </v-form>
    </template>
  </SimpleFormDialog>
</template>

<script setup>
import api from '@/api/study'
import { inject, computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import SimpleFormDialog from '@/components/tools/SimpleFormDialog.vue'
import StatusChip from '@/components/tools/StatusChip.vue'
import { useStudiesGeneralStore } from '@/stores/studies-general'

const props = defineProps({
  action: {
    type: String,
    default: '',
  },
  helpItems: {
    type: Array,
    default: () => [],
  },
  open: Boolean,
})

const { t } = useI18n()
const studiesGeneralStore = useStudiesGeneralStore()
const notificationHub = inject('notificationHub')
const formRules = inject('formRules')

const emit = defineEmits(['close', 'statusChanged'])

const observer = ref()
const formRef = ref()

const form = ref({})
const headers = [
  {
    title: t('Study.status'),
    key: 'current_metadata.version_metadata.study_status',
  },
  {
    title: t('Study.clinical_programme'),
    key: 'current_metadata.identification_metadata.clinical_programme_name',
  },
  {
    title: t('Study.project_number'),
    key: 'current_metadata.identification_metadata.project_number',
  },
  {
    title: t('Study.project_name'),
    key: 'current_metadata.identification_metadata.project_name',
  },
  {
    title: t('Study.study_number'),
    key: 'current_metadata.identification_metadata.study_number',
  },
  {
    title: t('Study.acronym'),
    key: 'current_metadata.identification_metadata.study_acronym',
  },
]

const title = computed(() => {
  return props.action === 'release'
    ? t('StudyStatusForm.release_title')
    : t('StudyStatusForm.lock_title')
})

function close() {
  notificationHub.clearErrors()
  form.value = {}
  observer.value.reset()
  emit('close')
}

function getValueByColumn(item, columnName) {
  const keys = columnName.split('.')
  return keys.reduce((acc, key) => (acc ? acc[key] : undefined), item)
}

async function submit() {
  notificationHub.clearErrors()

  try {
    if (props.action === 'release') {
      await api.releaseStudy(studiesGeneralStore.selectedStudy.uid, form.value)
      notificationHub.add({
        msg: t('StudyStatusForm.release_success'),
        type: 'success',
      })
    } else {
      const resp = await api.lockStudy(
        studiesGeneralStore.selectedStudy.uid,
        form.value
      )
      await studiesGeneralStore.selectStudy(resp.data)
      notificationHub.add({
        msg: t('StudyStatusForm.lock_success'),
        type: 'success',
      })
    }
    emit('statusChanged')
    close()
  } finally {
    formRef.value.working = false
  }
}
</script>

<style scoped lang="scss">
table {
  text-align: left;
  border-spacing: 0px;
  border-collapse: separate;
  overflow: hidden;
}
td,
th {
  border: 1px solid gray;
  padding-inline: 20px;
  padding-block: 6px;
  color: rgb(var(--v-theme-nnTrueBlue));
}
table {
  border: solid gray 1px;
  border-radius: 20px;
}

thead > tr:first-of-type {
  background-color: rgb(var(--v-theme-nnTrueBlue));
}
</style>
