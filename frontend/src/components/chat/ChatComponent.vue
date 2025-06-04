<script setup>
import {
  reactive,
  ref,
  onMounted,
  toRefs,
  nextTick,
  onUnmounted,
  watch,
  computed,
} from "vue";
import { onClickOutside } from "@vueuse/core";
import { useConfigStore } from "@/stores/config";
import { message } from "ant-design-vue";
import ChatHeader from "./ChatHeader.vue";
import ChatMessages from "./ChatMessages.vue";
import ChatInput from "./ChatInput.vue";

const props = defineProps({
  conversation: Object,
  sidebarState: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["rename-title", "newconv"]);
const configStore = useConfigStore();

const { conversation, sidebarState } = toRefs(props);
const chatContainer = ref(null);

const isStreaming = ref(false);
const userIsScrolling = ref(false);
const shouldAutoScroll = ref(true);

const panel = ref(null);
const modelCard = ref(null);
const examples = ref([
  "Write a simple bubble sort",
  "What's the weather like in Vietnam today?",
  "Introduce The Great Gatsby",
  "What day is today?",
]);

const opts = reactive({
  showPanel: false,
  showModelCard: false,
  openDetail: false,
  databases: [],
});

const meta = reactive(
  JSON.parse(localStorage.getItem("meta")) || {
    use_graph: false,
    use_web: false,
    graph_name: "neo4j",
    selectedKB: null,
    summary_title: false,
    history_round: 20,
    db_id: null,
    fontSize: "default",
    wideScreen: false,
  }
);

const consoleMsg = (msg) => console.log(msg);
onClickOutside(panel, () => setTimeout(() => (opts.showPanel = false), 30));
onClickOutside(modelCard, () => setTimeout(() => (opts.showModelCard = false), 30));

const getHistory = () => {
  const history = conversation.value.messages
    .map((msg) => {
      if (msg.content) {
        return {
          role: msg.role === "sent" ? "user" : "assistant",
          content: msg.content,
        };
      }
    })
    .reduce((acc, cur) => {
      if (cur) {
        acc.push(cur);
      }
      return acc;
    }, []);
  return history.slice(-meta.history_round);
};

const useDatabase = (index) => {
  const selected = opts.databases[index];
  console.log(selected);
  if (index != null && configStore.config.embed_model != selected.embed_model) {
    console.log(selected.embed_model, configStore.config.embed_model);
    message.error(
      `The vector model of the selected knowledge base (${selected.embed_model}) does not match the current vector model (${configStore.config.embed_model}), please select again`
    );
  } else {
    meta.selectedKB = index;
  }
};

const handleKeyDown = (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  } else if (e.key === "Enter" && e.shiftKey) {
    // Insert a newline character at the current cursor position
    const textarea = e.target;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    conversation.value.inputText = `${conversation.value.inputText.substring(
      0,
      start
    )}\n${conversation.value.inputText.substring(end)}`;
    nextTick(() => {
      textarea.setSelectionRange(start + 1, start + 1);
    });
  }
};

