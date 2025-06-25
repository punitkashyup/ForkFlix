/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      screens: {
        'tablet': { 'min': '768px', 'max': '1023px' }, // Tablet only range
        'tablet-lg': '1024px', // Large tablets in landscape
        'desktop': '1024px',   // Desktop and larger screens
        'xl': '1440px',        // Large desktop screens
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      },
      spacing: {
        '18': '4.5rem',  // 72px - Good for tablet touch targets
        '22': '5.5rem',  // 88px - Larger tablet spacing
      },
      fontSize: {
        'tablet-xs': ['0.75rem', '1rem'],   // 12px
        'tablet-sm': ['0.875rem', '1.25rem'], // 14px
        'tablet-base': ['1rem', '1.5rem'],   // 16px
        'tablet-lg': ['1.125rem', '1.75rem'], // 18px
        'tablet-xl': ['1.25rem', '1.75rem'],  // 20px
        'tablet-2xl': ['1.5rem', '2rem'],     // 24px
        'tablet-3xl': ['1.875rem', '2.25rem'], // 30px
        'tablet-4xl': ['2.25rem', '2.5rem'],   // 36px
      },
      minHeight: {
        'touch': '44px', // Minimum touch target for accessibility
      },
      maxWidth: {
        'tablet': '1024px',     // Max width for tablet layouts
        'tablet-content': '896px', // Content width for 13-inch tablets
      }
    }
  },
  plugins: []
}