<script setup>
import { ref, onMounted, watch } from "vue";
import { message, Empty } from "ant-design-vue";
import { PlusOutlined, DeleteOutlined, CopyOutlined } from "@ant-design/icons-vue";

const props = defineProps({
  agentId: {
    type: String,
    required: true,
  },
});

const tokens = ref([]);
const loading = ref(false);
const addTokenModalVisible = ref(false);
const newToken = ref({
  name: "",
});

const fetchTokens = async () => {
  loading.value = true;
  try {
    const response = await fetch(`/api/admin/tokens?agent_id=${props.agentId}`);
    if (response.ok) {
      const data = await response.json();
      tokens.value = data;
    } else {
      message.error("Failed to get token list");
    }
  } catch (error) {
    console.error("Failed to get token list:", error);
    message.error("Failed to get token list");
  } finally {
    loading.value = false;
  }
};

const createToken = async () => {
  if (!newToken.value.name.trim()) {
    message.warning("Please enter the token name");
    return;
  }

  try {
    const response = await fetch("/api/admin/tokens", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        agent_id: props.agentId,
        name: newToken.value.name,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      tokens.value.push(data);
      message.success("Token created successfully");
      addTokenModalVisible.value = false;
      newToken.value.name = "";
    } else {
      message.error("Failed to create token");
    }
  } catch (error) {
    console.error("Failed to create token:", error);
    message.error("Failed to create token");
  }
};

const deleteToken = async (tokenId) => {
  try {
    const response = await fetch(`/api/admin/tokens/${tokenId}`, {
      method: "DELETE",
    });

    if (response.ok) {
      tokens.value = tokens.value.filter((token) => token.id !== tokenId);
      message.success("Token deleted successfully");
    } else {
      message.error("Failed to delete token");
    }
  } catch (error) {
    console.error("Failed to delete token:", error);
    message.error("Failed to delete token");
  }
};

const copyToken = (token) => {
  navigator.clipboard.writeText(token).then(() => {
    message.success("Token copied to clipboard");
  });
};

const showAddTokenModal = () => {
  newToken.value.name = "";
  addTokenModalVisible.value = true;
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleString();
};

watch(
  () => props.agentId,
  (newAgentId) => {
    if (newAgentId) {
      fetchTokens();
    } else {
      tokens.value = [];
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.agentId) {
    fetchTokens();
  }
});
</script>

<template>
  <div class="token-manager">
    <div class="token-tools">
      <a-button type="primary" size="small" @click="showAddTokenModal">
        <PlusOutlined /> Create Token
      </a-button>
    </div>
    <div class="token-list" v-if="tokens.length > 0">
      <a-spin :spinning="loading">
        <a-list size="small">
          <a-list-item v-for="token in tokens" :key="token.id">
            <div class="token-item">
              <div class="token-info">
                <div class="token-name">{{ token.name }}</div>
                <div class="token-value">
                  <code>{{ token.token }}</code>
                  <a-button type="link" size="small" @click="copyToken(token.token)">
                    <CopyOutlined />
                  </a-button>
                </div>
                <div class="token-time">
                  Created at: {{ formatDate(token.created_at) }}
                </div>
              </div>
              <div class="token-actions">
                <a-popconfirm
                  title="Are you sure to delete this token?"
                  ok-text="Yes"
                  cancel-text="No"
                  @confirm="deleteToken(token.id)"
                >
                  <a-button type="text" danger size="small">
                    <DeleteOutlined />
                  </a-button>
                </a-popconfirm>
              </div>
            </div>
          </a-list-item>
        </a-list>
      </a-spin>
    </div>
    <a-empty
      v-else
      description="No access tokens yet"
      :image="Empty.PRESENTED_IMAGE_SIMPLE"
    />

    <a-modal
      v-model="addTokenModalVisible"
      title="Add access token"
      ok-text="Create"
      cancel-text="Cancel"
      @ok="createToken"
    >
      <a-form :model="newToken" layout="vertical">
        <a-form-item label="Token name" name="name">
          <a-input v-model="newToken.name" placeholder="Please enter the token name" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>
<style lang="less" scoped>
.token-manager {
  margin-top: 1rem;
  // padding: 0 0.5rem;
}

.manager-title {
  font-size: 1rem;
  margin-bottom: 1rem;
}

.token-tools {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-end;
}

.token-list {
  max-height: calc(100vh - 400px);
  overflow-y: auto;

  li.ant-list-item {
    background-color: var(--gray-100);
    border-radius: 0.5rem;
    padding: 0.5rem;
    margin-bottom: 0.5rem;
  }
}

.token-item {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.token-info {
  flex: 1;
}

.token-name {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.token-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  background-color: var(--main-light-4);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.25rem;
  overflow-x: auto;
  user-select: all;

  code {
    flex: 1;
  }
}

.token-time {
  font-size: 0.75rem;
  color: var(--gray-500);
}

.token-actions {
  display: flex;
  align-items: center;
}
</style>
