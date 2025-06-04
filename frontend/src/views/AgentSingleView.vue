<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import AgentChatComponent from "@/components/AgentChatComponent.vue";

const route = useRoute();
const agentId = computed(() => route.params.agent_id);

const tokenModalVisible = ref(false);
const tokenInput = ref("");
const isVerified = ref(false);
const verifying = ref(false);
const errorMessage = ref("");

const verifyToken = async () => {
  if (!tokenInput.value) {
    errorMessage.value = "Please enter the access token";
    return;
  }

  verifying.value = true;
  errorMessage.value = "";

  try {
    const response = await fetch("/api/admin/verify_token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        agent_id: agentId.value,
        token: tokenInput.value,
      }),
    });

    if (response.ok) {
      isVerified.value = true;
      tokenModalVisible.value = false;

      localStorage.setItem(`agent-token-${agentId.value}`, tokenInput.value);
    } else {
      const data = await response.json();
      errorMessage.value = data.detail || "Token verification failed";
    }
  } catch (error) {
    console.error("Failed to verify token:", error);
    errorMessage.value = "Failed to verify token";
  } finally {
    verifying.value = false;
  }
};

const checkVerification = async () => {
  const savedToken = localStorage.getItem(`agent-token-${agentId.value}`);

  if (savedToken) {
    verifying.value = true;

    try {
      const response = await fetch("/api/admin/verify_token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          agent_id: agentId.value,
          token: savedToken,
        }),
      });

      if (response.ok) {
        isVerified.value = true;
        tokenInput.value = savedToken;
      } else {
        localStorage.removeItem(`agent-token-${agentId.value}`);
        tokenModalVisible.value = true;
      }
    } catch (error) {
      console.error("Failed to verify token:", error);
      tokenModalVisible.value = true;
    } finally {
      verifying.value = false;
    }
  } else {
    tokenModalVisible.value = true;
  }
};

onMounted(() => {
  checkVerification();
});
</script>

<template>
  <div class="agent-single-view">
    <a-modal
      v-model="tokenModalVisible"
      title="Access verification"
      :closable="false"
      :maskClosable="false"
      :keyboard="false"
      :footer="null"
      width="500px"
    >
      <div class="token-verify-form">
        <p>Need to input the access token to use the agent</p>
        <a-input-password
          v-model="tokenInput"
          placeholder="Please enter the access token"
          @pressEnter="verifyToken"
        />
        <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
        <div class="token-actions">
          <a-button type="primary" :loading="verifying" @click="verifyToken"
            >Verify</a-button
          >
        </div>
      </div>
    </a-modal>

    <AgentChatComponent v-if="isVerified" :agent-id="agentId" />
  </div>
</template>

<style lang="less" scoped>
.agent-single-view {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.token-verify-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;

  .error-message {
    color: #ff4d4f;
    font-size: 0.85rem;
  }

  .token-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 0.5rem;
  }
}
</style>
