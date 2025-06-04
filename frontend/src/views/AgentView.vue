<script setup>
import { ref, onMounted, reactive, watch, computed, h } from "vue";
import { useRouter } from "vue-router";
import {
  RobotOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  CloseOutlined,
  SettingOutlined,
  KeyOutlined,
  LinkOutlined,
} from "@ant-design/icons-vue";
import { message } from "ant-design-vue";
import AgentChatComponent from "@/components/AgentChatComponent.vue";
import TokenManagerComponent from "@/components/TokenManagerComponent.vue";

const router = useRouter();

const agents = ref({});
const selectedAgentId = ref(null);
const availableTools = ref([]);
const state = reactive({
  debug_mode: false,
  isSidebarOpen: JSON.parse(localStorage.getItem("agent-sidebar-open") || "true"),
  isConfigSidebarOpen: false,
  configModalVisible: false,
  tokenModalVisible: false,
  isEmptyConfig: computed(
    () => !selectedAgentId.value || Object.keys(configurableItems.value).length === 0
  ),
});
const configSchema = computed(
  () => agents.value[selectedAgentId.value]?.config_schema || {}
);
const configurableItems = computed(() => configSchema.value.configurable_items || {});

const agentConfig = ref({});

const toggleDebugMode = () => {
  state.debug_mode = !state.debug_mode;
};

const openConfigModal = () => {
  state.configModalVisible = true;
};

const closeConfigModal = () => {
  state.configModalVisible = false;
};

const openTokenModal = () => {
  state.tokenModalVisible = true;
};

const closeTokenModal = () => {
  state.tokenModalVisible = false;
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

      if (selectedAgentId.value) {
        loadAgentConfig();
      }
    } else {
      console.error("Failed to get agents");
    }
  } catch (error) {
    console.error("Failed to get agents:", error);
  }
};

const fetchTools = async () => {
  try {
    const response = await fetch("/api/chat/tools");
    if (response.ok) {
      const data = await response.json();
      availableTools.value = data.tools;
      console.log("Available tools:", availableTools.value);
    } else {
      console.error("Failed to get tools");
    }
  } catch (error) {
    console.error("Failed to get tools:", error);
  }
};

const loadAgentConfig = () => {
  if (!selectedAgentId.value || !agents.value[selectedAgentId.value]) return;

  const agent = agents.value[selectedAgentId.value];
  const schema = agent.config_schema || {};
  const items = schema.configurable_items || {};

  agentConfig.value = {};

  if (schema.system_prompt) {
    agentConfig.value.system_prompt = schema.system_prompt;
  }

  if (schema.model) {
    agentConfig.value.model = schema.model;
  }

  if (schema.tools) {
    agentConfig.value.tools = schema.tools;
  }

  Object.keys(items).forEach((key) => {
    const item = items[key];

    if (typeof item.default === "boolean") {
      agentConfig.value[key] = item.default;
    } else {
      agentConfig.value[key] = item.default || "";
    }
  });

  const savedConfig = JSON.parse(
    localStorage.getItem(`agent-config-${selectedAgentId.value}`) || "{}"
  );

  if (savedConfig) {
    Object.keys(savedConfig).forEach((key) => {
      if (key in agentConfig.value) {
        agentConfig.value[key] = savedConfig[key];
      }
    });
  }
};

const saveConfig = () => {
  localStorage.setItem(
    `agent-config-${selectedAgentId.value}`,
    JSON.stringify(agentConfig.value)
  );

  message.success("Configuration saved");
  console.log("agentConfig.value", agentConfig.value);
  closeConfigModal();
};

const resetConfig = () => {
  localStorage.removeItem(`agent-config-${selectedAgentId.value}`);
  loadAgentConfig();
  message.info("Configuration reset");
};

watch(
  () => state.isSidebarOpen,
  (newValue) => {
    localStorage.setItem("agent-sidebar-open", JSON.stringify(newValue));
  }
);

watch(
  () => selectedAgentId.value,
  () => {
    loadAgentConfig();
  }
);

