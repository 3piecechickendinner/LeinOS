import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://lien-os-402756129398.us-central1.run.app',
        changeOrigin: true,
        secure: true
      }
    }
  }
})
