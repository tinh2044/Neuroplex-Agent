<script setup>
import { Graph } from "@antv/g6";
import { computed, onMounted, reactive, ref } from "vue";
import { message, Button as AButton } from "ant-design-vue";
import { useConfigStore } from "@/stores/config";
import { UploadOutlined, SyncOutlined } from "@ant-design/icons-vue";
import HeaderComponent from "@/components/HeaderComponent.vue";

const configStore = useConfigStore();
const cur_embed_model = computed(
  () =>
    configStore.config?.embed_model_names?.[configStore.config?.embed_model]?.name || ""
);
const modelMatched = computed(
  () =>
    !graphInfo?.value?.embed_model_name ||
    graphInfo.value.embed_model_name === cur_embed_model.value
);
const disabled = computed(() => state.precessing || !modelMatched.value);

let graphInstance;
const graphInfo = ref(null);
const container = ref(null);
const fileList = ref([]);
const sampleNodeCount = ref(100);
const graphData = reactive({
  nodes: [],
  edges: [],
});

const state = reactive({
  fetching: false,
  loadingGraphInfo: false,
  searchInput: "",
  searchLoading: false,
  showModal: false,
  precessing: false,
  indexing: false,
  showPage: computed(
    () =>
      configStore.config.enable_knowledge_base &&
      configStore.config.enable_knowledge_graph
  ),
});

const unindexedCount = computed(() => {
  return graphInfo.value?.unindexed_node_count || 0;
});

const loadGraphInfo = () => {
  state.loadingGraphInfo = true;
  fetch("/api/data/graph", {
    method: "GET",
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      graphInfo.value = data;
      state.loadingGraphInfo = false;
    })
    .catch((error) => {
      console.error(error);
      message.error(error.message);
      state.loadingGraphInfo = false;
    });
};

const getGraphData = () => {
  const nodeDegrees = {};

  graphData.nodes.forEach((node) => {
    nodeDegrees[node.id] = 0;
  });

  graphData.edges.forEach((edge) => {
    nodeDegrees[edge.source_id] = (nodeDegrees[edge.source_id] || 0) + 1;
    nodeDegrees[edge.target_id] = (nodeDegrees[edge.target_id] || 0) + 1;
  });

  return {
    nodes: graphData.nodes.map((node) => {
      const degree = nodeDegrees[node.id] || 0;
      const nodeSize = Math.min(15 + degree * 5, 50);

      return {
        id: node.id,
        data: {
          label: node.name,
          degree,
        },
      };
    }),
    edges: graphData.edges.map((edge) => {
      return {
        source: edge.source_id,
        target: edge.target_id,
        data: {
          label: edge.type,
        },
      };
    }),
  };
};

const addDocumentByFile = () => {
  state.precessing = true;
  const files = fileList.value
    .filter((file) => file.status === "done")
    .map((file) => file.response.file_path);
  fetch("/api/data/graph/add-by-jsonl", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      file_path: files[0],
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        message.success(data.message);
        state.showModal = false;
      } else {
        throw new Error(data.message);
      }
    })
    .catch((error) => {
      console.error(error);
      message.error(error.message);
    })
    .finally(() => (state.precessing = false));
};

const loadSampleNodes = () => {
  state.fetching = true;
  fetch(`/api/data/graph/nodes?kgdb_name=neo4j&num=${sampleNodeCount.value}`)
    .then((res) => {
      if (res.ok) {
        return res.json();
      } else if (configStore?.config && !configStore?.config.enable_knowledge_graph) {
        throw new Error(
          "Please go to the settings page to configure and enable the knowledge graph"
        );
      } else {
        throw new Error("Loading failed");
      }
    })
    .then((data) => {
      graphData.nodes = data.result.nodes;
      graphData.edges = data.result.edges;
      console.log(graphData);
      setTimeout(() => randerGraph(), 500);
    })
    .catch((error) => {
      message.error(error.message);
    })
    .finally(() => (state.fetching = false));
};

