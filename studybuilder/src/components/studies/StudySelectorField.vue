<template>
  <v-autocomplete
    v-model="selectedStudy"
    :label="$t('StudyQuickSelectForm.study_id_or_acronym')"
    :items="sortedStudies"
    :item-title="getStudyDisplayName"
    return-object
    :rules="[formRules.required]"
    variant="outlined"
    rounded="lg"
    density="compact"
    autocomplete="off"
    clearable
    :loading="loading"
    @update:model-value="emit('update:modelValue', $event)"
  />
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import studyApi from '@/api/study'

const props = defineProps({
  modelValue: {
    type: Object,
    default: null,
  },
  data: {
    type: Array,
    default: undefined,
  },
})
const emit = defineEmits(['update:modelValue'])

const formRules = inject('formRules')

const studies = ref([])
const selectedStudy = ref(props.modelValue)
const loading = ref(false)

watch(
  () => props.modelValue,
  (newValue) => {
    selectedStudy.value = newValue
  }
)

const sortedStudies = computed(() => {
  return studies.value.slice().sort((a, b) => {
    const nameA = getStudyDisplayName(a) || ''
    const nameB = getStudyDisplayName(b) || ''
    return nameA.localeCompare(nameB)
  })
})

function getStudyDisplayName(study) {
  const id =
    study?.id || study?.current_metadata?.identification_metadata?.study_id
  const acronym =
    study?.acronym ||
    study?.current_metadata?.identification_metadata?.study_acronym
  if (id && acronym) {
    return `${id} (${acronym})`
  } else if (id) {
    return id
  } else if (acronym) {
    return acronym
  }
}

onMounted(() => {
  console.log('StudySelectorField mounted, loading studies...', props.data)
  if (props.data !== undefined) {
    studies.value = props.data
    return
  }

  loading.value = true
  studyApi
    .getIds()
    .then((resp) => {
      studies.value = resp.data
    })
    .finally(() => {
      loading.value = false
    })
})
</script>
