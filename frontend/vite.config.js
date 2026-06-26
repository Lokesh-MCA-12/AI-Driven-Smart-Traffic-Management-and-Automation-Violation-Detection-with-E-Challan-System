import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Plugin to bypass Host header check for ngrok/tunnels
function allowAllHostsPlugin() {
  return {
    name: 'allow-all-hosts',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        // Remove the host check by always proceeding
        next()
      })
    },
  }
}

export default defineConfig({
  plugins: [react(), allowAllHostsPlugin()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    cors: true,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '.ngrok-free.app',
      '.ngrok.io',
      '.ngrok-free.dev',
      '.loca.lt',
      '.serveo.net',
    ],
    hmr: {
      protocol: 'ws',
      host: 'localhost',
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
