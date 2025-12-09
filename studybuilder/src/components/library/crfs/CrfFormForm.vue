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
            <v-col cols="7">
              <v-text-field
                v-model="form.name"
                :label="$t('CRFForms.name') + '*'"
                data-cy="form-oid-name"
                density="compact"
                clearable
                :disabled="readOnly"
                :rules="[formRules.required]"
              />
            </v-col>
            <v-col cols="5">
              <v-text-field
                v-model="form.oid"
                :label="$t('CRFForms.oid')"
                data-cy="form-oid"
                density="compact"
                clearable
                :disabled="readOnly"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2">
              <v-radio-group
                v-model="form.repeating"
                :label="$t('CRFForms.repeating')"
                :disabled="readOnly"
              >
                <v-radio :label="$t('_global.yes')" value="Yes" />
                <v-radio :label="$t('_global.no')" value="No" />
              </v-radio-group>
            </v-col>
            <v-col cols="5">
              <div class="subtitle-2">
                {{ $t('_global.description') }}
              </div>
              <div v-show="readOnly">
                <QuillEditor
                  v-model:content="engDescription.description"
                  content-type="html"
                  :toolbar="customToolbar"
                  :options="quillOptions"
                  theme="snow"
                />
              </div>
              <div v-show="!readOnly">
                <QuillEditor
                  v-model:content="engDescription.description"
                  content-type="html"
                  :toolbar="customToolbar"
                  :placeholder="$t('_global.description')"
                  theme="snow"
                />
              </div>
            </v-col>
            <v-col cols="5">
              <div class="subtitle-2">
                {{ $t('CRFDescriptions.sponsor_instruction') }}
              </div>
              <div v-show="readOnly">
                <QuillEditor
                  v-model:content="engDescription.sponsor_instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  :options="quillOptions"
                  data-cy="help-for-sponsor"
                  theme="snow"
                />
              </div>
              <div v-show="!readOnly">
                <QuillEditor
                  v-model:content="engDescription.sponsor_instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  :placeholder="$t('CRFDescriptions.sponsor_instruction')"
                  data-cy="help-for-sponsor"
                  theme="snow"
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
                data-cy="form-oid-displayed-text"
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
                  v-model:content="engDescription.instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  :options="quillOptions"
                  data-cy="form-help-for-site"
                  theme="snow"
                />
              </div>
              <div v-show="!readOnly">
                <QuillEditor
                  v-model:content="engDescription.instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  :placeholder="$t('CRFDescriptions.instruction')"
                  data-cy="form-help-for-site"
                  theme="snow"
                />
              </div>
            </v-col>
          </v-row>
        </v-card>
      </v-form>
    </template>
    <template #[`step.extensions`]>
      <CrfExtensionsManagementTable
        type="FormDef"
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
    <template #[`step.change_description`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <v-row>
          <v-col>
            <v-text-field
              v-model="form.change_description"
              :label="$t('CRFForms.change_desc')"
              data-cy="form-change-description"
              clearable
              :rules="[formRules.required]"
            />
          </v-col>
        </v-row>
      </v-form>
    </template>
    <template #actions>
      <ActionsMenu v-if="selectedForm" :actions="actions" :item="form" />
    </template>
  </HorizontalStepperForm>
  <CrfActivitiesModelsLinkForm
    :open="linkForm"
    :item-to-link="selectedForm"
    item-type="form"
    @close="closeLinkForm"
  />
  <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
  <CrfApprovalSummaryConfirmDialog ref="confirmApproval" />
  <CrfNewVersionSummaryConfirmDialog ref="confirmNewVersion" />
</template>

