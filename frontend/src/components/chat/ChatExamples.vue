<script setup>
const props = defineProps({
  title: {
    type: String,
    default: "Hello, I'm Neuroplex, an intelligent assistant based on knowledge graphs",
  },
  examples: {
    type: Array,
    default: () => [
      "Write a simple bubble sort algorithm",
      "What is the weather in Wuxi today?",
      "Introduce the novel Dream of the Red Chamber",
      "What day is it today?",
    ],
  },
});

const emit = defineEmits(["select-example"]);

const selectExample = (example) => {
  emit("select-example", example);
};
</script>

<template>
  <div class="chat-examples">
    <h1>{{ title }}</h1>
    <div class="opts">
      <div
        class="opt__button"
        v-for="(exp, key) in examples"
        :key="key"
        @click="selectExample(exp)"
      >
        {{ exp }}
      </div>
    </div>
  </div>
</template>

<style lang="less" scoped>
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
</style>
