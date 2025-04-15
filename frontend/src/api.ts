
import type { AxiosResponse } from 'axios'
import axios from "axios";

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


// axios functions
export default {
  // Device operations
  getDevices(): Promise<AxiosResponse<{ devices: Device[] }>> {
    return axios.get('/api/devices')
  },

  getDeviceCapabilities(deviceId: string): Promise<AxiosResponse<Device>> {
    return axios.get(`/api/devices/${deviceId}/capabilities`)
  },

  getDeviceCommands(deviceId: string): Promise<AxiosResponse<{ commands: Command[] }>> {
    return axios.get(`/api/devices/${deviceId}/commands`)
  },

  // Action operations
  getActionParameters(actionName: string): Promise<AxiosResponse<{
    action: string;
    parameters: ActionParameter[];
    description: string;
  }>> {
    return axios.get(`/api/actions/${actionName}/parameters`)
  },

  // Command operations
  executeCommand(
    deviceId: string,
    commandName: string,
    params: Record<string, any>
  ): Promise<AxiosResponse<CommandExecutionResponse>> {
    return axios.post('/api/execute-command', {
      deviceId,
      command: commandName,
      params
    })
  },

  getCommandStatus(commandId: string): Promise<AxiosResponse<Command>> {
    return axios.get(`/api/commands/${commandId}`)
  },

  getAllCommands(): Promise<AxiosResponse<{ commands: Command[] }>> {
    return axios.get('/api/commands')
  },

  generateToken(adminKey: string): Promise<AxiosResponse<{
    token: string;
    expiresAt: string;
  }>> {
    return axios.post('/api/admin/generate-token', { adminKey })
  },

  getTokens(): Promise<AxiosResponse<{ tokens: Token[] }>> {
    return axios.get('/api/admin/tokens')
  },

  getServerPublicKey(): Promise<AxiosResponse<{ publicKey: string }>> {
    return axios.get('/api/server-key')
  }
}