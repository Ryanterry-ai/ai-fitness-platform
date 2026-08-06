# Milestone 2: Design System — PURE HEALTH SUPPS

## Brand DNA (Extracted from Reference Images)

### Visual Identity
- **Brand**: PURE HEALTH SUPPS
- **Product**: PRIME X Pre-Workout
- **Positioning**: Premium Indian sports nutrition for serious athletes
- **Aesthetic**: Dark, powerful, high-energy, gym/fitness, no-nonsense

### Color Palette (from label/logo analysis)

#### Primary Colors
| Name | Hex | RGB | Usage |
|---|---|---|---|
| PURE Yellow | `#FFD700` | 255, 215, 0 | CTAs, accents, highlights, price |
| PURE Black | `#0A0A0B` | 10, 10, 11 | Backgrounds, text on light |
| PURE White | `#FFFFFF` | 255, 255, 255 | Text on dark, cards |

#### Secondary Colors
| Name | Hex | RGB | Usage |
|---|---|---|---|
| Dark Gray | `#1A1A1C` | 26, 26, 28 | Card backgrounds, secondary surfaces |
| Medium Gray | `#27272A` | 39, 39, 42 | Borders, dividers |
| Light Gray | `#A1A1AA` | 161, 161, 170 | Muted text, captions |
| Off-White | `#FAFAFA` | 250, 250, 250 | Light mode backgrounds |

#### Accent Colors
| Name | Hex | RGB | Usage |
|---|---|---|---|
| Orange | `#F97316` | 249, 115, 22 | Orange flavour accent |
| Red | `#EF4444` | 239, 68, 68 | Fruit Punch accent, errors |
| Purple | `#A855F7` | 168, 85, 247 | Rocket Lollipop accent |
| Green | `#22C55E` | 34, 197, 94 | Success, savings badge |

### Typography

#### Font Stack
```css
/* Headings: Bold, condensed, athletic */
font-family: 'Oswald', 'Impact', 'Bebas Neue', ui-sans-serif, system-ui, sans-serif;

/* Body: Clean, readable */
font-family: 'Inter', 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;

/* Mono: Prices, codes */
font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
```

#### Type Scale
| Name | Size | Weight | Line Height | Usage |
|---|---|---|---|---|
| Display | 4rem (64px) | 900 | 0.9 | Hero headline |
| H1 | 3rem (48px) | 800 | 1.0 | Page titles |
| H2 | 2.25rem (36px) | 700 | 1.1 | Section titles |
| H3 | 1.5rem (24px) | 700 | 1.2 | Card titles |
| H4 | 1.125rem (18px) | 600 | 1.3 | Subheadings |
| Body | 1rem (16px) | 400 | 1.5 | Paragraphs |
| Small | 0.875rem (14px) | 400 | 1.5 | Captions |
| XS | 0.75rem (12px) | 500 | 1.4 | Badges, labels |
| XXS | 0.625rem (10px) | 600 | 1.3 | Micro labels |

### Spacing Scale
| Token | Value | Usage |
|---|---|---|
| `space-1` | 0.25rem (4px) | Tight gaps |
| `space-2` | 0.5rem (8px) | Small gaps |
| `space-3` | 0.75rem (12px) | Card padding |
| `space-4` | 1rem (16px) | Standard gaps |
| `space-5` | 1.25rem (20px) | Section gaps |
| `space-6` | 1.5rem (24px) | Card padding large |
| `space-8` | 2rem (32px) | Section padding |
| `space-10` | 2.5rem (40px) | Large sections |
| `space-12` | 3rem (48px) | Hero spacing |
| `space-16` | 4rem (64px) | Major sections |

### Border Radius
| Token | Value | Usage |
|---|---|---|
| `radius-sm` | 0.375rem (6px) | Buttons, inputs |
| `radius-md` | 0.5rem (8px) | Small cards |
| `radius-lg` | 0.75rem (12px) | Cards, modals |
| `radius-xl` | 1rem (16px) | Large cards |
| `radius-2xl` | 1.5rem (24px) | Modals, drawers |
| `radius-full` | 9999px | Pills, badges |

