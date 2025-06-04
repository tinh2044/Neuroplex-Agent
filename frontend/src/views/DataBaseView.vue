<script setup>
import { ref, onMounted, reactive, watch, h } from "vue";
import { useRouter, useRoute } from "vue-router";
import { message, Button } from "ant-design-vue";
import {
  ReadFilled,
  PlusOutlined,
  AppstoreFilled,
  LoadingOutlined,
} from "@ant-design/icons-vue";
import { useConfigStore } from "@/stores/config";
import HeaderComponent from "@/components/HeaderComponent.vue";

const route = useRoute();
const router = useRouter();
const databases = ref([]);
const graph = ref(null);
const graphloading = ref(false);

const indicator = h(LoadingOutlined, { spin: true });
const configStore = useConfigStore();

const newDatabase = reactive({
  name: "",
  description: "",
  dimension: "",
  loading: false,
});

const loadDatabases = () => {
  fetch("/api/data/", {
    method: "GET",
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      databases.value = data.databases;
    });
};

const createDatabase = () => {
  newDatabase.loading = true;
  console.log(newDatabase);
  if (!newDatabase.name) {
    message.error("Knowledge base name cannot be empty");
    newDatabase.loading = false;
    return;
  }
  fetch("/api/data/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      database_name: newDatabase.name,
      description: newDatabase.description,
      dimension: newDatabase.dimension ? parseInt(newDatabase.dimension) : null,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      loadDatabases();
      newDatabase.open = false;
      newDatabase.name = "";
      (newDatabase.description = ""), (newDatabase.dimension = "");
    })
    .finally(() => {
      newDatabase.loading = false;
    });
};

const navigateToDatabase = (databaseId) => {
  router.push({ path: `/database/${databaseId}` });
};

const navigateToGraph = () => {
  router.push({ path: `/database/graph` });
};

watch(
  () => route.path,
  (newPath, oldPath) => {
    if (newPath === "/database") {
      loadDatabases();
    }
  }
);

onMounted(() => {
  loadDatabases();
});
</script>

<template>
  <div
    class="database-container layout-container"
    v-if="configStore.config.enable_knowledge_base"
  >
    <HeaderComponent
      title="Document Knowledge Base"
      description="Document knowledge base, mainly composed of non-structured text, using vector retrieval. If there is an issue, check the saves/data/database.json file for configuration."
    >
      <template #actions>
        <a-button type="primary" @click="newDatabase.open = true"
          >Create Knowledge Base</a-button
        >
      </template>
    </HeaderComponent>

    <a-modal
      :open="newDatabase.open"
      title="Create Knowledge Base"
      @ok="createDatabase"
      @cancel="newDatabase.open = false"
    >
      <h3>Knowledge Base Name<span style="color: var(--error-color)">*</span></h3>
      <a-input v-model="newDatabase.name" placeholder="Create Knowledge Base Name" />
      <h3 style="margin-top: 20px">Knowledge Base Description</h3>
      <p style="color: var(--gray-700); font-size: 14px">
        In the agent process, the description here will be used as the tool description.
        The agent will select the appropriate tool based on the title and description of
        the knowledge base. Therefore, the more detailed the description here, the easier
        it is for the agent to select the appropriate tool.
      </p>
      <a-textarea
        v-model="newDatabase.description"
        placeholder="Create Knowledge Base Description"
        :auto-size="{ minRows: 5, maxRows: 10 }"
      />
      <template #footer>
        <a-button key="back" @click="newDatabase.open = false">Cancel</a-button>
        <a-button
          key="submit"
          type="primary"
          :loading="newDatabase.loading"
          @click="createDatabase"
          >Create</a-button
        >
      </template>
    </a-modal>
    <div class="databases">
      <div class="new-database dbcard" @click="newDatabase.open = true">
        <div class="top">
          <div class="icon">
            <PlusOutlined />
          </div>
          <div class="info">
            <h3>Create Knowledge Base</h3>
          </div>
        </div>
        <p>
          Import your own text data or write data in real time through Webhook to enhance
          the context of LLM.
        </p>
      </div>
      <div
        v-for="database in databases"
        :key="database.db_id"
        class="database dbcard"
        @click="navigateToDatabase(database.db_id)"
      >
        <div class="top">
          <div class="icon">
            <ReadFilled />
          </div>
          <div class="info">
            <h3>{{ database.name }}</h3>
            <p>
              <span
                >{{
                  database.files ? Object.keys(database.files).length : 0
                }}
                Documents</span
              >
            </p>
          </div>
        </div>
        <p class="description">{{ database.description || "No description" }}</p>
        <div class="tags">
          <a-tag color="blue" v-if="database.embed_model">{{
            database.embed_model
          }}</a-tag>
          <a-tag color="green" v-if="database.dimension">{{ database.dimension }}</a-tag>
        </div>
      </div>
    </div>
  </div>
  <div class="database-empty" v-else>
    <a-empty>
      <template #description>
        <span>
          Go to the
          <router-link to="/setting" style="color: var(--main-color); font-weight: bold"
            >Setting</router-link
          >
          page to configure the knowledge base.
        </span>
      </template>
    </a-empty>
  </div>
</template>
<style lang="less" scoped>
.database-actions,
.document-actions {
  margin-bottom: 20px;
}

.databases {
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;

  .new-database {
    background-color: #f0f3f4;
  }
}

.database,
.graphbase {
  background-color: white;
  box-shadow: 0px 1px 2px 0px rgba(16, 24, 40, 0.06),
    0px 1px 3px 0px rgba(16, 24, 40, 0.1);
  border: 2px solid white;
  transition: box-shadow 0.2s ease-in-out;

  &:hover {
    box-shadow: 0px 4px 6px -2px rgba(16, 24, 40, 0.03),
      0px 12px 16px -4px rgba(16, 24, 40, 0.08);
  }
}

.dbcard,
.database {
  width: 100%;
  padding: 10px;
  border-radius: 12px;
  height: 160px;
  padding: 20px;
  cursor: pointer;

  .top {
    display: flex;
    align-items: center;
    height: 50px;
    margin-bottom: 10px;

    .icon {
      width: 50px;
      height: 50px;
      font-size: 28px;
      margin-right: 10px;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: #f5f8ff;
      border-radius: 8px;
      border: 1px solid #e0eaff;
      color: var(--main-color);
    }

    .info {
      h3,
      p {
        margin: 0;
        color: black;
      }

      h3 {
        font-size: 16px;
        font-weight: bold;
      }

      p {
        color: var(--gray-900);
        font-size: small;
      }
    }
  }

  .description {
    color: var(--gray-900);
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    text-overflow: ellipsis;
    margin-bottom: 10px;
  }
}

.database-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  flex-direction: column;
  color: var(--gray-900);
}

.database-container {
  padding: 0;
}
</style>
