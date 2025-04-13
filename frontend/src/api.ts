import axios, { AxiosResponse } from 'axios'

export interface Device {
  id: string;
  deviceId: string;
  deviceType: string;
  capabilities: string[];
  lastSeen: string;
}

export interface ActionParameter {
  name: string;
  type: string;
  required: boolean;
}

export interface CommandResult {
  status: string;
  result?: any;
  error?: string;
}

export interface Command {
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

export interface Token {
  token: string;
  createdAt: string;
  expiresAt: string;
  isUsed: boolean;
}

export interface CommandExecutionRequest {
  deviceId: string;
  command: string;
  params: Record<string, any>;
}

export interface CommandExecutionResponse {
  status: string;
  commandId: string;
}

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// API functions
export default {
  // Device operations
  getDevices(): Promise<AxiosResponse<{ devices: Device[] }>> {
    return api.get('/devices')
  },

  getDeviceCapabilities(deviceId: string): Promise<AxiosResponse<Device>> {
    return api.get(`/devices/${deviceId}/capabilities`)
  },

  getDeviceCommands(deviceId: string): Promise<AxiosResponse<{ commands: Command[] }>> {
    return api.get(`/devices/${deviceId}/commands`)
  },

  // Action operations
  getActionParameters(actionName: string): Promise<AxiosResponse<{
    action: string;
    parameters: ActionParameter[];
    description: string;
  }>> {
    return api.get(`/actions/${actionName}/parameters`)
  },

  // Command operations
  executeCommand(
    deviceId: string,
    commandName: string,
    params: Record<string, any>
  ): Promise<AxiosResponse<CommandExecutionResponse>> {
    return api.post('/execute-command', {
      deviceId,
      command: commandName,
      params
    })
  },

  getCommandStatus(commandId: string): Promise<AxiosResponse<Command>> {
    return api.get(`/commands/${commandId}`)
  },

  getAllCommands(): Promise<AxiosResponse<{ commands: Command[] }>> {
    return api.get('/commands')
  },

  // Token operations
  generateToken(adminKey: string): Promise<AxiosResponse<{
    token: string;
    expiresAt: string;
  }>> {
    return api.post('/admin/generate-token', { adminKey })
  },

  getTokens(): Promise<AxiosResponse<{ tokens: Token[] }>> {
    return api.get('/admin/tokens')
  },

  // Server information
  getServerPublicKey(): Promise<AxiosResponse<{ publicKey: string }>> {
    return api.get('/server-key')
  }
}