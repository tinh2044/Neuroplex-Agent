<script setup>
import { ref, computed } from "vue";
import { onClickOutside } from "@vueuse/core";
import { FolderOutlined, FolderOpenOutlined } from "@ant-design/icons-vue";

const props = defineProps({
  meta: {
    type: Object,
    required: true,
  },
  sidebarState: {
    type: Object,
    required: true,
  },
  modelConfig: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits([
  "toggle-sidebar",
  "new-conversation",
  "update-meta",
  "select-model",
]);
console.log(props.modelConfig);
const panel = ref(null);
const opts = ref({
  showPanel: false,
});

onClickOutside(panel, () => setTimeout(() => (opts.value.showPanel = false), 30));

// Computed properties for model selection
const modelNames = computed(() => props.modelConfig?.model);
const modelStatus = computed(() => props.modelConfig?.provider);
const customModels = computed(() => props.modelConfig?.custom_models || []);

// Filter active model providers
const modelKeys = computed(() => {
  return Object.keys(modelStatus.value || {}).filter((key) => modelStatus.value?.[key]);
});

// Model selection handler
const selectModel = (provider, name) => {
  emit("select-model", { provider, name });
};
</script>

<template>
  <div class="chat-header">
    <div class="header__left">
      <div
        v-if="!sidebarState.isOpen"
        class="close nav-btn nav-btn-icon-only"
        @click="$emit('toggle-sidebar')"
      >
        <a-tooltip title="Expand Sidebar" placement="right">
          <img
            src="@/assets/icons/sidebar_left.svg"
            class="iconfont icon-20"
            alt="Settings"
          />
        </a-tooltip>
      </div>

      <div class="newchat nav-btn nav-btn-icon-only" @click="$emit('new-conversation')">
        <a-tooltip title="New Conversation" placement="right">
          <PlusCircleOutlined />
        </a-tooltip>
      </div>

      <a-dropdown>
        <a class="model-select nav-btn" @click.prevent>
          <BulbOutlined />
          <a-tooltip :title="modelConfig?.model" placement="right">
            <span class="model-text text">{{ modelConfig?.model }}</span>
          </a-tooltip>
          <span class="text" style="color: #aaa">
            {{ modelConfig?.provider }}
          </span>
        </a>
        <template #overlay>
          <a-menu class="scrollable-menu">
            <a-menu-item-group
              v-for="(item, key) in modelKeys"
              :key="key"
              :title="modelNames[item]?.name"
            >
              <a-menu-item
                v-for="(model, idx) in modelNames[item]?.models"
                :key="`${item}-${idx}`"
                @click="selectModel(item, model)"
              >
                {{ model }}
              </a-menu-item>
            </a-menu-item-group>
            <a-menu-item-group v-if="customModels.length > 0" title="Custom Models">
              <a-menu-item
                v-for="(model, idx) in customModels"
                :key="`custom-${idx}`"
                @click="selectModel('custom', model.custom_id)"
              >
                custom/{{ model.custom_id }}
              </a-menu-item>
            </a-menu-item-group>
          </a-menu>
        </template>
      </a-dropdown>
    </div>

    <div class="header__right">
      <div class="nav-btn text" @click="opts.showPanel = !opts.showPanel">
        <component :is="opts.showPanel ? FolderOpenOutlined : FolderOutlined" />
        <span class="text">Options</span>
      </div>
      <div v-if="opts.showPanel" class="my-panal r0 top100 swing-in-top-fwd" ref="panel">
        <div
          class="flex-center"
          @click="$emit('update-meta', { summary_title: !meta.summary_title })"
        >
          Summarize Conversation Title
          <div @click.stop>
            <a-switch
              :checked="meta.summary_title"
              @update:checked="(val) => $emit('update-meta', { summary_title: val })"
            />
          </div>
        </div>
        <div class="flex-center">
          Maximum History Rounds
          <a-input-number
            :value="meta.history_round"
            @update:value="(val) => $emit('update-meta', { history_round: val })"
            :min="1"
            :max="50"
          />
        </div>
        <div class="flex-center">
          Font Size
          <a-select
            :value="meta.fontSize"
            @update:value="(val) => $emit('update-meta', { fontSize: val })"
            style="width: 100px"
            placeholder="Select Font Size"
          >
            <a-select-option value="smaller">Smaller</a-select-option>
            <a-select-option value="default">Default</a-select-option>
            <a-select-option value="larger">Larger</a-select-option>
          </a-select>
        </div>
        <div
          class="flex-center"
          @click="$emit('update-meta', { wideScreen: !meta.wideScreen })"
        >
          Wide Screen Mode
          <div @click.stop>
            <a-switch
              :checked="meta.wideScreen"
              @update:checked="(val) => $emit('update-meta', { wideScreen: val })"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="less" scoped>
.chat-header {
  user-select: none;
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  height: var(--header-height);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;

  .header__left,
  .header__right {
    display: flex;
    align-items: center;
  }
}

.nav-btn {
  height: 2.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
  color: var(--gray-900);
  cursor: pointer;
  width: auto;
  transition: background-color 0.3s;
  padding: 0.5rem 0.75rem;

  .text {
    margin-left: 10px;
  }

  &:hover {
    background-color: var(--main-light-3);
  }
}

.nav-btn-icon-only {
  font-size: 1rem;
}

.model-select {
  max-width: 350px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  .model-text {
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

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

.my-panal.r0.top100 {
  top: 100%;
  right: 0;
}

.scrollable-menu {
  max-height: 300px;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--gray-400);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: var(--gray-500);
  }
}

@media (max-width: 520px) {
  .chat-header {
    background: var(--main-light-4);

    .header__left,
    .header__right {
      gap: 24px;
    }

    .nav-btn {
      font-size: 1.3rem;
      padding: 0;

      &:hover {
        background-color: transparent;
        color: black;
      }

      .text {
        display: none;
      }
    }
  }
}
</style>
