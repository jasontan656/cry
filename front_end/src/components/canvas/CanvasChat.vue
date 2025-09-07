<template>
  <div class="canvas-chat-panel">
    <h4>Messages</h4>
    <div class="canvas-chat-wrap">
      <!-- Thread List -->
      <div class="canvas-chat-thread-list">
        <el-input
          placeholder="Search messages…"
          prefix-icon="el-icon-search"
          class="canvas-chat-mb8"
          v-model="searchQuery"
        />
        <el-menu
          default-active="1"
          class="canvas-chat-thread-menu"
          @select="handleSelect"
          v-model="activeThread"
        >
          <el-menu-item index="1">HR – Acme Corp</el-menu-item>
          <el-menu-item index="2">Maria S. (Applicant)</el-menu-item>
          <el-menu-item index="3">Hiring Team</el-menu-item>
        </el-menu>
      </div>

      <!-- Thread Body -->
      <div class="canvas-chat-thread-body">
        <div v-for="(message, index) in filteredMessages" :key="index" :class="['canvas-chat-bubble', message.side]">
          {{ message.text }}
        </div>

        <!-- Message Composer -->
        <div class="canvas-chat-composer">
          <el-input
            type="textarea"
            rows="2"
            placeholder="Write a message…"
            v-model="messageInput"
          />
          <el-button
            type="primary"
            size="small"
            class="canvas-chat-mt8"
            @click="sendMessage"
            :disabled="!messageInput"
          >
            Send
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CanvasChat',
  data() {
    return {
      activeThread: '1',
      messageInput: '',
      searchQuery: '',
      messages: {
        '1': [
          { side: 'left', text: 'Hi, thanks for applying! Can you share your portfolio?' },
          { side: 'right', text: 'Sure—here’s the link and my recent projects.' },
        ],
        '2': [
          { side: 'left', text: 'Hey Maria, how are you today?' },
          { side: 'right', text: 'I’m good, thanks! How about you?' },
        ],
        '3': [
          { side: 'left', text: 'Please confirm the interview schedule for tomorrow.' },
          { side: 'right', text: 'Got it! Looking forward to it.' },
        ],
      },
    };
  },
  computed: {
    filteredMessages() {
      // Filter messages based on active thread and search query
      return this.messages[this.activeThread].filter((message) =>
        message.text.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
  },
  methods: {
    handleSelect(index) {
      this.activeThread = index;
    },
    sendMessage() {
      if (this.messageInput.trim()) {
        const newMessage = { side: 'right', text: this.messageInput };
        this.messages[this.activeThread].push(newMessage);
        this.messageInput = ''; // Clear input after sending
        this.$nextTick(() => {
          const chatBody = this.$el.querySelector('.canvas-chat-thread-body');
          chatBody.scrollTop = chatBody.scrollHeight; // Auto-scroll to bottom
        });
      }
    },
  },
};
</script>

<style scoped>
.canvas-chat-panel {
  padding: 20px;
}

.canvas-chat-wrap {
  display: flex;
  gap: 20px;
}

.canvas-chat-thread-list {
  flex: 1 1 250px;
  min-width: 250px;
  border-right: 1px solid #e4e7ed;
  padding-right: 20px;
}

.canvas-chat-thread-menu {
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.canvas-chat-thread-body {
  flex: 2 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.canvas-chat-bubble {
  max-width: 60%;
  padding: 10px;
  border-radius: 5px;
  word-wrap: break-word;
}

.canvas-chat-bubble.left {
  background-color: #f0f0f0;
  align-self: flex-start;
}

.canvas-chat-bubble.right {
  background-color: #e3f7ff;
  align-self: flex-end;
}

.canvas-chat-composer {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.canvas-chat-composer .el-input {
  flex-grow: 1;
}

.canvas-chat-mb8 {
  margin-bottom: 8px;
}

.canvas-chat-mt8 {
  margin-top: 8px;
}
</style>
