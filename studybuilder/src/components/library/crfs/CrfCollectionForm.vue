<template>
  <SimpleFormDialog
    ref="form"
    :title="title"
    :help-items="helpItems"
    :open="open"
    :form-url="formUrl"
    @close="cancel"
    @submit="submit"
  >
    <template #body>
      <v-form ref="observer">
        <v-row>
          <v-col>
            <v-text-field
              v-model="form.name"
              :label="$t('CRFCollections.name') + '*'"
              data-cy="crf-collection-name"
              density="compact"
              clearable
              class="mt-3"
              :readonly="readOnly"
              :rules="[formRules.required]"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              v-model="form.oid"
              :label="$t('CRFCollections.oid')"
              data-cy="crf-collection-oid"
              density="compact"
              clearable
              :readonly="readOnly"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6">
            <v-menu
              v-model="effectiveDateMenu"
              :close-on-content-click="false"
              offset-y
              max-width="290px"
              min-width="290px"
            >
              <template #activator="{ props }">
                <v-text-field
                  :label="$t('CRFCollections.effective_date')"
                  data-cy="crf-collection-effective-date"
                  readonly
                  :model-value="effectiveDateDisp"
                  v-bind="props"
                />
              </template>
              <v-date-picker
                v-model="form.effective_date"
                locale="en-in"
                no-title
                data-cy="crf-collection-effective-date-picker"
                :readonly="readOnly"
                @input="effectiveDateMenu = false"
              />
            </v-menu>
          </v-col>
          <v-col cols="6">
            <v-menu
              v-model="retiredDateMenu"
              :close-on-content-click="false"
              offset-y
              max-width="290px"
              min-width="290px"
            >
              <template #activator="{ props }">
                <v-text-field
                  :label="$t('CRFCollections.retired_date')"
                  data-cy="crf-collection-retired-date"
                  readonly
                  :model-value="retiredDateDisp"
                  v-bind="props"
                />
              </template>
              <v-date-picker
                v-model="form.retired_date"
                locale="en-in"
                no-title
                data-cy="crf-collection-retired-date-picker"
                :readonly="readOnly"
                @input="retiredDateMenu = false"
              />
            </v-menu>
          </v-col>
        </v-row>
      </v-form>
    </template>
    <template #actions>
      <v-btn v-if="readOnly" class="primary mr-2" @click="newVersion">
        {{ $t('_global.new_version') }}
      </v-btn>
      <v-btn
        v-else-if="
          selectedCollection && selectedCollection.status === statuses.DRAFT
        "
        class="primary mr-2"
        @click="approve"
      >
        {{ $t('_global.approve') }}
      </v-btn>
    </template>
  </SimpleFormDialog>
  <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
  <CrfApprovalSummaryConfirmDialog ref="confirmApproval" />
</template>

<script>
import SimpleFormDialog from '@/components/tools/SimpleFormDialog.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import CrfApprovalSummaryConfirmDialog from '@/components/library/crfs/CrfApprovalSummaryConfirmDialog.vue'
import crfs from '@/api/crfs'
import _isEqual from 'lodash/isEqual'
import statuses from '@/constants/statuses'
import { useFormStore } from '@/stores/form'

