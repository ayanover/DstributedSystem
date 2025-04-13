<template>
  <div class="device-detail">
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else-if="device">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>{{ device.deviceType }} Device</h1>
        <router-link to="/" class="btn btn-outline-secondary">
          Back to Devices
        </router-link>
      </div>

      <div class="card mb-4">
        <div class="card-body">
          <h5 class="card-title">Device Information</h5>
          <div class="row">
            <div class="col-md-6">
              <p><strong>Device ID:</strong> {{ device.deviceId }}</p>
              <p><strong>Type:</strong> {{ device.deviceType }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Last Seen:</strong> {{ formatDate(device.lastSeen) }}</p>
              <p>
                <strong>Capabilities:</strong>
                <span v-for="capability in device.capabilities" :key="capability"
                      class="badge bg-info me-1">{{ capability }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <h2>Command History</h2>

      <div v-if="commands.length === 0" class="alert alert-info">
        No commands have been executed on this device yet.
      </div>

      <div v-else class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Command</th>
              <th>Parameters</th>
              <th>Status</th>
              <th>Result</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="command in commands" :key="command.id">
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

    <div v-else class="alert alert-warning">
      Device not found
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DeviceDetail',
  data() {
    return {
      device: null,
      commands: [],
      loading: true,
      error: null
    };
  },
  mounted() {
    this.fetchDeviceData();
  },
  methods: {
    fetchDeviceData() {
      const deviceId = this.$route.params.deviceId;

      // Fetch device data
      axios.get(`/api/devices/${deviceId}/capabilities`)
        .then(response => {
          this.device = response.data;

          // Fetch command history
          return axios.get(`/api/devices/${deviceId}/commands`);
        })
        .then(response => {
          this.commands = response.data.commands;
          this.loading = false;
        })
        .catch(error => {
          this.error = 'Error loading device data: ' + (error.response?.data?.error || error.message);
          this.loading = false;
        });
    },

    getStatusBadgeClass(status) {
      switch (status) {
        case 'completed': return 'badge bg-success';
        case 'pending': return 'badge bg-warning text-dark';
        case 'sent': return 'badge bg-info text-dark';
        case 'failed': return 'badge bg-danger';
        default: return 'badge bg-secondary';
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).format(date);
    }
  }
};
</script>