const onSearch = () => {
  if (state.searchLoading) {
    message.error("Please try again later");
    return;
  }

  if (graphInfo?.value?.embed_model_name !== cur_embed_model.value) {
    if (!graphInfo?.value?.embed_model_name) {
      message.error("Please upload the file first (json)");
      return;
    }

    if (
      !confirm(
        `The vector model when building a graph database is ${graphInfo?.value?.embed_model_name}，current vector model is ${cur_embed_model.value}，continue to query?`
      )
    ) {
      return;
    }
  }

  if (!state.searchInput) {
    message.error("Please enter the entity to query");
    return;
  }

  state.searchLoading = true;
  fetch(`/api/data/graph/node?entity_name=${state.searchInput}`)
    .then((res) => {
      if (!res.ok) {
        return res.json().then((errorData) => {
          throw new Error(
            errorData.message || `Query failed: ${res.status} ${res.statusText}`
          );
        });
      }
      return res.json();
    })
    .then((data) => {
      if (!data.result || !data.result.nodes || !data.result.edges) {
        throw new Error("The returned data format is incorrect");
      }
      graphData.nodes = data.result.nodes;
      graphData.edges = data.result.edges;
      if (graphData.nodes.length === 0) {
        message.info("No related entities found");
      }
      console.log(data);
      console.log(graphData);
      randerGraph();
    })
    .catch((error) => {
      console.error("Query error:", error);
      message.error(`Query error: ${error.message}`);
    })
    .finally(() => (state.searchLoading = false));
};

const randerGraph = () => {
  if (graphInstance) {
    graphInstance.destroy();
  }

  initGraph();
  graphInstance.setData(getGraphData());
  graphInstance.render();
};

const initGraph = () => {
  graphInstance = new Graph({
    container: container.value,
    width: container.value.offsetWidth,
    height: container.value.offsetHeight,
    autoFit: true,
    autoResize: true,
    layout: {
      type: "d3-force",
      preventOverlap: true,
      collide: {
        radius: 40,
        strength: 0.5,
      },
    },
    node: {
      type: "circle",
      style: {
        labelText: (d) => d.data.label,
        size: (d) => {
          const degree = d.data.degree || 0;
          return Math.min(15 + degree * 5, 50);
        },
      },
      palette: {
        field: "label",
        color: "tableau",
      },
    },
    edge: {
      type: "line",
      style: {
        labelText: (d) => d.data.label,
        labelBackground: "#fff",
        endArrow: true,
      },
    },
    behaviors: ["drag-element", "zoom-canvas", "drag-canvas"],
  });
  window.addEventListener("resize", randerGraph);
};

onMounted(() => {
  loadGraphInfo();
  loadSampleNodes();
});

const handleFileUpload = (event) => {
  console.log(event);
  console.log(fileList.value);
};

const handleDrop = (event) => {
  console.log(event);
  console.log(fileList.value);
};

const graphStatusClass = computed(() => {
  if (state.loadingGraphInfo) return "loading";
  return graphInfo.value?.status === "open" ? "open" : "closed";
});

const graphStatusText = computed(() => {
  if (state.loadingGraphInfo) return "加载中";
  return graphInfo.value?.status === "open" ? "已连接" : "已关闭";
});

const graphDescription = computed(() => {
  const dbName = graphInfo.value?.graph_name || "";
  const entityCount = graphInfo.value?.entity_count || 0;
  const relationCount = graphInfo.value?.relationship_count || 0;
  const modelName = graphInfo.value?.embed_model_name || "No file uploaded";
  const unindexed =
    unindexedCount.value > 0 ? `, ${unindexedCount.value} nodes not indexed` : "";

  return `${dbName} - ${entityCount} entities, ${relationCount} relationships. Vector model: ${modelName}${unindexed}`;
});

const indexNodes = () => {
  if (!modelMatched.value) {
    message.error(
      `The vector model does not match, cannot add an index, the current vector model is ${cur_embed_model.value}, the graph database vector model is ${graphInfo.value?.embed_model_name}`
    );
    return;
  }

  if (state.precessing) {
    message.error("The background is processing, please try again later");
    return;
  }

  state.indexing = true;
  fetch("/api/data/graph/index-nodes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      kgdb_name: "neo4j",
    }),
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((errorData) => {
          throw new Error(
            errorData.detail ||
              `Request failed: ${response.status} ${response.statusText}`
          );
        });
      }
      return response.json();
    })
    .then((data) => {
      message.success(data.message);
      loadGraphInfo();
    })
    .catch((error) => {
      console.error(error);
      message.error(error.message || "Failed to add index");
    })
    .finally(() => {
      state.indexing = false;
    });
};
</script>

