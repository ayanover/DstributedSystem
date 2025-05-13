<template>
  <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
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

    <div v-else-if="device">
      <div class="md:flex md:items-center md:justify-between mb-6">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold text-gray-900 flex items-center">
            {{ device.deviceType }} Device
            <span class="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <svg class="-ml-0.5 mr-1.5 h-2 w-2 text-green-400" fill="currentColor" viewBox="0 0 8 8">
                <circle cx="4" cy="4" r="3" />
              </svg>
              Last seen {{ formatDate(device.lastSeen) }}
            </span>
          </h1>
        </div>
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <router-link to="/"
                    class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            <svg class="-ml-1 mr-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
            Back to Devices
          </router-link>
        </div>
      </div>

      <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div class="px-4 py-5 sm:px-6 bg-gray-50">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Device Information</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">Details and capabilities.</p>
        </div>
        <div class="border-t border-gray-200">
          <dl>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Device ID</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 font-mono">{{ device.deviceId }}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Type</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ device.deviceType }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Last Seen</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ formatDate(device.lastSeen) }}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Capabilities</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div class="flex flex-wrap gap-2">
                  <span v-for="capability in device.capabilities" :key="capability"
                      class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-indigo-100 text-indigo-800">
                    {{ capability }}
                  </span>
                </div>
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold text-gray-900">Command History</h2>
        <button @click="refreshCommands"
                class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          <svg class="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7.805V10a1 1 0 01-2 0V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H16a1 1 0 110 2h-5a1 1 0 01-1-1v-5a1 1 0 112 0v2.101a7.002 7.002 0 01-8.601-3.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          Refresh
        </button>
      </div>

      <div v-if="commandsLoading" class="flex justify-center my-4">
        <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-indigo-500"></div>
      </div>

      <div v-else-if="commands.length === 0" class="bg-blue-50 border-l-4 border-blue-500 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-blue-700">
              No commands have been executed on this device yet.
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
                  <tr v-for="command in commands" :key="command.id">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="font-medium text-gray-900">{{ command.name }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <!-- For code execution commands -->
                      <template v-if="hasCode(command)">
                        <button @click="showCodePopup(command)"
                                class="inline-flex items-center px-2 py-1 text-xs font-medium text-indigo-700 bg-indigo-100 rounded-md hover:bg-indigo-200">
                          <svg class="h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                          </svg>
                          View Code
                        </button>

                        <!-- If there's input data, show a button for it as well -->
                        <button v-if="hasInputData(command)"
                                @click="showInputDataPopup(command)"
                                class="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 ml-2">
                          <svg class="h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          View Input
                        </button>
                      </template>

                      <!-- For non-code commands -->
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
                      <!-- For code execution results -->
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

    <div v-else class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-yellow-700">
            Device not found
          </p>
        </div>
      </div>
    </div>

    <!-- Code Overlay -->
    <CodeOverlay
      :show="showCode"
      :content="selectedCode"
      :title="codeTitle"
      @close="showCode = false"
    />

    <!-- Result Overlay -->
    <CodeOverlay
      :show="showResult"
      :content="selectedResult"
      :title="resultTitle"
      @close="showResult = false"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
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
  name: string;
  params: Record<string, any>;
  status: string;
  result: CommandResult | null;
  createdAt: string;
  updatedAt: string;
}

interface Device {
  deviceId: string;
  deviceType: string;
  capabilities: string[];
  lastSeen: string;
}

