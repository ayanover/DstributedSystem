<template>
  <div class="device-list">
    <h1>Connected Devices</h1>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else-if="devices.length === 0" class="alert alert-info">
      No devices are connected. Generate a token and register a device to get started.
    </div>

    <div v-else class="row">
      <div v-for="device in devices" :key="device.deviceId" class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">{{ device.deviceType }}</h5>
            <span class="badge bg-secondary">{{ formatDate(device.lastSeen) }}</span>
          </div>
          <div class="card-body">
            <p class="card-text">Device ID: {{ device.deviceId }}</p>
            <p class="card-text">
              <strong>Capabilities:</strong>
              <span v-for="capability in device.capabilities" :key="capability"
                    class="badge bg-info me-1">{{ capability }}</span>
            </p>
          </div>
          <div class="card-footer">
            <button @click="selectDevice(device)" class="btn btn-primary">
              Execute Command
            </button>
            <router-link :to="'/devices/' + device.deviceId" class="btn btn-outline-secondary ms-2">
              View History
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Command Execution Modal -->
    <div class="modal fade" id="commandModal" tabindex="-1" ref="commandModal">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedDevice">
          <div class="modal-header">
            <h5 class="modal-title">Execute Command on {{ selectedDevice.deviceType }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <!-- Step 1: Select Action -->
            <div v-if="commandStep === 1">
              <div class="mb-3">
                <label class="form-label">Select Action</label>
                <select v-model="selectedAction" class="form-select" @change="fetchActionParameters">
                  <option value="">-- Select Action --</option>
                  <option v-for="capability in selectedDevice.capabilities" :key="capability" :value="capability">
                    {{ capability }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Step 2: Enter Parameters -->
            <div v-else-if="commandStep === 2">
              <h6>Action: {{ selectedAction }}</h6>

              <div v-if="actionParameters.length === 0" class="alert alert-info">
                Loading parameters...
              </div>

              <form @submit.prevent="executeCommand" v-else>
                <div v-for="param in actionParameters" :key="param.name" class="mb-3">
                  <label :for="param.name" class="form-label">{{ param.name }}</label>
                  <input :type="param.type" class="form-control" :id="param.name"
                         v-model="paramValues[param.name]" :required="param.required">
                </div>
              </form>
            </div>

            <!-- Step 3: Result -->
            <div v-else-if="commandStep === 3">
              <div v-if="commandStatus === 'pending'" class="text-center my-3">
                <div class="spinner-border" role="status">
                  <span class="visually-hidden">Processing...</span>
                </div>
                <p class="mt-2">Command is being processed...</p>
              </div>

              <div v-else-if="commandStatus === 'completed'" class="alert alert-success">
                <h6>Command Completed</h6>
                <p><strong>Result:</strong> {{ commandResult.result }}</p>
              </div>

              <div v-else-if="commandStatus === 'failed'" class="alert alert-danger">
                <h6>Command Failed</h6>
                <p><strong>Error:</strong> {{ commandResult.error }}</p>
                </div>
              </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>

            <button v-if="commandStep === 1" type="button" class="btn btn-primary"
                    :disabled="!selectedAction" @click="commandStep = 2">
              Next
            </button>

            <button v-if="commandStep === 2" type="button" class="btn btn-secondary"
                    @click="commandStep = 1">
              Back
            </button>

            <button v-if="commandStep === 2" type="button" class="btn btn-primary"
                    @click="executeCommand">
              Execute
            </button>

            <button v-if="commandStep === 3" type="button" class="btn btn-primary"
                    @click="resetCommand">
              New Command
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Modal } from 'bootstrap';

export default {
  name: 'DeviceList',
  data() {
    return {
      devices: [],
      loading: true,
      error: null,
      selectedDevice: null,
      selectedAction: '',
      actionParameters: [],
      paramValues: {},
      commandStep: 1,
      commandId: null,
      commandStatus: null,
      commandResult: null,
      modal: null,
      pollInterval: null
    };
  },
  mounted() {
    this.fetchDevices();
  },
  unmounted() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  },
  methods: {
    fetchDevices() {
      this.loading = true;
      axios.get('/api/devices')
        .then(response => {
          this.devices = response.data.devices;
          this.loading = false;
        })
        .catch(error => {
          this.error = 'Error loading devices: ' + (error.response?.data?.error || error.message);
          this.loading = false;
        });
    },

    selectDevice(device) {
      this.selectedDevice = device;
      this.selectedAction = '';
      this.actionParameters = [];
      this.paramValues = {};
      this.commandStep = 1;
      this.commandId = null;
      this.commandStatus = null;
      this.commandResult = null;

      // Initialize and show modal
      if (!this.modal) {
        this.modal = new Modal(this.$refs.commandModal);
      }
      this.modal.show();
    },

    fetchActionParameters() {
      if (!this.selectedAction) return;

      axios.get(`/api/actions/${this.selectedAction}/parameters`)
        .then(response => {
          this.actionParameters = response.data.parameters;
          this.paramValues = {};

          // Initialize parameter values
          this.actionParameters.forEach(param => {
            this.paramValues[param.name] = '';
          });
        })
        .catch(error => {
          console.error('Error fetching parameters:', error);
          this.actionParameters = [
            { name: 'num1', type: 'number', required: true },
            { name: 'num2', type: 'number', required: true }
          ];
        });
    },

    executeCommand() {
      // Validate parameters
      let valid = true;
      this.actionParameters.forEach(param => {
        if (param.required && !this.paramValues[param.name]) {
          valid = false;
        }
      });

      if (!valid) {
        alert('Please fill in all required parameters');
        return;
      }

      // Create command data
      const commandData = {
        deviceId: this.selectedDevice.deviceId,
        command: this.selectedAction,
        params: this.paramValues
      };

      // Send command
      axios.post('/api/execute-command', commandData)
        .then(response => {
          this.commandId = response.data.commandId;
          this.commandStep = 3;
          this.commandStatus = 'pending';

          // Start polling for result
          this.pollCommandStatus();
        })
        .catch(error => {
          alert('Error executing command: ' + (error.response?.data?.error || error.message));
        });
    },

    pollCommandStatus() {
      // Clear any existing interval
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
      }

      // Set up polling
      this.pollInterval = setInterval(() => {
        axios.get(`/api/commands/${this.commandId}`)
          .then(response => {
            const command = response.data;

            if (command.status !== 'pending' && command.status !== 'sent') {
              // Command completed or failed
              clearInterval(this.pollInterval);
              this.pollInterval = null;

              this.commandStatus = command.status;
              this.commandResult = command.result;
            }
          })
          .catch(error => {
            console.error('Error polling command status:', error);
            clearInterval(this.pollInterval);
            this.pollInterval = null;

            this.commandStatus = 'failed';
            this.commandResult = { error: 'Error retrieving command status' };
          });
      }, 2000);  // Poll every 2 seconds
    },

    resetCommand() {
      this.commandStep = 1;
      this.selectedAction = '';
      this.paramValues = {};
      this.commandId = null;
      this.commandStatus = null;
      this.commandResult = null;
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    }
  }
};
</script>