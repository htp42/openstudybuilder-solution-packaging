<template>
  <v-card class="bg-nnBaseLight" rounded="lg" border="sm" flat>
    <v-card-text>
      <div class="d-flex mb-6">
        <v-select
          :model-value="props.testNameAic.uid"
          :label="$t('ActivityInstanceForm.activity_item_class')"
          :items="[props.testNameAic]"
          bg-color="white"
          item-title="display_name"
          item-value="uid"
          disabled
          variant="outlined"
          density="compact"
          class="w-50"
        />
        <SelectActivityItemTermField
          :key="props.testNameAic.uid"
          v-model="model"
          v-model:codelist="nameCodelist"
          v-model:search="search"
          :label="$t('ActivityInstanceForm.name_submission_value')"
          :activity-item-class="props.testNameAic"
          :data-domain="props.dataDomain"
          item-title="submission_value"
          class="ml-4 w-50"
          :disabled="props.disabled"
          :rules="[formRules.required]"
          @updatecodelist="changeCodelist"
        />
      </div>
      <div class="d-flex">
        <v-select
          :model-value="props.testCodeAic.uid"
          :label="$t('ActivityInstanceForm.activity_item_class')"
          :items="[props.testCodeAic]"
          bg-color="white"
          item-title="display_name"
          item-value="uid"
          disabled
          variant="outlined"
          density="compact"
          class="w-50"
        />
        <SelectActivityItemTermField
          :key="props.testCodeAic.uid"
          v-model="model"
          v-model:codelist="codeCodelist"
          v-model:search="search"
          :label="$t('ActivityInstanceForm.code_submission_value')"
          :activity-item-class="props.testCodeAic"
          :data-domain="props.dataDomain"
          item-title="submission_value"
          class="ml-4 w-50"
          :rules="[formRules.required]"
          :disabled="props.disabled"
          @updatecodelist="changeCodelist"
        />
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { inject, ref } from 'vue'
import SelectActivityItemTermField from './SelectActivityItemTermField.vue'

const props = defineProps({
  testCodeAic: {
    type: Object,
    default: null,
  },
  testNameAic: {
    type: Object,
    default: null,
  },
  dataDomain: {
    type: String,
    default: null,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const formRules = inject('formRules')

const model = defineModel({ type: String })
const codeCodelist = defineModel('codeCodelist', { type: String })
const nameCodelist = defineModel('nameCodelist', { type: String })

const search = ref('')

const changeCodelist = (codelist) => {
  if (!codelist) return
  if (
    codelist.paired_codes_codelist_uid &&
    codelist.paired_codes_codelist_uid !== codeCodelist.value
  ) {
    codeCodelist.value = codelist.paired_codes_codelist_uid
  } else if (
    codelist.paired_names_codelist_uid &&
    codelist.paired_names_codelist_uid !== nameCodelist.value
  ) {
    nameCodelist.value = codelist.paired_names_codelist_uid
  }
}
</script>
