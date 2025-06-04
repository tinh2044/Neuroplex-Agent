<script setup>
import { reactive, ref, watch, onMounted, computed } from "vue";
import ChatComponent from "../components/chat/ChatComponent.vue";

// Use consistent localStorage key
const STORAGE_KEY = "chat-conversations";

// Initialize with default conversation to prevent undefined access
const defaultConversation = {
  id: 0,
  title: "New Conversation",
  history: [],
  messages: [],
  inputText: "",
};

const conversations = reactive([defaultConversation]);

const sidebarState = reactive({
  isOpen: JSON.parse(localStorage.getItem("chat-sidebar-open") || "true"),
});

watch(
  () => sidebarState.isOpen,
  (newValue) => {
    localStorage.setItem("chat-sidebar-open", JSON.stringify(newValue));
  }
);

const curConversationId = ref(0);

const currentConversation = computed(() => {
  // Ensure conversations array exists and has at least one item
  if (!conversations || conversations.length === 0) {
    return defaultConversation;
  }

  // Ensure curConversationId is valid
  const validId = Math.max(
    0,
    Math.min(curConversationId.value, conversations.length - 1)
  );
  const conversation = conversations[validId];

  // Double check conversation exists
  if (!conversation) {
    return defaultConversation;
  }

  // Ensure all required properties exist
  return {
    id: conversation.id ?? validId,
    title: conversation.title || "New Conversation",
    history: Array.isArray(conversation.history) ? conversation.history : [],
    messages: Array.isArray(conversation.messages) ? conversation.messages : [],
    inputText: conversation.inputText || "",
  };
});

const generateRandomHash = (length) => {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let hash = "";
  for (let i = 0; i < length; i++) {
    hash += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return hash;
};

const renameTitle = (newTitle) => {
  if (conversations[curConversationId.value]) {
    conversations[curConversationId.value].title = newTitle;
  }
};

const goToConversation = (index) => {
  if (index >= 0 && index < conversations.length) {
    curConversationId.value = index;
    console.log(conversations[curConversationId.value]);
  }
};

const addNewConversation = () => {
  const newConversation = {
    id: generateRandomHash(8),
    title: "New Conversation",
    history: [],
    messages: [],
    inputText: "",
  };

  // Check if first conversation is empty
  if (conversations.length > 0 && conversations[0].messages.length === 0) {
    curConversationId.value = 0;
    return;
  }

  conversations.unshift(newConversation);
  curConversationId.value = 0;
};

const delConversation = (index) => {
  if (index < 0 || index >= conversations.length) {
    return;
  }

  conversations.splice(index, 1);

  if (index < curConversationId.value) {
    curConversationId.value -= 1;
  } else if (index === curConversationId.value) {
    curConversationId.value = 0;
  }

  if (conversations.length === 0) {
    addNewConversation();
  }

  // Ensure curConversationId is valid
  if (curConversationId.value >= conversations.length) {
    curConversationId.value = Math.max(0, conversations.length - 1);
  }
};

// Watch for changes and save to localStorage
watch(
  () => conversations,
  (newStates) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newStates));
  },
  { deep: true }
);

onMounted(() => {
  // Load saved conversations from localStorage
  const savedConversations = JSON.parse(localStorage.getItem(STORAGE_KEY));

  if (
    savedConversations &&
    Array.isArray(savedConversations) &&
    savedConversations.length > 0
  ) {
    // Clear existing conversations
    conversations.splice(0, conversations.length);

    // Add saved conversations with validation
    savedConversations.forEach((conversation, index) => {
      const validatedConv = {
        id: conversation.id ?? index,
        title: conversation.title || "New Conversation",
        history: Array.isArray(conversation.history) ? conversation.history : [],
        messages: Array.isArray(conversation.messages) ? conversation.messages : [],
        inputText: conversation.inputText || "",
      };
      conversations.push(validatedConv);
    });
  }

  // Ensure we have at least one conversation
  if (conversations.length === 0) {
    conversations.push(defaultConversation);
  }

  // Validate and reset curConversationId if needed
  if (curConversationId.value >= conversations.length) {
    curConversationId.value = 0;
  }
});
</script>

