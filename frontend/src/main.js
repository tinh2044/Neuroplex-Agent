import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './routes'

import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './assets/main.css'
import {
  CommentOutlined,
  DeleteOutlined,
  PlusCircleOutlined,
  BulbOutlined,
    FolderOutlined,
    CompassOutlined,
    DeploymentUnitOutlined,
    BookOutlined,
} from '@ant-design/icons-vue'

const app = createApp(App)

app.component('CommentOutlined', CommentOutlined)
app.component('DeleteOutlined', DeleteOutlined)
app.component('PlusCircleOutlined', PlusCircleOutlined)
app.component('BulbOutlined', BulbOutlined)
app.component('FolderOutlined', FolderOutlined)

app.use(createPinia())
app.use(router)
app.use(Antd)

app.mount('#app')
