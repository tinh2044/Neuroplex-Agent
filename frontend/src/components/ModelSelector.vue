<script setup>
import { BulbOutlined } from "@ant-design/icons-vue";

const props = defineProps({
  configStore: Object,
  modelKeys: Array,
  modelNames: Object,
  customModels: Array,
});

const emit = defineEmits(["select-model"]);

const selectModel = (provider, name) => {
  emit("select-model", provider, name);
};
</script>

<template>
  <a-dropdown>
    <a class="model-select nav-btn" @click.prevent>
      <BulbOutlined />
      <a-tooltip :title="configStore.config?.model_name" placement="right">
        <span class="model-text text"> {{ configStore.config?.model_name }} </span>
      </a-tooltip>
      <span class="text" style="color: #aaa"
        >{{ configStore.config?.model_provider }}
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
</template>

<style lang="less" scoped>
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
</style>
