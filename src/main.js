import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

app.mount('#app')

import { enableDragDropTouch } from "./drag-drop-touch.esm.min.js";

// Set up the default full page polyfill:
enableDragDropTouch();