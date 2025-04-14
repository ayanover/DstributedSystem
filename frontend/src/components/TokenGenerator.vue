// src/components/TokenGenerator.vue
<template>
  <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Authorization Tokens</h1>

    <!-- Token Generator Card -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
      <div class="px-4 py-5 sm:px-6 bg-gradient-to-r from-indigo-600 to-indigo-700">
        <h3 class="text-lg leading-6 font-medium text-white">Generate New Token</h3>
        <p class="mt-1 max-w-2xl text-sm text-indigo-200">
          Create a token that can be used to register a new device.
        </p>
      </div>
      <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
        <form @submit.prevent="generateToken" class="space-y-6">
          <div>
            <label for="adminKey" class="block text-sm font-medium text-gray-700">Admin Key</label>
            <div class="mt-1">
              <input
                id="adminKey"
                name="adminKey"
                type="password"
                v-model="adminKey"
                required
                class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                placeholder="Enter admin key"
              />
            </div>
            <p class="mt-2 text-sm text-gray-500">The admin key is required to generate new tokens.</p>
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generate Token
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- New Token Alert -->
    <div v-if="newToken" class="rounded-md bg-green-50 p-4 mb-8">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3 flex-1">
          <h3 class="text-sm font-medium text-green-800">Token Generated Successfully</h3>
          <div class="mt-2 text-sm text-green-700">
            <div class="mb-3">
              <p><strong>Token:</strong></p>
              <div class="mt-1 bg-white px-3 py-2 rounded border border-gray-300 font-mono text-sm break-all">
                {{ newToken.token }}
              </div>
            </div>
            <p><strong>Expires:</strong> {{ formatDate(newToken.expiresAt) }}</p>
            <p class="mt-2">Use this token to register a new device.</p>
          </div>
          <div class="mt-4 flex">
            <button
              type="button"
              @click="copyToken"
              class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="-ml-0.5 mr-1.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
              </svg>
              Copy Token
            </button>
            <button
              type="button"
              @click="downloadSetupFile"
              class="ml-3 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="-ml-0.5 mr-1.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
              Download Setup File
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Token List -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Active Tokens</h3>
        <p class="mt-1 max-w-2xl text-sm text-gray-500">
          Tokens can be used once to register a new device and expire after 24 hours.
        </p>
      </div>

      <div v-if="tokensLoading" class="flex justify-center py-6">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-500"></div>
      </div>

      <div v-else-if="tokensError" class="bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ tokensError }}</p>
          </div>
        </div>
      </div>

      <div v-else-if="tokens.length === 0" class="bg-blue-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-blue-700">
              No active tokens found. Generate a new token to get started.
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
                  Token
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Expires
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="token in tokens" :key="token.token">
                <td class="px-6 py-4 whitespace-nowrap font-mono text-sm text-gray-900">
                  {{ token.token.substring(0, 16) }}...
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(token.createdAt) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(token.expiresAt) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span v-if="token.isUsed" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    Used
                  </span>
                  <span v-else-if="isExpired(token.expiresAt)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Expired
                  </span>
                  <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Valid
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <button
                    v-if="!token.isUsed && !isExpired(token.expiresAt)"
                    @click="viewToken(token)"
                    class="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- View Token Modal -->
    <div v-if="modalOpen" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="closeModal"></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-indigo-100 sm:mx-0 sm:h-10 sm:w-10">
                <svg class="h-6 w-6 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Authentication Token
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500 mb-4">
                    This token can be used once to register a new device. Copy it now as you won't be able to view it again.
                  </p>

                  <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700">Token</label>
                    <div class="mt-1 flex rounded-md shadow-sm">
                      <input
                        type="text"
                        id="modalTokenValue"
                        :value="selectedToken?.token"
                        readonly
                        class="flex-1 min-w-0 block w-full px-3 py-2 rounded-md sm:text-sm border border-gray-300 font-mono"
                      />
                      <button
                        @click="copyModalToken"
                        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        Copy
                      </button>
                    </div>
                  </div>

                  <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700">Expires</label>
                    <input
                      type="text"
                      :value="selectedToken ? formatDate(selectedToken.expiresAt) : ''"
                      readonly
                      class="mt-1 block w-full px-3 py-2 rounded-md sm:text-sm border border-gray-300"
                    />
                  </div>

                  <div class="rounded-md bg-gray-50 p-4">
                    <div class="flex">
                      <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                        </svg>
                      </div>
                      <div class="ml-3 flex-1 md:flex md:justify-between">
                        <p class="text-sm text-gray-700">
                          Use this token to register a new device with the device simulator.
                        </p>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="downloadModalSetupFile"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Download Setup File
            </button>
            <button
              @click="closeModal"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
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