const renameTitle = () => {
  if (meta.summary_title) {
    const prompt =
      "Please give a short sentence about the theme of the following conversation, without punctuation:";
    const firstUserMessage = conversation.value.messages[0].content;
    const firstAiMessage = conversation.value.messages[1].content;
    const context = `${prompt}\n\nquestion: ${firstUserMessage}\n\nanswer: ${firstAiMessage}，theme: (one sentence)`;
    simpleCall(context).then((data) => {
      const response = data.response
        .split("：")[0]
        .replace(/^["'"']/g, "")
        .replace(/["'"']$/g, "");
      emit("rename-title", response);
    });
  } else {
    emit("rename-title", conversation.value.messages[0].content);
  }
};

const handleUserScroll = () => {
  // calculate if we are near the bottom (100 pixels)
  const isNearBottom =
    chatContainer.value.scrollHeight -
      chatContainer.value.scrollTop -
      chatContainer.value.clientHeight <
    20;

  // if the user is not at the bottom, then only mark it as user scrolling
  userIsScrolling.value = !isNearBottom;

  // if the user scrolls to the bottom again, then restore auto scrolling
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

const generateRandomHash = (length) => {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let hash = "";
  for (let i = 0; i < length; i++) {
    hash += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return hash;
};

const appendUserMessage = (msg) => {
  conversation.value.messages.push({
    id: generateRandomHash(16),
    role: "sent",
    content: msg,
  });
  scrollToBottom();
};

const appendAiMessage = (content, refs = null) => {
  conversation.value.messages.push({
    id: generateRandomHash(16),
    role: "received",
    content,
    reasoning_content: "",
    refs,
    status: "init",
    meta: {},
    showThinking: "show",
  });
  scrollToBottom();
};

const updateMessage = (info) => {
  const msg = conversation.value.messages.find((msg) => msg.id === info.id);
  if (msg) {
    try {
      // special handling: content needs to be appended rather than replaced
      if (info.content != null && info.content !== "") {
        msg.content += info.content;
      }

      // batch processing other properties, only update when the property value is not null/undefined and is not an empty string
      const propertiesToUpdate = [
        "reasoning_content",
        "model_name",
        "status",
        "message",
        "showThinking",
        "refs",
        "meta",
      ];

      propertiesToUpdate.forEach((prop) => {
        if (info[prop] != null && (typeof info[prop] !== "string" || info[prop] !== "")) {
          msg[prop] = info[prop];
        }
      });

      scrollToBottom();
    } catch (error) {
      console.error("Error updating message:", error);
      msg.status = "error";
      msg.content = "Message update failed";
    }
  } else {
    console.error("Message not found:", info.id);
  }
};

const groupRefs = (id) => {
  const msg = conversation.value.messages.find((msg) => msg.id === id);
  if (msg.refs && msg.refs.knowledge_base.results.length > 0) {
    msg.groupedResults = msg.refs.knowledge_base.results
      .filter((result) => result.file && result.file.filename)
      .reduce((acc, result) => {
        const { filename } = result.file;
        if (!acc[filename]) {
          acc[filename] = [];
        }
        acc[filename].push(result);
        return acc;
      }, {});
  }
  scrollToBottom();
};

const simpleCall = (msg) => {
  return new Promise((resolve, reject) => {
    fetch("/api/chat/call", {
      method: "POST",
      body: JSON.stringify({ query: msg }),
      headers: { "Content-Type": "application/json" },
    })
      .then((response) => response.json())
      .then((data) => resolve(data))
      .catch((error) => reject(error));
  });
};

const loadDatabases = () => {
  fetch("/api/data/", { method: "GET" })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      opts.databases = data.databases;
    });
};

// new function for handling fetch request
const fetchChatResponse = (user_input, cur_res_id) => {
  const controller = new AbortController();
  const signal = controller.signal;

  const params = {
    query: user_input,
    history: getHistory().slice(0, -1), // remove the last user message just added
    meta,
    cur_res_id,
  };
  console.log(params);

  fetch("/api/chat/", {
    method: "POST",
    body: JSON.stringify(params),
    headers: {
      "Content-Type": "application/json",
    },
    signal, // add signal for interrupting request
  })
    .then((response) => {
      if (!response.body) throw new Error("ReadableStream not supported.");
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      const readChunk = () => {
        return reader.read().then(({ done, value }) => {
          if (done) {
            const msg = conversation.value.messages.find((msg) => msg.id === cur_res_id);
            console.log(msg);
            groupRefs(cur_res_id);
            updateMessage({ showThinking: "no", id: cur_res_id });
            isStreaming.value = false;
            if (conversation.value.messages.length === 2) {
              renameTitle();
            }
            return;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");

          // process all complete lines except the last line
          for (let i = 0; i < lines.length - 1; i++) {
            const line = lines[i].trim();
            if (line) {
              try {
                const data = JSON.parse(line);
                updateMessage({
                  id: cur_res_id,
                  content: data.response,
                  reasoning_content: data.reasoning_content,
                  status: data.status,
                  meta: data.meta,
                  ...data,
                });
                if (data.history) {
                  conversation.value.history = data.history;
                }
              } catch (e) {
                console.error("JSON parse error:", e, line);
              }
            }
          }

          // keep the last possibly incomplete line
          buffer = lines[lines.length - 1];

          return readChunk(); // continue reading
        });
      };
      readChunk();
    })
    .catch((error) => {
      if (error.name === "AbortError") {
        console.log("Fetch aborted");
      } else {
        console.error(error);
        updateMessage({
          id: cur_res_id,
          status: "error",
        });
      }
      isStreaming.value = false;
    });

  // watch isStreaming change, when it is false, interrupt the request
  watch(isStreaming, (newValue) => {
    if (!newValue) {
      controller.abort();
    }
  });
};

// updated sendMessage function
const sendMessage = () => {
  const user_input = conversation.value.inputText.trim();
  const dbID = opts.databases.length > 0 ? opts.databases[meta.selectedKB]?.db_id : null;
  if (isStreaming.value) {
    message.error("Please wait for the previous message to be processed");
    return;
  }
  if (user_input) {
    isStreaming.value = true;
    appendUserMessage(user_input);
    appendAiMessage("", null);
    forceScrollToBottom();

    const cur_res_id =
      conversation.value.messages[conversation.value.messages.length - 1].id;
    conversation.value.inputText = "";
    meta.db_id = dbID;
    fetchChatResponse(user_input, cur_res_id);
  } else {
    console.log("Please input a message");
  }
};

const retryMessage = (id) => {
  // find the message corresponding to id, then delete the message and all subsequent messages
  const index = conversation.value.messages.findIndex((msg) => msg.id === id);
  const pastMessage = conversation.value.messages[index - 1];
  console.log("retryMessage", id, pastMessage);
  conversation.value.inputText = pastMessage.content;
  if (index !== -1) {
    conversation.value.messages = conversation.value.messages.slice(0, index - 1);
  }
  console.log(conversation.value.messages);
  sendMessage();
};

// load data from local storage
onMounted(() => {
  scrollToBottom();
  loadDatabases();

  chatContainer.value.addEventListener("scroll", handleUserScroll);

  // check if there is a message with empty content in the existing messages
  if (conversation.value.messages && conversation.value.messages.length > 0) {
    conversation.value.messages.forEach((msg) => {
      if (msg.role === "received" && (!msg.content || msg.content.trim() === "")) {
        msg.status = "error";
        msg.message = "Content loading failed";
      }
    });
  }

  // load data from local storage
  const storedMeta = localStorage.getItem("meta");
  if (storedMeta) {
    const parsedMeta = JSON.parse(storedMeta);
    Object.assign(meta, parsedMeta);
  }
});

onUnmounted(() => {
  if (chatContainer.value) {
    chatContainer.value.removeEventListener("scroll", handleUserScroll);
  }
});

// add new function to handle specific scrolling behavior
const forceScrollToBottom = () => {
  shouldAutoScroll.value = true;
  setTimeout(() => {
    chatContainer.value.scrollTop =
      chatContainer.value.scrollHeight - chatContainer.value.clientHeight;
  }, 10);
};

// watch meta object change, and save to local storage
watch(
  () => meta,
  (newMeta) => {
    localStorage.setItem("meta", JSON.stringify(newMeta));
  },
  { deep: true }
);

// handle sending or stopping
const handleSendOrStop = () => {
  if (isStreaming.value) {
    // stop generating
    isStreaming.value = false;
    const lastMessage =
      conversation.value.messages[conversation.value.messages.length - 1];
    if (lastMessage) {
      lastMessage.isStoppedByUser = true;
      lastMessage.status = "stopped";
    }
  } else {
    // send message
    sendMessage();
  }
};

// retry stopped message
const retryStoppedMessage = (id) => {
  // find the user's original question
  const messageIndex = conversation.value.messages.findIndex((msg) => msg.id === id);
  if (messageIndex > 0) {
    const userMessage = conversation.value.messages[messageIndex - 1];
    if (userMessage && userMessage.role === "sent") {
      conversation.value.inputText = userMessage.content;
      // delete the stopped message and all subsequent messages
      conversation.value.messages = conversation.value.messages.slice(
        0,
        messageIndex - 1
      );
      // sendMessage();
    }
  }
};

const modelNames = computed(() => configStore.config?.model_names);
const modelStatus = computed(() => configStore.config?.model_provider_status);
const customModels = computed(() => configStore.config?.custom_models || []);

// filter the keys in modelStatus that are true
const modelKeys = computed(() => {
  return Object.keys(modelStatus.value || {}).filter((key) => modelStatus.value?.[key]);
});

// method for selecting model
const selectModel = (provider, name) => {
  configStore.setConfigValue("provider", provider);
  configStore.setConfigValue("model", name);
};
console.log(sidebarState.value);
</script>

<template>
  <div class="chat" ref="chatContainer">
    <ChatHeader
      :meta="meta"
      :sidebar-state="sidebarState"
      :model-config="configStore.config"
      @toggle-sidebar="sidebarState.isOpen = true"
      @new-conversation="$emit('newconv')"
      @update-meta="(updates) => Object.assign(meta, updates)"
      @select-model="
        ({ provider, name }) => {
          configStore.setConfigValue('provider', provider);
          configStore.setConfigValue('model', name);
        }
      "
    />

    <ChatMessages
      :messages="conversation.messages"
      :is-streaming="isStreaming"
      :meta="meta"
      :examples="examples"
      @retry-message="retryMessage"
      @retry-stopped-message="retryStoppedMessage"
      @select-example="(exp) => (conversation.inputText = exp)"
    />

    <ChatInput
      :model-value="conversation.inputText"
      @update:model-value="conversation.inputText = $event"
      :is-streaming="isStreaming"
      :meta="meta"
      :databases="opts.databases"
      :config="configStore.config"
      @send-message="sendMessage"
      @stop-streaming="isStreaming = false"
      @update-meta="(updates) => Object.assign(meta, updates)"
      @use-database="useDatabase"
    />
  </div>
</template>

<style lang="less" scoped>
.chat {
  position: relative;
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
}

@media (max-width: 520px) {
  .chat {
    height: calc(100vh - 60px);
  }
}
</style>
