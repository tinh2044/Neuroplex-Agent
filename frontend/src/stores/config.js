import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useConfigStore = defineStore('config', () => {
  const config = ref({})
  function setConfig(newConfig) {
    config.value = newConfig
  }

  function setConfigValue(key, value) {
    config.value[key] = value
    fetch('/api/config', {
      method: 'POST',
      body: JSON.stringify({ key, value }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      console.debug('Success:', data)
      setConfig(data)
    })
  }

  function refreshConfig() {
    fetch('/api/config')
    .then(response => response.json())
    .then(data => {
      console.log("config", data)
      setConfig(data)
    })
  }

  return { config, setConfig, setConfigValue, refreshConfig }
})