<template>
  <HorizontalStepperForm
    ref="stepper"
    :title="title"
    :steps="steps"
    :form-observer-getter="getObserver"
    :editable="studyCompound !== undefined && studyCompound !== null"
    :help-items="helpItems"
    :edit-data="form"
    @close="close"
    @save="submit"
  >
    <template #[`step.type_of_treatment`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <NotApplicableField
          ref="naField"
          :clean-function="cleanTypeOfTreatment"
          :disabled="typeOfTreatment_uidNADisabled"
          :checked="studyCompound && !studyCompound.compound"
        >
          <template #mainField="{ notApplicable }">
            <v-autocomplete
              v-model="form.type_of_treatment"
              :data-cy="$t('StudyCompoundForm.type_of_treatment')"
              :label="$t('StudyCompoundForm.type_of_treatment')"
              :items="typeOfTreatments"
              item-title="sponsor_preferred_name"
              item-value="term_uid"
              return-object
              :rules="[
                (value) => formRules.requiredIfNotNA(value, notApplicable),
              ]"
              density="compact"
              clearable
              class="required"
            />
          </template>
        </NotApplicableField>
      </v-form>
    </template>
    <template #[`step.compoundAlias`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <div v-if="showAlerts" class="mx-0">
          <v-alert
            v-if="!form.compound_alias && form.compoundSimple"
            type="warning"
            density="compact"
            class="mb-8 text-white"
            :text="$t('StudyCompoundForm.compound_no_preferred_synonym')"
          />
          <v-alert
            v-if="medicinalProducts.length === 0 && form.compoundSimple"
            type="warning"
            density="compact"
            class="mb-8 text-white"
            :text="$t('StudyCompoundForm.compound_no_medicinal_product')"
          />
        </div>
        <v-row>
          <v-col cols="6">
            <v-autocomplete
              v-model="form.compoundSimple"
              :label="$t('StudyCompoundForm.compound')"
              :items="compounds"
              item-title="name"
              item-value="uid"
              return-object
              :rules="[formRules.required]"
              density="compact"
              clearable
              class="required"
            />
          </v-col>
          <v-col cols="6">
            <v-autocomplete
              v-model="form.compound_alias"
              :label="$t('StudyCompoundForm.compound_alias')"
              :items="compoundAliases"
              item-title="name"
              item-value="uid"
              return-object
              :rules="[formRules.required]"
              density="compact"
              readonly
              disabled
              class="required"
            />
          </v-col>
        </v-row>
        <template v-if="form.compound">
          <v-card class="mt-2 mb-8 pt-0 pb-4 px-2">
            <v-card-text>
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    :model-value="preferedSynonym"
                    :label="$t('StudyCompoundForm.preferred_alias')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    :model-value="otherSynonyms"
                    :label="$t('StudyCompoundForm.other_aliases')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="6">
                  <YesNoField
                    :model-value="form.compound.is_sponsor_compound"
                    :label="$t('StudyCompoundForm.sponsor_compound')"
                    inline
                    disabled
                    hide-details
                  />
                </v-col>
                <v-col cols="6">
                  <v-textarea
                    :model-value="
                      form.compound.definition ? form.compound.definition : '-'
                    "
                    :label="$t('StudyCompoundForm.compound_definition')"
                    density="compact"
                    auto-grow
                    rows="1"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </template>

        <v-row class="mt-8">
          <v-col cols="12">
            <v-autocomplete
              v-model="form.medicinalProduct"
              :label="$t('StudyCompoundForm.medicinal_product')"
              :items="medicinalProducts"
              item-title="name"
              item-value="uid"
              return-object
              :rules="[formRules.required]"
              density="compact"
              clearable
              class="required"
            />
          </v-col>
        </v-row>

        <template v-if="form.medicinalProduct">
          <v-card class="mt-2 mb-8 pt-0 pb-4 px-2">
            <v-card-text>
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    :model-value="form.medicinalProduct.dispenser.name"
                    :label="$t('StudyCompoundForm.dispensed_in')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    :model-value="form.medicinalProduct.delivery_device.name"
                    :label="$t('StudyCompoundForm.device')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          <v-card
            v-for="activeSubstance in activeSubstances"
            :key="activeSubstance.uid"
            class="mt-2 mb-8 py-4 px-2"
          >
            <v-card-subtitle class="mb-2">{{
              $t('StudyCompoundForm.active_substance')
            }}</v-card-subtitle>
            <v-card-text>
              <v-row>
                <v-col cols="3">
                  <v-text-field
                    :model-value="
                      activeSubstance.inn ? activeSubstance.inn : '-'
                    "
                    :label="$t('ActiveSubstance.inn')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
                <v-col cols="3">
                  <v-text-field
                    :model-value="
                      activeSubstance.analyte_number
                        ? activeSubstance.analyte_number
                        : '-'
                    "
                    :label="$t('ActiveSubstance.analyte_number')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
                <v-col cols="3">
                  <v-text-field
                    :model-value="
                      activeSubstance.long_number
                        ? activeSubstance.long_number
                        : '-'
                    "
                    :label="$t('ActiveSubstance.long_number')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
                <v-col cols="3">
                  <v-text-field
                    :model-value="
                      activeSubstance.short_number
                        ? activeSubstance.short_number
                        : '-'
                    "
                    :label="$t('ActiveSubstance.short_number')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="6">
                  <v-text-field
                    :model-value="
                      activeSubstance.unii?.substance_unii
                        ? activeSubstance.unii.substance_unii
                        : '-'
                    "
                    :label="$t('CompoundAliasForm.substance')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    :model-value="getPclassLabel(activeSubstance)"
                    :label="$t('CompoundAliasForm.pharmacological_class')"
                    density="compact"
                    readonly
                    variant="filled"
                    hide-details
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </template>
      </v-form>
    </template>
    <template #[`step.compound`]="{ step }">
      <v-form v-if="form.compound" :ref="`observer_${step}`">
        <v-row>
          <v-col>
            <v-textarea
              v-model="form.other_info"
              :data-cy="$t('StudyCompoundForm.other')"
              :label="$t('StudyCompoundForm.other')"
              auto-grow
              rows="1"
              density="compact"
              clearable
            />
          </v-col>
        </v-row>
      </v-form>
    </template>
  </HorizontalStepperForm>
