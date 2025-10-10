import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 8200,
    host: '0.0.0.0',
    open: true,
    allowedHosts: [
      'ljl.vue.cpolar.top',  // 你的 cpolar 域名
      '.cpolar.top',         // 允许所有 cpolar.top 的子域名
      'localhost'
    ]
  }
})
