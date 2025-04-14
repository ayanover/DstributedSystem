<template>
  <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Device Registration</h1>

    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
      <div class="px-4 py-5 sm:px-6 bg-gradient-to-r from-blue-600 to-blue-700">
        <h3 class="text-lg leading-6 font-medium text-white">Register New Device</h3>
        <p class="mt-1 max-w-2xl text-sm text-blue-200">
          Enter device information and authorization token to register a new device.
        </p>
      </div>
      <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
        <form @submit.prevent="registerDevice" class="space-y-6">
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
            <div>
              <label for="deviceId" class="block text-sm font-medium text-gray-700">Device ID</label>
              <div class="mt-1">
                <input
                  id="deviceId"
                  name="deviceId"
                  type="text"
                  v-model="deviceInfo.deviceId"
                  required
                  class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="e.g. DEVICE-001"
                />
              </div>
            </div>

            <div>
              <label for="deviceType" class="block text-sm font-medium text-gray-700">Device Type</label>
              <div class="mt-1">
                <select
                  id="deviceType"
                  name="deviceType"
                  v-model="deviceInfo.metadata.type"
                  required
                  class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="sensor">Sensor</option>
                  <option value="gateway">Gateway</option>
                  <option value="controller">Controller</option>
                  <option value="display">Display</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <div>
            <label for="publicKey" class="block text-sm font-medium text-gray-700">Public Key (PEM format)</label>
            <div class="mt-1">
              <textarea
                id="publicKey"
                name="publicKey"
                rows="4"
                v-model="deviceInfo.publicKey"
                required
                class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                placeholder="-----BEGIN PUBLIC KEY-----&#10;...&#10;-----END PUBLIC KEY-----"
              ></textarea>
            </div>
            <p class="mt-2 text-sm text-gray-500">Enter the device's public key in PEM format.</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Device Capabilities</label>
            <div class="mt-2 space-y-2">
              <div class="flex flex-wrap gap-2">
                <div v-for="(capability, index) in availableCapabilities" :key="index" class="flex items-center">
                  <input
                    :id="`capability-${index}`"
                    type="checkbox"
                    :value="capability"
                    v-model="deviceInfo.capabilities"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label :for="`capability-${index}`" class="ml-2 block text-sm text-gray-700">
                    {{ capability }}
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Additional Metadata</label>
            <div class="mt-1 grid grid-cols-1 gap-y-4 gap-x-4 sm:grid-cols-2">
              <div>
                <label for="location" class="block text-xs font-medium text-gray-500">Location</label>
                <input
                  id="location"
                  type="text"
                  v-model="deviceInfo.metadata.location"
                  class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="e.g. Building A, Floor 1"
                />
              </div>
              <div>
                <label for="groupId" class="block text-xs font-medium text-gray-500">Group ID</label>
                <input
                  id="groupId"
                  type="text"
                  v-model="deviceInfo.metadata.groupId"
                  class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="e.g. production-sensors"
                />
              </div>
              <div>
                <label for="firmwareVersion" class="block text-xs font-medium text-gray-500">Firmware Version</label>
                <input
                  id="firmwareVersion"
                  type="text"
                  v-model="deviceInfo.metadata.firmwareVersion"
                  class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="e.g. 1.0.0"
                />
              </div>
              <div>
                <label for="model" class="block text-xs font-medium text-gray-500">Model</label>
                <input
                  id="model"
                  type="text"
                  v-model="deviceInfo.metadata.model"
                  class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="e.g. IoT-2000"
                />
              </div>
            </div>
          </div>

          <div>
            <label for="authToken" class="block text-sm font-medium text-gray-700">Authorization Token</label>
            <div class="mt-1">
              <input
                id="authToken"
                name="authToken"
                type="text"
                v-model="authToken"
                required
                class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                placeholder="Enter your authorization token"
              />
            </div>
            <p class="mt-2 text-sm text-gray-500">A valid authorization token is required to register a new device.</p>
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Register Device
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Registration Success Alert -->
    <div v-if="registrationSuccess" class="rounded-md bg-green-50 p-4 mb-8">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3 flex-1">
          <h3 class="text-sm font-medium text-green-800">Registration Successful</h3>
          <div class="mt-2 text-sm text-green-700">
            <div class="mb-3">
              <p><strong>Device ID:</strong> {{ deviceInfo.deviceId }}</p>
              <p><strong>Type:</strong> {{ deviceInfo.metadata.type }}</p>
              <p><strong>Session Key:</strong></p>
              <div class="mt-1 bg-white px-3 py-2 rounded border border-gray-300 font-mono text-sm break-all">
                {{ sessionKey }}
              </div>
            </div>
            <p><strong>Server Time:</strong> {{ serverTime }}</p>
            <p class="mt-2">Device has been successfully registered and can now connect to the system.</p>
          </div>
          <div class="mt-4">
            <button
              type="button"
              @click="copySessionKey"
              class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="-ml-0.5 mr-1.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
              </svg>
              Copy Session Key
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Registered Devices -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Registered Devices</h3>
        <p class="mt-1 max-w-2xl text-sm text-gray-500">
          List of all devices registered in the system.
        </p>
      </div>

      <div v-if="devicesLoading" class="flex justify-center py-6">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>

      <div v-else-if="devicesError" class="bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ devicesError }}</p>
          </div>
        </div>
      </div>

      <div v-else-if="devices.length === 0" class="bg-blue-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-blue-700">
              No devices registered yet. Use the form above to register your first device.
            </p>
          </div>
        </div>
      </div>

      <div v-else>
        <div class="overflow-hidden overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Device ID
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Capabilities
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Seen
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="device in devices" :key="device.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ device.device_id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ device.device_type }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="(cap, index) in device.capabilities"
                      :key="index"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                    >
                      {{ cap }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      device.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    ]"
                  >
                    {{ device.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(device.last_seen) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <button
                    @click="viewDevice(device)"
                    class="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 mr-2"
                  >
                    Details
                  </button>
                  <button
                    @click="toggleDeviceStatus(device)"
                    :class="[
                      'inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded focus:outline-none focus:ring-2 focus:ring-offset-2',
                      device.is_active
                        ? 'text-red-700 bg-red-100 hover:bg-red-200 focus:ring-red-500'
                        : 'text-green-700 bg-green-100 hover:bg-green-200 focus:ring-green-500'
                    ]"
                  >
                    {{ device.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Device Details Modal -->
    <div v-if="deviceModalOpen" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="closeDeviceModal"></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
                <svg class="h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Device Details
                </h3>
                <div class="mt-4" v-if="selectedDevice">
                  <div class="bg-gray-50 px-4 py-3 sm:rounded-lg mb-4">
                    <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                      <div class="sm:col-span-1">
                        <dt class="text-sm font-medium text-gray-500">Device ID</dt>
                        <dd class="mt-1 text-sm text-gray-900">{{ selectedDevice.device_id }}</dd>
                      </div>
                      <div class="sm:col-span-1">
                        <dt class="text-sm font-medium text-gray-500">Type</dt>
                        <dd class="mt-1 text-sm text-gray-900">{{ selectedDevice.device_type }}</dd>
                      </div>
                      <div class="sm:col-span-1">
                        <dt class="text-sm font-medium text-gray-500">Status</dt>
                        <dd class="mt-1 text-sm text-gray-900">
                          <span
                            :class="[
                              'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                              selectedDevice.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            ]"
                          >
                            {{ selectedDevice.is_active ? 'Active' : 'Inactive' }}
                          </span>
                        </dd>
                      </div>
                      <div class="sm:col-span-1">
                        <dt class="text-sm font-medium text-gray-500">Registered</dt>
                        <dd class="mt-1 text-sm text-gray-900">{{ formatDate(selectedDevice.registered_at) }}</dd>
                      </div>
                      <div class="sm:col-span-2">
                        <dt class="text-sm font-medium text-gray-500">Capabilities</dt>
                        <dd class="mt-1 text-sm text-gray-900">
                          <div class="flex flex-wrap gap-1">
                            <span
                              v-for="(cap, index) in selectedDevice.capabilities"
                              :key="index"
                              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                            >
                              {{ cap }}
                            </span>
                          </div>
                        </dd>
                      </div>
                      <div class="sm:col-span-2">
                        <dt class="text-sm font-medium text-gray-500">Metadata</dt>
                        <dd class="mt-1 text-sm text-gray-900">
                          <div class="bg-gray-100 p-2 rounded font-mono text-xs overflow-x-auto">
                            <pre>{{ JSON.stringify(selectedDevice.metadata, null, 2) }}</pre>
                          </div>
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="closeDeviceModal"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import api from '@/api';

interface DeviceMetadata {
  type: string;
  location?: string;
  groupId?: string;
  firmwareVersion?: string;
  model?: string;
  [key: string]: any;
}

interface DeviceInfo {
  deviceId: string;
  publicKey: string;
  capabilities: string[];
  metadata: DeviceMetadata;
}

interface Device {
  id: string;
  device_id: string;
  device_type: string;
  capabilities: string[];
  metadata: DeviceMetadata;
  is_active: boolean;
  registered_at: string;
  last_seen: string;
  public_key: string;
  session_key: string;
}

export default defineComponent({
  name: 'DeviceRegistration',
  setup() {
    // State
    const authToken = ref<string>('');
    const deviceInfo = ref<DeviceInfo>({
      deviceId: '',
      publicKey: '',
      capabilities: [],
      metadata: {
        type: 'sensor',
        location: '',
        groupId: '',
        firmwareVersion: '',
        model: ''
      }
    });
    const availableCapabilities = ref<string[]>([
      'temperature', 'humidity', 'pressure', 'light', 'motion',
      'sound', 'camera', 'relay', 'gps', 'accelerometer',
      'co2', 'voc', 'display', 'bluetooth', 'wifi'
    ]);
    const loading = ref<boolean>(false);
    const registrationSuccess = ref<boolean>(false);
    const sessionKey = ref<string>('');
    const serverTime = ref<string>('');
    const devices = ref<Device[]>([]);
    const devicesLoading = ref<boolean>(true);
    const devicesError = ref<string | null>(null);
    const selectedDevice = ref<Device | null>(null);
    const deviceModalOpen = ref<boolean>(false);

    // Methods
    const registerDevice = async (): Promise<void> => {
      loading.value = true;
      registrationSuccess.value = false;

      try {
        // In a real application, you would encrypt the data here
        // For this example, we'll simulate the encryption
        const registrationData = {
          authToken: authToken.value,
          deviceInfo: {
            deviceId: deviceInfo.value.deviceId,
            publicKey: deviceInfo.value.publicKey,
            capabilities: deviceInfo.value.capabilities,
            metadata: deviceInfo.value.metadata
          }
        };

        // Simulate encryption - in a real app you would use actual encryption
        const encryptedData = btoa(JSON.stringify(registrationData));

        const response = await api.registerDevice({data: encryptedData});

        // Simulate decryption - in a real app you would use actual decryption
        const decryptedResponse = JSON.parse(atob(response.data));

        // Set success data
        sessionKey.value = decryptedResponse.sessionKey;
        serverTime.value = decryptedResponse.serverTime;
        registrationSuccess.value = true;

        // Reset form
        authToken.value = '';

        // Refresh device list
        fetchDevices();
      } catch (err: any) {
        alert(`Error registering device: ${err.response?.data?.error || err.message}`);
      } finally {
        loading.value = false;
      }
    };

    const fetchDevices = async (): Promise<void> => {
      devicesLoading.value = true;

      try {
        const response = await api.getDevices();
        devices.value = response.data.devices;
        devicesError.value = null;
      } catch (err: any) {
        devicesError.value = `Error loading devices: ${err.response?.data?.error || err.message}`;
        console.error('Error loading devices:', err);
      } finally {
        devicesLoading.value = false;
      }
    };

    const copySessionKey = (): void => {
      navigator.clipboard.writeText(sessionKey.value)
          .then(() => {
            alert('Session key copied to clipboard');
          })
          .catch(err => {
            console.error('Failed to copy session key:', err);
          });
    };

    const viewDevice = (device: Device): void => {
      selectedDevice.value = device;
      deviceModalOpen.value = true;
    };

    const closeDeviceModal = (): void => {
      deviceModalOpen.value = false;
      selectedDevice.value = null;
    };

    const toggleDeviceStatus = async (device: Device): Promise<void> => {
      try {
        await api.updateDeviceStatus(device.id, !device.is_active);
        // Update local state
        device.is_active = !device.is_active;

        // If we're viewing this device in the modal, update that too
        if (selectedDevice.value && selectedDevice.value.id === device.id) {
          selectedDevice.value.is_active = device.is_active;
        }
      } catch (err: any) {
        alert(`Error updating device status: ${err.response?.data?.error || err.message}`);
      }
    };
  };
