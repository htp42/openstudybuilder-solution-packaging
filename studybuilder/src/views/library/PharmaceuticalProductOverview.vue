<template>
  <div class="px-4">
    <div class="d-flex page-title">
      {{ product.uid }}
    </div>
    <PharmaceuticalProductOverview :pharmaceutical-product="product" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import pharmaceuticalProductsApi from '@/api/concepts/pharmaceuticalProducts'
import PharmaceuticalProductOverview from '@/components/library/PharmaceuticalProductOverview.vue'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const appStore = useAppStore()

const product = ref({})

pharmaceuticalProductsApi.getObject(route.params.id).then((resp) => {
  product.value = resp.data
  appStore.addBreadcrumbsLevel(
    product.value.uid,
    { name: 'PharmaceuticalProductOverview', params: route.params },
    4
  )
})
</script>
