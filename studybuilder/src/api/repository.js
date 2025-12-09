import axios from 'axios'

import { auth } from '@/plugins/auth'
import { notificationHub } from '@/plugins/notificationHub'
import { useGlobalConfig } from '@/main'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import { useErrorHandler } from '@/composables/errorHandler'

const _axios = axios.create()

_axios.interceptors.request.use(
  async function (config) {
    const studiesGeneralStore = useStudiesGeneralStore()
    if (config.method === 'get' && config.url.indexOf('studies/') !== -1) {
      if (config.params) {
        config.params.study_value_version =
          studiesGeneralStore.selectedStudyVersion
      } else {
        config.params = {
          study_value_version: studiesGeneralStore.selectedStudyVersion,
        }
      }
    }
    const globalConfig = useGlobalConfig()
    config.baseURL = globalConfig.API_BASE_URL

    // the component used to display available rows per page uses -1 to describe all elements
    // but API expects 0 to be sent to fetch all items in a paginated query
    if (config?.params?.page_size === -1) {
      config.params.page_size = 0
    }
    const accessToken = await auth.getAccessToken()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
      config.withCredentials = true
    } else {
      auth.clear()
    }

    // Check if we need to serialize filters
    if (
      config.method === 'get' &&
      config.params &&
      config.params.filters &&
      typeof config.params.filters !== 'string'
    ) {
      config.params.filters = JSON.stringify(config.params.filters)
    }

    return config
  },
  function (error) {
    // Do something with request error
    return Promise.reject(error)
  }
)

// Add a response interceptor
_axios.interceptors.response.use(
  function (response) {
    // Just return unchanged response data
    return response
  },
  function (error) {
    console.log(error)
    if (error.config && !error.config.ignoreErrors) {
      if (!error.response) {
        // We do not have a response, we don't know the tracing id, just display the error.message
        notificationHub.add({
          msg: error.message,
          type: 'error',
        })
      } else if (error.response.status === 401) {
        // Unauthorized: handled elsewhere either by login-redirect or token-refresh routine
      } else {
        // If status code is 422, display the validation error details from error.response.data.detail.
        // Otherwise, just display the error message contained in error.response.data.message.

        useErrorHandler(error)
      }
    }
    return Promise.reject(error)
  }
)

export default _axios
