<template>
  <div class="command-history">
    <h1>Command History</h1>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else-if="commands.length === 0" class="alert alert-info">
      No commands have been executed yet.
    </div>

    <div v-else>
      <div class="mb-4">
        <div class="input-group">
          <input type="text" class="form-control" placeholder="Filter commands..." v-model="filter">
          <button class="btn btn-outline-secondary" type="button" @click="fetchCommands">
            Refresh
          </button>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Device</th>
              <th>Command</th>
              <th>Parameters</th>
              <th>Status</th>
              <th>Result</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="command in filteredCommands" :key="command.id">
              <td>{{ command.deviceType }}</td>
              <td>{{ command.name }}</td>
              <td>
                <span v-for="(value, key) in command.params" :key="key">
                  {{ key }}: {{ value }}<br>
                </span>
              </td>
              <td>
                <span :class="getStatusBadgeClass(command.status)">
                  {{ command.status }}
                </span>
              </td>
              <td>
                <span v-if="command.result && command.result.status === 'success'">
                  {{ command.result.result }}
                </span>
                <span v-else-if="command.result && command.result.status === 'error'" class="text-danger">
                  {{ command.result.error }}
                </span>
                <span v-else>-</span>
              </td>
              <td>{{ formatDate(command.createdAt) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

interface CommandResult {
  status: string;
  result?: any;
  error?: string;
}

interface Command {
  id: string;
  deviceId: string;
  deviceType: string;
  name: string;
  params: Record<string, any>;
  status: string;
  result: CommandResult | null;
  createdAt: string;
  updatedAt: string;
}

export default defineComponent({
  name: 'CommandHistory',
  setup() {
    const commands = ref<Command[]>([]);
    const loading = ref(true);
    const error = ref<string | null>(null);
    const filter = ref('');
    const refreshInterval = ref<number | null>(null);

    const filteredCommands = computed(() => {
      if (!filter.value) return commands.value;

      const filterLower = filter.value.toLowerCase();
      return commands.value.filter(cmd =>
        cmd.name.toLowerCase().includes(filterLower) ||
        cmd.deviceType.toLowerCase().includes(filterLower)
      );
    });

    const fetchCommands = (silent = false) => {
      if (!silent) loading.value = true;

      axios.get('/api/commands')
        .then(response => {
          commands.value = response.data.commands;
          loading.value = false;
        })
        .catch(error => {
          const errorMessage = error.response?.data?.error || error.message;
          error.value = 'Error loading commands: ' + errorMessage;
          loading.value = false;
        });
    };

    const getStatusBadgeClass = (status: string): string => {
      switch (status) {
        case 'completed': return 'badge bg-success';
        case 'pending': return 'badge bg-warning text-dark';
        case 'sent': return 'badge bg-info text-dark';
        case 'failed': return 'badge bg-danger';
        default: return 'badge bg-secondary';
      }
    };

    const formatDate = (dateString: string): string => {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).format(date);
    };

    onMounted(() => {
      fetchCommands();

      // Set up auto-refresh
      refreshInterval.value = window.setInterval(() => {
        fetchCommands(true);
      }, 30000); // Refresh every 30 seconds
    });

    onUnmounted(() => {
      if (refreshInterval.value) {
        window.clearInterval(refreshInterval.value);
      }
    });

    return {
      commands,
      loading,
      error,
      filter,
      filteredCommands,
      fetchCommands,
      getStatusBadgeClass,
      formatDate
    };
  }
});
</script>