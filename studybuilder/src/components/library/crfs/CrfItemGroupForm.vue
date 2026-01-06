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
                :label="$t('CRFItemGroups.name') + '*'"
                data-cy="item-group-name"
                density="compact"
                clearable
                :disabled="isDisabled"
                :rules="[formRules.required]"
              />
            </v-col>
            <v-col cols="5">
              <v-text-field
                v-model="form.oid"
                :label="$t('CRFItemGroups.oid')"
                data-cy="item-group-oid"
                density="compact"
                clearable
                :disabled="isDisabled"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2">
              <v-radio-group
                v-model="form.repeating"
                class="mt-2"
                :label="$t('CRFItemGroups.repeating')"
                :disabled="isDisabled"
              >
                <v-radio :label="$t('_global.yes')" value="Yes" />
                <v-radio :label="$t('_global.no')" value="No" />
              </v-radio-group>
            </v-col>
            <v-col cols="5">
              <div class="subtitle-2">
                {{ $t('_global.description') }}
              </div>
              <div>
                <QuillEditor
                  v-model:content="engDescription.description"
                  content-type="html"
                  :toolbar="customToolbar"
                  :read-only="isDisabled"
                />
              </div>
            </v-col>
            <v-col cols="5">
              <div class="subtitle-2">
                {{ $t('CRFDescriptions.sponsor_instruction') }}
              </div>
              <div>
                <QuillEditor
                  v-model:content="engDescription.sponsor_instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  data-cy="crf-item-group-help-for-sponsor"
                  :read-only="isDisabled"
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
                data-cy="crf-item-group-displayed-text"
                density="compact"
                clearable
                :disabled="isDisabled"
              />
            </v-col>
            <v-col cols="9">
              <div class="subtitle-2">
                {{ $t('CRFDescriptions.instruction') }}
              </div>
              <div>
                <QuillEditor
                  v-model:content="engDescription.instruction"
                  content-type="html"
                  :toolbar="customToolbar"
                  data-cy="crf-item-group-help-for-site"
                  :read-only="isDisabled"
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
              <v-select
                v-model="form.sdtm_domains"
                :label="$t('CRFItemGroups.domain')"
                data-cy="item-group-domain"
                :items="domains"
                :item-props="sdtmDataDomainProps"
                density="compact"
                single-line
                clearable
                return-object
                multiple
              >
                <template #item="{ props }">
                  <v-list-item
                    v-bind="props"
                    @click="
                      () => {
                        props.onClick()
                        domainSearch = ''
                      }
                    "
                  >
                    <template #prepend="{ isActive }">
                      <v-list-item-action start>
                        <v-checkbox-btn :model-value="isActive" />
                      </v-list-item-action>
                    </template>
                    <template #title>
                      {{ props.title }}
                    </template>
                  </v-list-item>
                </template>

                <template #selection="{ index }">
                  <div v-if="index === 0">
                    <span>{{
                      form.sdtm_domains[0].sponsor_preferred_name ||
                      form.sdtm_domains[0].term_name
                    }}</span>
                  </div>
                  <span v-if="index === 1" class="grey--text text-caption mr-1">
                    (+{{ form.sdtm_domains.length - 1 }})
                  </span>
                </template>

                <template #prepend-item>
                  <v-row @keydown.stop>
                    <v-text-field
                      v-model="domainSearch"
                      class="pl-6"
                      :placeholder="$t('_global.search')"
                    />
                    <v-btn
                      variant="text"
                      size="small"
                      icon="mdi-close"
                      class="mr-3 mt-3"
                      @click="domainSearch = ''"
                    />
                  </v-row>
                </template>
              </v-select>
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.sas_dataset_name"
                :label="$t('CRFItemGroups.sas_dataset')"
                data-cy="item-group-sas-dataset-name"
                density="compact"
                clearable
                :disabled="isDisabled"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2">
              <v-radio-group
                v-model="form.is_reference_data"
                class="mt-2"
                :label="$t('CRFItemGroups.is_referential')"
                :disabled="isDisabled"
              >
                <v-radio :label="$t('_global.yes')" value="Yes" />
                <v-radio :label="$t('_global.no')" value="No" />
              </v-radio-group>
            </v-col>
            <v-col cols="4">
              <v-select
                v-model="form.origin"
                :label="$t('CRFItemGroups.origin')"
                data-cy="item-group-origin"
                :items="origins"
                item-title="nci_preferred_name"
                item-value="nci_preferred_name"
                density="compact"
                clearable
                :disabled="isDisabled"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model="form.purpose"
                :label="$t('CRFItemGroups.purpose')"
                data-cy="item-group-purpose"
                density="compact"
                clearable
                :disabled="isDisabled"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.comment"
                :label="$t('CRFItemGroups.comment')"
                data-cy="item-group-comment"
                density="compact"
                clearable
                :disabled="isDisabled"
              />
            </v-col>
          </v-row>
        </v-card>
      </v-form>
    </template>
    <template #[`step.extensions`]>
      <CrfExtensionsManagementTable
        type="ItemGroupDef"
        :read-only="isDisabled"
        :edit-extensions="selectedExtensions"
        @set-extensions="setExtensions"
      />
    </template>
    <template #[`step.alias`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <CrfAliasSelection v-model="form.aliases" :disabled="isDisabled" />
      </v-form>
    </template>
    <template #[`step.description`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <CrfDescriptionSelection v-model="desc" :disabled="isDisabled" />
      </v-form>
    </template>
    <template #[`step.change_description`]="{ step }">
      <v-form :ref="`observer_${step}`">
        <v-row>
          <v-col>
            <v-text-field
              v-model="form.change_description"
              :label="$t('CRFForms.change_desc')"
              data-cy="item-group-change-description"
              clearable
              :disabled="isDisabled"
              :rules="[formRules.required]"
            />
          </v-col>
        </v-row>
      </v-form>
    </template>
    <template #actions>
      <ActionsMenu
        v-if="selectedGroup && checkPermission($roles.LIBRARY_WRITE)"
        :actions="actions"
        :item="form"
      />
    </template>
  </HorizontalStepperForm>
  <CrfActivitiesModelsLinkForm
    :open="linkForm"
    :item-to-link="selectedGroup"
    item-type="itemGroup"
    @close="closeLinkForm"
  />
  <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
  <CrfApprovalSummaryConfirmDialog ref="confirmApproval" />
  <CrfNewVersionSummaryConfirmDialog ref="confirmNewVersion" />