const toggleSidebar = () => {
  state.isSidebarOpen = !state.isSidebarOpen;
};

const toggleConfigSidebar = (forceOpen) => {
  if (forceOpen !== undefined) {
    state.isConfigSidebarOpen = forceOpen;
  } else {
    state.isConfigSidebarOpen = !state.isConfigSidebarOpen;
  }
};

const selectAgent = (agentId) => {
  selectedAgentId.value = agentId;
  localStorage.setItem("last-selected-agent", agentId);
  loadAgentConfig();
};

onMounted(async () => {
  await fetchAgents();
  await fetchTools();

  const lastSelectedAgent = localStorage.getItem("last-selected-agent");
  if (lastSelectedAgent && agents.value[lastSelectedAgent]) {
    selectedAgentId.value = lastSelectedAgent;
  } else if (Object.keys(agents.value).length > 0) {
    selectedAgentId.value = Object.keys(agents.value)[0];
  }

  loadAgentConfig();
});

const getConfigLabel = (key, value) => {
  if (value.description) {
    return `${value.name}（${key}）`;
  }
  return key;
};

const getPlaceholder = (key, value) => {
  return `（默认: ${value.default}）`;
};

const goToAgentPage = () => {
  if (selectedAgentId.value) {
    window.open(`/agent/${selectedAgentId.value}`, "_blank");
  }
};

const isToolActive = (tool) => {
  if (!agentConfig.value.tools) {
    agentConfig.value.tools = [];
  }
  return agentConfig.value.tools.includes(tool);
};

const toggleTool = (tool, checked) => {
  if (!agentConfig.value.tools) {
    agentConfig.value.tools = [];
  }

  if (checked) {
    if (!agentConfig.value.tools.includes(tool)) {
      agentConfig.value.tools.push(tool);
    }
  } else {
    agentConfig.value.tools = agentConfig.value.tools.filter((item) => item !== tool);
  }
};
</script>