<script>
import crfs from '@/api/crfs'
import CrfAliasSelection from '@/components/library/crfs/CrfAliasSelection.vue'
import CrfDescriptionSelection from '@/components/library/crfs/CrfDescriptionSelection.vue'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm.vue'
import constants from '@/constants/libraries'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import CrfActivitiesModelsLinkForm from '@/components/library/crfs/CrfActivitiesModelsLinkForm.vue'
import actions from '@/constants/actions'
import parameters from '@/constants/parameters'
import CrfExtensionsManagementTable from '@/components/library/crfs/CrfExtensionsManagementTable.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import CrfApprovalSummaryConfirmDialog from '@/components/library/crfs/CrfApprovalSummaryConfirmDialog.vue'
import filteringParameters from '@/utils/filteringParameters'
import { useAppStore } from '@/stores/app'
import { computed } from 'vue'
import regex from '@/utils/regex'
import CrfNewVersionSummaryConfirmDialog from '@/components/library/crfs/CrfNewVersionSummaryConfirmDialog.vue'

export default {
  components: {
    HorizontalStepperForm,
    CrfAliasSelection,
    CrfDescriptionSelection,
    QuillEditor,
    ActionsMenu,
    CrfActivitiesModelsLinkForm,
    CrfExtensionsManagementTable,
    ConfirmDialog,
    CrfApprovalSummaryConfirmDialog,
    CrfNewVersionSummaryConfirmDialog,
  },
  inject: ['notificationHub', 'formRules'],
  props: {
    selectedForm: {
      type: Object,
      default: null,
    },
    readOnlyProp: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['updateForm', 'close', 'linkForm'],
  setup() {
    const appStore = useAppStore()
    return {
      userData: computed(() => appStore.userData),
      clearEmptyHtml: regex.clearEmptyHtml,
    }
  },
  data() {
    return {
      search: '',
      helpItems: [
        'CRFForms.name',
        'CRFForms.oid',
        'CRFForms.repeating',
        'CRFForms.description',
        'CRFForms.sponsor_instruction',
        'CRFForms.instruction',
        'CRFForms.displayed_text',
        'CRFForms.vendor_extensions',
        'CRFForms.aliases',
        'CRFForms.context',
      ],
      form: {
        oid: 'F.',
        repeating: 'No',
        aliases: [],
        descriptions: [],
      },
      aliases: [],
      aliasesTotal: 0,
      alias: {},
      createSteps: [
        { name: 'form', title: this.$t('CRFForms.form_details') },
        {
          name: 'extensions',
          title: this.$t('CRFForms.vendor_extensions'),
        },
        {
          name: 'description',
          title: this.$t('CRFForms.description_details'),
        },
        { name: 'alias', title: this.$t('CRFForms.alias_details') },
      ],
      editSteps: [
        { name: 'form', title: this.$t('CRFForms.form_details') },
        {
          name: 'extensions',
          title: this.$t('CRFForms.vendor_extensions'),
        },
        {
          name: 'description',
          title: this.$t('CRFForms.description_details'),
        },
        { name: 'alias', title: this.$t('CRFForms.alias_details') },
        { name: 'change_description', title: this.$t('CRFForms.change_desc') },
      ],
      desc: [],
      steps: [],
      customToolbar: [
        ['bold', 'italic', 'underline'],
        [{ script: 'sub' }, { script: 'super' }],
        [{ list: 'ordered' }, { list: 'bullet' }],
      ],
      quillOptions: {
        readOnly: true,
      },
      engDescription: { language: parameters.ENG },
      readOnly: this.readOnlyProp,
      linkForm: false,
      selectedExtensions: [],
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
    }
  },
  computed: {
    title() {
      if (this.isEdit()) {
        if (this.readOnly) {
          return this.$t('CRFForms.crf_form') + ' - ' + this.form.name
        }
        return this.$t('CRFForms.edit_form') + ' - ' + this.form.name
      }
      return this.$t('CRFForms.add_form')
    },
    formUrl() {
      if (this.isEdit()) {
        return `${window.location.href.replace('crf-tree', 'forms')}/form/${this.selectedForm.uid}`
      }
      return null
    },
  },
  watch: {
    readOnlyProp(value) {
      this.readOnly = value
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
      immediate: true,
    },
    selectedForm: {
      handler(value) {
        if (this.isEdit()) {
          this.steps = this.readOnly ? this.createSteps : this.editSteps
          this.initForm(value)
        } else {
          this.steps = this.createSteps
        }
        if (!this.userData.multilingual) {
          this.steps = this.steps.filter(function (obj) {
            return obj.name !== 'description'
          })
        }
      },
      immediate: true,
    },
  },
  async mounted() {
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
    getForm() {
      crfs.getForm(this.selectedForm.uid).then((resp) => {
        this.initForm(resp.data)
      })
    },
    openLinkForm() {
      this.linkForm = true
    },
    closeLinkForm() {
      this.linkForm = false
      this.getForm()
    },
    async newVersion() {
      if (
        await this.$refs.confirmNewVersion.open({
          agreeLabel: this.$t('CRFForms.create_new_version'),
          form: this.selectedForm,
        })
      ) {
        crfs.newVersion('forms', this.selectedForm.uid).then((resp) => {
          this.$emit('updateForm', resp.data)
          this.readOnly = false
          this.getForm()

          this.notificationHub.add({
            msg: this.$t('_global.new_version_success'),
          })
        })
      }
    },
    async approve() {
      if (
        await this.$refs.confirmApproval.open({
          agreeLabel: this.$t('CRFForms.approve_form'),
          form: this.selectedForm,
        })
      ) {
        crfs.approve('forms', this.selectedForm.uid).then((resp) => {
          this.$emit('updateForm', resp.data)
          this.readOnly = true
          this.close()
          this.getForm()

          this.notificationHub.add({
            msg: this.$t('CRFForms.approved'),
          })
        })
      }
    },
    async delete() {
      let relationships = 0
      await crfs
        .getRelationships(this.selectedForm.uid, 'forms')
        .then((resp) => {
          if (resp.data.OdmStudyEvent && resp.data.OdmStudyEvent.length > 0) {
            relationships = resp.data.OdmStudyEvent.length
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
          `${this.$t('CRFForms.delete_warning', { count: relationships })}`,
          options
        ))
      ) {
        crfs.delete('forms', this.selectedForm.uid).then(() => {
          this.$emit('close')
        })
      } else if (relationships === 0) {
        crfs.delete('forms', this.selectedForm.uid).then(() => {
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
    close() {
      this.notificationHub.clearErrors()
      this.form = {
        oid: 'F.',
        repeating: 'No',
        aliases: [],
      }
      this.engDescription = {
        language: parameters.ENG,
      }
      this.desc = []
      this.selectedExtensions = []
      this.$refs.stepper.reset()
      this.$emit('close')
    },
    async submit() {
      this.notificationHub.clearErrors()

      if (this.readOnly) {
        this.close()
        return
      }
      await this.setDescription()
      this.form.library_name = constants.LIBRARY_SPONSOR
      if (this.form.oid === 'F.') {
        this.form.oid = null
      }
      try {
        if (this.isEdit()) {
          await crfs
            .updateForm(this.form, this.selectedForm.uid)
            .then(async () => {
              await this.linkExtensions(this.selectedForm.uid)
              this.notificationHub.add({
                msg: this.$t('CRFForms.form_updated'),
              })
              this.close()
            })
        } else {
          await crfs.createForm(this.form).then(async (resp) => {
            await this.linkExtensions(resp.data.uid)
            this.notificationHub.add({
              msg: this.$t('CRFForms.form_created'),
            })
            this.$emit('linkForm', resp)
            this.close()
          })
        }
      } finally {
        this.$refs.stepper.loading = false
      }
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
      await crfs.setExtensions('forms', uid, data)
    },
    async initForm(item) {
      this.form = item
      this.form.aliases = item.aliases
      this.form.change_description = this.$t('_global.draft_change')
      if (item.descriptions.find((el) => el.language === parameters.ENG)) {
        this.engDescription = item.descriptions.find(
          (el) => el.language === parameters.ENG
        )
      }
      this.desc = item.descriptions.filter(
        (el) => el.language !== parameters.ENG
      )
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
      if (this.selectedForm) {
        return Object.keys(this.selectedForm).length !== 0
      }
      return false
    },
  },
}
</script>
