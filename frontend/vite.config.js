import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Detect backend URL (default to localhost for local dev, or docker service name in docker)
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
