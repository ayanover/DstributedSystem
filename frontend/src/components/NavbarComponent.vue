<template>
  <nav class="bg-white shadow">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <!-- Logo/Brand -->
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/" class="text-xl font-bold text-indigo-600">
              App
            </router-link>
          </div>

          <!-- Desktop Navigation Links -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <router-link
              to="/"
              class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              :class="{ 'border-indigo-500 text-gray-900': isActiveRoute('/') }"
            >
              Home
            </router-link>

            <router-link
              v-if="userStore.user.isAuthenticated"
              to="/dashboard"
              class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              :class="{ 'border-indigo-500 text-gray-900': isActiveRoute('/dashboard') }"
            >
              Dashboard
            </router-link>

            <router-link
              to="/about"
              class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              :class="{ 'border-indigo-500 text-gray-900': isActiveRoute('/about') }"
            >
              About
            </router-link>
          </div>
        </div>

        <!-- Auth Buttons / User Info -->
        <div class="hidden sm:ml-6 sm:flex sm:items-center">
          <template v-if="userStore.user.isAuthenticated">
            <!-- User Email -->
            <div class="mr-4 text-sm text-gray-500">
              {{ userStore.user?.email }}
            </div>

            <!-- Logout Button -->
            <button
              @click="handleLogout"
              class="ml-2 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Logout
            </button>
          </template>

          <template v-else>
            <!-- Login Button -->
            <router-link
              to="/login"
              class="px-4 py-2 text-sm font-medium text-indigo-600 hover:text-indigo-500"
            >
              Login
            </router-link>

            <!-- Register Button -->
            <router-link
              to="/register"
              class="ml-2 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Register
            </router-link>
          </template>
        </div>

        <!-- Mobile menu button -->
        <div class="flex items-center sm:hidden">
          <button
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
            aria-expanded="false"
          >
            <span class="sr-only">Open main menu</span>
            <!-- Icon when menu is closed -->
            <svg
              v-if="!isMobileMenuOpen"
              class="block h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <!-- Icon when menu is open -->
            <svg
              v-else
              class="block h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu, show/hide based on menu state -->
    <div v-if="isMobileMenuOpen" class="sm:hidden">
      <div class="pt-2 pb-3 space-y-1">
        <router-link
          to="/"
          class="bg-white border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          :class="{ 'bg-indigo-50 border-indigo-500 text-indigo-700': isActiveRoute('/') }"
          @click="isMobileMenuOpen = false"
        >
          Home
        </router-link>

        <router-link
          v-if="userStore.user.isAuthenticated"
          to="/dashboard"
          class="bg-white border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          :class="{ 'bg-indigo-50 border-indigo-500 text-indigo-700': isActiveRoute('/dashboard') }"
          @click="isMobileMenuOpen = false"
        >
          Dashboard
        </router-link>

        <router-link
          to="/about"
          class="bg-white border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          :class="{ 'bg-indigo-50 border-indigo-500 text-indigo-700': isActiveRoute('/about') }"
          @click="isMobileMenuOpen = false"
        >
          About
        </router-link>
      </div>

      <!-- Mobile Auth Buttons / User Info -->
      <div class="pt-4 pb-3 border-t border-gray-200">
        <template v-if="userStore.user.isAuthenticated">
          <div class="flex items-center px-4">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                <span class="text-indigo-800 font-medium text-sm">
                  {{ userStore.user?.email  }}
                </span>
              </div>
            </div>
            <div class="ml-3">
              <div class="text-base font-medium text-gray-800">
                {{ userStore.user?.email }}
              </div>
            </div>
          </div>
          <div class="mt-3 space-y-1">
            <button
              @click="handleLogout"
              class="block w-full text-left px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
            >
              Logout
            </button>
          </div>
        </template>

        <template v-else>
          <div class="space-y-1 px-4">
            <router-link
              to="/login"
              class="block py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
              @click="isMobileMenuOpen = false"
            >
              Login
            </router-link>

            <router-link
              to="/register"
              class="block py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
              @click="isMobileMenuOpen = false"
            >
              Register
            </router-link>
          </div>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import axios from "axios";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const isMobileMenuOpen = ref(false);

// Check if the current route matches the given path
const isActiveRoute = (path: string): boolean => {
  return route.path === path;
};



const handleLogout = async () => {
  try {
    userStore.logout();
    isMobileMenuOpen.value = false;
    router.push('/login');
  } catch (error) {
    console.error('Logout error:', error);
  }
};

onMounted(() => {

  userStore.initStore()
  const token = userStore.user.access
  if (token) {
    axios.defaults.headers.common["Authorization"] = "Bearer " + token
  } else {
    axios.defaults.headers.common["Authorization"] = ""
  }
})
</script>