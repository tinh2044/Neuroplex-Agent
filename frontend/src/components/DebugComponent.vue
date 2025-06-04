<script setup>
import {
  ref,
  onMounted,
  onActivated,
  onUnmounted,
  nextTick,
  reactive,
  computed,
} from "vue";
import { useConfigStore } from "@/stores/config";
import { useThrottleFn } from "@vueuse/core";
import dayjs from "dayjs";

const configStore = useConfigStore();
const config = configStore.config;

const logLevels = [
  { value: "INFO", label: "INFO" },
  { value: "ERROR", label: "ERROR" },
  { value: "DEBUG", label: "DEBUG" },
  { value: "WARNING", label: "WARNING" },
];

const logViewer = ref(null);

const state = reactive({
  fetching: false,
  autoRefresh: false,
  searchText: "",
  selectedLevels: logLevels.map((l) => l.value),
  rawLogs: [],
  isFullscreen: false,
});

const logs = ref("");
const error = ref("");
const logContainer = ref(null);
let autoRefreshInterval = null;

const parseLogLine = (line) => {
  const match = line.match(
    /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - ([^-]+) - (.+)$/
  );
  if (match) {
    return {
      timestamp: match[1],
      level: match[2],
      module: match[3].trim(),
      message: match[4].trim(),
      raw: line,
    };
  }
  return null;
};

const formatTimestamp = (timestamp) => {
  try {
    const normalizedTimestamp = timestamp.replace(",", ".");
    const date = dayjs(normalizedTimestamp);
    return date.isValid() ? date.format("HH:mm:ss.SSS") : timestamp;
  } catch (err) {
    console.error("Error formatting timestamp:", err);
    return timestamp;
  }
};

const processedLogs = computed(() => {
  return state.rawLogs
    .map(parseLogLine)
    .filter((log) => log !== null)
    .filter((log) => state.selectedLevels.includes(log.level))
    .filter((log) => {
      if (!state.searchText) return true;
      return log.raw.toLowerCase().includes(state.searchText.toLowerCase());
    });
});

const fetchLogs = async () => {
  state.fetching = true;
  try {
    error.value = "";
    const response = await fetch("/api/log");
    if (!response.ok) {
      throw new Error("Failed to get logs");
    }

    const data = await response.json();
    state.rawLogs = data.log.split("\n").filter((line) => line.trim());

    await nextTick();
    const scrollToBottom = useThrottleFn(() => {
      if (logContainer.value) {
        logContainer.value.scrollTop = logContainer.value.scrollHeight;
      }
    }, 100);
    scrollToBottom();
  } catch (err) {
    error.value = `Failed to get logs: ${err.message}`;
  } finally {
    state.fetching = false;
  }
};

const clearLogs = () => {
  state.rawLogs = [];
};

const onSearch = () => {};

const filterLogs = () => {};

const toggleAutoRefresh = (value) => {
  if (value) {
    autoRefreshInterval = setInterval(fetchLogs, 5000);
    state.autoRefresh = true;
  } else {
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
      autoRefreshInterval = null;
    }
    state.autoRefresh = false;
  }
};

const toggleFullscreen = async () => {
  try {
    if (!state.isFullscreen) {
      if (logViewer.value.requestFullscreen) {
        await logViewer.value.requestFullscreen();
      } else if (logViewer.value.webkitRequestFullscreen) {
        await logViewer.value.webkitRequestFullscreen();
      } else if (logViewer.value.msRequestFullscreen) {
        await logViewer.value.msRequestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        await document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        await document.webkitExitFullscreen();
      } else if (document.msExitFullscreen) {
        await document.msExitFullscreen();
      }
    }
  } catch (err) {
    console.error("Failed to toggle fullscreen:", err);
  }
};

const handleFullscreenChange = () => {
  state.isFullscreen = Boolean(
    document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.msFullscreenElement
  );
};

onMounted(() => {
  fetchLogs();
  document.addEventListener("fullscreenchange", handleFullscreenChange);
  document.addEventListener("webkitfullscreenchange", handleFullscreenChange);
  document.addEventListener("msfullscreenchange", handleFullscreenChange);
});

onActivated(() => {
  if (state.autoRefresh) {
    toggleAutoRefresh(true);
  } else {
    fetchLogs();
  }
});

onUnmounted(() => {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
  document.removeEventListener("fullscreenchange", handleFullscreenChange);
  document.removeEventListener("webkitfullscreenchange", handleFullscreenChange);
  document.removeEventListener("msfullscreenchange", handleFullscreenChange);
});

