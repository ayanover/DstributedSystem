<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="name" class="sr-only">Name</label>
            <input
              id="name"
              name="name"
              type="text"
              autocomplete="name"
              required
              v-model="name"
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Full name"
            />
          </div>
          <div>
            <label for="email-address" class="sr-only">Email address</label>
            <input
              id="email-address"
              name="email"
              type="email"
              autocomplete="email"
              required
              v-model="email"
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Email address"
            />
          </div>
          <div>
            <label for="password1" class="sr-only">Password</label>
            <input
              id="password1"
              name="password1"
              type="password"
              autocomplete="new-password"
              required
              v-model="password1"
              @input="validatePasswords"
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Password"
            />
          </div>
          <div>
            <label for="password2" class="sr-only">Confirm Password</label>
            <input
              id="password2"
              name="password2"
              type="password"
              autocomplete="new-password"
              required
              v-model="password2"
              @input="validatePasswords"
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Confirm Password"
            />
          </div>
        </div>

        <!-- Error display window -->
        <div v-if="hasErrors" class="p-3 rounded-md bg-red-50 border border-red-200">
          <p class="text-sm text-red-600 font-medium">Please fix the following issues:</p>
          <ul class="mt-1 text-sm text-red-600 list-disc list-inside">
            <li v-if="!isPasswordLengthValid">Password must be at least 8 characters long</li>
            <li v-if="isPasswordOnlyNumbers">Password cannot contain only numbers</li>
            <li v-if="!doPasswordsMatch">Passwords do not match</li>
            <li v-if="errorMessage">{{ errorMessage }}</li>
          </ul>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            Register
          </button>
        </div>
      </form>

      <div class="text-center mt-4">
        <p class="text-sm text-gray-600">
          Already have an account?
          <router-link to="/login" class="font-medium text-indigo-600 hover:text-indigo-500">
            Sign in
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const name = ref('');
const email = ref('');
const password1 = ref('');
const password2 = ref('');
const isLoading = ref(false);
const errorMessage = ref('');

const isPasswordLengthValid = ref(true);
const isPasswordOnlyNumbers = ref(false);
const doPasswordsMatch = ref(true);

const hasErrors = computed(() => {
  return !isPasswordLengthValid.value ||
         isPasswordOnlyNumbers.value ||
         !doPasswordsMatch.value ||
         errorMessage.value !== '';
});

const validatePasswords = () => {
  isPasswordLengthValid.value = password1.value.length === 0 || password1.value.length >= 8;

  isPasswordOnlyNumbers.value = password1.value.length > 0 && /^\d+$/.test(password1.value);

  doPasswordsMatch.value =
    password1.value.length === 0 ||
    password2.value.length === 0 ||
    password1.value === password2.value;

  if (errorMessage.value) {
    errorMessage.value = '';
  }
};

const isFormValid = computed(() => {
  return (
    name.value.trim() !== '' &&
    email.value.trim() !== '' &&
    password1.value.trim() !== '' &&
    password2.value.trim() !== '' &&
    password1.value === password2.value &&
    password1.value.length >= 8 &&
    !/^\d+$/.test(password1.value)
  );
});

const handleRegister = async () => {
  validatePasswords();

  if (!isFormValid.value) {
    return;
  }

  errorMessage.value = '';

  try {
    isLoading.value = true;

    const response = await axios.post('/api/register/', {
      name: name.value,
      email: email.value,
      password1: password1.value,
      password2: password2.value
    });

    console.log(response.data);

    if (response.data && response.data.message === 'success') {
      router.push('/login');
    } else {
      errorMessage.value = 'Registration failed. Please try again.';
    }
  } catch (error) {
    console.error('Registration error:', error);
    errorMessage.value = 'Failed to register. Please try again.';
  } finally {
    isLoading.value = false;
  }
};
</script>