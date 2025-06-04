<script setup>
import { message } from "ant-design-vue";
import { computed, reactive, ref, h, watch, onMounted, onUnmounted } from "vue";
import { useConfigStore } from "@/stores/config";
import {
  ReloadOutlined,
  SettingOutlined,
  CodeOutlined,
  ExceptionOutlined,
  FolderOutlined,
  DeleteOutlined,
  EditOutlined,
  InfoCircleOutlined,
  DownOutlined,
  UpOutlined,
  LoadingOutlined,
  UpCircleOutlined,
  DownCircleOutlined,
} from "@ant-design/icons-vue";
import HeaderComponent from "@/components/HeaderComponent.vue";
import TableConfigComponent from "@/components/TableConfigComponent.vue";
import { notification, Button } from "ant-design-vue";
import { modelIcons } from "@/utils/modelIcon";

const configStore = useConfigStore();
const items = computed(() => configStore.config._config_items);
const modelNames = computed(() => configStore.config?.model_names);
const modelStatus = computed(() => configStore.config?.model_provider_status);
const modelProvider = computed(() => configStore.config?.model_provider);
const isNeedRestart = ref(false);
const customModel = reactive({
  modelTitle: "Add custom model",
  visible: false,
  custom_id: "",
  name: "",
  api_key: "",
  api_base: "",
  edit_type: "add",
});
const providerConfig = reactive({
  visible: false,
  provider: "",
  providerName: "",
  models: [],
  allModels: [], //   all available models
  selectedModels: [], // user selected models
  loading: false,
});
const state = reactive({
  loading: false,
  section: "base",
  windowWidth: window?.innerWidth || 0,
});

// filter the keys of modelStatus that are true
const modelKeys = computed(() => {
  return Object.keys(modelStatus.value || {}).filter((key) => modelStatus.value?.[key]);
});

const notModelKeys = computed(() => {
  return Object.keys(modelStatus.value || {}).filter((key) => !modelStatus.value?.[key]);
});

// model expand state management
const expandedModels = reactive({});

// watch modelKeys change, ensure new added models are default expanded state
watch(
  modelKeys,
  (newKeys) => {
    newKeys.forEach((key) => {
      if (expandedModels[key] === undefined) {
        expandedModels[key] = true;
      }
    });
  },
  { immediate: true }
);

// method to toggle expand state
const toggleExpand = (item) => {
  expandedModels[item] = !expandedModels[item];
};

