/// <reference types="vite/client" />

// This adds Vite environment variable types
interface ImportMeta {
  readonly env: {
    readonly BASE_URL: string;
    readonly MODE: string;
    readonly DEV: boolean;
    readonly PROD: boolean;
    readonly SSR: boolean;
    readonly VITE_API_BASE_URL?: string;
    [key: string]: string | boolean | undefined;
  };
}

// Vue template SFCs type declaration
declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
} 