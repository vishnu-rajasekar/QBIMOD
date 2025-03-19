// https://nuxt.com/docs/api/configuration/nuxt-config

import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
   modules: ["@nuxtjs/tailwindcss", "@nuxt/icon"],

   // You can store Speckle credentials or server URL here:
  runtimeConfig: {
    // Not exposed to the client
    speckleToken: '',
    speckleServerUrl: 'https://speckle.xyz',
    speckleStreamId: '',

    // If you need some public variables, put them here:
    public: {
      // e.g. baseURL for some public API
    },
  },
  
})