export default {
  components: {
    SimpleFormDialog,
    ConfirmDialog,
    CrfApprovalSummaryConfirmDialog,
  },
  inject: ['notificationHub', 'formRules'],
  props: {
    selectedCollection: {
      type: Object,
      default: null,
    },
    open: Boolean,
    readOnlyProp: Boolean,
  },
  emits: ['updateCollection', 'close'],
  setup() {
    const formStore = useFormStore()
    return {
      formStore,
    }
  },
  data() {
    return {
      form: {},
      helpItems: [
        'CRFCollections.name',
        'CRFCollections.oid',
        'CRFCollections.effective_date',
        'CRFCollections.retired_date',
      ],
      effectiveDateMenu: false,
      retiredDateMenu: false,
      readOnly: this.readOnlyProp,
    }
  },
  computed: {
    title() {
      return this.isEdit()
        ? this.$t('CRFCollections.edit_collection') + ' - ' + this.form.name
        : this.$t('CRFCollections.add_collection')
    },
    effectiveDateDisp() {
      if (this.form.effective_date) {
        return this.formatDate(this.form.effective_date)
      }
      return ''
    },
    retiredDateDisp() {
      if (this.form.retired_date) {
        return this.formatDate(this.form.retired_date)
      }
      return ''
    },
    formUrl() {
      if (this.isEdit()) {
        return `${window.location.href.replace('crf-tree', 'collections')}/collection/${this.selectedCollection.uid}`
      }
      return null
    },
  },
  watch: {
    selectedCollection(value) {
      if (value) {
        this.form = { ...value }
        this.form.effective_date = this.form.effective_date
          ? new Date(this.form.effective_date)
          : null
        this.form.retired_date = this.form.retired_date
          ? new Date(this.form.retired_date)
          : null
        this.formStore.save(this.form)
      }
    },
    readOnlyProp(value) {
      this.readOnly = value
    },
  },
  created() {
    this.statuses = statuses
  },
  mounted() {
    if (this.isEdit()) {
      this.form = { ...this.selectedCollection }
      this.form.effective_date = new Date(this.form.effective_date)
      this.form.retired_date = new Date(this.form.retired_date)
      this.formStore.save(this.form)
    }
  },
  methods: {
    formatDate(value) {
      if (value.length <= 10) {
        return value
      }
      let month = 1 + value.getMonth()
      if (month < 10) {
        month = `0${month}`
      }
      let day = value.getDate()
      if (day < 10) {
        day = `0${day}`
      }
      const date = `${value.getFullYear()}-${month}-${day}`
      if (date === '1970-01-01') {
        return null
      }
      return `${value.getFullYear()}-${month}-${day}`
    },
    newVersion() {
      crfs
        .newVersion('study-events', this.selectedCollection.uid)
        .then((resp) => {
          this.$emit('updateCollection', resp.data)
          this.readOnly = false

          this.notificationHub.add({
            msg: this.$t('_global.new_version_success'),
          })
        })
    },
    async approve() {
      if (
        await this.$refs.confirmApproval.open({
          agreeLabel: this.$t('CRFCollections.approve_collection'),
          collection: this.selectedCollection,
        })
      ) {
        crfs
          .approve('study-events', this.selectedCollection.uid)
          .then((resp) => {
            this.$emit('updateCollection', resp.data)
            this.readOnly = true
            this.close()

            this.notificationHub.add({
              msg: this.$t('CRFCollections.approved'),
            })
          })
      }
    },
    async submit() {
      const { valid } = await this.$refs.observer.validate()
      if (!valid) return

      this.notificationHub.clearErrors()

      if (this.form.effective_date) {
        this.form.effective_date = this.formatDate(this.form.effective_date)
      }
      if (this.form.retired_date) {
        this.form.retired_date = this.formatDate(this.form.retired_date)
      }
      if (this.isEdit()) {
        crfs.updateCollection(this.form, this.selectedCollection.uid).then(
          () => {
            this.notificationHub.add({
              msg: this.$t('CRFCollections.updated'),
            })
            this.close()
          },
          () => {
            this.$refs.form.working = false
          }
        )
      } else {
        crfs.createCollection(this.form).then(
          () => {
            this.notificationHub.add({
              msg: this.$t('CRFCollections.created'),
            })
            this.close()
          },
          () => {
            this.$refs.form.working = false
          }
        )
      }
    },
    async cancel() {
      if (
        this.storedForm === '' ||
        _isEqual(this.storedForm, JSON.stringify(this.form))
      ) {
        this.close()
      } else {
        const options = {
          type: 'warning',
          cancelLabel: this.$t('_global.cancel'),
          agreeLabel: this.$t('_global.continue'),
        }
        if (
          await this.$refs.form.confirm(
            this.$t('_global.cancel_changes'),
            options
          )
        ) {
          this.close()
        }
      }
    },
    close() {
      this.notificationHub.clearErrors()
      this.form = {}
      this.$refs.observer.reset()
      this.$emit('close')
    },
    isEdit() {
      if (this.selectedCollection) {
        return Object.keys(this.selectedCollection).length !== 0
      }
      return false
    },
  },
}
</script>
