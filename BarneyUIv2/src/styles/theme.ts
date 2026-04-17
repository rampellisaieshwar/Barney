import { createStitches } from '@stitches/react';

export const {
  styled,
  css,
  globalCss,
  keyframes,
  getCssText,
  theme,
  createTheme,
  config,
} = createStitches({
  theme: {
    colors: {
      // Varanasi Cinematic Palette (Coal & Fire)
      backgroundDeep: '#050404',        // Absolute depth
      backgroundMid: '#0d0c0b',         // Sub-surface
      backgroundSurface: '#161412',     // Overlay depth
      
      // Atmospheric firelight
      amberWarm: '#d4a574',             // Classic amber
      amberGlow: '#f0c68e',             // Highlight shine
      amberFire: '#ff8c00',             // Core flame
      copper: '#b87333',                // Industrial copper
      copperGlow: 'rgba(184, 115, 51, 0.4)', // Border bloom
      bronze: '#8b6914',
      
      // Cinematic shadow & contrast accents
      coalDeep: '#121212',
      crimsonDeep: '#5e0d25',           // Receded blood
      crimson: '#a11832',               // Active fire
      
      // Text hierarchy (Parchment & Warmth)
      textPrimary: '#f5f0e8',
      textSecondary: '#a89f8f',
      textMuted: '#5c544d',
      
      // Glassmorphism (Varanasi Pane)
      glassBackground: 'rgba(10, 9, 8, 0.65)',
      glassBorder: 'rgba(212, 165, 116, 0.12)',
      glassHighlight: 'rgba(255, 255, 255, 0.03)',
      glassShadow: 'rgba(0, 0, 0, 0.5)',
      
      // Status (Jewel Tones)
      success: '#4ade80',
      running: '#38bdf8',
      variantHighlight: 'rgba(56, 189, 248, 0.15)',
      warning: '#fbbf24',
      error: '#f87171',
    },
    fonts: {
      body: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
      display: '"Space Grotesk", sans-serif',
    },
    fontSizes: {
      xs: '0.75rem',
      sm: '0.875rem',
      md: '1rem',
      lg: '1.125rem',
      xl: '1.5rem',
      '2xl': '2rem',
      '3xl': '3rem',
    },
    space: {
      1: '4px',
      2: '8px',
      3: '12px',
      4: '16px',
      5: '20px',
      6: '24px',
      8: '32px',
      10: '40px',
      12: '48px',
      16: '64px',
    },
    radii: {
      sm: '4px',
      md: '8px',
      lg: '12px',
      xl: '16px',
      '2xl': '24px',
      full: '9999px',
    },
    shadows: {
      glow: '0 0 40px rgba(212, 165, 116, 0.15)',
      deep: '0 8px 32px rgba(0, 0, 0, 0.6)',
      layer: '0 4px 16px rgba(0, 0, 0, 0.4)',
    },
    transitions: {
      slow: 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
      medium: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
      fast: 'all 0.15s ease-out',
    },
  },
  media: {
    mobile: '(max-width: 640px)',
    tablet: '(max-width: 1024px)',
    desktop: '(min-width: 1025px)',
  },
  utils: {
    px: (value: string | number) => ({ paddingLeft: value, paddingRight: value }),
    py: (value: string | number) => ({ paddingTop: value, paddingBottom: value }),
    mx: (value: string | number) => ({ marginLeft: value, marginRight: value }),
    my: (value: string | number) => ({ marginTop: value, marginBottom: value }),
  },
});

import { createContext, useContext } from 'react';

export const ThemeProvider = createContext<Record<string, unknown>>({});

export function useTheme() {
  return useContext(ThemeProvider);
}

export const globalStyles = globalCss({
  '@import': 'url(https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap)',

  '*': {
    margin: 0,
    padding: 0,
    boxSizing: 'border-box',
  },

  'html, body': {
    height: '100%',
    backgroundColor: '$backgroundDeep',
    color: '$textPrimary',
    fontFamily: '$body',
    fontSize: '16px',
    lineHeight: 1.6,
    overflow: 'hidden',
    WebkitFontSmoothing: 'antialiased',
    MozOsxFontSmoothing: 'grayscale',
  },

  '#root': {
    height: '100%',
  },

  '::selection': {
    backgroundColor: '$amberWarm',
    color: '$backgroundDeep',
  },

  '::-webkit-scrollbar': {
    width: '6px',
    height: '6px',
  },

  '::-webkit-scrollbar-track': {
    background: 'transparent',
  },

  '::-webkit-scrollbar-thumb': {
    background: '$glassBorder',
    borderRadius: '$full',
  },

  '::-webkit-scrollbar-thumb:hover': {
    background: '$amberWarm',
  },
});