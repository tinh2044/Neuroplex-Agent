<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import MessageComponent from "@/components/messages/MessageComponent.vue";

const props = defineProps({
  messages: {
    type: Array,
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
  examples: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["retry-message", "retry-stopped-message", "select-example"]);

const chatContainer = ref(null);
const userIsScrolling = ref(false);
const shouldAutoScroll = ref(true);

const handleUserScroll = () => {
  const isNearBottom =
    chatContainer.value.scrollHeight -
      chatContainer.value.scrollTop -
      chatContainer.value.clientHeight <
    20;

  userIsScrolling.value = !isNearBottom;
  shouldAutoScroll.value = isNearBottom;
};

const scrollToBottom = () => {
  if (shouldAutoScroll.value) {
    setTimeout(() => {
      chatContainer.value.scrollTop =
        chatContainer.value.scrollHeight - chatContainer.value.clientHeight;
    }, 10);
  }
};

const forceScrollToBottom = () => {
  shouldAutoScroll.value = true;
  setTimeout(() => {
    chatContainer.value.scrollTop =
      chatContainer.value.scrollHeight - chatContainer.value.clientHeight;
  }, 10);
};

onMounted(() => {
  scrollToBottom();
  chatContainer.value.addEventListener("scroll", handleUserScroll);
});

onUnmounted(() => {
  if (chatContainer.value) {
    chatContainer.value.removeEventListener("scroll", handleUserScroll);
  }
});
</script>

<template>
  <div class="chat-messages" ref="chatContainer">
    <div v-if="messages.length == 0" class="chat-examples">
      <h1>Hello, I'm Neuroplex, an intelligent assistant based on knowledge graphs</h1>
      <div class="opts">
        <div
          class="opt__button"
          v-for="(exp, key) in examples"
          :key="key"
          @click="$emit('select-example', exp)"
        >
          {{ exp }}
        </div>
      </div>
    </div>
    <div
      class="chat-box"
      :class="{
        'wide-screen': meta.wideScreen,
        'font-smaller': meta.fontSize === 'smaller',
        'font-larger': meta.fontSize === 'larger',
      }"
    >
      <MessageComponent
        v-for="message in messages"
        :message="message"
        :key="message.id"
        :is-processing="isStreaming"
        :show-refs="true"
        @retry="$emit('retry-message', message.id)"
        @retryStoppedMessage="$emit('retry-stopped-message', message.id)"
      />
    </div>
  </div>
</template>

<style lang="less" scoped>
.chat-messages {
  width: 100%;
  max-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  background: var(--main-light-7);
  position: relative;
  box-sizing: border-box;
  flex: 5 5 200px;
  overflow-y: scroll;

  &::-webkit-scrollbar {
    position: absolute;
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--gray-400);
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: rgb(100, 100, 100);
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:active {
    background: rgb(68, 68, 68);
    border-radius: 4px;
  }
}

.chat-examples {
  padding: 0 50px;
  text-align: center;
  position: absolute;
  top: 20%;
  width: 100%;
  z-index: 9;
  animation: slideInUp 0.5s ease-out;

  h1 {
    margin-bottom: 20px;
    font-size: 1.2rem;
    color: #333;
  }

  .opts {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;

    .opt__button {
      background-color: var(--gray-200);
      color: #333;
      padding: 0.5rem 1.5rem;
      border-radius: 2rem;
      cursor: pointer;
      transition: background-color 0.3s;

      &:hover {
        background-color: #f0f1f1;
      }
    }
  }
}

.chat-box {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  flex-grow: 1;
  padding: 1rem 2rem;
  display: flex;
  flex-direction: column;
  transition: max-width 0.3s ease;

  &.wide-screen {
    max-width: 1200px;
  }

  &.font-smaller {
    font-size: 14px;

    .message-box {
      font-size: 14px;
    }
  }

  &.font-larger {
    font-size: 16px;

    .message-box {
      font-size: 16px;
    }
  }
}

@keyframes slideInUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 520px) {
  .chat-messages {
    height: calc(100vh - 60px);
  }
}
</style>
