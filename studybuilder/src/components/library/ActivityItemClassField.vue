<template>
  <v-card class="bg-nnBaseLight" rounded="lg" border="sm" flat v-bind="$attrs">
    <v-card-text>
      <div class="d-flex">
        <slot name="prepend" />
        <v-select
          v-model="form.activity_item_class"
          :label="$t('ActivityInstanceForm.activity_item_class')"
          :items="compatibleActivityItemClasses"
          bg-color="white"
          item-title="display_name"
          item-value="uid"
          return-object
          :disabled="selectValueOnly || props.disabled"
          class="w-50"
          @update:model-value="resetAndUpdate"
        />
        <SelectActivityItemTermField
          v-if="
            !form.activity_item_class ||
            form.activity_item_class.name !== 'standard_unit'
          "
          ref="termField"
          v-model="form.ct_term_uid"
          v-model:codelist="codelist"
          v-model:search="search"
          :activity-item-class="form.activity_item_class"
          :data-domain="props.dataDomain"
          item-title="sponsor_preferred_name"
          class="ml-4 w-50"
          :multiple="props.multiple"
          :disabled="props.disabled"
          :rules="[formRules.required]"
          @update:model-value="update"
          @update:codelist="update"
        />
        <v-select
          v-else
          v-model="form.unit_definition_uid"
          :label="$t('ActivityInstanceForm.value')"
          :items="allowedUnits"
          item-title="name"
          item-value="uid"
          bg-color="white"
          class="ml-4 w-50"
          :loading="loading"
          :disabled="props.disabled"
          :rules="[formRules.required]"
          @update:model-value="update"
        />
        <slot name="append" />
        <v-btn
          v-if="props.withAdvancedSearch"
          variant="flat"
          class="ml-4"
          icon="mdi-text-box-search-outline"
          size="small"
          @click="openTermsSelectionForm()"
        >
        </v-btn>
      </div>
    </v-card-text>
  </v-card>
  <TermsSelectionForm
    v-model:codelist="codelist"
    v-model:term-selection="form.ct_term_uid"
    :open="showTermsSelectionForm"
    max-width="1200px"
    @selected="update"
    @close="closeTermsSelectionForm"
  />
</template>

<script setup>
import { computed, inject, ref, watch } from 'vue'
import SelectActivityItemTermField from './SelectActivityItemTermField.vue'
import TermsSelectionForm from '@/components/library/TermsSelectionForm.vue'
import unitsApi from '@/api/units'

const props = defineProps({
  modelValue: {
    type: Object,
    default: null,
  },
  multiple: {
    type: Boolean,
    default: false,
  },
  compatibleActivityItemClasses: {
    type: Array,
    default: null,
  },
  allActivityItemClasses: {
    type: Array,
    default: null,
  },
  selectValueOnly: {
    type: Boolean,
    default: false,
  },
  unitDimension: {
    type: String,
    default: null,
  },
  adamSpecific: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  dataDomain: {
    type: String,
    default: null,
  },
  withAdvancedSearch: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])
const formRules = inject('formRules')

const form = ref({})
const codelist = ref(null)
const allowedUnits = ref([])
const loading = ref(false)
const search = ref('')
const showTermsSelectionForm = ref(false)
const termField = ref(null)

const selectedTerm = computed(() => {
  if (!termField.value) {
    return null
  }
  return termField.value.allowedValues.find(
    (item) => item.term_uid === form.value.ct_term_uid
  )
})

function openTermsSelectionForm() {
  showTermsSelectionForm.value = true
}

function closeTermsSelectionForm() {
  showTermsSelectionForm.value = false
}

function fetchUnits() {
  if (!props.unitDimension) {
    allowedUnits.value = []
    return
  }
  loading.value = true
  unitsApi
    .get({
      params: {
        dimension: props.unitDimension,
        page_size: 0,
      },
    })
    .then((resp) => {
      allowedUnits.value = resp.data.items
      loading.value = false
    })
}

function update() {
  const value = {
    is_adam_param_specific: props.adamSpecific,
    ct_terms: [],
    unit_definition_uids: [],
    odm_item_uids: [],
  }
  if (form.value.activity_item_class) {
    value.activity_item_class_uid = form.value.activity_item_class.uid
    if (form.value.activity_item_class.name !== 'standard_unit') {
      if (!props.multiple) {
        if (selectedTerm.value) {
          value.ct_terms = [
            { term_uid: form.value.ct_term_uid, codelist_uid: codelist.value },
          ]
          value.ct_term_name = selectedTerm.value.sponsor_preferred_name // Only useful to propagate unit dimension name
        }
      } else {
        // We assume there won't be any unit based activity item class in multiple mode
        value.ct_terms = form.value.ct_term_uid.map((term_uid) => {
          return { term_uid, codelist_uid: codelist.value }
        })
      }
    } else if (form.value.unit_definition_uid) {
      value.unit_definition_uids = [form.value.unit_definition_uid]
    }
  }
  emit('update:modelValue', value)
}

function resetAndUpdate() {
  codelist.value = null
  form.value.ct_term_uid = null
  termField.value.allowedValues = []
  update()
}

watch(
  () => props.modelValue,
  (value) => {
    if (value) {
      // FIXME: why this watcher is being called twice whereas there is nochange?
      form.value = {}
      if (value.activity_item_class_uid) {
        form.value.activity_item_class = props.allActivityItemClasses.find(
          (item) => item.uid === value.activity_item_class_uid
        )
      }
      if (value.unit_definition_uids && value.unit_definition_uids.length) {
        form.value.unit_definition_uid = value.unit_definition_uids[0]
      } else if (value.ct_terms && value.ct_terms.length) {
        if (!props.multiple) {
          form.value.ct_term_uid =
            value.ct_terms[0].term_uid || value.ct_terms[0].uid
          codelist.value = value.ct_terms[0].codelist_uid
        } else {
          codelist.value = value.ct_terms[0].codelist_uid
          form.value.ct_term_uid = value.ct_terms.map(
            (ct_term) => ct_term.term_uid || ct_term.uid
          )
        }
      }
    } else {
      form.value = {}
      if (props.multiple) {
        form.value.ct_term_uid = []
      }
    }
  },
  { immediate: true, deep: true }
)

watch(
  () => props.unitDimension,
  () => {
    if (form.value?.activity_item_class?.name === 'standard_unit') {
      if (allowedUnits.value.length) {
        form.value.unit_definition_uid = null
      }
      fetchUnits()
    }
  },
  { immediate: true }
)

watch(
  () => props.dataDomain,
  () => {
    form.value.ct_term_uid = null
  }
)
</script>
