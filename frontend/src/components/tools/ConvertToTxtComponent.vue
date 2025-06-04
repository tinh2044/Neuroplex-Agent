<template>
  <div class="pdf2txt-container">
    <div class="sidebar">
      <div class="additional-params">
        <h4>Related Parameters</h4>
        <p>No related parameters</p>
      </div>
    </div>
    <div class="result-container">
      <div class="input-container">
        <div class="upload">
          <a-upload-dragger
            class="upload-dragger"
            v-model="fileList"
            name="file"
            :max-count="1"
            :disabled="state.uploading"
            action="/api/data/upload"
            @change="handleFileUpload"
            @drop="handleDrop"
          >
            <p class="ant-upload-text">
              Click or drag and drop the PDF file here to upload
            </p>
            <p class="ant-upload-hint">
              Only PDF files are supported. Duplicate files cannot be added.
            </p>
          </a-upload-dragger>
        </div>
        <a-button type="primary" @click="convertPdfToText" :loading="state.loading"
          >Convert PDF to Text</a-button
        >
      </div>
      <div class="output-container">
        <textarea
          v-model="convertedText"
          placeholder="Converted text will appear here"
          readonly
        />
        <div class="infos">
          <span>Character count: {{ charCount }}</span>
          <span>Token count: {{ estimatedTokenCount }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from "vue";
import { message } from "ant-design-vue";

const state = reactive({
  loading: false,
  uploading: false,
});

const fileList = ref([]);
const convertedText = ref("");

const charCount = computed(() => convertedText.value.length);
const estimatedTokenCount = computed(() => {
  const chars = convertedText.value.split("");
  let tokenCount = 0;
  for (const char of chars) {
    if (/[\u4e00-\u9fff]/.test(char)) {
      tokenCount += 1;
    } else if (/[a-zA-Z]/.test(char)) {
      tokenCount += 0.25;
    } else {
      tokenCount += 0.5;
    }
  }
  return Math.ceil(tokenCount);
});

const handleFileUpload = (info) => {
  const { status } = info.file;
  if (status !== "uploading") {
    console.log(info.file, info.fileList);
  }
  if (status === "done") {
    message.success(`${info.file.name} file uploaded successfully.`);
  } else if (status === "error") {
    message.error(`${info.file.name} file upload failed.`);
  }
};

const handleDrop = (e) => {
  console.log(e);
};

const convertPdfToText = async () => {
  if (fileList.value.length === 0) {
    message.error("Please upload a PDF file");
    return;
  }

  const file = fileList.value[0].response.file_path;

  try {
    state.loading = true;
    const response = await fetch("/api/tool/pdf2txt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(file.toString()),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    convertedText.value = data.text;
    state.loading = false;
  } catch (error) {
    console.error("Error converting PDF to text:", error);
    message.error("Failed to convert PDF to text, please try again");
    state.loading = false;
  }
};
</script>

<style lang="less" scoped>
.pdf2txt-container {
  display: flex;
  border-radius: 8px;
  font-family: "Arial", sans-serif;

  .sidebar {
    position: sticky;
    top: 0;
    width: 350px;
    background-color: var(--bg-sider);
    border-right: 1px solid var(--main-light-3);
    padding: 20px;
    min-width: 250px;
    flex: 1;

    .additional-params {
      h4 {
        font-size: 1.2em;
        margin-bottom: 10px;
      }
    }
  }

  .result-container {
    flex: 3;
    padding: 20px;

    .input-container {
      display: flex;
      flex-direction: column;
      margin-bottom: 15px;

      .upload {
        margin-bottom: 15px;
      }
    }

    .output-container {
      textarea {
        width: 100%;
        height: 300px;
        resize: vertical;
        padding: 1rem;
        border: 1px solid var(--gray-300);
        border-radius: 8px;
        font-size: 1rem;
        transition: border-color 0.3s;
        background-color: var(--gray-100);

        &:focus {
          border-color: var(--main-color);
          outline: none;
        }
      }

      .infos {
        padding: 10px;
        margin-top: 10px;
        font-size: 1em;
        color: var(--gray-800);
        display: flex;
        gap: 16px;
      }
    }
  }
}
</style>
