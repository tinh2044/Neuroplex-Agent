<script setup>
import { ref, reactive, KeepAlive, onMounted, computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import {
  MessageOutlined,
  MessageFilled,
  SettingOutlined,
  SettingFilled,
  BookOutlined,
  BookFilled,
  GithubOutlined,
  ToolFilled,
  ToolOutlined,
  BugOutlined,
  ProjectFilled,
  ProjectOutlined,
} from "@ant-design/icons-vue";
import { themeConfig } from "@/assets/theme";
import { useConfigStore } from "@/stores/config";
import { useDatabaseStore } from "@/stores/database";
import DebugComponent from "@/components/DebugComponent.vue";

const configStore = useConfigStore();
const databaseStore = useDatabaseStore();

const layoutSettings = reactive({
  showDebug: false,
  useTopBar: false,
});

const githubStars = ref(0);
const isLoadingStars = ref(false);

const getRemoteConfig = () => {
  configStore.refreshConfig();
};

const getRemoteDatabase = () => {
  if (!configStore.config.enable_knowledge_base) {
    return;
  }
  databaseStore.refreshDatabase();
};

const fetchGithubStars = async () => {
  try {
    isLoadingStars.value = true;
    const response = await fetch("https://api.github.com/repos/tinh2044/Neuroplex-Agent");
    const data = await response.json();
    githubStars.value = data.stargazers_count;
  } catch (error) {
    console.error("Error fetching GitHub stars:", error);
  } finally {
    isLoadingStars.value = false;
  }
};

onMounted(() => {
  getRemoteConfig();
  getRemoteDatabase();
  fetchGithubStars();
});

const route = useRoute();

const mainList = [
  {
    name: "Chat",
    path: "/chat",
    icon: MessageOutlined,
    activeIcon: MessageFilled,
  },
  {
    name: "Graph",
    path: "/graph",
    icon: ProjectOutlined,
    activeIcon: ProjectFilled,
    // hidden: !configStore.config.enable_knowledge_graph,
  },
  {
    name: "Knowledge Base",
    path: "/database",
    icon: BookOutlined,
    activeIcon: BookFilled,
    // hidden: !configStore.config.enable_knowledge_base,
  },
  {
    name: "Tools",
    path: "/tools",
    icon: ToolOutlined,
    activeIcon: ToolFilled,
  },
];
</script>

<template>
  <div class="app-layout" :class="{ 'use-top-bar': layoutSettings.useTopBar }">
    <div class="debug-panel">
      <a-float-button
        @click="layoutSettings.showDebug = !layoutSettings.showDebug"
        tooltip="Debug panel"
        :style="{
          right: '12px',
        }"
      >
        <template #icon>
          <BugOutlined />
        </template>
      </a-float-button>
      <a-drawer
        v-model="layoutSettings.showDebug"
        title="Debug"
        width="800"
        :contentWrapperStyle="{ maxWidth: '100%' }"
        placement="right"
      >
        <DebugComponent />
      </a-drawer>
    </div>
    <div class="header" :class="{ 'top-bar': layoutSettings.useTopBar }">
      <div class="logo circle">
        <RouterLink to="/">
          <img src="/logo.png" />
          <span class="logo-text">Neuroplex</span>
        </RouterLink>
      </div>
      <div class="nav">
        <RouterLink
          v-for="(item, index) in mainList"
          :key="index"
          :to="item.path"
          v-show="!item.hidden"
          class="nav-item"
          active-class="active"
        >
          <component
            class="icon"
            :is="route.path.startsWith(item.path) ? item.activeIcon : item.icon"
          />
          <span class="text">{{ item.name }}</span>
        </RouterLink>
      </div>
      <div class="fill" style="flex-grow: 1" />
      <div class="github nav-item">
        <a-tooltip placement="right">
          <template #title>GitHub</template>
          <a
            href="https://github.com/tinh2044/Neuroplex-Agent"
            target="_blank"
            class="github-link"
          >
            <GithubOutlined class="icon" style="color: #222" />
            <span v-if="githubStars > 0" class="github-stars">
              <span class="star-count">{{ githubStars.toFixed(1) }}</span>
            </span>
          </a>
        </a-tooltip>
      </div>
      <RouterLink class="nav-item setting" to="/setting" active-class="active">
        <a-tooltip placement="right">
          <template #title>Setting</template>
          <component
            class="icon"
            :is="route.path === '/setting' ? SettingFilled : SettingOutlined"
          />
        </a-tooltip>
      </RouterLink>
    </div>
    <div class="header-mobile">
      <RouterLink to="/chat" class="nav-item" active-class="active">Chat</RouterLink>
      <RouterLink to="/database" class="nav-item" active-class="active"
        >DataBase</RouterLink
      >
      <RouterLink to="/setting" class="nav-item" active-class="active"
        >Setting</RouterLink
      >
    </div>
    <a-config-provider :theme="themeConfig">
      <RouterView v-slot="{ Component, route }" id="app-router-view">
        <KeepAlive v-if="route.meta.keepAlive !== false">
          <component :is="Component" />
        </KeepAlive>
        <component :is="Component" v-else />
      </RouterView>
    </a-config-provider>
  </div>
