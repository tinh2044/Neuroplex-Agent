<script setup>
import { onMounted, reactive, ref, watch, toRaw, onUnmounted, computed } from "vue";
import { message, Modal } from "ant-design-vue";
import { useRoute, useRouter } from "vue-router";
import { useConfigStore } from "@/stores/config";
import HeaderComponent from "@/components/HeaderComponent.vue";
import {
  ReadOutlined,
  LeftOutlined,
  CheckCircleFilled,
  HourglassFilled,
  CloseCircleFilled,
  ClockCircleFilled,
  DeleteOutlined,
  CloudUploadOutlined,
  SearchOutlined,
  LoadingOutlined,
  CaretUpOutlined,
} from "@ant-design/icons-vue";

const route = useRoute();
const router = useRouter();
const databaseId = ref(route.params.database_id);
const database = ref({});

const fileList = ref([]);
const selectedFile = ref(null);

const queryText = ref("");
const queryResult = ref(null);
const filteredResults = ref([]);
const configStore = useConfigStore();

const state = reactive({
  loading: false,
  adding: false,
  refrashing: false,
  searchLoading: false,
  lock: false,
  drawer: false,
  refreshInterval: null,
  curPage: "files",
});

const meta = reactive({
  mode: "search",
  maxQueryCount: 30,
  filter: true,
  use_rewrite_query: "off",
  rerankThreshold: 0.1,
  distanceThreshold: 0.3,
  topK: 10,
  sortBy: "rerank_score",
});

const use_rewrite_queryOptions = ref([
  { value: "off", payload: { title: "off", subTitle: "Not enabled" } },
  { value: "on", payload: { title: "on", subTitle: "Enabled rewriting" } },
  { value: "hyde", payload: { title: "hyde", subTitle: "Pseudo document generation" } },
]);

const filterQueryResults = () => {
  if (!queryResult.value || !queryResult.value.all_results) {
    return;
  }

  let results = toRaw(queryResult.value.all_results);
  console.log("results", results);

  if (meta.filter) {
    results = results.filter((r) => r.distance >= meta.distanceThreshold);
    console.log("before", results);

    if (configStore.config.enable_reranker) {
      results = results.filter((r) => r.rerank_score >= meta.rerankThreshold);

      if (meta.sortBy === "rerank_score") {
        results = results.sort((a, b) => b.rerank_score - a.rerank_score);
      } else {
        results = results.sort((a, b) => b.distance - a.distance);
      }
    } else {
      results = results.sort((a, b) => b.distance - a.distance);
    }

    console.log("after", results);

    results = results.slice(0, meta.topK);
  }

  filteredResults.value = results;
};

const onQuery = () => {
  if (database.value.embed_model != configStore.config.embed_model) {
    message.error("Vector model mismatch, please select again");
    return;
  }

  console.log(queryText.value);
  state.searchLoading = true;
  if (!queryText.value.trim()) {
    message.error("Please enter the query content");
    state.searchLoading = false;
    return;
  }
  meta.db_id = database.value.db_id;
  fetch("/api/data/query-test", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: queryText.value.trim(),
      meta,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      queryResult.value = data;
      filterQueryResults();
    })
    .catch((error) => {
      console.error(error);
      message.error(error.message);
    })
    .finally(() => {
      state.searchLoading = false;
    });
};

const handleFileUpload = (event) => {
  console.log(event);
  console.log(fileList.value);
};

const handleDrop = (event) => {
  console.log(event);
  console.log(fileList.value);
};

const afterOpenChange = (visible) => {
  if (!visible) {
    selectedFile.value = null;
  }
};

const backToDatabase = () => {
  router.push("/database");
};

const handleRefresh = () => {
  state.refrashing = true;
  getDatabaseInfo().then(() => {
    state.refrashing = false;
    console.log(database.value);
  });
};