const generateRandomHash = (length) => {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let hash = "";
  for (let i = 0; i < length; i++) {
    hash += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return hash;
};

const handleModelLocalPathsUpdate = (config) => {
  handleChange("model_local_paths", config);
};

const handleChange = (key, e) => {
  if (key == "enable_knowledge_graph" && e && !configStore.config.enable_knowledge_base) {
    message.error("Enable knowledge graph must enable knowledge base first");
    return;
  }

  if (key == "enable_knowledge_base" && !e && configStore.config.enable_knowledge_graph) {
    message.error("Disable knowledge base must disable knowledge graph first");
    return;
  }

  // these are the configurations that need to be restarted
  if (
    key == "enable_reranker" ||
    key == "enable_knowledge_graph" ||
    key == "enable_knowledge_base" ||
    key == "enable_web_search" ||
    key == "embed_model" ||
    key == "reranker" ||
    key == "model_local_paths"
  ) {
    if (!isNeedRestart.value) {
      isNeedRestart.value = true;
      notification.info({
        message: "Need to reload model",
        description: "Click the button in the bottom right corner to reload the model",
        placement: "topLeft",
        duration: 0,
        btn: h(Button, { type: "primary", onClick: sendRestart }, "Reload now"),
      });
    }
  }

  configStore.setConfigValue(key, e);
};

const handleAddOrEditCustomModel = async () => {
  if (!customModel.name || !customModel.api_base) {
    message.error("Please fill in the complete model name and API Base information.");
    return;
  }

  let custom_models = configStore.config.custom_models || [];

  const model_info = {
    custom_id: customModel.custom_id || `${customModel.name}-${generateRandomHash(4)}`,
    name: customModel.name,
    api_key: customModel.api_key,
    api_base: customModel.api_base,
  };

  if (customModel.edit_type === "add") {
    if (custom_models.find((item) => item.custom_id === customModel.custom_id)) {
      message.error("Model ID already exists");
      return;
    }
    custom_models.push(model_info);
  } else {
    // if custom_id is the same, update
    custom_models = custom_models.map((item) =>
      item.custom_id === customModel.custom_id ? model_info : item
    );
  }

  customModel.visible = false;
  await configStore.setConfigValue("custom_models", custom_models);
  message.success(
    customModel.edit_type === "add"
      ? "Model added successfully"
      : "Model updated successfully"
  );
};

const handleDeleteCustomModel = (custom_id) => {
  const updatedModels = configStore.config.custom_models.filter(
    (item) => item.custom_id !== custom_id
  );
  configStore.setConfigValue("custom_models", updatedModels);
};

const prepareToEditCustomModel = (item) => {
  customModel.modelTitle = "Edit custom model";
  customModel.custom_id = item.custom_id;
  customModel.visible = true;
  customModel.edit_type = "edit";
  customModel.name = item.name;
  customModel.api_key = item.api_key;
  customModel.api_base = item.api_base;
};

const prepareToAddCustomModel = () => {
  customModel.modelTitle = "Add custom model";
  customModel.edit_type = "add";
  customModel.visible = true;
  clearCustomModel();
};

const clearCustomModel = () => {
  customModel.custom_id = "";
  customModel.name = "";
  customModel.api_key = "";
  customModel.api_base = "";
};

const handleCancelCustomModel = () => {
  clearCustomModel();
  customModel.visible = false;
};

const updateWindowWidth = () => {
  state.windowWidth = window?.innerWidth || 0;
};

onMounted(() => {
  updateWindowWidth();
  window.addEventListener("resize", updateWindowWidth);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateWindowWidth);
});

const sendRestart = () => {
  console.log("Restarting...");
  message.loading({ content: "Reloading model...", key: "restart", duration: 0 });
  fetch("/api/restart", {
    method: "POST",
  }).then(() => {
    console.log("Restarted");
    message.success({ content: "Reloaded successfully!", key: "restart", duration: 2 });
    setTimeout(() => {
      window.location.reload();
    }, 200);
  });
};

// get the model list of the provider
const fetchProviderModels = (provider) => {
  providerConfig.loading = true;
  fetch(`/api/chat/models?model_provider=${provider}`)
    .then((response) => response.json())
    .then((data) => {
      console.log(`${provider} 模型列表:`, data);

      // handle various possible API return formats
      let modelsList = [];

      // case 1: { data: [...] }
      if (data.data && Array.isArray(data.data)) {
        modelsList = data.data;
      }
      // case 2: { models: [...] } (string array)
      else if (data.models && Array.isArray(data.models)) {
        modelsList = data.models.map((model) =>
          typeof model === "string" ? { id: model } : model
        );
      }
      // case 3: { models: { data: [...] } }
      else if (data.models && data.models.data && Array.isArray(data.models.data)) {
        modelsList = data.models.data;
      }

      console.log("Processed model list:", modelsList);
      providerConfig.allModels = modelsList;
      providerConfig.loading = false;
    })
    .catch((error) => {
      console.error(`Failed to get ${provider} model list:`, error);
      message.error({
        content: `Failed to get ${modelNames.value[provider].name} model list`,
        duration: 2,
      });
      providerConfig.loading = false;
    });
};

const openProviderConfig = (provider) => {
  providerConfig.provider = provider;
  providerConfig.providerName = modelNames.value[provider].name;
  providerConfig.allModels = [];
  providerConfig.visible = true;
  providerConfig.loading = true;

  // get the current selected models as the initial selected value
  const currentModels = modelNames.value[provider]?.models || [];
  providerConfig.selectedModels = [...currentModels];

  // get all available models
  fetchProviderModels(provider);
};

