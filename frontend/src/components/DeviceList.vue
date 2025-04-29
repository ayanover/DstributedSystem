<template>
  <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Connected Devices</h1>

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

    <div v-else-if="devices.length === 0" class="bg-blue-50 border-l-4 border-blue-500 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-blue-700">
            No devices are connected. Generate a token and register a device to get started.
          </p>
        </div>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="device in devices" :key="device.deviceId"
           class="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200 transition-all duration-300 hover:shadow-lg">
        <div class="border-b border-gray-200 bg-gray-50 px-4 py-5 sm:px-6 flex justify-between items-center">
          <h3 class="text-lg leading-6 font-medium text-gray-900">{{ device.deviceType }}</h3>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {{ formatDate(device.lastSeen) }}
          </span>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <p class="text-sm text-gray-500 mb-3">
            <span class="font-medium text-gray-700">ID:</span>
            <span class="font-mono">{{ device.deviceId.substring(0, 16) }}...</span>
          </p>

          <div class="mb-4">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Capabilities:</h4>
            <div class="flex flex-wrap gap-2">
              <span v-for="capability in device.capabilities" :key="capability"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-indigo-100 text-indigo-800">
                {{ capability }}
              </span>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-4 sm:px-6 flex justify-between">
          <button @click="selectDevice(device)"
                  class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Execute Command
          </button>
          <router-link :to="'/devices/' + device.deviceId"
                      class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            View History
          </router-link>
        </div>
      </div>
    </div>

    <!-- Command Execution Modal -->
    <div v-if="modalOpen" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="closeModal"></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div v-if="selectedDevice" class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Execute Command on {{ selectedDevice.deviceType }}
                </h3>

                <!-- Step 1: Select Action -->
                <div v-if="commandStep === 1" class="mt-4">
                  <label for="action" class="block text-sm font-medium text-gray-700">Select Action</label>
                  <select id="action" v-model="selectedAction" @change="fetchActionParameters"
                          class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                    <option value="">-- Select Action --</option>
                    <option v-for="capability in selectedDevice.capabilities" :key="capability" :value="capability">
                      {{ capability }}
                    </option>
                  </select>
                </div>

                <!-- Step 2: Enter Parameters -->
                <div v-else-if="commandStep === 2" class="mt-4">
                  <div class="bg-gray-50 px-3 py-2 rounded-md mb-4">
                    <p class="text-sm font-medium text-gray-800">Action: {{ selectedAction }}</p>
                  </div>

                  <div v-if="actionParameters.length === 0" class="bg-blue-50 p-4 rounded-md">
                    <div class="flex">
                      <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                        </svg>
                      </div>
                      <div class="ml-3">
                        <p class="text-sm text-blue-700">Loading parameters...</p>
                      </div>
                    </div>
                  </div>

                  <form @submit.prevent="executeCommand" v-else>
                    <!-- Regular parameters -->
                    <div v-for="param in actionParameters" :key="param.name">
                      <!-- For code execution parameters -->
                      <div v-if="param.name === 'code'" class="mb-4">
                        <div class="flex justify-between items-center mb-1">
                          <label :for="param.name" class="block text-sm font-medium text-gray-700">Python Code</label>
                          <div class="flex space-x-2">
                            <!-- File upload button -->
                            <label class="inline-flex items-center px-2 py-1 border border-gray-300 text-xs font-medium rounded shadow-sm text-gray-700 bg-white hover:bg-gray-50 cursor-pointer">
                              <svg class="mr-1 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clip-rule="evenodd" />
                              </svg>
                              Upload .py
                              <input type="file" accept=".py" @change="handleFileUpload" class="hidden">
                            </label>

                            <!-- Sample code button -->
                            <button type="button" @click="loadSampleCode" class="inline-flex items-center px-2 py-1 border border-gray-300 text-xs font-medium rounded shadow-sm text-gray-700 bg-white hover:bg-gray-50">
                              <svg class="mr-1 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                              </svg>
                              Sample
                            </button>
                          </div>
                        </div>

                        <!-- Code editor -->
                        <textarea :id="param.name"
                                v-model="paramValues[param.name]"
                                rows="12"
                                class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md font-mono"
                                placeholder="Enter Python code here..."
                                :required="param.required"></textarea>
                        <p class="mt-1 text-xs text-gray-500">Python code that will execute on the device. You can define a 'result' variable to return values.</p>
                      </div>

                      <!-- For input data parameters -->
                      <div v-else-if="param.name === 'input_data'" class="mb-4">
                        <label :for="param.name" class="block text-sm font-medium text-gray-700">Input Data</label>
                        <textarea :id="param.name"
                                v-model="paramValues[param.name]"
                                rows="4"
                                class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md font-mono"
                                placeholder="Enter input data here..."
                                :required="param.required"></textarea>
                        <p class="mt-1 text-xs text-gray-500">This data will be available as 'input_data' variable in your code.</p>
                      </div>

                      <!-- For other parameters -->
                      <div v-else class="mb-4">
                        <label :for="param.name" class="block text-sm font-medium text-gray-700">{{ param.name }}</label>
                        <input :type="param.type" :id="param.name"
                               v-model="paramValues[param.name]" :required="param.required"
                               class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
                        <p v-if="param.description" class="mt-1 text-xs text-gray-500">{{ param.description }}</p>
                      </div>
                    </div>
                  </form>
                </div>

                <!-- Step 3: Result -->
                <div v-else-if="commandStep === 3" class="mt-4">
                  <div v-if="commandStatus === 'pending'" class="flex justify-center items-center flex-col py-6">
                    <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-indigo-500 mb-4"></div>
                    <p class="text-sm text-gray-600">Command is being processed...</p>
                  </div>

                  <div v-else-if="commandStatus === 'completed'" class="bg-green-50 p-4 rounded-md">
                    <div class="flex">
                      <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                      </div>
                      <div class="ml-3 w-full">
                        <h3 class="text-sm font-medium text-green-800">Command Completed</h3>

                        <!-- Code execution specific results -->
                        <div v-if="selectedAction === 'execute_code' || selectedAction === 'execute_code_with_input'" class="mt-2">
                          <!-- Result value -->
                          <div v-if="commandResult?.result?.result !== undefined" class="mt-2 border-t border-green-200 pt-2">
                            <h4 class="text-sm font-medium text-green-800">Return Value:</h4>
                            <pre class="mt-1 text-sm bg-green-100 p-2 rounded overflow-auto">{{ commandResult.result.result }}</pre>
                          </div>

                          <!-- Standard output -->
                          <div v-if="commandResult?.result?.stdout" class="mt-2 border-t border-green-200 pt-2">
                            <h4 class="text-sm font-medium text-green-800">Standard Output:</h4>
                            <pre class="mt-1 text-sm bg-gray-100 p-2 rounded overflow-auto">{{ commandResult.result.stdout }}</pre>
                          </div>

                          <!-- Standard error -->
                          <div v-if="commandResult?.result?.stderr" class="mt-2 border-t border-green-200 pt-2">
                            <h4 class="text-sm font-medium text-green-800">Standard Error:</h4>
                            <pre class="mt-1 text-sm bg-yellow-100 p-2 rounded overflow-auto">{{ commandResult.result.stderr }}</pre>
                          </div>
                        </div>

                        <!-- Regular result -->
                        <div v-else class="mt-2 text-sm text-green-700">
                          <p><strong>Result:</strong> {{ commandResult?.result }}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-else-if="commandStatus === 'failed'" class="bg-red-50 p-4 rounded-md">
                    <div class="flex">
                      <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                      </div>
                      <div class="ml-3 w-full">
                        <h3 class="text-sm font-medium text-red-800">Command Failed</h3>

                        <!-- Code execution specific errors -->
                        <div v-if="(selectedAction === 'execute_code' || selectedAction === 'execute_code_with_input') && commandResult?.result">
                          <!-- Error message -->
                          <div v-if="commandResult.result.error" class="mt-2 text-sm text-red-700">
                            <p><strong>Error:</strong> {{ commandResult.result.error_type || 'Error' }}: {{ commandResult.result.error }}</p>
                          </div>

                          <!-- Standard output -->
                          <div v-if="commandResult.result.stdout" class="mt-2 border-t border-red-200 pt-2">
                            <h4 class="text-sm font-medium text-red-800">Standard Output:</h4>
                            <pre class="mt-1 text-sm bg-gray-100 p-2 rounded overflow-auto">{{ commandResult.result.stdout }}</pre>
                          </div>

                          <!-- Standard error -->
                          <div v-if="commandResult.result.stderr" class="mt-2 border-t border-red-200 pt-2">
                            <h4 class="text-sm font-medium text-red-800">Standard Error:</h4>
                            <pre class="mt-1 text-sm bg-red-100 p-2 rounded overflow-auto">{{ commandResult.result.stderr }}</pre>
                          </div>
                        </div>

                        <!-- Regular error -->
                        <div v-else class="mt-2 text-sm text-red-700">
                          <p><strong>Error:</strong> {{ commandResult?.error }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button v-if="commandStep === 1" type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
                    :disabled="!selectedAction" @click="commandStep = 2">
              Next
            </button>

            <button v-if="commandStep === 2" type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
                    @click="executeCommand">
              Execute
            </button>

            <button v-if="commandStep === 3" type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
                    @click="resetCommand">
              New Command
            </button>

            <button v-if="commandStep === 2" type="button" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                    @click="commandStep = 1">
              Back
            </button>

            <button type="button" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm"
                    @click="closeModal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, onMounted, onBeforeUnmount } from 'vue';
import api from '@/api';

interface Device {
  id: string;
  deviceId: string;
  deviceType: string;
  capabilities: string[];
  lastSeen: string;
}

interface ActionParameter {
  name: string;
  type: string;
  required: boolean;
  description?: string;
}

interface CommandResult {
  status: 'success' | 'error';
  result?: any;
  error?: string;
}

export default defineComponent({
  name: 'DeviceList',
  setup() {
    // State
    const devices = ref<Device[]>([]);
    const loading = ref<boolean>(true);
    const error = ref<string | null>(null);
    const selectedDevice = ref<Device | null>(null);
    const selectedAction = ref<string>('');
    const actionParameters = ref<ActionParameter[]>([]);
    const paramValues = reactive<Record<string, any>>({});
    const commandStep = ref<number>(1);
    const commandId = ref<string | null>(null);
    const commandStatus = ref<string | null>(null);
    const commandResult = ref<CommandResult | null>(null);
    const modalOpen = ref<boolean>(false);
    const pollInterval = ref<number | null>(null);

    // Methods
    const fetchDevices = async (): Promise<void> => {
      loading.value = true;
      try {
        const response = await api.getDevices();
        devices.value = response.data.devices;
      } catch (err: any) {
        error.value = `Error loading devices: ${err.response?.data?.error || err.message}`;
      } finally {
        loading.value = false;
      }
    };

    const selectDevice = (device: Device): void => {
      selectedDevice.value = device;
      selectedAction.value = '';
      actionParameters.value = [];
      Object.keys(paramValues).forEach(key => delete paramValues[key]);
      commandStep.value = 1;
      commandId.value = null;
      commandStatus.value = null;
      commandResult.value = null;
      modalOpen.value = true;
    };

    const closeModal = (): void => {
      modalOpen.value = false;
      stopPolling();
    };

    const fetchActionParameters = async (): Promise<void> => {
      if (!selectedAction.value) return;

      try {
        const response = await api.getActionParameters(selectedAction.value);
        actionParameters.value = response.data.parameters;

        // Initialize parameter values
        actionParameters.value.forEach(param => {
          paramValues[param.name] = '';
        });
      } catch (err) {
        console.error('Error fetching parameters:', err);
        actionParameters.value = [
          { name: 'num1', type: 'number', required: true },
          { name: 'num2', type: 'number', required: true }
        ];
      }
    };

    const executeCommand = async (): Promise<void> => {
      if (!selectedDevice.value) return;

      // Validate parameters
      let valid = true;
      actionParameters.value.forEach(param => {
        if (param.required && !paramValues[param.name]) {
          valid = false;
        }
      });

      if (!valid) {
        alert('Please fill in all required parameters');
        return;
      }

      try {
        const response = await api.executeCommand(
          selectedDevice.value.deviceId,
          selectedAction.value,
          paramValues
        );

        commandId.value = response.data.commandId;
        commandStep.value = 3;
        commandStatus.value = 'pending';

        // Start polling for result
        startPolling();
      } catch (err: any) {
        alert(`Error executing command: ${err.response?.data?.error || err.message}`);
      }
    };

    const startPolling = (): void => {
      // Clear any existing interval
      stopPolling();

      if (!commandId.value) return;

      // Set up polling
      pollInterval.value = window.setInterval(async () => {
        try {
          const response = await api.getCommandStatus(commandId.value as string);
          const command = response.data;

          if (command.status !== 'pending' && command.status !== 'sent') {
            // Command completed or failed
            stopPolling();

            commandStatus.value = command.status;
            commandResult.value = command.result;
          }
        } catch (err) {
          console.error('Error polling command status:', err);
          stopPolling();

          commandStatus.value = 'failed';
          commandResult.value = {
            status: 'error',
            error: 'Error retrieving command status'
          };
        }
      }, 2000);  // Poll every 2 seconds
    };

    const stopPolling = (): void => {
      if (pollInterval.value) {
        window.clearInterval(pollInterval.value);
        pollInterval.value = null;
      }
    };

    const resetCommand = (): void => {
      commandStep.value = 1;
      selectedAction.value = '';
      Object.keys(paramValues).forEach(key => delete paramValues[key]);
      commandId.value = null;
      commandStatus.value = null;
      commandResult.value = null;
    };

    const formatDate = (dateString: string): string => {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    };

    // New methods for code execution
    const handleFileUpload = (event: Event): void => {
      const input = event.target as HTMLInputElement;
      if (!input.files || input.files.length === 0) return;

      const file = input.files[0];
      if (!file.name.endsWith('.py')) {
        alert('Please select a Python (.py) file');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target && typeof e.target.result === 'string') {
          // Set the file content to the code parameter
          paramValues['code'] = e.target.result;
        }
      };
      reader.readAsText(file);
    };

    const loadSampleCode = (): void => {
      // Set a sample Python code snippet
      paramValues['code'] = `# Sample Python code for device execution
import os
import platform
import datetime

# Get system information
system_info = {
    "platform": platform.platform(),
    "python_version": platform.python_version(),
    "processor": platform.processor(),
    "hostname": platform.node(),
    "current_time": str(datetime.datetime.now())
}

# Print some information
print("Running Python code on IoT device...")
print(f"Current time: {system_info['current_time']}")
print(f"Python version: {system_info['python_version']}")

# Define a result to be returned to the server
result = {
    "system_info": system_info,
    "execution_successful": True
}

# The 'result' variable will be returned to the server
`;
    };

    // Lifecycle hooks
    onMounted(() => {
      fetchDevices();
    });

    onBeforeUnmount(() => {
      stopPolling();
    });

    return {
      devices,
      loading,
      error,
      selectedDevice,
      selectedAction,
      actionParameters,
      paramValues,
      commandStep,
      commandId,
      commandStatus,
      commandResult,
      modalOpen,
      fetchDevices,
      selectDevice,
      closeModal,
      fetchActionParameters,
      executeCommand,
      resetCommand,
      formatDate,
      // New methods for code execution
      handleFileUpload,
      loadSampleCode
    };
  }
});
</script>