import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router/index.ts'

const app = createApp(App)

axios.defaults.baseURL = "http://127.0.0.1:8000"
axios.defaults.headers.common['Content-Type'] = 'application/json';

app.use(createPinia())
app.use(router, axios)

app.mount('#app')
