<script setup>
import MessageInputComponent from "@/components/messages/MessageInputComponent.vue";
import {
  CompassOutlined,
  DeploymentUnitOutlined,
  BookOutlined,
} from "@ant-design/icons-vue";

const props = defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
  meta: {
    type: Object,
    required: true,
  },
  databases: {
    type: Array,
    default: () => [],
  },
  config: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits([
  "update:modelValue",
  "send-message",
  "stop-streaming",
  "keydown",
  "update-meta",
  "use-database",
]);

const handleKeyDown = (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    emit("send-message");
  } else if (e.key === "Enter" && e.shiftKey) {
    const textarea = e.target;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newText = `${props.modelValue.substring(
      0,
      start
    )}\n${props.modelValue.substring(end)}`;
    emit("update:modelValue", newText);
    nextTick(() => {
      textarea.setSelectionRange(start + 1, start + 1);
    });
  }
};

const handleSendOrStop = () => {
  if (props.isStreaming) {
    emit("stop-streaming");
  } else {
    emit("send-message");
  }
};
</script>

<template>
  <div class="bottom">
    <div class="message-input-wrapper" :class="{ 'wide-screen': meta.wideScreen }">
      <MessageInputComponent
        :model-value="modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
        :is-loading="isStreaming"
        :send-button-disabled="!modelValue && !isStreaming"
        :auto-size="{ minRows: 2, maxRows: 10 }"
        @send="handleSendOrStop"
        @keydown="handleKeyDown"
      >
        <template #options-left>
          <div
            :class="{ switch: true, 'opt-item': true, active: meta.use_web }"
            v-if="config.enable_web_search"
            @click="$emit('update-meta', { use_web: !meta.use_web })"
          >
            <CompassOutlined style="margin-right: 3px" />
            Web Search
          </div>
          <div
            :class="{ switch: true, 'opt-item': true, active: meta.use_graph }"
            v-if="config.enable_knowledge_graph"
            @click="$emit('update-meta', { use_graph: !meta.use_graph })"
          >
            <DeploymentUnitOutlined style="margin-right: 3px" />
            Knowledge Graph
          </div>
          <a-dropdown
            v-if="config.enable_knowledge_base && databases.length > 0"
            :class="{ 'opt-item': true, active: meta.selectedKB !== null }"
          >
            <a class="ant-dropdown-link" @click.prevent>
              <BookOutlined style="margin-right: 3px" />
              <span class="text">{{
                meta.selectedKB === null
                  ? "Do Not Use Knowledge Base"
                  : databases[meta.selectedKB]?.name
              }}</span>
            </a>
            <template #overlay>
              <a-menu>
                <a-menu-item
                  v-for="(db, index) in databases"
                  :key="index"
                  @click="$emit('use-database', index)"
                >
                  <a href="javascript:;">{{ db.name }}</a>
                </a-menu-item>
                <a-menu-item @click="$emit('use-database', null)">
                  <a href="javascript:;">Do Not Use</a>
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </template>
      </MessageInputComponent>
      <p class="note">
        Please be aware of the reliability of the content. By
        {{ config?.provider }}: {{ config?.model }}
      </p>
    </div>
  </div>
</template>

<style lang="less" scoped>
.bottom {
  position: sticky;
  bottom: 0;
  width: 100%;
  margin: 0 auto;
  padding: 4px 2rem 0 2rem;

  .message-input-wrapper {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
    background-color: white;
    animation: width 0.3s ease-in-out;

    &.wide-screen {
      max-width: 1200px;
    }

    .note {
      width: 100%;
      font-size: small;
      text-align: center;
      padding: 0;
      color: #ccc;
      margin-top: 4px;
      margin-bottom: 0;
      user-select: none;
    }
  }
}

.opt-item {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;

  &:hover {
    background-color: var(--main-light-3);
  }

  &.active {
    background-color: var(--main-light-4);
  }
}

.ant-dropdown-link {
  color: var(--gray-900);
  cursor: pointer;
}

@media (max-width: 520px) {
  .bottom {
    padding: 0.5rem 0.5rem;

    .message-input-wrapper {
      border-radius: 8px;
      padding: 0.5rem;

      textarea.user-input {
        padding: 0.5rem 0;
      }
    }

    .note {
      display: none;
    }
  }
}
</style>