export default defineComponent({
  name: 'DeviceDetail',
  components: {
    CodeOverlay
  },
  setup() {
    const route = useRoute();
    const router = useRouter();

    // State
    const device = ref<Device | null>(null);
    const commands = ref<Command[]>([]);
    const loading = ref<boolean>(true);
    const commandsLoading = ref<boolean>(false);
    const error = ref<string | null>(null);
    const refreshInterval = ref<number | null>(null);

    // Overlay states
    const showCode = ref<boolean>(false);
    const showResult = ref<boolean>(false);
    const selectedCode = ref<string>('');
    const selectedResult = ref<string>('');
    const codeTitle = ref<string>('Code View');
    const resultTitle = ref<string>('Result Output');

    // Computed
    const deviceId = computed<string>(() => route.params.deviceId as string);

    // Methods
    const fetchDeviceData = async (): Promise<void> => {
      if (!deviceId.value) {
        router.push('/');
        return;
      }

      loading.value = true;
      error.value = null;

      try {
        // Fetch device capabilities
        const deviceResponse = await api.getDeviceCapabilities(deviceId.value);
        device.value = deviceResponse.data;

        // Fetch command history
        await fetchCommands();

      } catch (err: any) {
        error.value = `Error loading device data: ${err.response?.data?.error || err.message}`;
        console.error('Error fetching device data:', err);
      } finally {
        loading.value = false;
      }
    };

    const fetchCommands = async (): Promise<void> => {
      if (!deviceId.value) return;

      commandsLoading.value = true;

      try {
        const commandsResponse = await api.getDeviceCommands(deviceId.value);
        commands.value = commandsResponse.data.commands;
      } catch (err: any) {
        console.error('Error fetching commands:', err);
        // Don't set the main error state for this to avoid hiding device info
      } finally {
        commandsLoading.value = false;
      }
    };

    const refreshCommands = (): void => {
      fetchCommands();
    };

    const startAutoRefresh = (): void => {
      // Auto refresh every 15 seconds
      refreshInterval.value = window.setInterval(() => {
        refreshCommands();
      }, 15000);
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

    const formatDate = (dateString: string): string => {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }).format(date);
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

    // Code-related methods
    const hasCode = (command: Command): boolean => {
      return command.name === 'execute_code' || command.name === 'execute_code_with_input';
    };

    const hasInputData = (command: Command): boolean => {
      return command.name === 'execute_code_with_input' && !!command.params.input_data;
    };

    const getCodeValue = (command: Command): string => {
      return command.params.code || '';
    };

    // Result-related methods
    const hasCodeExecutionResult = (command: Command): boolean => {
      return (command.name === 'execute_code' || command.name === 'execute_code_with_input') &&
             command.result &&
             (command.result.stdout ||
              command.result.stderr ||
              command.result.error);
    };

    // Popup methods
    const showCodePopup = (command: Command): void => {
      selectedCode.value = getCodeValue(command);
      codeTitle.value = `Code: ${command.name}`;
      showCode.value = true;
    };

    const showInputDataPopup = (command: Command): void => {
      selectedCode.value = command.params.input_data || '';
      codeTitle.value = `Input Data: ${command.name}`;
      showCode.value = true;
    };

    const showResultPopup = (command: Command): void => {
      // Format the result to show only stdout and stderr
      let output = '';

      if (command.result && command.result.result.stdout) {
        output += command.result.result.stdout;
      }

      if (command.result && command.result.result.stderr) {
        if (output) output += '\n\n';
        output += '=== STDERR ===\n';
        output += command.result.result.stderr;
      }

      if (command.result && command.result.result.error) {
        if (output) output += '\n\n';
        output += '=== ERROR ===\n';
        output += command.result.error_type ? `${command.result.error_type}: ${command.result.error}` : command.result.error;
      }

      if (!output && command.result && command.result.result !== undefined) {
        output = JSON.stringify(command.result.result, null, 2);
      }

      // If still no output
      if (!output) {
        output = command.status === 'completed' ? 'Command completed successfully with no output.' : 'No output available.';
      }

      selectedResult.value = output;
      resultTitle.value = `Result: ${command.name}`;
      showResult.value = true;
    };

    // Lifecycle hooks
    onMounted(() => {
      fetchDeviceData();
      startAutoRefresh();
    });

    onBeforeUnmount(() => {
      stopAutoRefresh();
    });

    return {
      device,
      commands,
      loading,
      commandsLoading,
      error,
      showCode,
      showResult,
      selectedCode,
      selectedResult,
      codeTitle,
      resultTitle,
      fetchDeviceData,
      refreshCommands,
      getStatusBadgeClass,
      formatDate,
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