<template>
  <div class="agent-view">
    <div class="sidebar" :class="{ 'is-open': state.isSidebarOpen }">
      <h2 class="sidebar-title">
        Agent List
        <div class="toggle-sidebar" @click="toggleSidebar">
          <img
            src="@/assets/icons/sidebar_left.svg"
            class="iconfont icon-20"
            alt="设置"
          />
        </div>
      </h2>
      <div class="agent-info">
        <a-select
          v-model="selectedAgentId"
          class="agent-list"
          style="width: 100%"
          @change="selectAgent"
        >
          <a-select-option v-for="(agent, name) in agents" :key="name" :value="name">
            {{ agent.name }}
          </a-select-option>
        </a-select>
        <p style="padding: 0 4px">
          {{ agents[selectedAgentId]?.description }}
        </p>

        <div class="agent-action-buttons">
          <a-button class="action-button" @click="openConfigModal">
            <template #icon><SettingOutlined /></template>
            Agent Configuration
          </a-button>

          <a-button class="action-button" @click="openTokenModal">
            <template #icon><KeyOutlined /></template>
            Access Token
          </a-button>

          <a-button class="action-button" @click="goToAgentPage" v-if="selectedAgentId">
            <template #icon><LinkOutlined /></template>
            Open Independent Page
          </a-button>
        </div>

        <div
          v-if="
            agents[selectedAgentId]?.requirements &&
            agents[selectedAgentId]?.requirements.length > 0
          "
          class="info-section"
        >
          <h3>Required Environment Variables:</h3>
          <div class="requirements-list">
            <a-tag v-for="req in agents[selectedAgentId].requirements" :key="req">
              {{ req }}
            </a-tag>
          </div>
        </div>

        <div
          v-if="
            agents[selectedAgentId]?.all_tools &&
            agents[selectedAgentId]?.all_tools.length > 0
          "
          class="info-section"
        >
          <h3>Available Tools:</h3>
          <div class="all-tools-list">
            <a-tag v-for="tool in agents[selectedAgentId].all_tools" :key="tool">
              {{ tool }}
            </a-tag>
          </div>
        </div>
      </div>
    </div>

    <div class="content">
      <AgentChatComponent
        :agent-id="selectedAgentId"
        :config="agentConfig"
        :state="state"
        @open-config="toggleConfigSidebar(true)"
      >
        <template #header-left>
          <div
            class="toggle-sidebar nav-btn"
            @click="toggleSidebar"
            v-if="!state.isSidebarOpen"
          >
            <img
              src="@/assets/icons/sidebar_left.svg"
              class="iconfont icon-20"
              alt="设置"
            />
          </div>
        </template>
      </AgentChatComponent>
    </div>

    <div class="config-sidebar" :class="{ 'is-open': state.isConfigSidebarOpen }">
      <h2 class="sidebar-title">
        <div class="sidebar-title-text" @click="toggleDebugMode">Agent Configuration</div>
        <div class="toggle-sidebar" @click="toggleConfigSidebar(false)">
          <CloseOutlined class="iconfont icon-20" />
        </div>
      </h2>
      <div v-if="selectedAgentId" class="config-form"></div>
      <div v-else class="no-agent-selected">Please select an agent first</div>
      <p>Hello, agent</p>
    </div>

    <a-modal
      v-model="state.configModalVisible"
      title="Agent Configuration"
      width="650px"
      :footer="null"
      @cancel="closeConfigModal"
    >
      <div v-if="selectedAgentId && configSchema" class="config-modal-content">
        <a-form :model="agentConfig" layout="vertical">
          <div class="empty-config" v-if="state.isEmptyConfig">
            <a-alert
              type="warning"
              message="This agent has no configuration items"
              show-icon
            />
          </div>
          <template v-for="(value, key) in configurableItems" :key="key">
            <a-form-item
              :label="getConfigLabel(key, value)"
              :name="key"
              class="config-item"
            >
              <p v-if="value.description" class="description">{{ value.description }}</p>
              <a-switch
                v-if="typeof agentConfig[key] === 'boolean'"
                v-model="agentConfig[key]"
              />
              <a-textarea
                v-else-if="key === 'system_prompt'"
                v-model="agentConfig[key]"
                :rows="4"
                :placeholder="getPlaceholder(key, value)"
              />
              <a-select v-else-if="value?.options" v-model="agentConfig[key]">
                <a-select-option
                  v-for="option in value.options"
                  :key="option"
                  :value="option"
                />
              </a-select>
              <a-input
                v-else
                v-model="agentConfig[key]"
                :placeholder="getPlaceholder(key, value)"
              />
            </a-form-item>
          </template>

          <a-form-item label="Available Tools" name="tools" class="config-item">
            <p class="description">
              Select the tools to enable (Note: The retrieve tool only shows the knowledge
              base that matches the current vector model, please check the docker logs for
              details.)
            </p>
            <a-form-item-rest>
              <div class="tools-switches">
                <div v-for="tool in availableTools" :key="tool" class="tool-switch-item">
                  <span class="tool-name">{{ tool }}</span>
                  <a-switch
                    size="small"
                    :checked="isToolActive(tool)"
                    @change="(checked) => toggleTool(tool, checked)"
                  />
                </div>
              </div>
            </a-form-item-rest>
          </a-form-item>

          <div class="form-actions" v-if="!state.isEmptyConfig">
            <a-button type="primary" @click="saveConfig">Save Configuration</a-button>
            <a-button @click="resetConfig">Reset</a-button>
            <a-button @click="closeConfigModal">Cancel</a-button>
          </div>
        </a-form>
      </div>
    </a-modal>

    <a-modal
      v-model="state.tokenModalVisible"
      title="Access Token Management"
      width="650px"
      :footer="null"
      @cancel="closeTokenModal"
    >
      <TokenManagerComponent v-if="selectedAgentId" :agent-id="selectedAgentId" />
    </a-modal>
  </div>
