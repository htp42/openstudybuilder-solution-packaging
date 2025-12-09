<template>
  <HorizontalStepperForm
    ref="stepper"
    :title="title"
    :help-items="helpItems"
    :steps="steps"
    :form-observer-getter="getObserver"
    :form-url="formUrl"
    :editable="isEdit()"
    :save-from-any-step="isEdit()"
    @close="close"
    @save="submit"
  >
    <template #[`step.form`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <v-card elevation="4" class="mx-auto pa-4">
          <div class="text-h5 mb-4">
            {{ $t('CRFForms.definition') }}
          </div>
          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model="form.name"
                :label="$t('CRFItems.name') + '*'"
                data-cy="item-name"
                :rules="[formRules.required]"
                density="compact"
                clearable
                :disabled="readOnly"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.oid"
                :label="$t('CRFItems.oid')"
                data-cy="item-oid"
                density="compact"
                clearable
                :disabled="readOnly"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="4">
              <v-select
                v-model="form.datatype"
                :label="$t('CRFItems.data_type') + '*'"
                data-cy="item-data-type"
                :items="dataTypes"
                item-title="submission_value"
                item-value="submission_value"
                :rules="[formRules.required]"
                density="compact"
                clearable
                class="mt-3"
                :disabled="readOnly"
                @update:model-value="checkIfNumeric()"
              />
            </v-col>
            <v-col v-if="lengthFieldCheck" cols="4">
              <v-text-field
                v-model="form.length"
                :label="$t('CRFItems.length')"
                data-cy="item-length"
                density="compact"
                :rules="[lengthRequired]"
                clearable
                class="mt-3"
                type="number"
                :disabled="readOnly"
              />
            </v-col>
            <v-col v-if="digitsFieldCheck" cols="4">
              <v-text-field
                v-model="form.significant_digits"
                :label="$t('CRFItems.significant_digits')"
                data-cy="item-significant-digits"
                density="compact"
                :rules="[significantDigitsRequired]"
                clearable
                class="mt-3"
                type="number"
                :disabled="readOnly"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <div class="subtitle-2">
                {{ $t('_global.description') }}
              </div>
              <div v-show="readOnly">
                <QuillEditor
                  v-show="readOnly"
                  v-model:content="engDescription.description"
                  content-type="html"
                  :toolbar="customToolbar"
                  :disabled="readOnly"
                />
              </div>
              <div v-show="!readOnly">
                <QuillEditor
                  v-show="!readOnly"
                  v-model:content="engDescription.description"
                  content-type="html"
                  :toolbar="customToolbar"
                  :placeholder="$t('_global.description')"
                  :disabled="readOnly"
                />
              </div>
            </v-col>
            <v-col cols="6">
              <div class="subtitle-2">
                {{ $t('CRFDescriptions.sponsor_instruction') }}
              </div>
              <div v-show="readOnly">
                <QuillEditor
                  v-show="readOnly"
                  v-model:content="engDescription.sponsor_instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  :disabled="readOnly"
                />
              </div>
              <div v-show="!readOnly">
                <QuillEditor
                  v-show="!readOnly"
                  v-model:content="engDescription.sponsor_instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  :placeholder="$t('CRFDescriptions.sponsor_instruction')"
                  :disabled="readOnly"
                />
              </div>
            </v-col>
          </v-row>
        </v-card>
        <v-card elevation="4" class="mx-auto mt-3 pa-4">
          <div class="text-h5 mb-4">
            {{ $t('CRFForms.display') }}
          </div>
          <v-row>
            <v-col cols="3">
              <v-text-field
                v-model="engDescription.name"
                :label="$t('CRFDescriptions.name')"
                data-cy="form-oid-name"
                density="compact"
                clearable
                :disabled="readOnly"
              />
            </v-col>
            <v-col cols="9">
              <div class="subtitle-2">
                {{ $t('CRFDescriptions.instruction') }}
              </div>
              <div v-show="readOnly">
                <QuillEditor
                  v-show="readOnly"
                  v-model:content="engDescription.instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  :disabled="readOnly"
                />
              </div>
              <div v-show="!readOnly">
                <QuillEditor
                  v-show="!readOnly"
                  v-model:content="engDescription.instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  :placeholder="$t('CRFDescriptions.instruction')"
                  :disabled="readOnly"
                />
              </div>
            </v-col>
          </v-row>
        </v-card>
        <v-card elevation="4" class="mx-auto mt-3 pa-4">
          <div class="text-h5 mb-4">
            {{ $t('CRFForms.annotations') }}
          </div>
          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model="form.sas_field_name"
                :label="$t('CRFItems.sas_name')"
                data-cy="item-sas-name"
                density="compact"
                clearable
                :disabled="readOnly"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.sds_var_name"
                :label="$t('CRFItems.sds_name')"
                data-cy="item-sds-name"
                density="compact"
                clearable
                :disabled="readOnly"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col v-if="originFieldCheck" cols="4">
              <v-select
                v-model="form.origin"
                :label="$t('CRFItems.origin')"
                data-cy="item-origin"
                :items="origins"
                item-title="nci_preferred_name"
                item-value="nci_preferred_name"
                density="compact"
                clearable
                :disabled="readOnly"
              />
            </v-col>
            <v-col cols="8">
              <v-text-field
                v-model="form.comment"
                :label="$t('CRFItems.comment')"
                data-cy="item-comment"
                density="compact"
                clearable
                :disabled="readOnly"
              />
            </v-col>
          </v-row>
        </v-card>
      </v-form>
    </template>
    <template #[`step.extensions`]>
      <CrfExtensionsManagementTable
        type="ItemDef"
        :read-only="readOnly"
        :edit-extensions="selectedExtensions"
        @set-extensions="setExtensions"
      />
    </template>
    <template #[`step.alias`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <CrfAliasSelection v-model="form.aliases" :disabled="readOnly" />
      </v-form>
    </template>
    <template #[`step.description`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <CrfDescriptionSelection v-model="desc" :disabled="readOnly" />
      </v-form>
    </template>
    <template #[`step.codelist`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <v-data-table
          height="135px"
          :headers="selectedCodelistHeaders"
          :items="selectedCodelists"
        >
          <template #[`item.allowsMultiChoice`]>
            <v-checkbox v-model="form.allows_multi_choice" class="mb-n4" />
          </template>
          <template #[`item.delete`]="{ item }">
            <v-btn
              icon="mdi-delete-outline"
              class="mt-1"
              size="small"
              variant="outlined"
              color="nnBaseBlue"
              :disabled="readOnly"
              @click="removeCodelist(item)"
            />
          </template>
        </v-data-table>
      </v-form>
    </template>
    <template #[`step.codelist.after`]>
      <v-col class="pt-0 mt-0">
        <NNTable
          v-model:options="options"
          :headers="codelistHeaders"
          item-value="uid"
          :items="codelists"
          :server-items-length="total"
          hide-export-button
          hide-default-switches
          column-data-resource="ct/codelists"
          @filter="fetchCodelists"
        >
          <template #[`item.actions`]="{ item }">
            <v-btn
              icon="mdi-plus"
              class="mt-1"
              size="small"
              variant="outlined"
              color="nnBaseBlue"
              :disabled="readOnly"
              @click="addCodelist(item)"
            />
          </template>
        </NNTable>
      </v-col>
    </template>
    <template #[`step.terms`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <v-data-table :headers="selectedTermsHeaders" :items="selectedTerms">
          <template #[`item.mandatory`]="{ item }">
            <v-checkbox v-model="item.mandatory" :disabled="readOnly" />
          </template>
          <template #[`item.display_text`]="{ item }">
            <v-text-field
              v-model="item.display_text"
              :disabled="readOnly"
              density="compact"
            />
          </template>
          <template #[`item.delete`]="{ item }">
            <v-btn
              icon="mdi-delete-outline"
              class="mt-1"
              variant="text"
              :disabled="readOnly"
              @click="removeTerm(item)"
            />
          </template>
        </v-data-table>
      </v-form>
    </template>
    <template #[`step.terms.after`]>
      <v-col class="pt-0 mt-0">
        <NNTable
          :headers="termsHeaders"
          item-value="uid"
          :items="terms"
          :items-length="totalTerms"
          hide-export-button
          only-text-search
          hide-default-switches
          @filter="getCodeListTerms"
        >
          <template #[`item.add`]="{ item }">
            <v-btn
              icon="mdi-plus"
              class="mt-1"
              variant="text"
              :disabled="
                readOnly ||
                selectedTerms.find((e) => e.term_uid === item.term_uid)
              "
              @click="addTerm(item)"
            />
          </template>
        </NNTable>
      </v-col>
    </template>
    <template #[`step.unit`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <NNTable
          :headers="unitHeaders"
          item-value="uid"
          disable-filtering
          :items="chosenUnits"
          hide-export-button
          hide-default-switches
        >
          <template #actions="">
            <v-btn
              class="ml-2"
              size="small"
              variant="outlined"
              color="nnBaseBlue"
              :label="$t('CRFItemGroups.new_translation')"
              :disabled="readOnly"
              icon="mdi-plus"
              @click.stop="addUnit"
            />
          </template>
          <template #[`item.name`]="{ index }">
            <v-autocomplete
              v-model="chosenUnits[index].name"
              :items="units"
              :label="$t('CRFItems.unit_name')"
              data-cy="item-unit-name"
              density="compact"
              class="mt-3"
              item-title="name"
              item-value="name"
              return-object
              :disabled="readOnly"
              @update:model-value="setUnit(index)"
            />
          </template>
          <template #[`item.mandatory`]="{ item }">
            <v-checkbox v-model="item.mandatory" :disabled="readOnly" />
          </template>
          <template #[`item.delete`]="{ index }">
            <v-btn
              icon="mdi-delete-outline"
              class="mt-n5"
              variant="text"
              :disabled="readOnly"
              @click="removeUnit(index)"
            />
          </template>
        </NNTable>
      </v-form>
    </template>
    <template #[`step.change_description`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <v-row>
          <v-col>
            <v-text-field
              v-model="form.change_description"
              :label="$t('CRFItems.change_desc')"
              data-cy="item-change-description"
              :rules="[formRules.required]"
              clearable
              :disabled="readOnly"
            />
          </v-col>
        </v-row>
      </v-form>
    </template>
    <template #actions>
      <ActionsMenu v-if="selectedItem" :actions="actions" :item="form" />
    </template>
  </HorizontalStepperForm>
  <CrfActivitiesModelsLinkForm
    :open="linkForm"
    :item-to-link="selectedItem"
    item-type="item"
    @close="closeLinkForm"
  />
  <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
  <CrfApprovalSummaryConfirmDialog ref="confirmApproval" />
  <CrfNewVersionSummaryConfirmDialog ref="confirmNewVersion" />
