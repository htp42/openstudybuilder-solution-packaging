<template>
  <div>
    <v-row>
      <v-col>
        <div class="text-h5 mb-4">
          {{ $t('CRFAliases.add') }}
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <v-text-field
          v-model="inputAlias.context"
          :label="$t('CRFAliases.context')"
          data-cy="alias-context"
          density="compact"
          :disabled="props.disabled"
        />
      </v-col>
      <v-col>
        <v-text-field
          v-model="inputAlias.name"
          :label="$t('CRFAliases.name')"
          data-cy="alias-name"
          density="compact"
          :disabled="props.disabled"
        />
      </v-col>
      <v-col>
        <v-btn
          color="secondary"
          class="mr-2"
          data-cy="alias-add-button"
          block
          :disabled="props.disabled"
          @click="addAlias"
        >
          {{ t('_global.add') }}
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <div class="text-h5 mb-4">
          {{ $t('CRFAliases.select') }}
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <NNTable
          v-model="modelValue"
          :headers="headers"
          :items="aliases"
          hide-default-switches
          hide-export-button
          :show-select="!disabled"
          :hide-default-footer="props.disabled"
          :hide-search-field="props.disabled"
          table-height="400px"
          :items-length="total"
          disable-filtering
          column-data-resource="concepts/odm-metadata/aliases"
          @filter="getAliases"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ref, computed, onMounted } from 'vue'
import filteringParameters from '@/utils/filteringParameters'
import NNTable from '@/components/tools/NNTable.vue'
import crfs from '@/api/crfs'

const { t } = useI18n()

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
})

const modelValue = defineModel({
  type: Array,
  default: () => [],
})

const headers = computed(() => [
  { title: t('CRFAliases.context'), key: 'context' },
  { title: t('CRFAliases.name'), key: 'name' },
])

const inputAlias = ref({
  context: '',
  name: '',
})

const aliases = ref([])
const total = ref(0)

onMounted(() => {
  getAliases()
})

const getAliases = (filters, options, filtersUpdated) => {
  if (!props.disabled) {
    const params = filteringParameters.prepareParameters(
      options,
      null,
      filtersUpdated
    )
    params.search = options.search
    crfs.getAliases(params).then((resp) => {
      aliases.value = resp.data.items
      total.value = resp.data.total
    })
  } else {
    aliases.value = [...modelValue.value]
  }
}

const addAlias = () => {
  if (inputAlias.value.name && inputAlias.value.context) {
    const alias = {
      context: inputAlias.value.context,
      name: inputAlias.value.name,
    }

    const isDuplicate = aliases.value.some(
      (a) => a.context === alias.context && a.name === alias.name
    )

    if (!isDuplicate) {
      aliases.value.push({ ...alias })
    }

    modelValue.value.push({ ...alias })
    inputAlias.value = {}
  }
}
</script>
