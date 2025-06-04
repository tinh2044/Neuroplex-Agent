<script setup>
import { ref, onMounted, watch, nextTick, computed } from "vue";
import { message } from "ant-design-vue";
import MessageInputComponent from "@/components/MessageInputComponent.vue";
import MessageComponent from "@/components/MessageComponent.vue";

const props = defineProps({
  agentId: {
    type: String,
    default: null,
  },
  config: {
    type: Object,
    default: () => ({}),
  },
  state: {
    type: Object,
    default: () => ({}),
  },
});

const state = ref(props.state);
const waitingServerResponse = ref(false);
const showMsgRefs = (msg) => {
  if (msg.isLast) {
    return ["copy", "regenerate"];
  }
  return false;
};

const messagesContainer = ref(null);

const agents = ref({});
const currentAgent = ref(null);
const userInput = ref("");
const messages = ref([]);
const isProcessing = ref(false);

const toolCalls = ref([]);
const currentToolCallId = ref(null);
const currentRunId = ref(null);
const messageStepMap = ref({});
const expandedToolCalls = ref(new Set());

const scrollToBottom = async () => {
  await nextTick();
  if (!messagesContainer.value) return;

  const containerBox = messagesContainer.value;
  const container = document.querySelector(".chat");
  if (!container) return;

  const scrollOptions = { top: container.scrollHeight, behavior: "smooth" };

  container.scrollTo(scrollOptions);
  setTimeout(() => container.scrollTo(scrollOptions), 50);
  setTimeout(() => container.scrollTo(scrollOptions), 150);
  setTimeout(
    () => container.scrollTo({ top: container.scrollHeight, behavior: "auto" }),
    300
  );
};

const messageMap = ref(new Map());
const toolCallMap = ref(new Map());

const resetStatusSteps = () => {
  toolCalls.value = [];
  currentToolCallId.value = null;
  currentRunId.value = null;
  messageStepMap.value = {};
  messageMap.value.clear();
  toolCallMap.value.clear();
};

const resetThread = () => {
  messages.value = [];
  resetStatusSteps();
  saveState();
};

const prepareMessageHistory = (msgs) => {
  const toolCallsByRunAndStep = {};
  const toolResultsByRunAndStep = {};

  msgs
    .filter((msg) => msg.role === "tool_call")
    .forEach((msg) => {
      const runId = msg.tool?.run_id || "unknown";
      const step = msg.tool?.step !== undefined ? msg.tool.step : -1;
      const key = `${runId}:${step}`;
      toolCallsByRunAndStep[key] = msg;
    });

  msgs
    .filter((msg) => msg.role === "tool")
    .forEach((msg) => {
      const runId = msg.tool?.run_id || "unknown";
      const step =
        msg.tool?.tool_call_step !== undefined
          ? msg.tool.tool_call_step
          : msg.tool?.step !== undefined
          ? msg.tool.step - 1
          : -1;
      const key = `${runId}:${step}`;
      toolResultsByRunAndStep[key] = msg;
    });

  const validToolCallKeys = new Set();

  for (const key in toolCallsByRunAndStep) {
    if (
      toolResultsByRunAndStep[
        `${key.split(":")[0]}:${parseInt(key.split(":")[1]) + 1}`
      ] ||
      toolResultsByRunAndStep[key.replace(/:\d+$/, ":result")]
    ) {
      validToolCallKeys.add(key);
    }
  }

  return msgs.filter((msg) => {
    if (msg.role === "user" || msg.role === "assistant") return true;

    if (msg.role === "tool_call") {
      const runId = msg.tool?.run_id || "unknown";
      const step = msg.tool?.step !== undefined ? msg.tool.step : -1;
      const key = `${runId}:${step}`;
      return validToolCallKeys.has(key);
    }

    if (msg.role === "tool") {
      const runId = msg.tool?.run_id || "unknown";
      const callStep =
        msg.tool?.tool_call_step !== undefined
          ? msg.tool.tool_call_step
          : msg.tool?.step !== undefined
          ? msg.tool.step - 1
          : -1;
      const key = `${runId}:${callStep}`;
      return validToolCallKeys.has(key);
    }

    return false;
  });
};

const handleKeyDown = (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (userInput.value.trim() && currentAgent.value && !isProcessing.value) {
      const tempUserInput = userInput.value;
      userInput.value = "";
      setTimeout(() => {
        sendMessageWithText(tempUserInput);
      }, 0);
    }
  }
};