<template>
  <div class="chat-container">
    <div class="conversations" :class="{ 'is-open': sidebarState.isOpen }">
      <div class="actions">
        <!-- <div class="action new" @click="addNewConv"><FormOutlined /></div> -->
        <span class="header-title">Neuroplex</span>
        <div class="action close" @click="sidebarState.isOpen = !sidebarState.isOpen">
          <img
            src="@/assets/icons/sidebar_left.svg"
            class="iconfont icon-20"
            alt="Settings"
          />
        </div>
      </div>
      <div class="conversation-list">
        <div
          class="conversation"
          v-for="(state, index) in conversations"
          :key="state.id || index"
          :class="{ active: curConversationId === index }"
          @click="goToConversation(index)"
        >
          <div class="conversation__title">
            <CommentOutlined /> &nbsp;{{ state.title }}
          </div>
          <div class="conversation__delete" @click.stop="delConversation(index)">
            <DeleteOutlined />
          </div>
        </div>
      </div>
    </div>
    <ChatComponent
      v-if="currentConversation && currentConversation.messages"
      :conversation="currentConversation"
      :sidebar-state="sidebarState"
      @rename-title="renameTitle"
      @newconv="addNewConversation"
    />
    <div v-else class="loading-placeholder">Loading...</div>
  </div>
</template>

<style lang="less" scoped>
@import "@/assets/main.css";

.chat-container {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
}

.loading-placeholder {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--gray-600);
}

.conversations {
  width: 230px;
  max-width: 230px;
  border-right: 1px solid var(--main-light-3);
  background-color: var(--bg-sider);
  transition: all 0.3s ease;
  white-space: nowrap;
  /* Prevent text wrapping */
  overflow: hidden;
  /* Ensure content doesn't overflow */

  &.is-open {
    width: 230px;
  }

  &:not(.is-open) {
    width: 0;
    padding: 0;
    overflow: hidden;
  }

  & .actions {
    height: var(--header-height);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    z-index: 9;
    border-bottom: 1px solid var(--main-light-3);

    .header-title {
      font-weight: bold;
      user-select: none;
      white-space: nowrap;
      overflow: hidden;
    }

    .action {
      font-size: 1.2rem;
      width: 2.5rem;
      height: 2.5rem;
      display: flex;
      justify-content: center;
      align-items: center;
      border-radius: 8px;
      color: var(--gray-800);
      cursor: pointer;

      &:hover {
        background-color: var(--main-light-3);
      }

      .nav-btn-icon {
        width: 1.2rem;
        height: 1.2rem;
      }
    }
  }

  .conversation-list {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    max-height: 100%;
  }

  .conversation-list .conversation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    cursor: pointer;
    width: 100%;
    user-select: none;
    transition: background-color 0.2s ease-in-out;

    &__title {
      color: var(--gray-700);
      white-space: nowrap;
      /* Disable line breaks */
      overflow: hidden;
      /* Hide overflow */
      text-overflow: ellipsis;
      /* Show ellipsis */
    }

    &__delete {
      display: none;
      color: var(--gray-500);
      transition: all 0.2s ease-in-out;

      &:hover {
        color: #f93a37;
        background-color: #eee;
      }
    }

    &.active {
      border-right: 3px solid var(--main-500);
      padding-right: 13px;
      background-color: var(--gray-200);

      & .conversation__title {
        color: var(--gray-1000);
      }
    }

    &:not(.active):hover {
      background-color: var(--main-light-3);

      & .conversation__delete {
        display: block;
      }
    }
  }
}

.conversation-list::-webkit-scrollbar {
  position: absolute;
  width: 4px;
}

.conversation-list::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 4px;
}

.conversation-list::-webkit-scrollbar-thumb {
  background: var(--gray-400);
  border-radius: 4px;
}

.conversation-list::-webkit-scrollbar-thumb:hover {
  background: rgb(100, 100, 100);
  border-radius: 4px;
}

.conversation-list::-webkit-scrollbar-thumb:active {
  background: rgb(68, 68, 68);
  border-radius: 4px;
}

@media (max-width: 520px) {
  .conversations {
    position: absolute;
    z-index: 101;
    width: 300px;
    height: 100%;
    border-radius: 0 16px 16px 0;
    box-shadow: 0 0 10px 1px rgba(0, 0, 0, 0.05);

    &:not(.is-open) {
      width: 0;
      padding: 0;
      overflow: hidden;
    }
  }
}
</style>