const saveProviderConfig = async () => {
  if (!modelStatus.value[providerConfig.provider]) {
    message.error(
      "Please configure the corresponding APIKEY in the src/.env file and restart the service"
    );
    return;
  }

  message.loading({
    content: "Saving configuration...",
    key: "save-config",
    duration: 0,
  });

  try {
    // send the selected model list to the backend
    const response = await fetch(
      `/api/chat/models/update?model_provider=${providerConfig.provider}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(providerConfig.selectedModels),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to save model configuration");
    }

    const data = await response.json();
    console.log("Updated model list:", data.models);

    message.success({
      content: "Model configuration saved!",
      key: "save-config",
      duration: 2,
    });

    // close the modal
    providerConfig.visible = false;

    // refresh the configuration
    configStore.refreshConfig();
  } catch (error) {
    console.error("Failed to save configuration:", error);
    message.error({
      content: `Failed to save configuration: ${error.message}`,
      key: "save-config",
      duration: 2,
    });
  }
};

const cancelProviderConfig = () => {
  providerConfig.visible = false;
};
</script>

<template>
  <div class="">
    <HeaderComponent title="Settings" class="setting-header">
      <template #description>
        <p>
          The configuration file can also be modified in
          <code>saves/config/base.yaml</code>
        </p>
      </template>
      <template #actions>
        <a-button
          :type="isNeedRestart ? 'primary' : 'default'"
          @click="sendRestart"
          :icon="h(ReloadOutlined)"
        >
          {{ isNeedRestart ? "Need to refresh" : "Reload" }}
        </a-button>
      </template>
    </HeaderComponent>
    <div class="setting-container layout-container">
      <div class="sider" v-if="state.windowWidth > 520">
        <a-button
          type="text"
          :class="{ activesec: state.section === 'base' }"
          @click="state.section = 'base'"
          :icon="h(SettingOutlined)"
        >
          Base Settings
        </a-button>
        <a-button
          type="text"
          :class="{ activesec: state.section === 'model' }"
          @click="state.section = 'model'"
          :icon="h(CodeOutlined)"
        >
          Model Settings
        </a-button>
        <a-button
          type="text"
          :class="{ activesec: state.section === 'path' }"
          @click="state.section = 'path'"
          :icon="h(FolderOutlined)"
        >
          Path Settings
        </a-button>
      </div>
      <div class="setting" v-if="state.windowWidth <= 520 || state.section === 'base'">
        <h3>Function Settings</h3>
        <div class="section">
          <div class="card">
            <span class="label">{{ items?.enable_knowledge_base.des }}</span>
            <a-switch
              :checked="configStore.config.enable_knowledge_base"
              @change="
                handleChange(
                  'enable_knowledge_base',
                  !configStore.config.enable_knowledge_base
                )
              "
            />
          </div>
          <div class="card">
            <span class="label">{{ items?.enable_knowledge_graph.des }}</span>
            <a-switch
              :checked="configStore.config.enable_knowledge_graph"
              @change="
                handleChange(
                  'enable_knowledge_graph',
                  !configStore.config.enable_knowledge_graph
                )
              "
            />
          </div>
        </div>
        <h3>Retrieval Settings</h3>
        <div class="section">
          <div class="card card-select">
            <span class="label">{{ items?.embed_model.des }}</span>
            <a-select
              style="width: 300px"
              :value="configStore.config?.embed_model"
              @change="handleChange('embed_model', $event)"
            >
              <a-select-option
                v-for="(name, idx) in items?.embed_model.choices"
                :key="idx"
                :value="name"
                >{{ name }}
              </a-select-option>
            </a-select>
          </div>
          <div class="card card-select">
            <span class="label">{{ items?.reranker.des }}</span>
            <a-select
              style="width: 300px"
              :value="configStore.config?.reranker"
              @change="handleChange('reranker', $event)"
              :disabled="!configStore.config.enable_reranker"
            >
              <a-select-option
                v-for="(name, idx) in items?.reranker.choices"
                :key="idx"
                :value="name"
                >{{ name }}
              </a-select-option>
            </a-select>
          </div>
          <div class="card">
            <span class="label">{{ items?.enable_reranker.des }}</span>
            <a-switch
              :checked="configStore.config.enable_reranker"
              @change="
                handleChange('enable_reranker', !configStore.config.enable_reranker)
              "
            />
          </div>
          <div class="card card-select">
            <span class="label">{{ items?.use_rewrite_query.des }}</span>
            <a-select
              style="width: 200px"
              :value="configStore.config?.use_rewrite_query"
              @change="handleChange('use_rewrite_query', $event)"
            >
              <a-select-option
                v-for="(name, idx) in items?.use_rewrite_query.choices"
                :key="idx"
                :value="name"
                >{{ name }}
              </a-select-option>
            </a-select>
          </div>
        </div>
      </div>
      <div class="setting" v-if="state.windowWidth <= 520 || state.section === 'model'">
        <h3>Model Settings</h3>
        <p>
          Please configure the corresponding APIKEY in the <code>src/.env</code> file and
          restart the service
        </p>
        <div class="model-provider-card">
          <div class="card-header">
            <h3>Custom Models</h3>
          </div>
          <div class="card-body">
            <div
              :class="{
                model_selected:
                  modelProvider == 'custom' &&
                  configStore.config.model_name == item.custom_id,
                'card-models': true,
                'custom-model': true,
              }"
              v-for="item in configStore.config.custom_models"
              :key="item.custom_id"
              @click="
                handleChange('model_provider', 'custom');
                handleChange('model_name', item.custom_id);
              "
            >
              <div class="card-models__header">
                <div class="name" :title="item.name">{{ item.name }}</div>
                <div class="action">
                  <a-popconfirm
                    title="Confirm delete this model?"
                    @confirm="handleDeleteCustomModel(item.custom_id)"
                    okText="Confirm Delete"
                    cancelText="Cancel"
                    ok-type="danger"
                    :disabled="configStore.config.model_name == item.name"
                  >
                    <a-button
                      type="text"
                      :disabled="configStore.config.model_name == item.name"
                      @click.stop
                      ><DeleteOutlined
                    /></a-button>
                  </a-popconfirm>
                  <a-button type="text" @click.stop="prepareToEditCustomModel(item)"
                    ><EditOutlined
                  /></a-button>
                </div>
              </div>
              <div class="api_base">{{ item.api_base }}</div>
            </div>
            <div class="card-models custom-model" @click="prepareToAddCustomModel">
              <div class="card-models__header">
                <div class="name">+ Add Model</div>
              </div>
              <div class="api_base">Add compatible OpenAI models</div>
              <a-modal
                class="custom-model-modal"
                :open="customModel.visible"
                :title="customModel.modelTitle"
                @ok="handleAddOrEditCustomModel"
                @cancel="handleCancelCustomModel"
                :okText="'Confirm'"
                :cancelText="'Cancel'"
                :okButtonProps="{ disabled: !customModel.name || !customModel.api_base }"
                :ok-type="'primary'"
              >
                <p>The model added is a compatible OpenAI model, such as vllm, Ollama.</p>
                <a-form :model="customModel" layout="vertical">
                  <a-form-item
                    label="Model Name"
                    name="name"
                    :rules="[{ required: true, message: 'Please enter model name' }]"
                  >
                    <p class="form-item-description">
                      The name of the model to be called
                    </p>
                    <a-input
                      :value="customModel.name"
                      :disabled="customModel.edit_type == 'edit'"
                    />
                  </a-form-item>
                  <a-form-item
                    label="API Base"
                    name="api_base"
                    :rules="[{ required: true, message: 'Please enter API Base' }]"
                  >
                    <a-input :value="customModel.api_base" />
                  </a-form-item>
                  <a-form-item label="API KEY" name="api_key">
                    <a-input-password
                      :value="customModel.api_key"
                      :visibilityToggle="false"
                      autocomplete="new-password"
                    />
                  </a-form-item>
                </a-form>
              </a-modal>
            </div>
          </div>
        </div>
        <div class="model-provider-card" v-for="(item, key) in modelKeys" :key="key">
          <div class="card-header" @click="toggleExpand(item)">
            <!-- <div v-if="modelStatus[item]" class="success"></div> -->
            <div :class="{ 'model-icon': true, available: modelStatus[item] }">
              <img :src="modelIcons[item] || modelIcons.default" alt="Model Icon" />
            </div>
            <div class="model-title-container">
              <h3>{{ modelNames[item].name }}</h3>
            </div>
            <a-button
              type="text"
              class="expand-button"
              @click.stop="openProviderConfig(item)"
              title="Configuration model provider"
            >
              <SettingOutlined />
            </a-button>
            <a-button type="text" class="expand-button" @click.stop="toggleExpand(item)">
              <span class="icon-wrapper" :class="{ rotated: expandedModels[item] }">
                <DownCircleOutlined />
              </span>
            </a-button>
          </div>
          <div class="card-body-wrapper" :class="{ expanded: expandedModels[item] }">
            <div class="card-body" v-if="modelStatus[item]">
              <div
                :class="{
                  model_selected:
                    modelProvider == item && configStore.config.model_name == model,
                  'card-models': true,
                }"
                v-for="(model, idx) in modelNames[item].models"
                :key="idx"
                @click="
                  handleChange('model_provider', item);
                  handleChange('model_name', model);
                "
              >
                <div class="model_name">{{ model }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="model-provider-card" v-for="(item, key) in notModelKeys" :key="key">
          <div class="card-header">
            <div class="model-icon">
              <img :src="modelIcons[item] || modelIcons.default" alt="Model Icon" />
            </div>
            <div class="model-title-container">
              <h3 style="font-weight: 400">{{ modelNames[item].name }}</h3>
              <a :href="modelNames[item].url" target="_blank" class="model-url">
                <InfoCircleOutlined />
              </a>
            </div>
            <a-button
              type="text"
              class="config-button"
              @click.stop="openProviderConfig(item)"
              title="Configuration model provider"
            >
              <SettingOutlined />
            </a-button>
            <div class="missing-keys">
              Need to configure<span
                v-for="(key, idx) in modelNames[item].env"
                :key="idx"
                >{{ key }}</span
              >
            </div>
          </div>
        </div>
      </div>
      <div class="setting" v-if="state.windowWidth <= 520 || state.section === 'path'">
        <h3>Local Model Settings</h3>
        <p>
          If you are using Docker, please ensure that the volumes are mapped in the
          docker-compose.dev.yaml file.
        </p>
        <TableConfigComponent
          :config="configStore.config?.model_local_paths"
          @update:config="handleModelLocalPathsUpdate"
        />
      </div>
    </div>
    <a-modal
      class="provider-config-modal"
      :open="providerConfig.visible"
      :title="`Configure ${providerConfig.providerName} model`"
      @ok="saveProviderConfig"
      @cancel="cancelProviderConfig"
      :okText="'Save'"
      :cancelText="'Cancel'"
      :ok-type="'primary'"
      :width="800"
      :bodyStyle="{ padding: '16px 24px' }"
    >
      <div v-if="providerConfig.loading" class="modal-loading-container">
        <a-spin
          :indicator="
            h(LoadingOutlined, {
              style: { fontSize: '32px', color: 'var(--main-color)' },
            })
          "
        />
        <div class="loading-text">Getting model list...</div>
      </div>
      <div v-else class="modal-config-content">
        <div class="modal-config-header">
          <h3>Select {{ providerConfig.providerName }} models</h3>
          <p class="description">
            Select the models you want to enable in the system. Please note that the list
            may include non-dialogue models, please carefully.
          </p>
        </div>

        <div class="modal-models-section">
          <div class="modal-checkbox-list">
            <a-checkbox-group :value="providerConfig.selectedModels">
              <div
                v-for="(model, index) in providerConfig.allModels"
                :key="index"
                class="modal-checkbox-item"
              >
                <a-checkbox :value="model.id">{{ model.id }}</a-checkbox>
              </div>
            </a-checkbox-group>
          </div>
          <div v-if="providerConfig.allModels.length === 0" class="modal-no-models">
            <a-alert
              v-if="!modelStatus[providerConfig.provider]"
              type="warning"
              message="Please configure the corresponding APIKEY in src/.env and restart the service"
            />
            <div v-else>
              <a-alert
                type="warning"
                message="The provider has not yet adapted the method of obtaining the model list. If you need to add a model, please add it in src/static/models.private.yml."
              />
              <img
                src="@/assets/pics/guides/how-to-add-models.png"
                alt="Add model guide"
                style="width: 100%; height: 100%"
              />
            </div>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<style lang="less" scoped>
:root {
  --setting-header-height: 200px;
}

.setting-header {
  height: var(--setting-header-height);
}

.setting-header p {
  margin: 8px 0 0;
}

.setting-container {
  padding: 0;
  box-sizing: border-box;
  display: flex;
  position: relative;
  min-height: calc(100vh - var(--setting-header-height));
}

.sider {
  width: 200px;
  height: 100%;
  padding: 0 20px;
  position: sticky;
  top: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1px solid var(--main-light-3);
  gap: 8px;
  padding-top: 20px;

  & > * {
    width: 100%;
    height: auto;
    padding: 6px 16px;
    cursor: pointer;
    transition: all 0.1s;
    text-align: left;
    font-size: 15px;
    border-radius: 8px;
    color: var(--gray-700);

    &:hover {
      background: var(--gray-100);
    }

    &.activesec {
      background: var(--gray-200);
      color: var(--gray-900);
    }
  }
}

.setting {
  width: 100%;
  flex: 1;
  margin: 0 auto;
  height: 100%;
  padding: 0 20px;
  margin-bottom: 40px;

  h3 {
    margin-top: 20px;
  }

  .section {
    margin-top: 20px;
    background-color: var(--gray-10);
    padding: 20px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    border: 1px solid var(--gray-300);
  }

  .card {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .label {
      margin-right: 20px;

      button {
        margin-left: 10px;
        height: 24px;
        padding: 0 8px;
        font-size: smaller;
      }
    }
  }

  .model-provider-card {
    border: 1px solid var(--gray-300);
    background-color: white;
    border-radius: 8px;
    margin-bottom: 12px;
    padding: 12px;
    .card-header {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;

      .model-title-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 10px;
        flex: 1;
      }

      .model-url {
        font-size: 12px;
        width: fit-content;
        color: var(--gray-500);
      }

      .model-icon {
        width: 28px;
        height: 28px;

        filter: grayscale(100%);
        img {
          width: 100%;
          height: 100%;
          border-radius: 4px;
          border: 1px solid var(--gray-300);
        }

        &.available {
          filter: grayscale(0%);
        }
      }

      h3 {
        margin: 0;
        font-size: 0.9rem;
        font-weight: bold;
      }

      a {
        text-decoration: none;
        color: var(--gray-500);
        font-size: 12px;
        transition: all 0.1s;

        &:hover {
          color: var(--gray-900);
        }
      }

      .details,
      .missing-keys {
        margin-left: auto;
      }

      .success {
        width: 0.75rem;
        height: 0.75rem;
        background-color: rgb(91, 186, 91);
        border-radius: 50%;
        box-shadow: 0 0 10px 1px rgba(0, 128, 0, 0.1);
        border: 2px solid white;
      }

      .missing-keys {
        margin-top: 4px;
        color: var(--gray-600);
        font-size: 12px;
        & > span {
          margin-left: 6px;
          user-select: all;
          background-color: var(--gray-100);
          padding: 2px 6px;
          border-radius: 4px;
          color: var(--gray-800);
        }
      }

      .expand-button {
        margin-left: auto;
        height: 32px;
        width: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        cursor: pointer;
        color: var(--gray-500);

        &:hover {
          background-color: var(--gray-100);
        }

        .icon-wrapper {
          display: inline-flex;
          transition: transform 0.2s ease;

          &.rotated {
            transform: rotate(180deg);
          }
        }
      }
    }

    .card-body-wrapper {
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.2s ease-out;

      &.expanded {
        max-height: 700px;
      }
    }

    .card-body {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 12px;
      margin-top: 10px;
      .card-models {
        width: 100%;
        border-radius: 8px;
        border: 1px solid var(--gray-300);
        padding: 12px 16px;
        display: flex;
        gap: 6px;
        justify-content: space-between;
        align-items: center;
        cursor: pointer;
        box-sizing: border-box;
        background-color: var(--gray-50);
        transition: box-shadow 0.1s;
        &:hover {
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .model_name {
          font-size: 14px;
          color: var(--gray-900);
        }
        .select-btn {
          width: 16px;
          height: 16px;
          flex: 0 0 16px;
          border-radius: 50%;
        }

        &.model_selected {
          border: 2px solid var(--main-color);
          padding: 9px 15px;
          .model_name {
            color: var(--gray-1000);
          }
          .select-btn {
            border-color: var(--main-color);
            border: 2px solid var(--main-color);
          }
        }

        &.custom-model {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          padding-right: 8px;
          gap: 10px;
          .card-models__header {
            width: 100%;
            height: 24px;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            .name {
              color: var(--gray-1000);
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
              flex: 1;
              margin-right: 8px;
              position: relative;

              &:hover::after {
                content: attr(title);
                position: absolute;
                left: 0;
                top: 100%;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                white-space: nowrap;
                z-index: 1000;
                margin-top: 5px;
              }
            }
            .action {
              opacity: 0;
              user-select: none;
              margin-left: auto;
              flex-shrink: 0;
              button {
                padding: 4px 8px;
              }
            }
            .custom-model-modal {
              .ant-form-item {
                margin-bottom: 10px;
                .form-item-description {
                  font-size: 12px;
                  color: var(--gray-600);
                  margin-bottom: 10px;
                }
              }
            }
          }
          .api_base {
            font-size: 12px;
            color: var(--gray-600);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            width: 100%;
          }

          &:hover {
            .card-models__header {
              .action {
                opacity: 1;
              }
            }
          }
        }
        &.model_selected.custom-model {
          padding: 9px 7px 9px 15px;
          .card-models__header {
            .action {
              opacity: 1;
            }
          }
        }
      }
    }
  }
}

@media (max-width: 520px) {
  .setting-container {
    flex-direction: column;
  }

  .card.card-select {
    gap: 0.75rem;
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>

<style lang="less">
.provider-config-modal {
  .ant-modal-body {
    padding: 16px 0 !important;
    .modal-loading-container {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 200px;

      .loading-text {
        margin-top: 20px;
        color: var(--gray-700);
        font-size: 14px;
      }
    }

    .modal-config-content {
      max-height: 70vh;
      overflow-y: auto;
      // padding-right: 10px;

      .modal-config-header {
        margin-bottom: 20px;

        .description {
          font-size: 14px;
          color: var(--gray-600);
          margin: 0;
        }
      }

      .modal-models-section {
        .modal-checkbox-list {
          max-height: 50vh;
          overflow-y: auto;
          .modal-checkbox-item {
            margin-bottom: 4px;
            padding: 4px 6px;
            border-radius: 6px;
            background-color: white;
            border: 1px solid var(--gray-200);

            &:hover {
              background-color: var(--gray-50);
            }
          }
        }
      }
    }
  }
}
</style>
