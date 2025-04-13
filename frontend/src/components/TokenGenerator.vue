<template>
  <div class="token-generator">
    <h1>Authorization Tokens</h1>

    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Generate New Token</h5>
        <form @submit.prevent="generateToken">
          <div class="mb-3">
            <label for="adminKey" class="form-label">Admin Key</label>
            <input type="password" class="form-control" id="adminKey" v-model="adminKey" required>
            <div class="form-text">Enter the admin key to generate a new token.</div>
          </div>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
            Generate Token
          </button>
        </form>
      </div>
    </div>

    <div v-if="newToken" class="alert alert-success">
      <h5>Token Generated Successfully</h5>
      <p><strong>Token:</strong> <code>{{ newToken.token }}</code></p>
      <p><strong>Expires:</strong> {{ formatDate(newToken.expiresAt) }}</p>
      <p>Use this token to register a new device.</p>
      <div class="mt-3">
        <button @click="copyToken" class="btn btn-outline-primary btn-sm">
          Copy Token
        </button>
      </div>
    </div>

    <h2>Active Tokens</h2>

    <div v-if="tokensLoading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="tokensError" class="alert alert-danger">
      {{ tokensError }}
    </div>

    <div v-else-if="tokens.length === 0" class="alert alert-info">
      No active tokens found. Generate a new token to get started.
    </div>

    <div v-else class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Token</th>
            <th>Created</th>
            <th>Expires</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="token in tokens" :key="token.token">
            <td><code>{{ token.token.substring(0, 16) }}...</code></td>
            <td>{{ formatDate(token.createdAt) }}</td>
            <td>{{ formatDate(token.expiresAt) }}</td>
            <td>
              <span v-if="token.isUsed" class="badge bg-secondary">Used</span>
              <span v-else-if="isExpired(token.expiresAt)" class="badge bg-danger">Expired</span>
              <span v-else class="badge bg-success">Valid</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axios from 'axios';

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
    const adminKey = ref('');
    const loading = ref(false);
    const newToken = ref<NewToken | null>(null);
    const tokens = ref<Token[]>([]);
    const tokensLoading = ref(true);
    const tokensError = ref<string | null>(null);

    const generateToken = () => {
      loading.value = true;
      newToken.value = null;

      axios.post('/api/admin/generate-token', { adminKey: adminKey.value })
        .then(response => {
          newToken.value = response.data;
          adminKey.value = ''; // Clear admin key
          loading.value = false;

          // Refresh token list
          fetchTokens();
        })
        .catch(error => {
          alert('Error generating token: ' + (error.response?.data?.error || error.message));
          loading.value = false;
        });
    };

    const fetchTokens = () => {
      tokensLoading.value = true;

      axios.get('/api/admin/tokens')
        .then(response => {
          tokens.value = response.data.tokens;
          tokensLoading.value = false;
        })
        .catch(error => {
          const errorMessage = error.response?.data?.error || error.message;
          tokensError.value = 'Error loading tokens: ' + errorMessage;
          tokensLoading.value = false;
        });
    };

    const copyToken = () => {
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
      generateToken,
      fetchTokens,
      copyToken,
      isExpired,
      formatDate
    };
  }
});
</script>