</template>

<script>
import compoundAliases from '@/api/concepts/compoundAliases'
import compounds from '@/api/concepts/compounds'
import compoundsSimple from '@/api/concepts/compoundsSimple'
import constants from '@/constants/studyCompounds'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm.vue'
import NotApplicableField from '@/components/tools/NotApplicableField.vue'
import statuses from '@/constants/statuses'
import studyConstants from '@/constants/study'
import terms from '@/api/controlledTerminology/terms'
import YesNoField from '@/components/tools/YesNoField.vue'
import { useStudiesCompoundsStore } from '@/stores/studies-compounds'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import medicinalProducts from '@/api/concepts/medicinalProducts'
import pharmaceuticalProducts from '@/api/concepts/pharmaceuticalProducts'

export default {
  components: {
    HorizontalStepperForm,
    NotApplicableField,
    YesNoField,
  },
  inject: ['notificationHub', 'formRules'],
  props: {
    studyCompound: {
      type: Object,
      default: undefined,
    },
  },
  emits: ['added', 'close'],
  setup() {
    const studiesCompoundsStore = useStudiesCompoundsStore()
    const studiesGeneralStore = useStudiesGeneralStore()

    return {
      studiesCompoundsStore,
      studiesGeneralStore,
    }
  },
  data() {
    return {
      showAlerts: false,
      compoundAliases: [],
      medicinalProducts: [],
      activeSubstances: [],
      compounds: [],
      helpItems: [
        'StudyCompoundForm.type_of_treatment',
        'StudyCompoundForm.compound',
        'StudyCompoundForm.compound_alias',
        'StudyCompoundForm.pharma_class',
        'StudyCompoundForm.substance',
        'StudyCompoundForm.unii',
        'StudyCompoundForm.route_of_admin',
        'StudyCompoundForm.dosage_form',
        'StudyCompoundForm.dispensed_in',
        'StudyCompoundForm.device',
        'StudyCompoundForm.formulation',
        'StudyCompoundForm.other',
      ],
      form: this.getInitialForm(),
      typeOfTreatments: [],
      steps: this.getInitialSteps(),
    }
  },
  computed: {
    preferedSynonym() {
      const preferedSynonym = this.compoundAliases.find(
        (item) => item.is_preferred_synonym
      )
      return preferedSynonym ? preferedSynonym.name : '-'
    },
    otherSynonyms() {
      const otherSynonyms = this.compoundAliases.filter(
        (item) => !item.is_preferred_synonym
      )

      return otherSynonyms.length
        ? otherSynonyms.map((item) => item.name).join(', ')
        : '-'
    },
    title() {
      if (this.studyCompound) {
        return this.$t('StudyCompoundForm.edit_title')
      }
      return this.$t('StudyCompoundForm.add_title')
    },
    typeOfTreatment_uidNADisabled() {
      if (
        (this.$refs.naField && this.$refs.naField.notApplicable) ||
        (this.studyCompound && !this.studyCompound.compound)
      ) {
        return false
      }
      if (!this.form.type_of_treatment) {
        return true
      }
      const types = [
        constants.TYPE_OF_TREATMENT_INVESTIGATIONAL_PRODUCT,
        constants.TYPE_OF_TREATMENT_CURRENT_TREATMENT,
        constants.TYPE_OF_TREATMENT_COMPARATIVE_TREATMENT,
      ]
      if (
        !types.find(
          (item) => item === this.form.type_of_treatment.sponsor_preferred_name
        )
      ) {
        return true
      }
      const studyCompounds =
        this.studiesCompoundsStore.getStudyCompoundsByTypeOfTreatment(
          this.form.type_of_treatment.term_uid
        )
      if (studyCompounds.length) {
        return true
      }
      const NAstudyCompounds =
        this.studiesCompoundsStore.getNAStudyCompoundsByTypeOfTreatment(
          this.form.type_of_treatment.term_uid
        )
      return !!NAstudyCompounds.length
    },
  },
  watch: {
    studyCompound: {
      handler: function (val) {
        if (val) {
          this.form.type_of_treatment = {
            term_uid: val.type_of_treatment.term_uid,
            sponsor_preferred_name: val.type_of_treatment.term_name,
          }
          this.form.other_info = val.other_info
          if (val.compound) {
            this.form.compound = val.compound
            this.form.compoundSimple = {
              uid: val.compound.uid,
              name: val.compound.name,
            }
            const filters = {
              compound_uid: { v: [val.compound.uid] },
              status: { v: [statuses.FINAL] },
            }
            compoundAliases.getFiltered({ filters }).then((resp) => {
              this.compoundAliases = resp.data.items
            })
            medicinalProducts.getFiltered({ filters }).then((resp) => {
              this.medicinalProducts = resp.data.items.map((item) => {
                item.name = item.name + ' (' + item.dose_frequency?.name + ')'
                return item
              })
            })
          } else {
            this.steps = [
              {
                name: 'type_of_treatment',
                title: this.$t('StudyCompoundForm.step1_title'),
              },
            ]
          }
          if (val.compound_alias) {
            this.form.compound_alias = val.compound_alias
          }
          if (val.medicinal_product) {
            this.form.medicinalProduct = val.medicinal_product
          }
          if (val.dosage_form) {
            this.form.dosage_form_uid = val.dosage_form.term_uid
          }
          if (val.route_of_administration) {
            this.form.route_of_administration_uid =
              val.route_of_administration.term_uid
          }
          if (val.dispensed_in) {
            this.form.dispenser_uid = val.dispensed_in.term_uid
          }
          if (val.device) {
            this.form.delivery_device_uid = val.device.term_uid
          }
          if (val.strength_value) {
            this.form.strength_value_uid = val.strength_value.uid
          }
        }
      },
      immediate: true,
    },
    compoundAliases(newValue) {
      if (newValue) {
        // Auto-select preferred alias only for Create form.
        // Edit form should preserve the current value of compound alias.
        if (!this.studyCompound) {
          const preferedSynonym = this.compoundAliases.find(
            (item) => item.is_preferred_synonym
          )
          this.form.compound_alias = preferedSynonym
        }
      }
    },
    'form.compoundSimple'(newValue) {
      this.showAlerts = false
      if (newValue) {
        if (
          !this.studyCompound ||
          this.studyCompound.compound.uid !== newValue.uid
        ) {
          this.form.compound_alias = null
        }
        this.form.medicinalProduct = null
        const filters = {
          compound_uid: { v: [newValue.uid] },
          status: { v: [statuses.FINAL] },
        }
        compoundAliases.getFiltered({ filters }).then((resp) => {
          this.compoundAliases = resp.data.items
          this.showAlerts = true
        })
        medicinalProducts.getFiltered({ filters }).then((resp) => {
          this.medicinalProducts = resp.data.items.map((item) => {
            item.name = `${item.name} (${item.dose_frequency ? item.dose_frequency.name : ''})`
            return item
          })
          this.showAlerts = true
        })
        if (newValue.uid) {
          compounds.getObject(newValue.uid).then((resp) => {
            this.form.compound = resp.data
          })
        }
      }
    },
    'form.medicinalProduct': {
      handler: function (newValue) {
        if (newValue) {
          this.activeSubstances = []
          medicinalProducts.getObject(newValue.uid).then((resp) => {
            resp.data.pharmaceutical_products.forEach((item) =>
              pharmaceuticalProducts.getObject(item.uid).then((resp) => {
                const ingredients = resp.data.formulations
                  .map((formulation) => formulation.ingredients)
                  .flat()
                  .map((ingredient) => ingredient.active_substance)
                  .flat()
                this.activeSubstances =
                  this.activeSubstances.concat(ingredients)
              })
            )
          })
        }
      },
      immediate: true,
    },
  },
  mounted() {
    const filters = {
      status: { v: [statuses.FINAL] },
    }
    compoundsSimple.getFiltered({ filters }).then((resp) => {
      this.compounds = resp.data.items
    })
    terms.getTermsByCodelist('typeOfTreatment').then((resp) => {
      this.typeOfTreatments = resp.data.items
    })
  },
  methods: {
    close() {
      this.$emit('close')
      this.notificationHub.clearErrors()
      this.form = this.getInitialForm()
      this.$refs.stepper.reset()
      this.$refs.naField.reset()
    },
    getInitialForm() {
      return {
        compound: null,
        compoundSimple: null,
        compound_alias: null,
        medicinalProduct: null,
        type_of_treatment: null,
        dosage_form_uid: null,
        strength_value_uid: null,
        route_of_administration_uid: null,
        dispenser_uid: null,
        delivery_device_uid: null,
        other_info: null,
      }
    },
    getInitialSteps() {
      return [
        {
          name: 'type_of_treatment',
          title: this.$t('StudyCompoundForm.step1_title'),
        },
        {
          name: 'compoundAlias',
          title: this.$t('StudyCompoundForm.step2_title'),
        },
        { name: 'compound', title: this.$t('StudyCompoundForm.step3_title') },
      ]
    },
    getObserver(step) {
      return this.$refs[`observer_${step}`]
    },
    cleanTypeOfTreatment(value) {
      if (value) {
        this.steps = [
          {
            name: 'type_of_treatment',
            title: this.$t('StudyCompoundForm.step1_title'),
          },
        ]
      } else {
        this.steps = this.getInitialSteps()
      }
    },
    getPclassLabel(activeSubstance) {
      const labels = []
      if (activeSubstance.unii && activeSubstance.unii.pclass_name) {
        labels.push(activeSubstance.unii.pclass_name)
      }

      if (activeSubstance.unii && activeSubstance.unii.pclass_id) {
        labels.push(`(${activeSubstance.unii.pclass_id})`)
      }
      return labels.length ? labels.join(' ') : '-'
    },
    async submit() {
      this.notificationHub.clearErrors()

      const data = JSON.parse(JSON.stringify(this.form))
      data.type_of_treatment_uid = data.type_of_treatment.term_uid
      delete data.type_of_treatment
      delete data.compound

      if (data.medicinalProduct) {
        data.medicinal_product_uid = data.medicinalProduct.uid
      }

      if (data.compound_alias) {
        data.compound_alias_uid = data.compound_alias.uid || null
      } else {
        data.reason_for_missing_null_value_uid =
          studyConstants.TERM_NOT_APPLICABLE
      }

      let action = null
      let notification = null
      let args = null
      let event
      if (!this.studyCompound) {
        action = 'addStudyCompound'
        notification = 'add_success'
        event = 'added'
        args = { studyUid: this.studiesGeneralStore.selectedStudy.uid, data }
      } else {
        action = 'updateStudyCompound'
        notification = 'update_success'
        args = {
          studyUid: this.studiesGeneralStore.selectedStudy.uid,
          studyCompoundUid: this.studyCompound.study_compound_uid,
          data,
        }
      }
      try {
        await this.studiesCompoundsStore[action](args)
        this.notificationHub.add({
          msg: this.$t(`StudyCompoundForm.${notification}`),
        })
        if (event) {
          this.$emit(event)
        }
        this.close()
      } finally {
        this.$refs.stepper.loading = false
      }
    },
  },
}
</script>

<style scoped>
.text-white {
  color: white !important;
}
</style>