interface Token {
  token: string;
  createdAt: string;
  expiresAt: string;
  isUsed: boolean;
}

interface NewToken {
  token: string;
  expiresAt: string;
}

export default defineComponent({
  name: 'TokenGenerator',
  setup() {
    // State
    const adminKey = ref<string>('');
    const loading = ref<boolean>(false);
    const newToken = ref<NewToken | null>(null);
    const tokens = ref<Token[]>([]);
    const tokensLoading = ref<boolean>(true);
    const tokensError = ref<string | null>(null);
    const selectedToken = ref<Token | null>(null);
    const modalOpen = ref<boolean>(false);

    // Methods
    const generateToken = async (): Promise<void> => {
      loading.value = true;

      try {
        const response = await api.generateToken(adminKey.value);
        newToken.value = response.data;
        adminKey.value = ''; // Clear admin key

        // Refresh token list
        fetchTokens();
      } catch (err: any) {
        alert(`Error generating token: ${err.response?.data?.error || err.message}`);
      } finally {
        loading.value = false;
      }
    };

    const fetchTokens = async (): Promise<void> => {
      tokensLoading.value = true;

      try {
        const response = await api.getTokens();
        tokens.value = response.data.tokens;
        tokensError.value = null;
      } catch (err: any) {
        tokensError.value = `Error loading tokens: ${err.response?.data?.error || err.message}`;
        console.error('Error loading tokens:', err);
      } finally {
        tokensLoading.value = false;
      }
    };

    const copyToken = (): void => {
      if (newToken.value) {
        navigator.clipboard.writeText(newToken.value.token)
          .then(() => {
            alert('Token copied to clipboard');
          })
          .catch(err => {
            console.error('Failed to copy token:', err);
          });
      }
    };

    const copyModalToken = (): void => {
      const tokenInput = document.getElementById('modalTokenValue') as HTMLInputElement;
      if (tokenInput) {
        tokenInput.select();
        document.execCommand('copy');
        alert('Token copied to clipboard');
      }
    };

    const downloadSetupFile = (): void => {
      if (!newToken.value) return;

      createAndDownloadSetupFile(newToken.value.token, newToken.value.expiresAt);
    };

    const downloadModalSetupFile = (): void => {
      if (!selectedToken.value) return;

      createAndDownloadSetupFile(selectedToken.value.token, selectedToken.value.expiresAt);
    };

    const createAndDownloadSetupFile = (token: string, expiresAt: string): void => {
      const setupData = {
        server_url: window.location.origin,
        auth_token: token,
        expires_at: expiresAt,
        generated_at: new Date().toISOString()
      };

      const blob = new Blob([JSON.stringify(setupData, null, 2)], {type: 'application/json'});
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = `device_setup_${new Date().getTime()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    };

    const viewToken = (token: Token): void => {
      selectedToken.value = token;
      modalOpen.value = true;
    };

    const closeModal = (): void => {
      modalOpen.value = false;
      selectedToken.value = null;
    };

    const isExpired = (dateString: string): boolean => {
      return new Date(dateString) < new Date();
    };

    const formatDate = (dateString: string): string => {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    };

    // Lifecycle hooks
    onMounted(() => {
      fetchTokens();
    });

    return {
      adminKey,
      loading,
      newToken,
      tokens,
      tokensLoading,
      tokensError,
      selectedToken,
      modalOpen,
      generateToken,
      fetchTokens,
      copyToken,
      copyModalToken,
      downloadSetupFile,
      downloadModalSetupFile,
      viewToken,
      closeModal,
      isExpired,
      formatDate
    };
  }
});
</script>