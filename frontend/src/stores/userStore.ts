import { defineStore } from "pinia";
import axios from "axios";

interface User {
  isAuthenticated: boolean;
  id: number | null;
  email: string | null;
  name: string | null;
  is_staff: boolean;
  access: string | null;
  refresh: string | null;
}

interface State {
  user: User;
  loading: boolean;
  error: string | null;
}

export const useUserStore = defineStore("user",{
  state: (): State => ({
    user: {
      isAuthenticated: false,
      id: null,
      email: null,
      name: null,
      is_staff: false,
      access: null,
      refresh: null,
    },
    loading: false,
    error: null,
  }),
  actions: {
    async initStore(): Promise<void> {
      if (localStorage.getItem("user.access")) {
        this.user.access = localStorage.getItem("user.access");
        this.user.refresh = localStorage.getItem("user.refresh");
        this.user.isAuthenticated = true;

        try {
          const response = await axios.get("/api/me/", {
            headers: {
              Authorization: `Bearer ${this.user.access}`,
            },
          });
          this.setUserInfo(response.data);
        } catch (error) {
          console.error("Failed to fetch user info:", error);
          this.removeToken();
        }

        this.refreshToken();
      }
    },
    setToken(data: { access: string; refresh: string }): void {
      console.log('g');
      this.user.access = data.access;
      this.user.refresh = data.refresh;
      this.user.isAuthenticated = true;
      localStorage.setItem("user.access", data.access);
      localStorage.setItem("user.refresh", data.refresh);
    },
    removeToken(): void {
      this.user.isAuthenticated = false;
      this.user.access = null;
      this.user.refresh = null;
      this.user.id = null;
      this.user.email = null;
      this.user.name = null;
      this.user.is_staff = false;
      localStorage.clear();
    },
    setUserInfo(user: Omit<User, 'isAuthenticated' | 'access' | 'refresh'>): void {
      this.user.id = user.id;
      this.user.email = user.email;
      this.user.name = user.name;
      this.user.is_staff = user.is_staff;
      localStorage.setItem("user.id", user.id?.toString() || "");
      localStorage.setItem("user.email", user.email || "");
      localStorage.setItem("user.email", user.name || "");
      localStorage.setItem("user.is_staff", user.is_staff.toString());
    },
    async refreshToken(): Promise<void> {
      try {
        const response = await axios.post("/api/refresh/", {
          refresh: this.user.refresh,
        });
        this.user.access = response.data.access;
        localStorage.setItem("user.access", response.data.access);
        axios.defaults.headers.common["Authorization"] = `Bearer ${response.data.access}`;
      } catch (error) {
        this.removeToken();
      }
    },

    logout(): void {
      this.removeToken();
    },
  },
});