const deleteDatabse = () => {
  Modal.confirm({
    title: "Delete database",
    content: "Are you sure you want to delete this database?",
    okText: "Confirm",
    cancelText: "Cancel",
    onOk: () => {
      state.lock = true;
      fetch(`/api/data/?db_id=${databaseId.value}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          db_id: databaseId.value,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
          message.success(data.message);
          router.push("/database");
        })
        .catch((error) => {
          console.error(error);
          message.error(error.message);
        })
        .finally(() => {
          state.lock = false;
        });
    },
    onCancel: () => {
      console.log("Cancel");
    },
  });
};

const openFileDetail = (record) => {
  state.lock = true;
  fetch(`/api/data/document?db_id=${databaseId.value}&file_id=${record.file_id}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      if (data.status == "failed") {
        message.error(data.message);
        return;
      }
      state.lock = false;
      selectedFile.value = {
        ...record,
        lines: data.lines || [],
      };
      state.drawer = true;
    })
    .catch((error) => {
      console.error(error);
      message.error(error.message);
    });
};

const formatRelativeTime = (timestamp) => {
  const now = Date.now();
  const secondsPast = (now - timestamp) / 1000;
  if (secondsPast < 60) {
    return `${Math.round(secondsPast)} seconds ago`;
  } else if (secondsPast < 3600) {
    return `${Math.round(secondsPast / 60)} minutes ago`;
  } else if (secondsPast < 86400) {
    return `${Math.round(secondsPast / 3600)} hours ago`;
  } else {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${year} ${month} ${day}`;
  }
};

const getDatabaseInfo = () => {
  const db_id = databaseId.value;
  if (!db_id) {
    return;
  }
  state.lock = true;
  return new Promise((resolve, reject) => {
    fetch(`/api/data/info?db_id=${db_id}`, {
      method: "GET",
    })
      .then((response) => response.json())
      .then((data) => {
        database.value = data;
        resolve(data);
      })
      .catch((error) => {
        console.error(error);
        message.error(error.message);
        reject(error);
      })
      .finally(() => {
        state.lock = false;
      });
  });
};

const deleteFile = (fileId) => {
  console.log(fileId);
  Modal.confirm({
    title: "Delete file",
    content: "Are you sure you want to delete this file?",
    okText: "Confirm",
    cancelText: "Cancel",
    onOk: () => {
      state.lock = true;
      fetch("/api/data/document", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          db_id: databaseId.value,
          file_id: fileId,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
          message.success(data.message);
          getDatabaseInfo();
        })
        .catch((error) => {
          console.error(error);
          message.error(error.message);
        })
        .finally(() => {
          state.lock = false;
        });
    },
    onCancel: () => {
      console.log("Cancel");
    },
  });
};

const chunkParams = ref({
  chunk_size: 1000,
  chunk_overlap: 200,
  use_parser: false,
});

const chunkResults = ref([]);
const activeFileKeys = ref([]);

const getTotalChunks = () => {
  return chunkResults.value.reduce((total, file) => total + file.nodes.length, 0);
};

const chunkFiles = () => {
  console.log(fileList.value);
  const files = fileList.value
    .filter((file) => file.status === "done")
    .map((file) => file.response.file_path);
  console.log(files);

  if (files.length === 0) {
    message.error("Please upload files first");
    return;
  }

  state.loading = true;

  fetch("/api/data/file-to-chunk", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      files,
      params: chunkParams.value,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("File chunk information:", data);
      chunkResults.value = Object.values(data);
      activeFileKeys.value = chunkResults.value.length > 0 ? [0] : [];
    })
    .catch((error) => {
      console.error(error);
      message.error(error.message);
    })
    .finally(() => {
      state.loading = false;
    });
};

const addToDatabase = () => {
  if (chunkResults.value.length === 0) {
    message.error("No chunks to add");
    return;
  }

  state.adding = true;
  state.lock = true;

  const fileChunks = {};
  chunkResults.value.forEach((file) => {
    fileChunks[file.file_id] = file;
  });

  fetch("/api/data/add-by-chunks", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      db_id: databaseId.value,
      file_chunks: fileChunks,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);

      if (data.status === "failed") {
        message.error(data.message);
      } else {
        message.success(data.message);
        fileList.value = [];
        chunkResults.value = [];
        activeFileKeys.value = [];
      }
    })
    .catch((error) => {
      console.error(error);
      message.error(error.message);
    })
    .finally(() => {
      getDatabaseInfo();
      state.adding = false;
      state.lock = false;
    });
};

const addDocumentByFile = () => {
  console.log(
    "This function is no longer needed, replaced by chunkFiles and addToDatabase"
  );
};

const columns = [
  { title: "Filename", dataIndex: "filename", key: "filename" },
  { title: "Upload time", dataIndex: "created_at", key: "created_at" },
  { title: "Status", dataIndex: "status", key: "status" },
  { title: "Type", dataIndex: "type", key: "type" },
  { title: "Action", key: "action", dataIndex: "file_id" },
];

watch(
  () => route.params.database_id,
  (newId) => {
    databaseId.value = newId;
    console.log(newId);
    clearInterval(state.refreshInterval);
    getDatabaseInfo();
  }
);

watch(
  () => meta,
  () => {
    filterQueryResults();
  },
  { deep: true }
);

const queryExamples = ref([
  "What are the main characters of Game of Thrones?",
  "Who is the president of the United States?",
  "What is the capital of France?",
]);

const useQueryExample = (example) => {
  queryText.value = example;
  onQuery();
};

onMounted(() => {
  getDatabaseInfo();
  state.refreshInterval = setInterval(() => {
    getDatabaseInfo();
  }, 10000);
});

onUnmounted(() => {
  if (state.refreshInterval) {
    clearInterval(state.refreshInterval);
    state.refreshInterval = null;
  }
});
</script>

<template>
  <div>
    <HeaderComponent :title="database.name || 'Database information'">
      <template #description>
        <div class="database-info">
          <a-tag color="blue" v-if="database.embed_model">{{
            database.embed_model
          }}</a-tag>
          <a-tag color="green" v-if="database.dimension">{{ database.dimension }}</a-tag>
          <span class="row-count"
            >{{ database.files ? Object.keys(database.files).length : 0 }} documents ·
            {{ database.db_id }}</span
          >
        </div>
      </template>
      <template #actions>
        <a-button type="primary" @click="backToDatabase">
          <LeftOutlined /> Back
        </a-button>
        <a-button type="primary" danger @click="deleteDatabse">
          <DeleteOutlined /> Delete database
        </a-button>
      </template>
    </HeaderComponent>
    <a-alert
      v-if="
        configStore.config.embed_model &&
        database.embed_model != configStore.config.embed_model
      "
      message="Vector model does not match, please select again"
      type="warning"
      style="margin: 10px 20px"
    />
    <div class="db-main-container">
      <a-tabs v-modol="state.curPage" class="atab-container" type="card">
        <a-tab-pane key="files">
          <template #tab
            ><span> <ReadOutlined />File list </span></template
          >
          <div class="db-tab-container">
            <div class="actions">
              <a-button @click="handleRefresh" :loading="state.refrashing"
                >Refresh</a-button
              >
            </div>
            <a-table
              :columns="columns"
              :data-source="Object.values(database.files || {})"
              row-key="file_id"
              class="my-table"
            >
              <template #bodyCell="{ column, text, record }">
                <template v-if="column.key === 'filename'">
                  <a-button
                    class="main-btn"
                    type="link"
                    @click="openFileDetail(record)"
                    >{{ text }}</a-button
                  >
                </template>
                <template v-else-if="column.key === 'type'">
                  <span :class="['span-type', text]">{{ text?.toUpperCase() }}</span>
                </template>
                <template v-else-if="column.key === 'status' && text === 'done'">
                  <CheckCircleFilled style="color: #41a317" />
                </template>
                <template v-else-if="column.key === 'status' && text === 'failed'">
                  <CloseCircleFilled style="color: #ff4d4f" />
                </template>
                <template v-else-if="column.key === 'status' && text === 'processing'">
                  <HourglassFilled style="color: #1677ff" />
                </template>
                <template v-else-if="column.key === 'status' && text === 'waiting'">
                  <ClockCircleFilled style="color: #ffcd43" />
                </template>
                <template v-else-if="column.key === 'action'">
                  <a-button
                    class="del-btn"
                    type="link"
                    @click="deleteFile(text)"
                    :disabled="
                      state.lock ||
                      record.status === 'processing' ||
                      record.status === 'waiting'
                    "
                    >Delete
                  </a-button>
                </template>
                <span v-else-if="column.key === 'created_at'">{{
                  formatRelativeTime(Math.round(text * 1000))
                }}</span>
                <span v-else>{{ text }}</span>
              </template>
            </a-table>
            <a-drawer
              width="50%"
              v-model="state.drawer"
              class="custom-class"
              :title="selectedFile?.filename || 'Document Details'"
              placement="right"
              @after-open-change="afterOpenChange"
            >
              <h2>共 {{ selectedFile?.lines?.length || 0 }} 个片段</h2>
              <p
                v-for="line in selectedFile?.lines || []"
                :key="line.id"
                class="line-text"
              >
                {{ line.text }}
              </p>
            </a-drawer>
          </div>
        </a-tab-pane>

        <a-tab-pane key="add">
          <template #tab
            ><span> <CloudUploadOutlined />Add files </span></template
          >
          <div class="db-tab-container">
            <div class="upload-section">
              <div class="upload-sidebar">
                <div class="chunking-params">
                  <div class="params-info">
                    <p>
                      Adjusting the chunking parameters can control the text splitting
                      method, which affects the retrieval quality and document loading
                      efficiency.
                    </p>
                  </div>
                  <a-form
                    :model="chunkParams"
                    name="basic"
                    autocomplete="off"
                    layout="vertical"
                  >
                    <a-form-item label="Chunk Size" name="chunk_size">
                      <a-input-number
                        v-model="chunkParams.chunk_size"
                        :min="100"
                        :max="10000"
                      />
                      <p class="param-description">
                        Maximum number of characters per text fragment
                      </p>
                    </a-form-item>
                    <a-form-item label="Chunk Overlap" name="chunk_overlap">
                      <a-input-number
                        v-model="chunkParams.chunk_overlap"
                        :min="0"
                        :max="1000"
                      />
                      <p class="param-description">
                        Number of overlapping characters between adjacent text fragments
                      </p>
                    </a-form-item>
                    <a-form-item label="Use file node parser" name="use_parser">
                      <a-switch v-model="chunkParams.use_parser" />
                      <p class="param-description">
                        Enable intelligent analysis of specific file formats
                      </p>
                    </a-form-item>
                  </a-form>
                </div>
              </div>
              <div class="upload-main">
                <div class="upload">
                  <a-upload-dragger
                    class="upload-dragger"
                    v-model="fileList"
                    name="file"
                    :multiple="true"
                    :disabled="state.loading"
                    :action="'/api/data/upload?db_id=' + databaseId"
                    @change="handleFileUpload"
                    @drop="handleDrop"
                  >
                    <p class="ant-upload-text">Click or drag files here to upload</p>
                    <p class="ant-upload-hint">
                      Currently only supports uploading text files, such as .pdf, .txt,
                      .md. The same name file cannot be added repeatedly.
                    </p>
                  </a-upload-dragger>
                </div>
                <div class="actions">
                  <a-button
                    type="primary"
                    @click="chunkFiles"
                    :loading="state.loading"
                    :disabled="fileList.length === 0"
                    style="margin: 0px 20px 20px 0"
                  >
                    Generate chunks
                  </a-button>
                </div>
              </div>
            </div>

            <!-- Chunk result preview area -->
            <div class="chunk-preview" v-if="chunkResults.length > 0">
              <div class="preview-header">
                <h3>
                  Chunk preview (共 {{ chunkResults.length }} 个文件，{{
                    getTotalChunks()
                  }}
                  chunks)
                </h3>
                <a-button type="primary" @click="addToDatabase" :loading="state.adding">
                  Add to database
                </a-button>
              </div>

              <a-collapse v-model="activeFileKeys">
                <a-collapse-panel
                  v-for="(file, fileIdx) in chunkResults"
                  :key="fileIdx"
                  :header="file.filename + ' (' + file.nodes.length + ' chunks)'"
                >
                  <div id="result-cards" class="result-cards">
                    <div v-for="(chunk, index) in file.nodes" :key="index" class="chunk">
                      <p>
                        <strong>#{{ index + 1 }}</strong> {{ chunk.text }}
                      </p>
                    </div>
                  </div>
                </a-collapse-panel>
              </a-collapse>
            </div>
          </div>
        </a-tab-pane>

        <a-tab-pane key="query-test" force-render>
          <template #tab
            ><span> <SearchOutlined />Query test </span></template
          >
          <div class="query-test-container db-tab-container">
            <div class="sider">
              <div class="sider-top">
                <div class="query-params" v-if="state.curPage == 'query-test'">
                  <!-- <h3 class="params-title">查询参数</h3> -->
                  <div class="params-group">
                    <div class="params-item">
                      <p>Retrieval count:</p>
                      <a-input-number
                        size="small"
                        v-model="meta.maxQueryCount"
                        :min="1"
                        :max="20"
                      />
                    </div>
                    <div class="params-item">
                      <p>Filter low quality:</p>
                      <a-switch v-model="meta.filter" />
                    </div>
                    <div class="params-item">
                      <p>Filter TopK:</p>
                      <a-input-number
                        size="small"
                        v-model="meta.topK"
                        :min="1"
                        :max="meta.maxQueryCount"
                      />
                    </div>
                    <div class="params-item" v-if="configStore.config.enable_reranker">
                      <p>Sorting method:</p>
                      <a-radio-group
                        v-model="meta.sortBy"
                        button-style="solid"
                        size="small"
                      >
                        <a-radio-button value="rerank_score"
                          >Reranking score</a-radio-button
                        >
                        <a-radio-button value="distance">Similarity</a-radio-button>
                      </a-radio-group>
                    </div>
                  </div>
                  <div class="params-group">
                    <div
                      class="params-item w100"
                      v-if="configStore.config.enable_reranker"
                    >
                      <p>Reranking threshold:</p>
                      <a-slider
                        v-model="meta.rerankThreshold"
                        :min="0"
                        :max="1"
                        :step="0.01"
                      />
                    </div>
                    <div class="params-item w100">
                      <p>Distance threshold:</p>
                      <a-slider
                        v-model="meta.distanceThreshold"
                        :min="0"
                        :max="1"
                        :step="0.01"
                      />
                    </div>
                  </div>
                  <div class="params-group">
                    <div class="params-item col">
                      <p>Rewrite query<small>（Modified after retrieval）</small>:</p>
                      <a-segmented
                        v-model="meta.use_rewrite_query"
                        :options="use_rewrite_queryOptions"
                      >
                        <template #label="{ payload }">
                          <div>
                            <p style="margin: 4px 0">{{ payload.subTitle }}</p>
                          </div>
                        </template>
                      </a-segmented>
                    </div>
                  </div>
                </div>
              </div>
              <div class="sider-bottom" />
            </div>
            <div class="query-result-container">
              <div class="query-action">
                <a-textarea
                  v-model="queryText"
                  placeholder="Enter the query sentence"
                  :auto-size="{ minRows: 2, maxRows: 10 }"
                />
                <a-button
                  class="btn-query"
                  @click="onQuery"
                  :disabled="queryText.length == 0"
                >
                  <span v-if="!state.searchLoading"> <SearchOutlined /> Query </span>
                  <span v-else>
                    <LoadingOutlined />
                  </span>
                </a-button>
              </div>
              <div class="query-test" v-if="queryResult">
                <div class="results-overview">
                  <div class="results-stats">
                    <span class="stat-item">
                      <strong>Total:</strong> {{ queryResult.all_results.length }}
                    </span>
                    <span class="stat-item">
                      <strong>After filtering:</strong> {{ filteredResults.length }}
                    </span>
                    <span class="stat-item">
                      <strong>TopK:</strong> {{ meta.topK }}
                    </span>
                    <span class="stat-item">
                      <strong>Sorting:</strong>
                      {{
                        meta.sortBy === "rerank_score" ? "Reranking score" : "Similarity"
                      }}
                    </span>
                  </div>
                  <div class="rewritten-query" v-if="queryResult.rw_query">
                    <strong>Rewritten query:</strong>
                    <span class="query-text">{{ queryResult.rw_query }}</span>
                  </div>
                </div>
                <div
                  class="query-result-card"
                  v-for="(result, idx) in filteredResults"
                  :key="idx"
                >
                  <p>
                    <strong>#{{ idx + 1 }}&nbsp;&nbsp;&nbsp;</strong>
                    <span>{{ result.file.filename }}&nbsp;&nbsp;&nbsp;</span>
                    <span
                      ><strong>Similarity</strong>：{{
                        result.distance.toFixed(4)
                      }}&nbsp;&nbsp;&nbsp;</span
                    >
                    <span v-if="result.rerank_score"
                      ><strong>Reranking score</strong>：{{
                        result.rerank_score.toFixed(4)
                      }}</span
                    >
                  </p>
                  <p class="query-text">{{ result.entity.text }}</p>
                </div>
              </div>
            </div>
          </div>
        </a-tab-pane>
      </a-tabs>
    </div>
  </div>
</template>

<style lang="less" scoped>
.database-info {
  margin: 8px 0 0;
}

.db-main-container {
  display: flex;
  width: 100%;
}

.db-tab-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.query-test-container {
  display: flex;
  flex-direction: row;
  gap: 20px;

  .sider {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 325px;
    height: 100%;
    padding: 0;
    flex: 0 0 325px;

    .sider-top {
      .query-params {
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
        font-size: 15px;
        gap: 12px;
        padding-top: 12px;
        padding-right: 16px;
        border: 1px solid var(--main-light-3);
        background-color: var(--main-light-6);
        border-radius: 8px;
        padding: 16px;
        margin-right: 8px;

        .params-title {
          margin-top: 0;
          margin-bottom: 16px;
          color: var(--main-color);
          font-size: 18px;
          text-align: center;
          font-weight: bold;
        }

        .params-group {
          margin-bottom: 16px;
          padding-bottom: 16px;
          border-bottom: 1px solid var(--main-light-3);

          &:last-child {
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
          }
        }

        .params-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          margin-bottom: 12px;

          &:last-child {
            margin-bottom: 0;
          }

          p {
            margin: 0;
            color: var(--gray-900);
          }

          &.col {
            align-items: flex-start;
            flex-direction: column;
            width: 100%;
            height: auto;
          }

          &.w100,
          &.col {
            & > * {
              width: 100%;
            }
          }
        }

        .ant-slider {
          margin: 6px 0px;
        }
      }
    }
  }

  .query-result-container {
    flex: 1;
    padding-bottom: 20px;
  }

  .query-action {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;

    textarea {
      padding: 12px 16px;
      border: 1px solid var(--main-light-2);
    }

    button.btn-query {
      height: auto;
      width: 100px;
      box-shadow: none;
      border: none;
      font-weight: bold;
      background: var(--main-light-3);
      color: var(--main-color);

      &:disabled {
        cursor: not-allowed;
        background: var(--main-light-4);
        color: var(--gray-700);
      }
    }
  }

  .query-examples-container {
    margin-bottom: 20px;
    padding: 12px;
    background: var(--main-light-6);
    border-radius: 8px;
    border: 1px solid var(--main-light-3);

    .examples-title {
      font-weight: bold;
      margin-bottom: 10px;
      color: var(--main-color);
    }

    .query-examples {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 10px 0 0;

      .ant-btn {
        font-size: 14px;
        padding: 4px 12px;
        height: auto;
        background-color: var(--gray-200);
        border: none;
        color: var(--gray-800);

        &:hover {
          color: var(--main-color);
        }
      }
    }
  }

  .query-test {
    display: flex;
    flex-direction: column;
    border-radius: 12px;
    gap: 20px;

    .results-overview {
      background-color: #fff;
      border-radius: 8px;
      padding: 16px;
      border: 1px solid var(--main-light-3);

      .results-stats {
        display: flex;
        justify-content: flex-start;

        .stat-item {
          border-radius: 4px;
          font-size: 14px;
          margin-right: 24px;
          padding: 4px 8px;

          strong {
            color: var(--main-color);
            margin-right: 4px;
          }
        }
      }

      .rewritten-query {
        border-radius: 4px;
        font-size: 14px;
        padding: 4px 8px;

        strong {
          color: var(--main-color);
          margin-right: 8px;
        }

        .query-text {
          font-style: italic;
          color: var(--gray-900);
        }
      }
    }

    .query-result-card {
      padding: 20px;
      border-radius: 8px;
      background: #fff;
      border: 1px solid var(--main-light-3);
      transition: box-shadow 0.3s ease;

      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      }

      p {
        margin-bottom: 8px;
        line-height: 1.6;
        color: var(--gray-900);

        &:last-child {
          margin-bottom: 0;
        }
      }

      strong {
        color: var(--main-color);
      }

      .query-text {
        font-size: 15px;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid var(--main-light-3);
      }
    }
  }
}

.upload {
  margin-bottom: 20px;

  .upload-dragger {
    margin: 0px;
  }
}

.my-table {
  button.ant-btn-link {
    padding: 0;
  }

  .span-type {
    color: white;
    padding: 2px 4px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    opacity: 0.8;
    user-select: none;
    background: #005f77;
  }

  .pdf {
    background: #005f77;
  }

  .txt {
    background: #068033;
  }

  .docx,
  .doc {
    background: #2c59b7;
  }

  .md {
    background: #020817;
  }

  button.main-btn {
    font-weight: bold;
    font-size: 14px;

    &:hover {
      cursor: pointer;
      color: var(--main-color);
      font-weight: bold;
    }
  }

  button.del-btn {
    cursor: pointer;

    &:hover {
      color: var(--error-color);
    }

    &:disabled {
      cursor: not-allowed;
    }
  }
}

.custom-class .line-text {
  padding: 10px;
  border-radius: 4px;

  &:hover {
    background-color: var(--main-light-4);
  }
}

.upload-section {
  display: flex;
  gap: 20px;

  .upload-sidebar {
    width: 280px;
    padding: 20px;
    background-color: var(--main-light-6);
    border-radius: 8px;
    border: 1px solid var(--main-light-3);
    // box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

    .chunking-params {
      h4 {
        margin-top: 0;
        margin-bottom: 16px;
        color: var(--main-color);
        font-size: 18px;
        text-align: center;
        font-weight: bold;
        padding-bottom: 10px;
        border-bottom: 1px dashed var(--main-light-3);
      }

      .params-info {
        background-color: var(--main-light-4);
        border-radius: 6px;
        padding: 10px 12px;
        margin-bottom: 16px;

        p {
          margin: 0;
          font-size: 13px;
          line-height: 1.5;
          color: var(--gray-700);
        }
      }

      .ant-form-item {
        margin-bottom: 16px;

        .ant-form-item-label {
          padding-bottom: 6px;

          label {
            color: var(--gray-800);
            font-weight: 500;
            font-size: 15px;
          }
        }
      }

      .ant-input-number {
        width: 100%;
        border-radius: 6px;

        &:hover,
        &:focus {
          border-color: var(--main-color);
        }
      }

      .ant-switch {
        background-color: var(--gray-400);

        &.ant-switch-checked {
          background-color: var(--main-color);
        }
      }

      .param-description {
        color: var(--gray-600);
        font-size: 12px;
        margin-top: 4px;
        margin-bottom: 0;
      }
    }
  }

  .upload-main {
    flex: 1;
  }
}

.chunk-preview {
  margin-top: 20px;

  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      color: var(--main-color);
      font-size: 18px;
    }
  }

  .result-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
    gap: 12px;
    margin-top: 10px;
  }

  .chunk {
    background-color: var(--main-light-5);
    border: 1px solid var(--main-light-3);
    border-radius: 8px;
    padding: 16px;
    word-wrap: break-word;
    word-break: break-all;
    transition: all 0.2s ease;

    &:hover {
      background-color: var(--main-light-4);
      border-color: var(--main-light-2);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    }

    p {
      margin: 0;
      line-height: 1.6;

      strong {
        color: var(--main-color);
        margin-right: 6px;
      }
    }
  }
}
</style>

<style lang="less">
.atab-container {
  padding: 0;
  width: 100%;
  max-height: 100%;
  overflow: auto;

  div.ant-tabs-nav {
    background: var(--main-light-5);
    padding: 8px 20px;
    padding-bottom: 0;
  }

  .ant-tabs-content-holder {
    padding: 0 20px;
  }
}

.params-item.col .ant-segmented {
  width: 100%;

  div.ant-segmented-group {
    display: flex;
    justify-content: space-around;
  }
}
</style>

<style lang="less">
.db-main-container {
  .atab-container {
    padding: 0;
    width: 100%;
    max-height: 100%;
    overflow: auto;

    div.ant-tabs-nav {
      background: var(--main-light-5);
      padding: 8px 20px;
      padding-bottom: 0;
    }

    .ant-tabs-content-holder {
      padding: 0 20px;
    }
  }

  .params-item.col .ant-segmented {
    width: 100%;
    font-size: smaller;

    div.ant-segmented-group {
      display: flex;
      justify-content: space-around;
    }

    label.ant-segmented-item {
      flex: 1;
      text-align: center;

      div.ant-segmented-item-label > div > p {
        font-size: small;
      }
    }
  }
}
</style>