</template>
<style lang="less" scoped>
.agent-view {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  --agent-sidebar-width: 300px;
  --config-sidebar-width: 350px;
}

.sidebar {
  width: 0;
  max-width: var(--agent-sidebar-width);
  border-right: 1px solid var(--main-light-3);
  background-color: var(--bg-sider);
  box-sizing: content-box;
  overflow-y: auto;
  transition: width 0.3s ease;
  overflow: hidden;

  &.is-open {
    width: var(--agent-sidebar-width);
  }
}

.config-sidebar {
  width: 0;
  max-width: var(--config-sidebar-width);
  border-left: 1px solid var(--main-light-3);
  background-color: var(--bg-sider);
  box-sizing: content-box;
  overflow-y: auto;
  transition: width 0.3s ease;
  overflow: hidden;
  position: relative;
  z-index: 100;

  &.is-open {
    width: var(--config-sidebar-width);
  }

  .config-form {
    padding: 16px;
    min-width: calc(var(--config-sidebar-width) - 16px);
    overflow-y: auto;
    max-height: calc(100vh - 100px);

    .token-section {
      margin-top: 1.5rem;
      border-top: 1px solid var(--main-light-3);
      padding-top: 1rem;
    }
  }

  .no-agent-selected {
    padding: 16px;
    color: var(--gray-500);
    text-align: center;
    margin-top: 20px;
  }
}

.sidebar-title {
  height: var(--header-height);
  font-weight: bold;
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
  padding-bottom: 1rem;
  font-size: 1rem;
  border-bottom: 1px solid var(--main-light-3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  margin: 0;
}

.toggle-sidebar {
  cursor: pointer;

  &.nav-btn {
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
    overflow: hidden;

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

.agent-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 1rem;
}

.agent-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;

  &:hover {
    background-color: var(--main-light-4);
  }

  &.active {
    background-color: var(--main-light-3);
  }
}

.agent-info {
  padding: 16px;
  min-width: calc(var(--agent-sidebar-width) - 16px);
  overflow-y: auto;
  max-height: calc(100vh - 60px);
  scrollbar-width: thin;

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background-color: var(--main-light-4);
    border-radius: 4px;
  }
}

.agent-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-desc {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.content {
  flex: 1;
  overflow: hidden;
}

.info-section {
  margin-top: 16px;
  border-top: 1px solid var(--main-light-3);
  padding-top: 12px;

  h3 {
    font-size: 14px;
    margin-bottom: 8px;
    font-weight: 500;
  }
}

.requirements-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  .ant-tag {
    user-select: all;
  }
}

@media (max-width: 520px) {
  .sidebar {
    position: absolute;
    z-index: 101;
    width: 0;
    height: 100%;
    border-radius: 0 16px 16px 0;
    box-shadow: 0 0 10px 1px rgba(0, 0, 0, 0.05);

    &.is-open {
      width: var(--agent-sidebar-width);
      padding: 16px;
    }
  }

  .config-sidebar {
    position: absolute;
    z-index: 101;
    right: 0;
    width: 0;
    height: 100%;
    border-radius: 16px 0 0 16px;
    box-shadow: 0 0 10px 1px rgba(0, 0, 0, 0.05);

    &.is-open {
      width: 90%;
      max-width: var(--config-sidebar-width);
    }
  }
}

.config-modal-content {
  max-height: 70vh;
  overflow-y: auto;

  .description {
    font-size: 12px;
    color: var(--gray-700);
  }

  .form-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    gap: 10px;
  }
}

.agent-action-buttons {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-button {
  background-color: white;
  border: 1px solid var(--main-light-3);
  text-align: left;
  height: auto;
  padding: 8px 12px;

  &:hover {
    background-color: var(--main-light-4);
  }

  .anticon {
    margin-right: 8px;
  }
}

.tools-switches {
  display: flex;
  flex-direction: column;
  gap: 12px;

  .tool-switch-item {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .tool-name {
      margin-left: 10px;
    }
  }
}
</style>
