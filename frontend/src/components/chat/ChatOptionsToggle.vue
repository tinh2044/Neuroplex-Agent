<script setup>
defineProps({
  showPanel: Boolean,
});

defineEmits(["toggle-panel"]);
</script>
<template>
  <div class="nav-btn text" @click="$emit('toggle-panel')">
    <component :is="showPanel ? FolderOpenOutlined : FolderOutlined" />
    <span class="text">Options</span>
  </div>
</template>

<style lang="less" scoped>
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
</style>
