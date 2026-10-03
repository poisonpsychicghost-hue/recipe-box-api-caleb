# recipe-box frontend —style guide

## 1. brand & tone
- adjectives:
    - calm
    - bento-box-like
    - minimal
    -clean
- goal: 
    - feel like an organized quiet kitchen workstation
    - UX should feel predictable and low-friction, never loud

## 2. color system

>> NOTE: hex codes are. initial; adjustments needed after visualization prototyping

- primary:
    - nmae: seaweed green-black
    - hex: `#0F2A24`
    - usage:
        - header beackground
        - primary buttons
        - key text on light backgrounds

- background:
    - name: cowrie-shell off-white
    - hex: `#F7F3EC`
    - usage:
        - main app background
        - page surfaces

- surface: 
    - name: card shell 
    - hex: `#FBF7F0`
    - usage: 
        - recipe cards
        - modal backgrounds

- accent: 
    - name: textured slate
    - hex: `#4C5C68`
    - usage:
        - borders
        - dividers
        - secondary buttons

- state colors: 
    - success: `#46B38A` (soft green)
    - error: `#D56464` (muted red)
    - info: `#4D7EA8` (calm blue)
    - warning: `#E6A15D` (warm amber)

- dark theme: 
    - background: near-black green `#040908`
    - surfaces: dark slate `#222B32`
    - text: cowrie-shell off-white
    - keep constrasts comfortable, avoid neons

## 3. typography

- base font stack:
    - `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- headings (H1-H3, recipe titles):
    - serif font:
        - `"Merriweather", "Gerogia", "Times New Roman", serif`
- navigation / UI chrome: 
    - `"Lato", "Roboto", system-ui, sans-serif`
- dyslexic-friendly option:
    - configurable in Settings:
        - `"OpenDyslexic", "Atkinson Hyperlegible", system-ui, sans-serif`
    - implementation:
        -when enabled, apply as base font-family on `body`

- sizes (base scale):
    - body: 16px
    - small text: 14px
    - h3: 20px
    - h2: 24px
    - h1: 30px
- scaling:
    - `fontSizeScale` setting in theme composable:
        - small: 0.9
        - normal: 1.0
        - large: 1.1
        - extra-large: 1.25

## 4. spacing & layout

- base spacing unit: **8px**
    - XS: 4px
    - S: 8px
    - M: 16px
    - L: 24px
    - XL: 32px

- card layout: 
    - border rapdius: 12px
    - padding: 
        - outer:  16px
        - inner: 8px
    - shadow:
        - very soft, low blur, to keep the feel calm

- grid behavior:
    - desktop (>= 1024px): up to 3 columns
    - tablet / landscape mobile (>= 768px): up to 2 columns
    - mobile (< 768px): 1 column
- content:
    - max content width for main panel: 960-1200px to keep lines readable

# 5. components — visual rules

### 5.1 recipe card
- structure:
    - header: title (serif, medium weight)
    - body:
        - two columns on wide screens: 
            - left: instructions (scrollable area)
            - right: ingredients (scrollable area)
        - stacked vertically in mobile
    - footer:
    - owner (shown only if user is owner or admin)
    - action buttons: Modify, Delete
- behavior: 
    - hover: slight elevation + subtle border color shift
    - focus (keyboard): visible outline using accent color

### 5.2 navigation bar
- background: primary color in light theme
- text: off-white for light-theme; reversed for dark
- active tab: 
    - pill highlight
    - slightly higher contrast
- right side: 
    - `username` + `role` tag (badge)
    - light/dark toggle (simple icon)

### 5.3 forms (login, add, edit)
- labels always visible (no placeholder-only)
- input background: card shell white
- focus: 
    - outlined with accent green
- error messages: 
    - muted red text, small size under field
- submit buttons: 
    - filled primary color
    - disabled state: lower opacity, no hover effect

### 5.4 modals & notifications
- modals: 
    - centered, max width (e.g 480px)
    - smae card styling
    - clear primary action vs secondary action
- toasts/snackbars:
    - appear top-right
    - types:
        - success: (green)
        - error: (red)
        - info (blue)
    - auto-dismiss after a few seconds (10), with manual close option (x)

## 6. accessibility & UX notes:
- color constras:
    - aim for WCAG AA for body text
- keyboard: 
    - all interacitve elements focusable
    - modals trap focus while open
- motion: 
    - keep animation subtle (fade <= 200ms)
- states: 
    - always show visual fedback on:
        - loading (spinner)
        - errors (clear messages)
        - empty lists (friends "No Recipes Yet" message)
    
## 7. theming implementation notes
- expose tokens as CSS variables:
    - `--color-bg`, `--color-surface`, `--color-primary`, `--radius-card`, `--space-unit`, etc
- light/dark switch toggles a root class:
    - `.theme-light` vs `.theme-dark`
- dyslexic font toggle:
    - add class on `body` (`.font-dyslexic`) and adjust font family