</template>

<script>
import crfs from '@/api/crfs'
import terms from '@/api/controlledTerminology/terms'
import HorizontalStepperForm from '@/components/tools/HorizontalStepperForm.vue'
import libraries from '@/constants/libraries'
import CrfAliasSelection from '@/components/library/crfs/CrfAliasSelection.vue'
import CrfDescriptionSelection from '@/components/library/crfs/CrfDescriptionSelection.vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import ActionsMenu from '@/components/tools/ActionsMenu.vue'
import CrfActivitiesModelsLinkForm from '@/components/library/crfs/CrfActivitiesModelsLinkForm.vue'
import actions from '@/constants/actions'
import parameters from '@/constants/parameters'
import CrfExtensionsManagementTable from '@/components/library/crfs/CrfExtensionsManagementTable.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import CrfApprovalSummaryConfirmDialog from '@/components/library/crfs/CrfApprovalSummaryConfirmDialog.vue'
import CrfNewVersionSummaryConfirmDialog from '@/components/library/crfs/CrfNewVersionSummaryConfirmDialog.vue'
import filteringParameters from '@/utils/filteringParameters'
import { useAppStore } from '@/stores/app'
import { computed } from 'vue'
import regex from '@/utils/regex'
import { useAccessGuard } from '@/composables/accessGuard'

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
    selectedGroup: {
      type: Object,
      default: null,
    },
    readOnlyProp: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['updateItemGroup', 'close', 'linkGroup'],
  setup() {
    const appStore = useAppStore()
    const accessGuard = useAccessGuard()

    return {
      checkPermission: accessGuard.checkPermission,
      userData: computed(() => appStore.userData),
      clearEmptyHtml: regex.clearEmptyHtml,
    }
  },
  data() {
    return {
      helpItems: [
        'CRFItemGroups.name',
        'CRFItemGroups.oid',
        'CRFItemGroups.repeating',
        'CRFItemGroups.description',
        'CRFItemGroups.sponsor_instruction',
        'CRFItemGroups.instruction',
        'CRFItemGroups.displayed_text',
        'CRFItemGroups.aliases',
        'CRFItemGroups.context',
      ],
      form: {
        oid: 'G.',
        repeating: 'No',
        isReferenceData: 'No',
        aliases: [],
        descriptions: [],
        sdtm_domains: [],
      },
      desc: [],
      aliases: [],
      aliasesTotal: 0,
      alias: {},
      steps: [],
      selectedExtensions: [],
      createSteps: [
        { name: 'form', title: this.$t('CRFItemGroups.group_details') },
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
        { name: 'form', title: this.$t('CRFItemGroups.group_details') },
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
      domains: [],
      engDescription: { language: parameters.ENG },
      customToolbar: [
        ['bold', 'italic', 'underline'],
        [{ script: 'sub' }, { script: 'super' }],
        [{ list: 'ordered' }, { list: 'bullet' }],
      ],
      readOnly: this.readOnlyProp,
      linkForm: false,
      actions: [
        {
          label: this.$t('_global.approve'),
          icon: 'mdi-check-decagram',
          iconColor: 'success',
          condition: () => !this.readOnly,
          click: this.approve,
        },
        {
          label: this.$t('_global.new_version'),
          icon: 'mdi-plus-circle-outline',
          iconColor: 'primary',
          condition: () => this.readOnly,
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
          click: this.delete,
        },
        {
          label: this.$t('CRFLinkingForm.link_activity_sub_groups'),
          icon: 'mdi-plus',
          iconColor: 'primary',
          condition: () => this.readOnly,
          click: this.openLinkForm,
        },
      ],
      domainSearch: '',
    }
  },
  computed: {
    isDisabled() {
      return this.readOnly || !this.checkPermission(this.$roles.LIBRARY_WRITE)
    },
    title() {
      return this.isEdit()
        ? this.readOnly
          ? this.$t('CRFItemGroups.item_group') + ' - ' + this.form.name
          : this.$t('CRFItemGroups.edit_group') + ' - ' + this.form.name
        : this.$t('CRFItemGroups.add_group')
    },
    formUrl() {
      if (this.isEdit()) {
        return `${window.location.href.replace('crf-tree', 'item-groups')}/item-group/${this.selectedGroup.uid}`
      }
      return null
    },
  },
  watch: {
    readOnlyProp(value) {
      this.readOnly = value
    },
    domainSearch() {
      this.filterSdtmDomains()
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
    selectedGroup: {
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
  mounted() {
    terms.getTermsByCodelist('originType').then((resp) => {
      this.origins = resp.data.items
    })

    this.filterSdtmDomains()

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
    async filterSdtmDomains() {
      clearTimeout(this.domainSearchTimeout)
      const baseParams = {
        page_size: 10,
        sort_by: JSON.stringify({ submission_value: true }),
      }
      let params = { ...baseParams }
      if (this.domainSearch && this.domainSearch.trim().length > 0) {
        params.filters = JSON.stringify({
          sponsor_preferred_name: { v: [this.domainSearch], op: 'co' },
          submission_value: { v: [this.domainSearch], op: 'co' },
        })
        params.operator = 'or'
        this.domainSearchTimeout = setTimeout(async () => {
          const resp = await terms.getTermsByCodelist(
            'sdtmDomainAbbreviation',
            params
          )
          this.domains = [
            ...this.form.sdtm_domains,
            ...resp.data.items.filter(
              (item) =>
                !this.form.sdtm_domains.some(
                  (domain) => domain.term_uid === item.term_uid
                )
            ),
          ]
        }, 400)
      } else {
        const resp = await terms.getTermsByCodelist(
          'sdtmDomainAbbreviation',
          baseParams
        )
        this.domains = [
          ...this.form.sdtm_domains,
          ...resp.data.items.filter(
            (item) =>
              !this.form.sdtm_domains.some(
                (domain) => domain.term_uid === item.term_uid
              )
          ),
        ]
      }
    },
    sdtmDataDomainProps(item) {
      return {
        title: `${item.sponsor_preferred_name || item.term_name} (${item.submission_value})`,
        value: item.term_uid,
      }
    },
    getGroup() {
      crfs.getItemGroup(this.selectedGroup.uid).then((resp) => {
        this.initForm(resp.data)
      })
    },
    openLinkForm() {
      this.linkForm = true
    },
    closeLinkForm() {
      this.linkForm = false
      this.getGroup()
    },
    async newVersion() {
      if (
        await this.$refs.confirmNewVersion.open({
          agreeLabel: this.$t('CRFItemGroups.create_new_version'),
          itemGroup: this.selectedGroup,
        })
      ) {
        crfs.newVersion('item-groups', this.selectedGroup.uid).then((resp) => {
          this.$emit('updateItemGroup', resp.data)
          this.readOnly = false
          this.getGroup()

          this.notificationHub.add({
            msg: this.$t('_global.new_version_success'),
          })
        })
      }
    },
    async approve() {
      if (
        await this.$refs.confirmApproval.open({
          agreeLabel: this.$t('CRFItemGroups.approve_group'),
          itemGroup: this.selectedGroup,
        })
      ) {
        crfs.approve('item-groups', this.selectedGroup.uid).then((resp) => {
          this.$emit('updateItemGroup', resp.data)
          this.readOnly = true
          this.close()
          this.getGroup()

          this.notificationHub.add({
            msg: this.$t('CRFItemGroups.approved'),
          })
        })
      }
    },
    async delete() {
      let relationships = 0
      await crfs
        .getRelationships(this.selectedGroup.uid, 'item-groups')
        .then((resp) => {
          if (resp.data.OdmForm && resp.data.OdmForm.length > 0) {
            relationships = resp.data.OdmForm.length
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
          `${this.$t('CRFItemGroups.delete_warning', { count: relationships })}`,
          options
        ))
      ) {
        crfs.delete('item-groups', this.selectedGroup.uid).then(() => {
          this.$emit('close')
        })
      } else if (relationships === 0) {
        crfs.delete('item-groups', this.selectedGroup.uid).then(() => {
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
        oid: 'G.',
        repeating: 'No',
        isReferenceData: 'No',
        aliases: [],
        sdtm_domains: [],
      }
      this.desc = []
      this.selectedExtensions = []
      this.engDescription = {
        language: parameters.ENG,
      }
      this.$refs.stepper.reset()
      this.$emit('close')
    },
    async submit() {
      if (this.isDisabled) {
        this.close()
        return
      }

      this.notificationHub.clearErrors()

      await this.setDescription()
      this.form.library_name = libraries.LIBRARY_SPONSOR
      if (this.form.oid === 'G.') {
        this.form.oid = null
      }
      try {
        this.form.sdtm_domain_uids = this.form.sdtm_domains.map(
          (el) => el.term_uid
        )
        if (this.isEdit()) {
          await crfs
            .updateItemGroup(this.form, this.selectedGroup.uid)
            .then(async () => {
              await this.linkExtensions(this.selectedGroup.uid)
              this.notificationHub.add({
                msg: this.$t('CRFItemGroups.group_updated'),
              })
              this.close()
            })
        } else {
          await crfs.createItemGroup(this.form).then(async (resp) => {
            await this.linkExtensions(resp.data.uid)
            this.notificationHub.add({
              msg: this.$t('CRFItemGroups.group_created'),
            })
            this.$emit('linkGroup', resp)
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
      await crfs.setExtensions('item-groups', uid, data)
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
      this.form.sdtm_domains = item.sdtm_domains
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
      if (this.selectedGroup) {
        return Object.keys(this.selectedGroup).length !== 0
      }
      return false
    },
  },
}
</script>