<template>
  <div class="database-empty" v-if="!state.showPage">
    <a-empty>
      <template #description>
        <span>
          Go to the
          <router-link to="/setting" style="color: var(--main-color); font-weight: bold"
            >Settings</router-link
          >
          page to enable the knowledge graph.
        </span>
      </template>
    </a-empty>
  </div>
  <div class="graph-container layout-container" v-else>
    <HeaderComponent title="Graph Database" :description="graphDescription">
      <template #actions>
        <div class="status-wrapper">
          <div class="status-indicator" :class="graphStatusClass" />
        </div>
        <AButton type="primary" @click="state.showModal = true"
          ><UploadOutlined /> Upload File</AButton
        >
        <AButton
          v-if="unindexedCount > 0"
          type="primary"
          @click="indexNodes"
          :loading="state.indexing"
        >
          <SyncOutlined /> Add index to {{ unindexedCount }} nodes
        </AButton>
      </template>
    </HeaderComponent>

    <div class="actions">
      <div class="actions-left">
        <input
          v-model="state.searchInput"
          placeholder="Enter the entity to query"
          style="width: 200px"
          @keydown.enter="onSearch"
        />
        <AButton
          type="primary"
          :loading="state.searchLoading"
          :disabled="state.searchLoading"
          @click="onSearch"
        >
          Query entity
        </AButton>
      </div>
      <div class="actions-right">
        <input v-model="sampleNodeCount" />
        <AButton @click="loadSampleNodes" :loading="state.fetching">Get nodes</AButton>
      </div>
    </div>
    <div
      class="main"
      id="container"
      ref="container"
      v-show="graphData.nodes.length > 0"
    />
    <a-empty v-show="graphData.nodes.length === 0" style="padding: 4rem 0" />

    <a-modal
      :open="state.showModal"
      title="Upload File"
      @ok="addDocumentByFile"
      @cancel="() => (state.showModal = false)"
      ok-text="Add to graph database"
      cancel-text="Cancel"
      :ok-button-props="{ disabled: disabled }"
      :confirm-loading="state.precessing"
    >
      <div v-if="graphInfo?.embed_model_name">
        <a-alert
          v-if="!modelMatched"
          message="The model does not match, building an index may result in no retrieval!"
          type="warning"
        />
        <p>
          The current graph database vector model: {{ graphInfo?.embed_model_name }}, the
          current vector model is {{ cur_embed_model }}
        </p>
      </div>
      <p v-else>
        After the first creation, the vector model cannot be modified, the current vector
        model is {{ cur_embed_model }}
      </p>
      <div class="upload">
        <a-upload-dragger
          class="upload-dragger"
          :fileList="fileList"
          name="file"
          :max-count="1"
          :disabled="disabled"
          action="/api/data/upload"
          @change="handleFileUpload"
          @drop="handleDrop"
        >
          <p class="ant-upload-text">Click or drag the file here to upload</p>
          <p class="ant-upload-hint">
            Currently only jsonl files are supported. The same name file cannot be added
            repeatedly.
          </p>
        </a-upload-dragger>
      </div>
    </a-modal>
  </div>
</template>

<style lang="less" scoped>
.graph-container {
  padding: 0;
}

.status-wrapper {
  display: flex;
  align-items: center;
  margin-right: 16px;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.65);
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;

  &.loading {
    background-color: #faad14;
    animation: pulse 1.5s infinite ease-in-out;
  }

  &.open {
    background-color: #52c41a;
  }

  &.closed {
    background-color: #f5222d;
  }
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
}

.actions {
  display: flex;
  justify-content: space-between;
  margin: 20px 0;
  padding: 0 24px;

  .actions-left,
  .actions-right {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  input {
    width: 100px;
    border-radius: 8px;
    padding: 4px 12px;
    border: 2px solid var(--main-300);
    outline: none;
    height: 42px;

    &:focus {
      border-color: var(--main-color);
    }
  }

  button {
    border-width: 2px;
    height: 40px;
    box-shadow: none;
  }
}

.upload {
  margin-bottom: 20px;

  .upload-dragger {
    margin: 0px;
  }
}

#container {
  background: #f7f7f7;
  margin: 20px 24px;
  border-radius: 16px;
  width: calc(100% - 48px);
  height: calc(100vh - 200px);
  resize: horizontal;
  overflow: hidden;
}

.database-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  flex-direction: column;
  color: var(--gray-900);
}
</style>