</template>

<style lang="less" scoped>
@import "@/assets/main.css";

.app-layout {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100vh;
  min-width: var(--min-width);

  .header-mobile {
    display: none;
  }

  .debug-panel {
    position: absolute;
    z-index: 100;
    right: 0;
    bottom: 50px;
    border-radius: 20px 0 0 20px;
    cursor: pointer;
  }
}

div.header,
#app-router-view {
  height: 100%;
  max-width: 100%;
  user-select: none;
}

#app-router-view {
  flex: 1 1 auto;
  overflow-y: auto;
}

.header {
  display: flex;
  flex-direction: column;
  flex: 0 0 70px;
  justify-content: flex-start;
  align-items: center;
  background-color: var(--gray-100);
  height: 100%;
  width: 70px;
  border-right: 1px solid var(--gray-300);

  .logo {
    width: 60px;
    height: 60px;
    margin: 14px 0 14px 0;

    img {
      width: 100%;
      height: 100%;
      border-radius: 4px; // 50% for circle
    }

    .logo-text {
      display: none;
    }

    & > a {
      text-decoration: none;
      font-size: 24px;
      font-weight: bold;
      color: #333;
    }
  }

  .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 52px;
    padding: 4px;
    padding-top: 10px;
    border: 1px solid transparent;
    border-radius: 8px;
    background-color: transparent;
    color: #222;
    font-size: 20px;
    transition: background-color 0.2s ease-in-out;
    margin: 0;
    text-decoration: none;
    cursor: pointer;

    &.github {
      padding: 10px 12px;

      &:hover {
        background-color: transparent;
        border: 1px solid transparent;
      }

      .github-link {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: inherit;
      }

      .github-stars {
        display: flex;
        align-items: center;
        font-size: 12px;
        margin-top: 4px;

        .star-icon {
          color: #f0a742;
          font-size: 12px;
          margin-right: 2px;
        }

        .star-count {
          font-weight: 600;
        }
      }
    }

    &.api-docs {
      padding: 10px 12px;
    }

    &.active {
      font-weight: bold;
      color: var(--main-600);
      background-color: white;
      border: 1px solid white;
    }

    &.warning {
      color: red;
    }

    &:hover {
      background-color: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(10px);
    }

    .text {
      font-size: 12px;
      margin-top: 4px;
      text-align: center;
    }
  }

  .setting {
    width: auto;
    font-size: 20px;
    color: #333;
    margin-bottom: 20px;
    margin-top: 10px;
    padding: 16px 12px;

    &:hover {
      cursor: pointer;
    }
  }
}

.header .nav {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  position: relative;
  height: 45px;
  gap: 16px;
}

@media (max-width: 520px) {
  .app-layout {
    flex-direction: column-reverse;

    div.header {
      display: none;
    }

    .debug-panel {
      bottom: 10rem;
    }
  }

  .app-layout div.header-mobile {
    display: flex;
    flex-direction: row;
    width: 100%;
    padding: 0 20px;
    justify-content: space-around;
    align-items: center;
    flex: 0 0 60px;
    border-right: none;
    height: 40px;

    .nav-item {
      text-decoration: none;
      width: 40px;
      color: var(--gray-900);
      font-size: 1rem;
      font-weight: bold;
      transition: color 0.1s ease-in-out, font-size 0.1s ease-in-out;

      &.active {
        color: black;
        font-size: 1.1rem;
      }
    }
  }

  .app-layout .chat-box::webkit-scrollbar {
    width: 0;
  }
}

.app-layout.use-top-bar {
  flex-direction: column;
}

.header.top-bar {
  flex-direction: row;
  flex: 0 0 50px;
  width: 100%;
  height: 50px;
  border-right: none;
  border-bottom: 1px solid var(--main-light-2);
  background-color: var(--main-light-3);
  padding: 0 20px;
  gap: 24px;

  .logo {
    width: fit-content;
    height: 28px;
    margin-right: 16px;
    display: flex;
    align-items: center;

    a {
      display: flex;
      align-items: center;
      text-decoration: none;
      color: inherit;
    }

    img {
      width: 28px;
      height: 28px;
      margin-right: 8px;
    }

    .logo-text {
      display: block;
      font-size: 16px;
      font-weight: 600;
      letter-spacing: 0.5px;
      color: var(--main-600);
      white-space: nowrap;
    }
  }

  .nav {
    flex-direction: row;
    height: auto;
    gap: 20px;
  }

  .nav-item {
    flex-direction: row;
    width: auto;
    padding: 4px 16px;
    margin: 0;

    .icon {
      margin-right: 8px;
      font-size: 15px;
    }

    .text {
      margin-top: 0;
      font-size: 15px;
    }

    &.github,
    &.setting {
      padding: 8px 12px;

      .icon {
        margin-right: 0;
        font-size: 18px;
      }

      &.active {
        color: var(--main-600);
      }
    }

    &.github {
      a {
        display: flex;
        align-items: center;
      }

      .github-stars {
        display: flex;
        align-items: center;
        margin-left: 6px;

        .star-icon {
          color: #f0a742;
          font-size: 14px;
          margin-right: 2px;
        }
      }
    }
  }
}
</style>
