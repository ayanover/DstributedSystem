<template>
  <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="sm:flex sm:items-center sm:justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Command History</h1>
      <div class="mt-3 sm:mt-0">
        <button @click="fetchCommands"
                class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          <svg class="-ml-1 mr-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7.805V10a1 1 0 01-2 0V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H16a1 1 0 110 2h-5a1 1 0 01-1-1v-5a1 1 0 112 0v2.101a7.002 7.002 0 01-8.601-3.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
      <div class="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Commands Overview</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">History of all commands executed across all devices.</p>
          </div>

          <div class="relative max-w-xs">
            <input
              type="text"
              v-model="filter"
              placeholder="Filter commands..."
              class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
            />
            <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center my-12">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="filteredCommands.length === 0" class="bg-blue-50 border-l-4 border-blue-500 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-blue-700">
            No commands found. {{ filter ? 'Try a different filter.' : 'Execute a command on a device to get started.' }}
          </p>
        </div>
      </div>
    </div>

    <div v-else class="flex flex-col">
      <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
          <div class="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Device
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Command
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Parameters
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Result
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="command in filteredCommands" :key="command.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">{{ command.deviceType }}</div>
                    <div class="text-xs text-gray-500 font-mono truncate max-w-xs">{{ command.deviceId }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">{{ command.name }}</div>
                  </td>
                  <td class="px-6 py-4">
                    <template v-if="hasCode(command)">
                      <button @click="showCodePopup(command)"
                              class="inline-flex items-center px-2 py-1 text-xs font-medium text-indigo-700 bg-indigo-100 rounded-md hover:bg-indigo-200">
                        <svg class="h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                        </svg>
                        View Code
                      </button>

                      <button v-if="hasInputData(command)"
                              @click="showInputDataPopup(command)"
                              class="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 ml-2">
                        <svg class="h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        View Input
                      </button>
                    </template>

                    <div v-else v-for="(value, key) in command.params" :key="key" class="text-sm text-gray-500">
                      <span class="font-medium text-gray-700">{{ key }}:</span> {{ value }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="getStatusBadgeClass(command.status)">
                      {{ command.status }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <template v-if="hasCodeExecutionResult(command)">
                      <button @click="showResultPopup(command)"
                              class="inline-flex items-center px-2 py-1 text-xs font-medium text-indigo-700 bg-indigo-100 rounded-md hover:bg-indigo-200">
                        <svg class="h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        View Result
                      </button>
                    </template>

                    <!-- For non-code execution results -->
                    <template v-else>
                      <span v-if="command.result && command.status === 'completed'" class="text-sm text-green-600">
                        {{ command.result }}
                      </span>
                      <span v-else-if="command.result && command.status === 'failed'" class="text-sm text-red-600">
                        {{ command.result.error || 'Failed' }}
                      </span>
                      <span v-else class="text-sm text-gray-500">-</span>
                    </template>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatTime(command.createdAt) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <CodeOverlay
    :show="showCode"
    :content="selectedCode"
    :title="codeTitle"
    @close="showCode = false"
  />

  <CodeOverlay
    :show="showResult"
    :content="selectedResult"
    :title="resultTitle"
    @close="showResult = false"
  />
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue';
import api from '@/api';
import CodeOverlay from './CodeOverlay.vue';

interface CommandResult {
  status: 'success' | 'error';
  result?: any;
  error?: string;
  stdout?: string;
  stderr?: string;
  error_type?: string;
  success?: boolean;
}

interface Command {
  id: string;
  deviceId: string;
  deviceType: string;
  name: string;
  params: Record<string, any>;
  status: string;
  result: CommandResult | any;
  createdAt: string;
  updatedAt: string;
}

export default defineComponent({
  name: 'CommandHistory',
  components: {
    CodeOverlay
  },
  setup() {
    const commands = ref<Command[]>([]);
    const loading = ref<boolean>(true);
    const error = ref<string | null>(null);
    const filter = ref<string>('');
    const refreshInterval = ref<number | null>(null);

    const showCode = ref<boolean>(false);
    const showResult = ref<boolean>(false);
    const selectedCode = ref<string>('');
    const selectedResult = ref<string>('');
    const codeTitle = ref<string>('Code View');
    const resultTitle = ref<string>('Result Output');

    const filteredCommands = computed(() => {
      if (!filter.value) return commands.value;

      const searchTerm = filter.value.toLowerCase();
      return commands.value.filter(cmd =>
        cmd.name.toLowerCase().includes(searchTerm) ||
        cmd.deviceType.toLowerCase().includes(searchTerm) ||
        (typeof cmd.result === 'string' && cmd.result.toLowerCase().includes(searchTerm)) ||
        (cmd.params.code && cmd.params.code.toLowerCase().includes(searchTerm))
      );
    });

    const fetchCommands = async (silent = false): Promise<void> => {
      if (!silent) loading.value = true;

      try {
        const response = await api.getAllCommands();
        commands.value = response.data.commands;
        error.value = null;
      } catch (err: any) {
        error.value = `Error loading commands: ${err.response?.data?.error || err.message}`;
        console.error('Error loading commands:', err);
      } finally {
        loading.value = false;
      }
    };

    const startAutoRefresh = (): void => {
      refreshInterval.value = window.setInterval(() => {
        fetchCommands(true);
      }, 30000);
    };

    const stopAutoRefresh = (): void => {
      if (refreshInterval.value) {
        window.clearInterval(refreshInterval.value);
        refreshInterval.value = null;
      }
    };

    const getStatusBadgeClass = (status: string): string => {
      switch (status) {
        case 'completed':
          return 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800';
        case 'pending':
          return 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800';
        case 'sent':
          return 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800';
        case 'failed':
          return 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800';
        default:
          return 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800';
      }
    };

    const formatTime = (dateString: string): string => {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).format(date);
    };

    const hasCode = (command: Command): boolean => {
      return command.name === 'execute_code' || command.name === 'execute_code_with_input';
    };

    const hasInputData = (command: Command): boolean => {
      return command.name === 'execute_code_with_input' && !!command.params.input_data;
    };

    const getCodeValue = (command: Command): string => {
      return command.params.code || '';
    };

    const hasCodeExecutionResult = (command: Command): boolean => {
      return (command.name === 'execute_code' || command.name === 'execute_code_with_input') &&
             command.result;
    };

    const showCodePopup = (command: Command): void => {
      selectedCode.value = getCodeValue(command);
      codeTitle.value = `Code: ${command.name} (${command.deviceType})`;
      showCode.value = true;
    };

    const showInputDataPopup = (command: Command): void => {
      selectedCode.value = command.params.input_data || '';
      codeTitle.value = `Input Data: ${command.name} (${command.deviceType})`;
      showCode.value = true;
    };

    const showResultPopup = (command: Command): void => {
      let output = '';

      if (command.result && command.result.result.stdout != null) {
        output += command.result.result.stdout;
      }

      if (command.result && command.result.result.stderr != null) {
        if (output) output += '\n\n';
        output += command.result.result.stderr;
      }

      if (!output && command.result && command.result.result !== undefined) {
        output = JSON.stringify(command.result.result, null, 2);
      }

      if (!output) {
        output = command.status === 'completed' ? 'Command completed successfully with no output.' : 'No output available.';
      }

      selectedResult.value = output;
      resultTitle.value = `Result: ${command.name} (${command.deviceType})`;
      showResult.value = true;
    };

    onMounted(() => {
      fetchCommands();
      startAutoRefresh();
    });

    onBeforeUnmount(() => {
      stopAutoRefresh();
    });

    return {
      commands,
      loading,
      error,
      filter,
      filteredCommands,
      showCode,
      showResult,
      selectedCode,
      selectedResult,
      codeTitle,
      resultTitle,
      fetchCommands,
      getStatusBadgeClass,
      formatTime,
      hasCode,
      hasInputData,
      getCodeValue,
      hasCodeExecutionResult,
      showCodePopup,
      showInputDataPopup,
      showResultPopup
    };
  }
});
</script>