const printConfig = () => {
  console.log("Current config:", config);
};
</script>

<template>
  <div :class="['log-viewer', { fullscreen: state.isFullscreen }]" ref="logViewer">
    <div class="control-panel">
      <div class="button-group">
        <a-button @click="fetchLogs" :loading="state.fetching">
          <template #icon><ReloadOutlined /></template>
          Refresh
        </a-button>
        <a-button @click="clearLogs">
          <template #icon><ClearOutlined /></template>
          Clear
        </a-button>
        <a-button @click="printConfig">
          <template #icon><SettingOutlined /></template>
          Print Config
        </a-button>
        <a-button @click="toggleFullscreen">
          <template #icon>
            <FullscreenOutlined v-if="!state.isFullscreen" />
            <FullscreenExitOutlined v-else />
          </template>
          {{ state.isFullscreen ? "Exit Fullscreen" : "Fullscreen" }}
        </a-button>
        <a-tooltip
          :title="
            state.autoRefresh
              ? 'Click to stop auto refresh'
              : 'Click to start auto refresh'
          "
        >
          <a-button
            :type="state.autoRefresh ? 'primary' : 'default'"
            @click="toggleAutoRefresh(!state.autoRefresh)"
          >
            <template #icon>
              <SyncOutlined :spin="state.autoRefresh" />
            </template>
            Auto Refresh
            <span v-if="state.autoRefresh" class="refresh-interval">(5s)</span>
          </a-button>
        </a-tooltip>
      </div>
      <div class="filter-group">
        <a-input-search
          :value="state.searchText"
          placeholder="Search logs..."
          style="width: 200px"
          @search="onSearch"
        />
        <a-select
          :value="state.selectedLevels"
          mode="multiple"
          placeholder="Select log level"
          :options="logLevels"
          @change="filterLogs"
        />
      </div>
    </div>
    <div ref="logContainer" class="log-container">
      <div v-if="processedLogs.length" class="log-lines">
        <div
          v-for="(log, index) in processedLogs"
          :key="index"
          :class="['log-line', `level-${log.level.toLowerCase()}`]"
        >
          <span class="timestamp">{{ formatTimestamp(log.timestamp) }}</span>
          <span class="level">{{ log.level }}</span>
          <span class="module">{{ log.module }}</span>
          <span class="message">{{ log.message }}</span>
        </div>
      </div>
      <div v-else class="empty-logs">No logs</div>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<style lang="less" scoped>
.log-viewer {
  background: white;
  height: 100%;
}

.log-viewer.fullscreen {
  padding: 16px;
}

.control-panel {
  margin-bottom: 16px;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;

  .refresh-interval {
    font-size: 12px;
    opacity: 0.8;
    margin-left: 2px;
  }
}

.filter-group {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.error {
  color: var(--error-color);
}

.log-container {
  height: calc(100vh - 200px);
  overflow-y: auto;
  background: #0c0c0c;
  color: #d1d1d1;
  border-radius: 5px;
  font-family: "Consolas", "Monaco", monospace;
  font-size: 13px;
}

.log-lines {
  padding: 8px;
}

.log-line {
  padding: 2px 4px;
  display: flex;
  gap: 8px;
  line-height: 1.4;
}

.log-line:hover {
  background: rgba(255, 255, 255, 0.05);
}

.timestamp {
  color: #6a9955;
  min-width: 80px;
}

.level {
  min-width: 40px;
  font-weight: bold;
}

.module {
  color: #569cd6;
  min-width: 30px;
}

.message {
  flex: 1;
  white-space: pre-wrap;
  word-break: break-all;
}

.level-info {
  .level {
    color: #4ec9b0;
  }
}

.level-error {
  .level {
    color: #f14c4c;
  }
}

.level-debug {
  .level {
    color: #9cdcfe;
  }
}

.level-warning {
  .level {
    color: #dcd900;
  }
}

.empty-logs {
  padding: 16px;
  text-align: center;
  color: #666;
}

@media (prefers-color-scheme: dark) {
  .log-container {
    background: #1e1e1e;
  }
}

:fullscreen .log-container {
  height: calc(100vh - 120px);
}

:-webkit-full-screen .log-container {
  height: calc(100vh - 120px);
}

:-ms-fullscreen .log-container {
  height: calc(100vh - 120px);
}
</style>
