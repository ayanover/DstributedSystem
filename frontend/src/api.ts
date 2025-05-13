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
  description?: string;
}

export interface CommandResult {
  status: string;
  result?: any;
  error?: string;
  stdout?: string;
  stderr?: string;
  error_type?: string;
  success?: boolean;
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

const API_URL = import.meta.env.VITE_API_URL || '/api/';

// axios functions
export default {
  // Authentication
  login(email: string, password: string): Promise<AxiosResponse<any>> {
    return axios.post(`${API_URL}login/`, { email, password });
  },

  register(user: any): Promise<AxiosResponse<any>> {
    return axios.post(`${API_URL}register/`, user);
  },

  getMe(): Promise<AxiosResponse<any>> {
    return axios.get(`${API_URL}me/`);
  },

  // Device operations
  getDevices(): Promise<AxiosResponse<{ devices: Device[] }>> {
    return axios.get(`${API_URL}devices/`);
  },

  getDeviceCapabilities(deviceId: string): Promise<AxiosResponse<Device>> {
    return axios.get(`${API_URL}devices/${deviceId}/capabilities/`);
  },

  getDeviceCommands(deviceId: string): Promise<AxiosResponse<{ commands: Command[] }>> {
    return axios.get(`${API_URL}devices/${deviceId}/commands/`);
  },
  getAllDevices() {
  return axios.get(`${API_URL}devices/all/`);
  },
  // Action operations
  getActionParameters(actionName: string): Promise<AxiosResponse<{
    action: string;
    parameters: ActionParameter[];
    description: string;
  }>> {
    return axios.get(`${API_URL}actions/${actionName}/parameters/`);
  },

  // Command operations
  executeCommand(
    deviceId: string,
    commandName: string,
    params: Record<string, any>
  ): Promise<AxiosResponse<CommandExecutionResponse>> {
    return axios.post(`${API_URL}execute-command/`, {
      deviceId,
      command: commandName,
      params
    });
  },

  getCommandStatus(commandId: string): Promise<AxiosResponse<Command>> {
    return axios.get(`${API_URL}commands/${commandId}/status/`);
  },

  // Updated to use the new all commands endpoint
  getAllCommands(): Promise<AxiosResponse<{ commands: Command[] }>> {
    return axios.get(`${API_URL}commands/all/`);
  },

  // Token operations
  generateToken(adminKey: string): Promise<AxiosResponse<{
    token: string;
    expiresAt: string;
  }>> {
    return axios.post(`${API_URL}tokens/generate/`, { adminKey });
  },

  getTokens(): Promise<AxiosResponse<{ tokens: Token[] }>> {
    return axios.get(`${API_URL}tokens/active/`);
  },

  // Server operations
  getServerPublicKey(): Promise<AxiosResponse<{ publicKey: string }>> {
    return axios.get(`${API_URL}server-key/`);
  },

  // Device reconnection
  reconnectDevice(deviceId: string, publicKey: string): Promise<AxiosResponse<any>> {
    return axios.post(`${API_URL}reconnect-device/`, {
      deviceId,
      publicKey
    });
  }
}