### Shadows
| Token | Value | Usage |
|---|---|---|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.3)` | Subtle elevation |
| `shadow-md` | `0 4px 6px rgba(0,0,0,0.4)` | Cards |
| `shadow-lg` | `0 10px 15px rgba(0,0,0,0.5)` | Modals |
| `shadow-xl` | `0 20px 25px rgba(0,0,0,0.6)` | Drawers |
| `shadow-glow` | `0 0 30px rgba(255,215,0,0.3)` | Yellow glow |
| `shadow-glow-strong` | `0 0 60px rgba(255,215,0,0.5)` | CTA glow |

### Easing Curves (Emil Kowalski)
```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);      /* Primary UI */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);   /* On-screen movement */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);    /* Drawer/panel */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* Bouncy feel */
```

### Duration Scale
| Token | Value | Usage |
|---|---|---|
| `dur-fast` | 150ms | Button press, hover |
| `dur-normal` | 280ms | Standard transitions |
| `dur-slow` | 480ms | Page transitions |
| `dur-slower` | 700ms | Scroll reveals |

---

## Component Specifications

### 1. BUTTONS

#### Primary Button (Yellow)
```
Background: #FFD700
Text: #0A0A0B (bold, uppercase, tracking-wide)
Padding: 12px 32px
Border: none
Border-radius: 12px
Font: 14px, weight 700, uppercase, tracking 0.05em
Hover: translateY(-2px), shadow-glow
Active: scale(0.98)
Transition: all 280ms var(--ease-out)
```

#### Secondary Button (Outline)
```
Background: transparent
Border: 2px solid #FFD700
Text: #FFD700
Padding: 12px 32px
Border-radius: 12px
Font: 14px, weight 700, uppercase, tracking 0.05em
Hover: bg #FFD700, text #0A0A0B
Active: scale(0.98)
```

#### Ghost Button
```
Background: rgba(255,255,255,0.05)
Border: 1px solid rgba(255,255,255,0.1)
Text: white
Padding: 8px 16px
Border-radius: 8px
Hover: bg rgba(255,255,255,0.1)
```

### 2. CARDS

#### Product Card
```
Background: linear-gradient(180deg, #1A1A1C 0%, #0A0A0B 100%)
Border: 1px solid rgba(255,255,255,0.05)
Border-radius: 24px
Padding: 0 (image), 24px (content)
Hover: border-color rgba(255,215,0,0.3), shadow-lg
Image: aspect-square, object-cover, hover scale 1.05
```

#### Glass Card
```
Background: rgba(255,255,255,0.05)
Backdrop-filter: blur(20px)
Border: 1px solid rgba(255,255,255,0.1)
Border-radius: 16px
```

### 3. INPUTS

#### Text Input
```
Background: #1A1A1C
Border: 1px solid #27272A
Border-radius: 12px
Padding: 12px 16px
Text: white, 14px
Placeholder: #A1A1AA
Focus: border-color #FFD700, ring 2px rgba(255,215,0,0.2)
```

### 4. MODALS

#### Quick View Modal
```
Backdrop: rgba(0,0,0,0.8), backdrop-blur(8px)
Container: max-width 640px, border-radius 24px
Background: #0A0A0B
Border: 1px solid rgba(255,255,255,0.1)
Animation: scale-in from 0.95, opacity 0 to 1
Duration: 400ms var(--ease-out)
```

### 5. DRAWERS

#### Cart Drawer
```
Width: 400px (max)
Background: #0A0A0B
Border-left: 1px solid rgba(255,255,255,0.1)
Animation: translateX(100%) to translateX(0)
Duration: 500ms var(--ease-drawer)
```

---

## Interaction Patterns

### Hover States
- **Cards**: translateY(-4px), border-glow, shadow-elevation
- **Buttons**: translateY(-2px), color-shift, shadow-glow
- **Images**: scale(1.05) with overflow hidden
- **Links**: color-shift with underline slide-in

### Scroll Reveals
- **Direction**: Up (default), Left, Right
- **Initial**: opacity 0, translateY(40px), scale(0.95)
- **Final**: opacity 1, translateY(0), scale(1)
- **Duration**: 700ms var(--ease-out)
- **Stagger**: 100ms between items

### Micro-interactions
- **Button press**: scale(0.98) for 150ms
- **Wishlist toggle**: Heart fill animation (scale bounce)
- **Cart badge**: Pop animation on count change
- **Add to cart**: Success checkmark fade-in
- **Quantity change**: Number slide animation

### Loading States
- **Skeleton**: Shimmer animation on placeholder
- **Button**: Spinner icon replaces text
- **Page**: Top progress bar

---

## Responsive Breakpoints

| Name | Width | Columns |
|---|---|---|
| `sm` | 640px | 1-2 |
| `md` | 768px | 2-3 |
| `lg` | 1024px | 3-4 |
| `xl` | 1280px | 4 |
| `2xl` | 1536px | 4-5 |

### Mobile-First Adjustments
- **Hero**: Stack columns (text above image)
- **Product grid**: 1 col → 2 col → 4 col
- **Cart drawer**: Full width on mobile
- **Modals**: Full width with padding
- **Nav**: Hamburger menu below lg breakpoint
