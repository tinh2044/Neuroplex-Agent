<script setup>
import { ref, reactive, computed, watch } from "vue";
import { message } from "ant-design-vue";

const props = defineProps({
  config: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(["update:config"]);

const configList = reactive([]);

props.config &&
  Object.entries(props.config).forEach(([key, value]) => {
    configList.push({ key, value });
  });

const addConfigModalVisible = ref(false);
const isAdding = ref(false);

const newConfig = ref({ key: "", value: "" });

const addConfig = () => {
  isAdding.value = true;
  addConfigModalVisible.value = true;
};

const confirmAddConfig = () => {
  if (newConfig.value.key === "" || newConfig.value.value === "") {
    message.warning("Key or value cannot be empty");
    return;
  }
  if (configList.some((item) => item.key === newConfig.value.key)) {
    message.warning("Key already exists");
    return;
  }
  configList.push({ key: newConfig.value.key, value: newConfig.value.value });
  addConfigModalVisible.value = false;
  newConfig.value = { key: "", value: "" };
  isAdding.value = false;
};

const deleteConfig = (index) => {
  configList.splice(index, 1);
};

const updateValue = (index) => {};

const configObject = computed(() => {
  return configList.reduce((acc, item) => {
    acc[item.key] = item.value;
    return acc;
  }, {});
});

watch(
  configObject,
  (newValue) => {
    emit("update:config", newValue);
  },
  { deep: true }
);

watch(addConfigModalVisible, (newValue) => {
  if (!newValue) {
    isAdding.value = false;
  }
});
</script>

<template>
  <a-card class="config-card" style="max-width: 960px">
    <a-form layout="vertical">
      <div v-for="(item, index) in configList" :key="index" class="config-item">
        <a-row :gutter="[16, 8]" align="middle">
          <a-col :span="8">
            <a-input
              v-model="item.key"
              placeholder="Model Name"
              readonly
              class="key-input"
            />
          </a-col>
          <a-col :span="14">
            <a-input
              v-model="item.value"
              @change="updateValue(index)"
              placeholder="Model Local Path"
              class="value-input"
            />
          </a-col>
          <a-col :span="2" class="delete-btn-col">
            <a-button type="link" danger class="delete-btn" @click="deleteConfig(index)">
              <DeleteOutlined />
            </a-button>
          </a-col>
        </a-row>
      </div>

      <a-button block @click="addConfig" class="add-btn" :disabled="isAdding">
        <PlusOutlined /> Add Path Mapping
      </a-button>
    </a-form>

    <a-modal
      title="Add Path Mapping"
      v-model="addConfigModalVisible"
      @ok="confirmAddConfig"
      class="config-modal"
    >
      <a-form layout="vertical">
        <a-form-item
          label="Model Name (same as Huggingface name, e.g. BAAI/bge-large-zh-v1.5)"
          required
        >
          <a-input
            v-model="newConfig.key"
            placeholder="Please enter model name"
            class="modal-input"
          />
        </a-form-item>
        <a-form-item
          label="Model Local Path (absolute path, e.g. /hdd/models/BAAI/bge-large-zh-v1.5)"
          required
        >
          <a-input
            v-model="newConfig.value"
            placeholder="Please enter model local path"
            class="modal-input"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </a-card>
</template>
<style scoped>
.config-card {
  background-color: var(--gray-10);
  border-radius: 8px;
  border: 1px solid var(--gray-300);
}

.config-item {
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 0;
  transition: background-color 0.3s ease;
}

.config-item:hover {
  background-color: #fafafa;
}

.config-item:last-child {
  border-bottom: none;
}

.key-input {
  background-color: #f8f8f8;
  border-color: #e8e8e8;
}

.delete-btn-col {
  display: flex;
  justify-content: center;
  align-items: center;
}

.delete-btn {
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.delete-btn:hover {
  opacity: 1;
}

.add-btn {
  margin-top: 16px;
  height: 40px;
  transition: all 0.3s ease;
  width: auto;
}

.modal-input {
  margin-bottom: 8px;
}

:deep(.ant-modal-content) {
  border-radius: 8px;
}

:deep(.ant-card-body) {
  padding: 16px;
}
</style>
