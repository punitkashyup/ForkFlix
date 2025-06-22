/**
 * Global type declarations for Recipe Reel Manager
 */

// Instagram embed script types
declare global {
  interface Window {
    instgrm?: {
      Embeds: {
        process(): void;
      };
    };
  }
}

export {};