const sendMessage = () => {
  if (!userInput.value || !currentAgent.value || isProcessing.value) return;
  const tempUserInput = userInput.value;
  userInput.value = "";
  nextTick(() => {
    sendMessageWithText(tempUserInput);
  });
};

const retryMessage = (message) => {
  const requestId = message.request_id;
  const sendMessage = messages.value.find((msg) => msg.id === requestId);
  const sendMessageIndex = messages.value.indexOf(sendMessage);

  messages.value = messages.value.slice(0, sendMessageIndex);

  sendMessageWithText(sendMessage.content);
};

const sendMessageWithText = async (text) => {
  if (!text || !currentAgent.value || isProcessing.value) return;

  resetStatusSteps();

  const userMessage = text.trim();
  const requestId = `${currentAgent.value.name}-${new Date().getTime()}`;

  messages.value.push({
    role: "user",
    content: userMessage,
    id: requestId,
  });

  isProcessing.value = true;
  await scrollToBottom();

  try {
    const history = messages.value
      .filter((msg) => msg.role !== "assistant" || msg.status !== "loading")
      .filter((msg) => msg.role !== "tool_call" && msg.role !== "tool")
      .map((msg) => ({
        role: msg.role === "user" || msg.role === "assistant" ? msg.role : "assistant",
        content: msg.content,
      }));

    waitingServerResponse.value = true;
    const requestData = {
      query: userMessage,
      history: history.slice(0, -1),
      config: {
        ...props.config,
      },
      meta: {
        request_id: requestId,
      },
    };

    const response = await fetch(`/api/chat/agent/${currentAgent.value.name}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      throw new Error("Request failed");
    }

    await handleStreamResponse(response);
  } catch (error) {
    console.error("Send message error:", error);
    const loadingMsgIndex = messages.value.length - 1;
    if (loadingMsgIndex >= 0) {
      messages.value[loadingMsgIndex] = {
        role: "assistant",
        content: `An error occurred: ${error.message}`,
        status: "error",
      };
    }
  } finally {
    waitingServerResponse.value = false;
    isProcessing.value = false;
    await scrollToBottom();
  }
};

const handleStreamResponse = async (response) => {
  try {
    await scrollToBottom();

    if ("TransformStream" in window && "ReadableStream" in window) {
      const jsonStream = new TransformStream({
        start(controller) {
          this.buffer = "";
          this.decoder = new TextDecoder();
        },
        transform(chunk, controller) {
          this.buffer += this.decoder.decode(chunk, { stream: true });

          let position;
          while ((position = this.buffer.indexOf("\n")) !== -1) {
            const line = this.buffer.substring(0, position).trim();
            this.buffer = this.buffer.substring(position + 1);

            if (line) {
              try {
                controller.enqueue(JSON.parse(line));
              } catch (e) {}
            }
          }
        },
        flush(controller) {
          if (this.buffer.trim()) {
            try {
              controller.enqueue(JSON.parse(this.buffer.trim()));
            } catch (e) {
              console.warn("Final buffer content cannot be parsed:", this.buffer);
            }
          }
        },
      });

      const transformedStream = response.body.pipeThrough(jsonStream);
      const reader = transformedStream.getReader();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        if (value) {
          if (value.debug_mode) {
            console.log("debug_mode", value);
          }

          if (value.status === "init") {
            await handleInit(value);
          } else if (value.status === "finished") {
            await handleFinished(value);
          } else if (value.status === "error") {
            await handleError(value);
          } else {
            await handleMessageById(value);
          }

          await scrollToBottom();
        }
      }
    } else {
      const reader = response.body.getReader();
      let buffer = "";
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data = JSON.parse(line.trim());

              if (data.debug_mode) {
                console.log("debug_mode", data);
              }

              if (data.status === "init") {
                await handleInit(data);
              } else if (data.status === "finished") {
                await handleFinished(data);
              } else {
                await handleMessageById(data);
              }
            } catch (e) {
              console.debug("Error parsing JSON:", e.message);
            }
          }
        }

        await scrollToBottom();
      }

      if (buffer.trim()) {
        try {
          const data = JSON.parse(buffer.trim());
          if (data.status === "init") {
            await handleInit(data);
          } else if (data.status === "finished") {
            await handleFinished(data);
          } else {
            await handleMessageById(data);
          }
        } catch (e) {
          console.warn("Final buffer content cannot be parsed:", buffer);
        }
      }
    }
  } catch (error) {
    console.error("Stream processing error:", error);
    const lastMsg = messages.value[messages.value.length - 1];
    if (lastMsg.role === "assistant") {
      lastMsg.status = "error";
      lastMsg.message = error.message;
    } else {
      messages.value.push({
        role: "assistant",
        message: `An error occurred: ${error.message}`,
        status: "error",
      });
      await scrollToBottom();
    }
    isProcessing.value = false;
  }
};

const handleInit = async (data) => {
  waitingServerResponse.value = false;
  console.log("handleInit", data);
  const initMsg = {
    role: "assistant",
    content: "",
    status: "init",
    toolCalls: {},
    toolCallIds: {},
    request_id: data.request_id,
  };
  messages.value.push(initMsg);
  await scrollToBottom();
};

const handleFinished = async (data) => {
  const lastAssistantMsg = messages.value[messages.value.length - 1];
  if (lastAssistantMsg) {
    if (
      (!lastAssistantMsg.content || lastAssistantMsg.content.trim().length === 0) &&
      (!lastAssistantMsg.toolCalls ||
        Object.keys(lastAssistantMsg.toolCalls).length === 0)
    ) {
      lastAssistantMsg.content = "已完成";
    }
    lastAssistantMsg.status = "finished";
    lastAssistantMsg.isLast = true;
    lastAssistantMsg.meta = data.meta;
  }

  isProcessing.value = false;
  await scrollToBottom();
};

const handleMessageById = async (data) => {
  const msgId = data.msg.id;
  const msgType = data.msg.type;

  const existingMsgIndex = messageMap.value.get(msgId);

  if (existingMsgIndex === undefined) {
    if (msgType === "tool") {
      await appendToolMessageToExistingAssistant(data);
    } else {
      const loadingAssistantIndex = messages.value.findIndex(
        (m) => m.role === "assistant" && m.status === "init"
      );
      if (loadingAssistantIndex !== -1) {
        messages.value[loadingAssistantIndex].id = msgId;
        messageMap.value.set(msgId, loadingAssistantIndex);
        console.log("更新现有助手消息", messages.value[loadingAssistantIndex]);
        await updateExistingMessage(data, loadingAssistantIndex);
      } else {
        await createAssistantMessage(data);
      }
    }
  } else {
    await updateExistingMessage(data, existingMsgIndex);
  }
};

const createAssistantMessage = async (data) => {
  const msgId = data.msg.id;
  const msgContent = data.response || "";
  const runId = data.metadata?.run_id;
  const step = data.metadata?.langgraph_step;
  const requestId = data.metadata?.request_id || data.request_id;

  let currentMsg = null;
  const lastMsg = messages.value[messages.value.length - 1];
  const lastMsgIsInit =
    lastMsg.role === "assistant" &&
    lastMsg.status === "init" &&
    lastMsg.request_id === requestId &&
    !lastMsg.id;

  if (lastMsgIsInit) {
    currentMsg = lastMsg;
  } else {
    currentMsg = {
      role: "assistant",
      status: "init",
      toolCalls: {},
      toolCallIds: {},
      request_id: requestId,
    };
    messages.value.push(currentMsg);
  }

  currentMsg.id = msgId;
  currentMsg.content = msgContent;
  currentMsg.run_id = runId;
  currentMsg.step = step;

  const toolCalls = data.msg.additional_kwargs?.tool_calls;
  if (toolCalls && toolCalls.length > 0) {
    for (const toolCall of toolCalls) {
      const toolCallId = toolCall.id;
      const toolIndex = toolCall.index || 0;
      currentMsg.toolCallIds[toolCallId] = toolIndex;
      currentMsg.toolCalls[toolIndex] = toolCall;
      toolCallMap.value.set(toolCallId, msgId);
    }
  }

  const newIndex = messages.value.length - 1;
  messageMap.value.set(msgId, newIndex);

  await scrollToBottom();
};

const updateExistingMessage = async (data, existingMsgIndex) => {
  const msgInstance = messages.value[existingMsgIndex];

  if (msgInstance.status === "init") {
    msgInstance.status = data.status || "loading";
    msgInstance.run_id = data.metadata?.run_id;
    msgInstance.step = data.metadata?.langgraph_step;
  }

  if (data.response) {
    msgInstance.content = msgInstance.content || "";
    msgInstance.content += data.response;
  }

  const toolCalls = data.msg.additional_kwargs?.tool_calls;
  if (toolCalls && toolCalls.length > 0) {
    for (const toolCall of toolCalls) {
      const toolIndex = toolCall.index || 0;

      const newToolCalls = { ...msgInstance.toolCalls };
      const newToolCallIds = { ...msgInstance.toolCallIds };
      if (!newToolCalls[toolIndex]) {
        newToolCalls[toolIndex] = toolCall;
        newToolCallIds[toolCall.id] = toolIndex;
      } else {
        newToolCalls[toolIndex]["function"]["arguments"] += toolCall.function.arguments;
      }
      msgInstance.toolCalls = newToolCalls;
      msgInstance.toolCallIds = newToolCallIds;

      toolCallMap.value.set(toolCall.id, msgInstance.id);
    }
  }

  if (data.status === "error") {
    msgInstance.status = "error";
    msgInstance.message = data.message;
  }

  await nextTick();
  await scrollToBottom();
};

const handleError = async (data) => {
  const lastMsg = messages.value[messages.value.length - 1];
  if (lastMsg) {
    lastMsg.status = "error";
    lastMsg.message = data.message;
  }
  isProcessing.value = false;
};

const appendToolMessageToExistingAssistant = async (data) => {
  currentToolCallId.value = data.msg.tool_call_id;
  const assignedMsgId = toolCallMap.value.get(currentToolCallId.value);
  if (assignedMsgId === undefined) {
    return;
  }

  const msgIndex = messageMap.value.get(assignedMsgId);
  if (msgIndex === undefined) {
    return;
  }

  const msgInstance = messages.value[msgIndex];
  const toolCallIndex = msgInstance.toolCallIds[currentToolCallId.value];
  if (toolCallIndex === undefined) {
    return;
  }

  msgInstance.toolCalls[toolCallIndex].toolResultMsg = data.msg;
  msgInstance.toolCalls[toolCallIndex].toolResultMetadata = data.metadata;
  await scrollToBottom();
};

const fetchAgents = async () => {
  try {
    const response = await fetch("/api/chat/agent");
    if (response.ok) {
      const data = await response.json();
      agents.value = data.agents.reduce((acc, agent) => {
        acc[agent.name] = agent;
        return acc;
      }, {});
      console.log("agents", agents.value);
    } else {
      console.error("Failed to get agents");
    }
  } catch (error) {
    console.error("Error getting agents:", error);
  }
};

watch(
  messages,
  () => {
    scrollToBottom();
  },
  { deep: true }
);

onMounted(async () => {
  try {
    await fetchAgents();

    setTimeout(async () => {
      await loadAgentData();
    }, 10);
  } catch (error) {
    console.error("Component mounting error:", error);
  }
});

const toggleToolCall = (toolCallId) => {
  if (expandedToolCalls.value.has(toolCallId)) {
    expandedToolCalls.value.delete(toolCallId);
  } else {
    expandedToolCalls.value.add(toolCallId);
  }
};

const loadAgentData = async () => {
  try {
    if (Object.keys(agents.value).length === 0) {
      await fetchAgents();
    }

    if (props.agentId && agents.value && agents.value[props.agentId]) {
      currentAgent.value = agents.value[props.agentId];
    } else if (!props.agentId) {
      const storagePrefix = "agent-multi";
      const savedAgent = localStorage.getItem(`${storagePrefix}-current-agent`);
      if (savedAgent && agents.value && agents.value[savedAgent]) {
        currentAgent.value = agents.value[savedAgent];
      }
    }

    loadState();

    if (messages.value && messages.value.length > 0) {
      messages.value = prepareMessageHistory(messages.value);
    }
  } catch (error) {
    console.error("Error loading agent data:", error);
  }
};

const loadState = () => {
  try {
    const storagePrefix = props.agentId ? `agent-${props.agentId}` : "agent-multi";

    if (!storagePrefix) {
      console.error("Unable to determine storage prefix, agent_id missing");
      return;
    }

    const savedMessages = localStorage.getItem(`${storagePrefix}-messages`);
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        if (Array.isArray(parsedMessages)) {
          messages.value = parsedMessages;
        }
      } catch (e) {
        console.error("Error parsing message history:", e);
      }
    }

    const savedThreadId = localStorage.getItem(`${storagePrefix}-thread-id`);
    if (savedThreadId) {
      currentRunId.value = savedThreadId;
    }
  } catch (error) {
    console.error("Error loading state from localStorage:", error);
  }
};

watch(
  () => props.agentId,
  async (newAgentId, oldAgentId) => {
    try {
      if (newAgentId !== oldAgentId) {
        messages.value = [];
        currentRunId.value = null;
        resetStatusSteps();
        await loadAgentData();
      }
    } catch (error) {
      console.error("Error handling agent ID change:", error);
    }
  },
  { immediate: true }
);

const saveState = () => {
  try {
    if (!currentAgent.value) {
      console.warn("No agent selected, skipping save");
      return;
    }

    const prefix = props.agentId ? `agent-${props.agentId}` : "agent-multi";
    if (!props.agentId && currentAgent.value) {
      localStorage.setItem(`${prefix}-current-agent`, currentAgent.value.name);
    }

    if (messages.value && messages.value.length > 0) {
      localStorage.setItem(`${prefix}-messages`, JSON.stringify(messages.value));
    } else {
      localStorage.removeItem(`${prefix}-messages`);
    }

    if (currentRunId.value) {
      localStorage.setItem(`${prefix}-thread-id`, currentRunId.value);
    } else {
      localStorage.removeItem(`${prefix}-thread-id`);
    }
  } catch (error) {
    console.error("Error saving state to localStorage:", error);
  }
};

const sayHi = () => {
  message.success(
    `Hi, I am ${currentAgent.value.name}, ${currentAgent.value.description}`
  );
};

watch(
  [currentAgent, messages, currentRunId],
  () => {
    try {
      saveState();
    } catch (error) {
      console.error("Error saving state:", error);
    }
  },
  { deep: true }
);
</script>

<template>
  <div class="chat-container">
    <div class="chat">
      <div class="chat-header">
        <div class="header__left">
          <slot name="header-left" class="nav-btn" />
          <div class="newchat nav-btn" @click="resetThread" :disabled="isProcessing">
            <PlusCircleOutlined /> <span class="text">New Conversation</span>
          </div>
        </div>
        <div class="header__center">
          <slot name="header-center" />
        </div>
        <div class="header__right">
          <div class="current-agent nav-btn" @click="sayHi">
            <RobotOutlined />&nbsp;
            <span v-if="currentAgent">{{ currentAgent.name }}</span>
            <span v-else>Loading...</span>
          </div>
          <slot name="header-right" />
        </div>
      </div>

      <div v-if="messages.length === 0" class="chat-examples">
        <h1>
          {{
            currentAgent
              ? currentAgent.name
              : "Please select an agent to start a conversation"
          }}
        </h1>
        <p>
          {{
            currentAgent
              ? currentAgent.description
              : "Different agents have different specialties and capabilities"
          }}
        </p>
      </div>

      <div
        class="chat-box"
        ref="messagesContainer"
        :class="{ 'is-debug': state.debug_mode }"
      >
        <MessageComponent
          v-for="(message, index) in messages"
          :message="message"
          :key="index"
          :is-processing="isProcessing"
          :debug-mode="state.debug_mode"
          :show-refs="showMsgRefs(message)"
          @retry="retryMessage(message)"
        >
          <div v-if="state.debug_mode" class="status-info">{{ message }}</div>

          <template #tool-calls>
            <div
              v-if="message.toolCalls && Object.keys(message.toolCalls).length > 0"
              class="tool-calls-container"
            >
              <div
                v-for="(toolCall, index) in message.toolCalls || {}"
                :key="index"
                class="tool-call-container"
              >
                <div
                  v-if="toolCall"
                  class="tool-call-display"
                  :class="{ 'is-collapsed': !expandedToolCalls.has(toolCall.id) }"
                >
                  <div class="tool-header" @click="toggleToolCall(toolCall.id)">
                    <span v-if="!toolCall.toolResultMsg">
                      <LoadingOutlined /> &nbsp;
                      <span>Calling tool: </span>
                      <span class="tool-name">{{ toolCall.function.name }}</span>
                    </span>
                    <span v-else>
                      <ThunderboltOutlined /> Tool
                      <span class="tool-name">{{ toolCall.function.name }}</span>
                      completed
                    </span>
                  </div>
                  <div class="tool-content" v-show="expandedToolCalls.has(toolCall.id)">
                    <div
                      class="tool-params"
                      v-if="toolCall.function && toolCall.function.arguments"
                    >
                      <div class="tool-params-header">Parameters:</div>
                      <div class="tool-params-content">
                        <pre>{{ toolCall.function.arguments }}</pre>
                      </div>
                    </div>
                    <div
                      class="tool-params"
                      v-if="toolCall.toolResultMsg && toolCall.toolResultMsg.content"
                    >
                      <div class="tool-params-header">Execution result</div>
                      <div class="tool-params-content">
                        {{ toolCall.toolResultMsg.content }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </MessageComponent>
      </div>

      <div class="bottom">
        <div class="message-input-wrapper">
          <MessageInputComponent
            v-model="userInput"
            :is-loading="isProcessing"
            :disabled="!currentAgent || isProcessing"
            :send-button-disabled="!userInput || !currentAgent || isProcessing"
            :placeholder="'Enter your question...'"
            @send="sendMessage"
            @keydown="handleKeyDown"
          />
          <div class="bottom-actions">
            <p class="note">Please verify the reliability of the content</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="less" scoped>
@import "@/assets/main.css";

.chat-container {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
  min-height: 100vh;
}

.chat {
  position: relative;
  flex: 1;
  max-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  background: white;
  position: relative;
  box-sizing: border-box;
  overflow-y: scroll;

  .chat-header {
    user-select: none;
    position: sticky;
    top: 0;
    z-index: 10;
    background-color: white;
    height: var(--header-height);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--main-light-3);

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
    font-size: 15px;
    width: auto;
    padding: 0.5rem 1rem;
    transition: background-color 0.3s;

    .text {
      margin-left: 10px;
    }

    &:hover {
      background-color: var(--main-light-3);
    }

    .nav-btn-icon {
      width: 1.5rem;
      height: 1.5rem;
    }
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
    color: var(--gray-900);
  }

  p {
    color: var(--gray-700);
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

  .tool-calls-container {
    width: 100%;
    margin-top: 10px;

    .tool-call-container {
      margin-bottom: 10px;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

.chat-box.is-debug {
  .message-box .assistant-message {
    outline: 1px solid red;
    outline-offset: 10px;
    outline-style: dashed;

    .status-info {
      display: block;
      background-color: var(--gray-50);
      color: var(--gray-700);
      padding: 10px;
      border-radius: 8px;
      margin-bottom: 10px;
    }
  }
}

.bottom {
  position: sticky;
  bottom: 0;
  width: 100%;
  margin: 0 auto;
  padding: 4px 2rem 0 2rem;
  background: white;

  .message-input-wrapper {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;

    .bottom-actions {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .note {
      font-size: small;
      color: #ccc;
      margin: 4px 0;
      user-select: none;
    }
  }
}

.conversation-list::-webkit-scrollbar {
  position: absolute;
  width: 4px;
  height: 4px;
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

.chat::-webkit-scrollbar {
  position: absolute;
  width: 4px;
  height: 4px;
}

.chat::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 4px;
}

.chat::-webkit-scrollbar-thumb {
  background: var(--gray-400);
  border-radius: 4px;
}

.chat::-webkit-scrollbar-thumb:hover {
  background: rgb(100, 100, 100);
  border-radius: 4px;
}

.loading-dots {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.loading-dots div {
  width: 8px;
  height: 8px;
  margin: 0 4px;
  background-color: var(--gray-700);
  border-radius: 50%;
  opacity: 0.3;
  animation: pulse 0.5s infinite ease-in-out both;
}

.loading-dots div:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots div:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes pulse {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes swing-in-top-fwd {
  0% {
    transform: rotateX(-100deg);
    transform-origin: top;
    opacity: 0;
  }
  100% {
    transform: rotateX(0deg);
    transform-origin: top;
    opacity: 1;
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

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (max-width: 520px) {
  .chat-box {
    padding: 1rem 1rem;
  }

  .bottom {
    padding: 0.5rem 0.5rem;
  }

  .chat-header {
    padding: 0.5rem 1rem !important;

    .nav-btn {
      font-size: 14px !important;
      padding: 0.4rem 0.8rem !important;
    }
  }
}
</style>
