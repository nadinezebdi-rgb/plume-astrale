/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))'
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))'
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))'
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))'
        },
        plume: {
          night: '#111625',
          'night-deep': '#0C1120',
          'night-soft': '#1A2035',
          gold: '#D4AF37',
          'gold-bright': '#E8C766',
          lavender: '#E3D7FF',
          fire: '#E8A855',
          water: '#7BA5D9',
          air: '#C4B0E0',
          earth: '#9DAA82'
        },
        // Nocturne Éditorial — v4 (Feb 2026)
        nocturne: {
          night:       '#0B1A2E',
          astre:       '#141B2E',
          fusain:      '#0A0A0F',
          celeste:     '#F5F0E6',
          velin:       '#EDE6D8',
          craie:       '#FBF8F2',
          laiton:      '#B8935A',
          'laiton-dk': '#A17E4A',
          terre:       '#B47562',
          sauge:       '#8A9E8E',
          noctilucent: '#3D5A80',
          vigne:       '#4A2C3D',
        }
      },
      fontFamily: {
        'plume-serif': ['Cinzel', 'serif'],
        'plume-italic': ['"Cormorant Garamond"', 'serif'],
        'plume-body': ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        // Nocturne Éditorial
        'ne-serif': ['Fraunces', '"Cormorant Garamond"', 'Georgia', 'serif'],
        'ne-sans':  ['"Inter Tight"', 'Inter', 'system-ui', 'sans-serif'],
        'ne-mono':  ['"JetBrains Mono"', '"IBM Plex Mono"', 'monospace'],
      },
      spacing: {
        'ne-16': '128px',
        'ne-24': '192px',
      },
      transitionTimingFunction: {
        'plume-silk': 'cubic-bezier(0.22, 1, 0.36, 1)'
      },
      boxShadow: {
        'plume-glow': '0 0 24px rgba(212,175,55,0.35)',
        'plume-glow-lg': '0 0 40px rgba(212,175,55,0.55)',
        'plume-featured': '0 0 60px rgba(212,175,55,0.18), 0 0 0 1px rgba(212,175,55,0.08)'
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to:   { height: 'var(--radix-accordion-content-height)' }
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to:   { height: '0' }
        },
        'plume-fade-up': {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        }
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up':   'accordion-up 0.2s ease-out',
        'plume-fade-up':  'plume-fade-up 800ms cubic-bezier(0.22, 1, 0.36, 1) both'
      }
    }
  },
  plugins: [require("tailwindcss-animate")],
};
