export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4F46E5',
          light: '#818CF8',
          dark: '#3730A3',
          tint: '#EEF2FF'
        },
        accent: '#7C3AED',
        cta: {
          DEFAULT: '#F97316',
          dark: '#EA580C'
        },
        surface: '#FFFFFF',
        page: '#F8FAFC',
        'bg-alt': '#EEF2FF',
        ink: {
          primary: '#1E1B4B',
          secondary: '#64748B',
          muted: '#94A3B8'
        },
        line: {
          DEFAULT: '#E2E8F0',
          focus: '#C7D2FE'
        },
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
        info: '#0EA5E9'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', "'Segoe UI'", 'sans-serif']
      },
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)',
        'card-hover': '0 4px 16px rgba(79,70,229,0.12)',
        modal: '0 20px 60px rgba(0,0,0,0.15)'
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '16px'
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' }
        }
      },
      animation: {
        shimmer: 'shimmer 1.5s infinite'
      }
    }
  },
  plugins: []
}