</template>

<script>
import crfs from '@/api/crfs'
import NNTable from '@/components/tools/NNTable.vue'
import terms from '@/api/controlledTerminology/terms'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm.vue'
import controlledTerminology from '@/api/controlledTerminology'
import constants from '@/constants/libraries'
import CrfAliasSelection from '@/components/library/crfs/CrfAliasSelection.vue'
import CrfDescriptionSelection from '@/components/library/crfs/CrfDescriptionSelection.vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import crfTypes from '@/constants/crfTypes'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import CrfActivitiesModelsLinkForm from '@/components/library/crfs/CrfActivitiesModelsLinkForm.vue'
import actions from '@/constants/actions'
import parameters from '@/constants/parameters'
import CrfExtensionsManagementTable from '@/components/library/crfs/CrfExtensionsManagementTable.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import { useAppStore } from '@/stores/app'
import { computed } from 'vue'
import { useUnitsStore } from '@/stores/units'
import filteringParameters from '@/utils/filteringParameters'
import regex from '@/utils/regex'
import CrfNewVersionSummaryConfirmDialog from '@/components/library/crfs/CrfNewVersionSummaryConfirmDialog.vue'
import CrfApprovalSummaryConfirmDialog from '@/components/library/crfs/CrfApprovalSummaryConfirmDialog.vue'

