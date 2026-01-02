import { createApp } from 'vue'
import App from './App.vue'

// 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入日文字体
import '@fontsource/noto-sans-jp/400.css'
import '@fontsource/noto-sans-jp/700.css'

const app = createApp(App)

app.use(ElementPlus)
app.mount('#app')