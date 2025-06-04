<template>
  <div class="my-panal r0 top100 swing-in-top-fwd">
    <div class="flex-center" @click="toggleSummaryTitle">
      Summarize Conversation Title 
      <div @click.stop>
        <a-switch :checked="meta.summary_title" @update:checked="updateSummaryTitle" />
      </div>
    </div>
    
    <div class="flex-center">
      Maximum History Rounds 
      <a-input-number 
        id="inputNumber" 
        :value="meta.history_round" 
        @update:value="updateHistoryRound" 
        :min="1" 
        :max="50" 
      />
    </div>
    
    <div class="flex-center">
      Font Size
      <a-select 
        :value="meta.fontSize" 
        @update:value="updateFontSize" 
        style="width: 100px" 
        placeholder="Select Font Size"
      >
        <a-select-option value="smaller">Smaller</a-select-option>
        <a-select-option value="default">Default</a-select-option>
        <a-select-option value="larger">Larger</a-select-option>
      </a-select>
    </div>
    
    <div class="flex-center" @click="toggleWideScreen">
      Wide Screen Mode 
      <div @click.stop>
        <a-switch :checked="meta.wideScreen" @update:checked="updateWideScreen" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  meta: {
    type: Object,
    required: true
  }
})

const emit = defineEmits([
  'update:meta', 
  'toggle-summary-title', 
  'toggle-wide-screen'
])

const toggleSummaryTitle = () => {
  emit('update:meta', { ...props.meta, summary_title: !props.meta.summary_title })
}

const updateSummaryTitle = (val) => {
  emit('update:meta', { ...props.meta, summary_title: val })
}

const updateHistoryRound = (val) => {
  emit('update:meta', { ...props.meta, history_round: val })
}

const updateFontSize = (val) => {
  emit('update:meta', { ...props.meta, fontSize: val })
}

const toggleWideScreen = () => {
  emit('update:meta', { ...props.meta, wideScreen: !props.meta.wideScreen })
}

const updateWideScreen = (val) => {
  emit('update:meta', { ...props.meta, wideScreen: val })
}
</script>

<style lang="less" scoped>
.my-panal {
  position: absolute;
  margin-top: 5px;
  background-color: white;
  border: 1px solid #ccc;
  box-shadow: 0px 0px 10px 1px rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  padding: 12px;
  z-index: 11;
  width: 280px;
  transition: transform 0.3s ease, opacity 0.3s ease;

  .flex-center {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s;

    &:hover {
      background-color: var(--main-light-3);
    }

    .anticon {
      margin-right: 8px;
      font-size: 16px;
    }
    
    .ant-switch {
      &.ant-switch-checked {
        background-color: var(--main-500);
      }
    }
  }
}

.r0.top100 {
  top: 100%;
  right: 0;
}
</style> 