export default {
  components: {
    NNTable,
    HorizontalStepperForm,
    CrfAliasSelection,
    CrfDescriptionSelection,
    QuillEditor,
    ActionsMenu,
    CrfActivitiesModelsLinkForm,
    CrfExtensionsManagementTable,
    ConfirmDialog,
    CrfNewVersionSummaryConfirmDialog,
    CrfApprovalSummaryConfirmDialog,
  },
  inject: ['notificationHub', 'formRules'],
  props: {
    selectedItem: {
      type: Object,
      default: null,
    },
    readOnlyProp: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['updateItem', 'close', 'linkItem'],
  setup() {
    const appStore = useAppStore()
    const unitsStore = useUnitsStore()

    return {
      fetchUnits: unitsStore.fetchUnits,
      userData: computed(() => appStore.userData),
      units: computed(() => unitsStore.units),
      clearEmptyHtml: regex.clearEmptyHtml,
    }
  },
  data() {
    return {
      helpItems: [
        'CRFItems.name',
        'CRFItems.oid',
        'CRFItems.data_type',
        'CRFItems.length',
        'CRFItems.significant_digits',
        'CRFItems.sponsor_instruction',
        'CRFItems.instruction',
        'CRFItems.sas_name',
        'CRFItems.sds_name',
        'CRFItems.origin',
        'CRFItems.comment',
        'CRFItems.context',
      ],
      form: {
        oid: 'I.',
        aliases: [],
        descriptions: [],
      },
      desc: [],
      selectedExtensions: [],
      selectedCodelistHeaders: [
        { title: this.$t('CtCatalogueTable.concept_id'), key: 'codelist_uid' },
        { title: this.$t('CtCatalogueTable.cd_name'), key: 'attributes.name' },
        {
          title: this.$t('CtCatalogueTable.submission_value'),
          key: 'attributes.submission_value',
        },
        {
          title: this.$t('CtCatalogueTable.nci_pref_name'),
          key: 'attributes.nci_preferred_name',
        },
        {
          title: this.$t('CRFItems.multiple_choice'),
          key: 'allowsMultiChoice',
        },
        { title: '', key: 'delete' },
      ],
      codelistHeaders: [
        { title: this.$t('CtCatalogueTable.concept_id'), key: 'codelist_uid' },
        { title: this.$t('CtCatalogueTable.cd_name'), key: 'attributes.name' },
        {
          title: this.$t('CtCatalogueTable.submission_value'),
          key: 'attributes.submission_value',
        },
        {
          title: this.$t('CtCatalogueTable.nci_pref_name'),
          key: 'attributes.nci_preferred_name',
        },
        { title: '', key: 'actions' },
      ],
      unitHeaders: [
        { title: this.$t('CRFItemGroups.name'), key: 'name', width: '25%' },
        { title: this.$t('CRFItems.sponsor_unit'), key: 'oid', width: '20%' },
        { title: this.$t('UnitTable.ucum_unit'), key: 'ucum' },
        { title: this.$t('UnitTable.ct_units'), key: 'terms', width: '30%' },
        { title: this.$t('_global.mandatory'), key: 'mandatory' },
        { title: '', key: 'delete' },
      ],
      termsHeaders: [
        { title: this.$t('CtCatalogueTable.concept_id'), key: 'term_uid' },
        { title: this.$t('_global.name'), key: 'name.sponsor_preferred_name' },
        { title: '', key: 'add' },
      ],
      selectedTermsHeaders: [
        {
          title: this.$t('CtCatalogueTable.concept_id'),
          key: 'term_uid',
          width: '10%',
        },
        {
          title: this.$t('CRFItems.sponsor_pref_name'),
          key: 'name',
          width: '40%',
        },
        { title: this.$t('_global.mandatory'), key: 'mandatory', width: '5%' },
        {
          title: this.$t('CRFItems.displayed_name'),
          key: 'display_text',
          width: '40%',
        },
        { title: '', key: 'delete', width: '1%' },
      ],
      aliases: [],
      aliasesTotal: 0,
      alias: {},
      steps: [],
      createSteps: [
        { name: 'form', title: this.$t('CRFItems.item_details') },
        {
          name: 'extensions',
          title: this.$t('CRFForms.vendor_extensions'),
        },
        {
          name: 'description',
          title: this.$t('CRFItemGroups.description_details'),
        },
        { name: 'alias', title: this.$t('CRFItemGroups.alias_details') },
      ],
      editSteps: [
        { name: 'form', title: this.$t('CRFItems.item_details') },
        {
          name: 'extensions',
          title: this.$t('CRFForms.vendor_extensions'),
        },
        {
          name: 'description',
          title: this.$t('CRFItemGroups.description_details'),
        },
        { name: 'alias', title: this.$t('CRFItemGroups.alias_details') },
        { name: 'change_description', title: this.$t('CRFForms.change_desc') },
      ],
      origins: [],
      chosenUnits: [{ name: '', mandatory: true }],
      codelists: [],
      selectedCodelists: [],
      options: {},
      total: 0,
      filters: '',
      dataTypes: [],
      descKey: 0,
      customToolbar: [
        ['bold', 'italic', 'underline'],
        [{ script: 'sub' }, { script: 'super' }],
        [{ list: 'ordered' }, { list: 'bullet' }],
      ],
      engDescription: {
        library_name: constants.LIBRARY_SPONSOR,
        language: parameters.ENG,
      },
      terms: [],
      selectedTerms: [],
      readOnly: this.readOnlyProp,
      linkForm: false,
      actions: [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: () => !this.readOnly,
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.approve,
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: () => this.readOnly,
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.newVersion,
        },
        {
          label: this.$t('_global.delete'),
          icon: 'mdi-delete-outline',
          iconColor: 'error',
          condition: (item) =>
            item.possible_actions
              ? item.possible_actions.find(
                  (action) => action === actions.DELETE
                )
              : false,
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.delete,
        },
        {
          label: this.$t('CRFLinkingForm.link_activities'),
          icon: 'mdi-plus',
          iconColor: 'primary',
          condition: () => this.readOnly,
          accessRole: this.$roles.LIBRARY_WRITE,
          click: this.openLinkForm,
        },
      ],
      lengthFieldCheck: false,
      digitsFieldCheck: false,
      originFieldCheck: true,
      filteringTerms: [],
      selectedFilteringTerms: [],
      search: '',
      operators: ['or', 'and'],
      termsFilterOperator: 'or',
      totalTerms: 0,
    }
  },
  computed: {
    title() {
      return this.isEdit()
        ? this.readOnly
          ? this.$t('CRFItems.crf_item') + ' - ' + this.form.name
          : this.$t('CRFItems.edit_item') + ' - ' + this.form.name
        : this.$t('CRFItems.add_item')
    },
    formUrl() {
      if (this.isEdit()) {
        return `${window.location.href.replace('crf-tree', 'items')}/item/${this.selectedItem.uid}`
      }
      return null
    },
  },
  watch: {
    readOnlyProp(value) {
      this.readOnly = value
    },
    selectedCodelists() {
      this.getCodeListTerms()
    },
    userData: {
      handler() {
        if (!this.userData.multilingual) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'description'
          })
        } else {
          this.steps = this.createSteps
        }
      },
    },
    selectedItem: {
      handler(value) {
        if (this.isEdit()) {
          this.steps = this.readOnly ? this.createSteps : this.editSteps
          if (value.datatype.indexOf('STRING') !== -1) {
            this.steps.splice(1, 0, {
              name: 'codelist',
              title: this.$t('CRFItems.codelist_details'),
            })
            this.steps.splice(2, 0, {
              name: 'terms',
              title: this.$t('CRFItems.codelist_subset'),
            })
          }
          this.initForm(value)
        } else {
          this.steps = this.createSteps
        }
        if (!this.userData.multilingual) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'description'
          })
        }
        const uniqueSteps = Array.from(
          new Set(this.steps.map((a) => a.name))
        ).map((name) => {
          return this.steps.find((a) => a.name === name)
        })
        this.steps = uniqueSteps
      },
      immediate: true,
    },
    options: {
      handler() {
        this.fetchCodelists()
      },
      deep: true,
    },
    search() {
      this.fetchTerms()
    },
    selectedFilteringTerms() {
      this.fetchCodelists()
    },
    termsFilterOperator() {
      this.fetchCodelists()
    },
  },
  created() {
    this.crfTypes = crfTypes
  },
  mounted() {
    this.fetchCodelists()
    terms.getTermsByCodelist('originType').then((resp) => {
      this.origins = resp.data.items
    })
    terms.getTermsByCodelist('dataType').then((resp) => {
      this.dataTypes = resp.data.items.sort((a, b) =>
        a.submission_value.localeCompare(b.submission_value)
      )
    })
    this.fetchUnits({ page_size: 0 })
    if (this.isEdit()) {
      this.steps = this.readOnly ? this.createSteps : this.editSteps
    } else {
      this.steps = this.createSteps
    }
    if (!this.userData.multilingual) {
      this.steps = this.steps.filter(function (obj) {
        return obj.name !== 'description'
      })
    }
  },
  methods: {
    lengthRequired(value) {
      if (
        ['STRING', 'TEXT'].includes(this.form.datatype) ||
        (this.form.significant_digits !== null &&
          this.form.significant_digits !== undefined)
      ) {
        return this.formRules.required(value)
      }
      return true
    },
    significantDigitsRequired(value) {
      if (this.form.length !== null && this.form.length !== undefined) {
        return this.formRules.required(value)
      }
      return true
    },
    checkFieldAvailable(dataType) {
      this.digitsFieldCheck = false
      this.originFieldCheck = true
      this.lengthFieldCheck = true

      if (!['TEXT', 'STRING', 'INTEGER', 'FLOAT'].includes(dataType)) {
        this.lengthFieldCheck = false
        this.form.length = null
      }

      if (dataType === 'FLOAT') {
        this.digitsFieldCheck = true
      }

      if (dataType === 'COMMENT') {
        this.originFieldCheck = false
      }
    },
    getItem() {
      crfs.getItem(this.selectedItem.uid).then((resp) => {
        this.initForm(resp.data)
      })
    },
    openLinkForm() {
      this.linkForm = true
    },
    closeLinkForm() {
      this.linkForm = false
      this.getItem()
    },
    async newVersion() {
      if (
        await this.$refs.confirmNewVersion.open({
          agreeLabel: this.$t('CRFItems.create_new_version'),
          item: this.selectedItem,
        })
      ) {
        crfs.newVersion('items', this.selectedItem.uid).then((resp) => {
          this.$emit('updateItem', resp.data)
          this.readOnly = false
          this.getItem()

          this.notificationHub.add({
            msg: this.$t('_global.new_version_success'),
          })
        })
      }
    },
    async approve() {
      if (
        await this.$refs.confirmApproval.open({
          agreeLabel: this.$t('CRFItems.approve_item'),
          item: this.selectedItem,
        })
      ) {
        crfs.approve('items', this.selectedItem.uid).then((resp) => {
          this.$emit('updateItem', resp.data)
          this.readOnly = true
          this.close()
          this.getItem()

          this.notificationHub.add({
            msg: this.$t('CRFItems.approved'),
          })
        })
      }
    },
    async delete() {
      let relationships = 0
      await crfs
        .getRelationships(this.selectedItem.uid, 'items')
        .then((resp) => {
          if (resp.data.OdmItemGroup && resp.data.OdmItemGroup.length > 0) {
            relationships = resp.data.OdmItemGroup.length
          }
        })
      const options = {
        type: 'warning',
        cancelLabel: this.$t('_global.cancel'),
        agreeLabel: this.$t('_global.continue'),
      }
      if (
        relationships > 0 &&
        (await this.$refs.confirm.open(
          `${this.$t('CRFItems.delete_warning', { count: relationships })}`,
          options
        ))
      ) {
        crfs.delete('items', this.selectedItem.uid).then(() => {
          this.$emit('close')
        })
      } else if (relationships === 0) {
        crfs.delete('items', this.selectedItem.uid).then(() => {
          this.$emit('close')
        })
      }
    },
    setDesc(desc) {
      this.desc = desc
    },
    getObserver(step) {
      return this.$refs[`observer_${step}`]
    },
    checkIfNumeric() {
      if (this.form.datatype) {
        if (
          this.form.datatype.indexOf('INTEGER') !== -1 ||
          this.form.datatype.indexOf('FLOAT') !== -1 ||
          this.form.datatype.indexOf('DOUBLE') !== -1
        ) {
          this.steps.splice(1, 0, {
            name: 'unit',
            title: this.$t('CRFItems.unit_details'),
          })
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'codelist' && obj.name !== 'terms'
          })
        } else if (this.form.datatype.indexOf('STRING') !== -1) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'unit'
          })
          this.steps.splice(1, 0, {
            name: 'codelist',
            title: this.$t('CRFItems.codelist_details'),
          })
          this.steps.splice(2, 0, {
            name: 'terms',
            title: this.$t('CRFItems.codelist_subset'),
          })
        }
        if (
          this.form.datatype.indexOf('STRING') === -1 &&
          this.form.datatype.indexOf('TEXT') === -1
        ) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'codelist' && obj.name !== 'terms'
          })
        }
        if (
          this.form.datatype.indexOf('INTEGER') === -1 &&
          this.form.datatype.indexOf('FLOAT') === -1 &&
          this.form.datatype.indexOf('DOUBLE') === -1
        ) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'unit'
          })
        }
      } else {
        this.steps = this.steps.filter(function (obj) {
          return (
            obj.name !== 'unit' &&
            obj.name !== 'codelist' &&
            obj.name !== 'terms'
          )
        })
      }
      const uniqueSteps = Array.from(
        new Set(this.steps.map((a) => a.name))
      ).map((name) => {
        return this.steps.find((a) => a.name === name)
      })
      this.steps = uniqueSteps
      this.checkFieldAvailable(this.form.datatype)
    },
    close() {
      this.notificationHub.clearErrors()
      this.form = {
        oid: 'I.',
        aliases: [],
      }
      this.desc = []
      this.chosenUnits = [{ name: '', mandatory: true }]
      this.selectedCodelists = []
      this.selectedTerms = []
      this.selectedExtensions = []
      this.engDescription = {
        library_name: constants.LIBRARY_SPONSOR,
        language: parameters.ENG,
      }
      this.$refs.stepper.reset()
      this.$emit('close')
    },
    getCodeListTerms(filters, options, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        options,
        filters,
        filtersUpdated
      )
      if (this.selectedCodelists[0]) {
        params.codelist_uid = this.selectedCodelists[0].codelist_uid
        terms.getTermsByCodelistUid(params).then((resp) => {
          this.terms = resp.data.items
          if (this.form.terms) {
            this.selectedTerms = this.form.terms
          }
          this.totalTerms = resp.data.total
        })
      } else {
        this.terms = []
      }
    },
    addTerm(item) {
      item.mandatory = true
      if (!this.selectedTerms.some((el) => el.term_uid === item.term_uid)) {
        const itemToAdd = Object.assign({}, item)
        itemToAdd.name = itemToAdd.name.sponsor_preferred_name
        this.selectedTerms.push(itemToAdd)
      }
    },
    removeTerm(item) {
      this.selectedTerms = this.selectedTerms.filter(
        (el) => el.term_uid !== item.term_uid
      )
    },
    async submit() {
      this.notificationHub.clearErrors()

      if (this.readOnly) {
        this.close()
        return
      }
      await this.setDescription()
      this.form.library_name = constants.LIBRARY_SPONSOR
      if (this.form.oid === 'I.') {
        this.form.oid = null
      }
      this.chosenUnits = this.chosenUnits.filter((el) => {
        return el.name !== ''
      })
      this.form.unit_definitions =
        this.chosenUnits.length === 0
          ? []
          : this.chosenUnits.map((e) => ({
              uid: e.uid ? e.uid : e.name.uid,
              mandatory: e.mandatory,
            }))
      if (this.form.datatype !== 'STRING') {
        this.form.codelist_uid = null
        this.form.terms = []
      } else {
        this.form.codelist_uid = this.selectedCodelists[0]
          ? this.selectedCodelists[0].codelist_uid
          : null
        this.form.terms = this.selectedTerms.map((el) => ({
          uid: el.term_uid,
          mandatory: el.mandatory,
          display_text: el.display_text,
        }))
      }
      if (this.form.length == '') {
        this.form.length = null
      }
      if (this.form.significant_digits == '') {
        this.form.significant_digits = null
      }
      try {
        if (this.isEdit()) {
          await crfs
            .updateItem(this.form, this.selectedItem.uid)
            .then(async () => {
              await this.linkExtensions(this.selectedItem.uid)
              this.notificationHub.add({
                msg: this.$t('CRFItems.item_updated'),
              })
              this.close()
            })
        } else {
          await crfs.createItem(this.form).then(async (resp) => {
            await this.linkExtensions(resp.data.uid)
            this.notificationHub.add({
              msg: this.$t('CRFItems.item_created'),
            })
            this.$emit('linkItem', resp)
            this.close()
          })
        }
      } finally {
        this.$refs.stepper.loading = false
      }
    },
    setExtensions(extensions) {
      this.selectedExtensions = extensions
    },
    async linkExtensions(uid) {
      let elements = []
      let attributes = []
      let eleAttributes = []
      this.selectedExtensions.forEach((ex) => {
        if (ex.type) {
          attributes.push(ex)
        } else {
          elements.push(ex)
          if (ex.vendor_attributes) {
            eleAttributes = [...eleAttributes, ...ex.vendor_attributes]
          }
        }
      })
      const data = {
        elements: elements,
        element_attributes: eleAttributes,
        attributes: attributes,
      }
      await crfs.setExtensions('items', uid, data)
    },
    addUnit() {
      this.chosenUnits.push({ name: '', mandatory: true })
    },
    removeUnit(index) {
      this.chosenUnits.splice(index, 1)
    },
    setUnit(index) {
      this.chosenUnits[index].ucum = this.chosenUnits[index].name.ucum
        ? this.chosenUnits[index].name.ucum.name
        : ''
      this.chosenUnits[index].oid = this.chosenUnits[index].name.name
      this.chosenUnits[index].terms = this.chosenUnits[index].name.ct_units[0]
        ? this.chosenUnits[index].name.ct_units[0].term_name
        : ''
      this.chosenUnits[index].uid = this.chosenUnits[index].name.uid
    },
    getAliases(filters, options, filtersUpdated) {
      const params = filteringParameters.prepareParameters(
        options,
        filters,
        filtersUpdated
      )
      crfs.getAliases(params).then((resp) => {
        this.aliases = resp.data.items
        this.aliasesTotal = resp.data.total
      })
    },
    addAlias() {
      if (!this.alias.name || !this.alias.context) {
        return
      }
      const alias = {
        name: this.alias.name,
        context: this.alias.context,
      }

      const isDuplicate = this.aliases.some(
        (a) => a.name === alias.name && a.context === alias.context
      )

      if (!isDuplicate) {
        this.aliases.push({ ...alias })
      }

      this.form.aliases.push({ ...alias })
      this.alias = {}
    },
    async setDescription() {
      const descArray = []

      if (!this.engDescription.name) {
        this.engDescription.name = this.form.name
      }
      this.engDescription.description = this.clearEmptyHtml(
        this.engDescription.description
      )
      this.engDescription.instruction = this.clearEmptyHtml(
        this.engDescription.instruction
      )
      this.engDescription.sponsor_instruction = this.clearEmptyHtml(
        this.engDescription.sponsor_instruction
      )
      descArray.push(this.engDescription)
      this.form.descriptions = [...descArray, ...this.desc]
    },
    async initForm(item) {
      this.form = item
      this.form.aliases = item.aliases
      if (item.descriptions.find((el) => el.language === parameters.ENG)) {
        this.engDescription = item.descriptions.find(
          (el) => el.language === parameters.ENG
        )
      }
      this.desc = item.descriptions.filter(
        (el) => el.language !== parameters.ENG
      )
      if (!item.unit_definitions || item.unit_definitions.length === 0) {
        this.chosenUnits = []
      } else {
        item.unit_definitions.forEach((e) => {
          if (!this.chosenUnits.some((el) => el.uid === e.uid)) {
            this.chosenUnits.unshift({
              uid: e.uid,
              oid: e.name,
              name: e.name,
              ucum: e.ucum ? e.ucum.name : '',
              terms: e.ct_units[0] ? e.ct_units[0].name : '',
              mandatory: e.mandatory,
            })
          }
        })
      }
      if (this.selectedCodelists.length === 0 && item.codelist) {
        this.selectedCodelists.push({
          codelist_uid: item.codelist.uid,
          attributes: {
            name: item.codelist.name,
            submission_value: item.codelist.submission_value,
            nci_preferred_name: item.codelist.preferred_term,
          },
        })
      }
      if (item.terms) {
        this.selectedTerms = item.terms
      }
      this.form.change_description = this.$t('_global.draft_change')
      this.checkIfNumeric()
      item.vendor_attributes.forEach((attr) => (attr.type = 'attr'))
      item.vendor_elements.forEach((element) => {
        element.vendor_attributes = item.vendor_element_attributes.filter(
          (attribute) => attribute.vendor_element_uid === element.uid
        )
      })
      this.selectedExtensions = [
        ...item.vendor_attributes,
        ...item.vendor_elements,
      ]
    },
    isEdit() {
      if (this.selectedItem) {
        return Object.keys(this.selectedItem).length !== 0
      }
      return false
    },
    fetchCodelists(filters) {
      this.filters = filters
      if (this.filtersUpdated) {
        this.options.page = 1
      }
      const params = {
        page_number: this.options.page,
        page_size: this.options.itemsPerPage,
        total_count: true,
        library_name: this.library,
      }
      if (this.filters !== undefined) {
        params.filters = this.filters
      }
      if (this.selectedFilteringTerms.length > 0) {
        params.term_filter = {
          term_uids: this.selectedFilteringTerms.map((term) => term.term_uid),
          operator: this.termsFilterOperator,
        }
      }
      controlledTerminology.getCodelists(params).then((resp) => {
        this.codelists = resp.data.items.filter(
          (ar) =>
            !this.selectedCodelists.find(
              (rm) => rm.codelist_uid === ar.codelist_uid
            )
        )
        this.total = resp.data.total
      })
    },
    fetchTerms() {
      const params = {
        filters: {
          'name.sponsor_preferred_name': {
            v: [this.search ? this.search : ''],
            op: 'co',
          },
        },
        page_size: 20,
      }
      controlledTerminology.getCodelistTerms(params).then((resp) => {
        this.filteringTerms = [
          ...resp.data.items,
          ...this.selectedFilteringTerms,
        ]
      })
    },
    addCodelist(item) {
      if (this.selectedCodelists.length === 0) {
        this.selectedCodelists.push(item)
        this.codelists.splice(this.codelists.indexOf(item), 1)
      }
    },
    removeCodelist(item) {
      this.selectedCodelists = []
      this.codelists.unshift(item)
    },
  },
}
</script>
<style scoped>
.max-width-100 {
  max-width: 100px;
}
.max-width-300 {
  max-width: 300px;
}
</style>
