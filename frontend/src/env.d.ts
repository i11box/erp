/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Declare module resolutions for path aliases
declare module '@/services/api' {
  const api: import('axios').AxiosInstance
  export default api
}

declare module '@/stores/*' {
  const store: any
  export default store
  export * from 'pinia'
}