# PURE HEALTH SUPPS — PRIME X Website Brief

## 1. Brand Identity
- **Brand**: PURE HEALTH SUPPS
- **Logo**: Text "PURE" using Anton font with `skewX(-6deg)` italic skew. White by default, yellow `#FFD100` on hover. Used in nav and footer. NO image logo.
- **Primary Color**: `#FFD100` (yellow) — used for CTAs, accents, eyebrows, highlights
- **Secondary**: `#E8BE00` (darker yellow for gradients)
- **Background**: `#000000` (ink) — all section backgrounds are transparent, showing through to body
- **Text**: `#FFFFFF` (paper) — white text on dark background
- **Muted Text**: `rgba(255,255,255,0.62)` for paragraphs, `rgba(255,255,255,0.45)` for subtle text
- **Border/Line**: `rgba(255,255,255,0.12)` for dividers and card borders

## 2. Typography
- **Display/Headings**: `Anton` (Google Font) — uppercase, used for h1-h3, brand, section headings, buttons
- **Body**: `Space Grotesk` (Google Font) — paragraphs, nav links, general text
- **Mono/Accent**: `JetBrains Mono` (Google Font) — eyebrows, labels, prices, small caps, ingredient values
- **Skew**: `-6deg` applied to brand text and accent words via `transform: skewX(-6deg)`

## 3. Background System
- **Body**: `background-color: #000` with `background-image: linear-gradient(rgba(0,0,0,0.82), rgba(0,0,0,0.82)), url('/products/BG3.jpg')` — BG3.jpg is a light textured image, overlaid with 82% dark gradient. Fixed attachment.
- **ALL sections**: Transparent backgrounds — body shows through everywhere
- **NO section has its own solid background color** — except nav (on scroll), footer, marquee, and banner which have dark backgrounds
- **Parallax breaks**: Use `hero-slide.png` as background image with `rgba(0,0,0,0.75)` overlay
- **Hero**: Uses `hero-slide.png` as background with `rgba(0,0,0,0.25-0.40)` gradient overlay (lightened) + mouse-tracking radial gradient at `rgba(255,209,0,0.10)` + solid black scroll-reveal overlay at z-index 5

## 4. Page Structure (Top to Bottom)

### 4.1 Custom Cursor
- Two elements: `.cursor-dot` (8px yellow dot) and `.cursor-ring` (34px yellow border ring)
- Follows mouse with lag effect (ring uses `requestAnimationFrame` with 0.16 lerp)
- Hidden on touch devices (`@media(hover:none)`)
- Uses `mix-blend-mode: difference` on dot

### 4.2 Welcome Popup
- **Trigger**: Appears after 2.5s delay on first visit, stored in `localStorage('pure_popup_dismissed')`
- **Layout**: Full-screen background image (`popup-bg.png` covering viewport)
- **Form panel**: Left side, 420px wide, `backdrop-filter: blur(12px)`, dark gradient background, slides in from left
  - Mobile: Panel slides from bottom with rounded corners
- **Content**: "PURE" text logo (52px, centered, Anton, skewed), "SUBSCRIBE & GET 20% OFF ON BUNDLE" headline, form (Name, Mobile, Email), "SEND DISCOUNT CODE" button
- **No close button, no "No thanks" link** — user MUST fill form to dismiss
- **Escape key blocked**, popstate blocked — cannot be dismissed without submission
- **Body scroll lock** when open
- **API integration**: Calls `/api/send-discount` on submit (Nodemailer SMTP)
- **Success state**: Dark panel with "CODE SENT!" message — no coupon code displayed on screen (code only sent via email)
- **Error handling**: Graceful fallback when SMTP not configured

### 4.3 Navigation
- **Fixed** at top, `z-index: 100`
- **Default**: Transparent background
- **Scrolled** (>40px): `rgba(0,0,0,0.92)` with `backdrop-filter: blur(12px)`, bottom border `var(--line)`
- **Layout**: 3-column flex — left links | center logo | right links + CTA
- **Left links** (desktop only): Products → `/shop`, Stack & Save, Formula, Why PURE, Journal
- **Center**: "PURE" text logo (Anton, skewX, white→yellow hover)
- **Right**: Contact (desktop only) + "Shop PRIME X" yellow CTA button → `/shop`
- **Link hover**: Yellow underline grows from left (`width: 0 → 100%`)
- **Mobile**: Nav links hidden, CTA hidden, hamburger not implemented (links use anchor hrefs)

### 4.4 Hero Section
- **Height**: `100svh` (full viewport)
- **Background**: `hero-slide.png` (product/fruit imagery) with dark gradient overlay
- **Content**: EMPTY — no text, no products, no canvas particles. Just the background image with overlay.
- **Scroll-reveal overlay**: Solid black `div` at `z-index: 5` that covers the hero. Fades from `opacity: 1` to `opacity: 0` as user scrolls through 65% of viewport height. Once revealed, stays visible even on scroll-up (`heroRevealed` flag prevents re-hiding).
- **Overlay**: Multi-layer:
  1. `radial-gradient` tracking mouse position (`--mx`, `--my` CSS vars) with `rgba(255,209,0,0.10)` yellow glow
  2. `linear-gradient` from `rgba(0,0,0,0.25)` top to `rgba(0,0,0,0.40)` bottom (lightened from original 0.72-0.82)
- **Grid overlay**: `.hero-grid` — CSS grid lines (`64px` spacing, `rgba(255,255,255,0.045)`) with radial mask, parallax scrolls at 0.15x speed
- **Canvas particles**: Yellow dots (`#FFD100`) floating upward, count based on viewport area, `globalAlpha` variation

### 4.5 Marquee
- **Background**: `var(--ink)` (black)
- **Text**: `var(--yellow)` — "FOCUS ● PUMP ● ENERGY" repeating
- **Font**: Anton, 26px, uppercase
- **Animation**: `translateX(0)` to `translateX(-50%)` over 26s linear infinite
- **Borders**: Top and bottom `1px solid rgba(255,209,0,0.2)`

### 4.6 Parallax Break 1 — "Explosive Energy"
- **Full-bleed** (`width: 100vw`, centered via negative margin)
- **Background**: `hero-slide.png` with JS parallax (translateY based on scroll, `scale(1.15)`)
- **Overlay**: `rgba(0,0,0,0.75)`
- **Content**: "Explosive **Energy**" heading (yellow accent word), subtext about concentration/strength/focus
- **Reveal**: `reveal-on-scroll="fade"`

### 4.7 Products Section
- **Section padding**: `120px 0`
- **Heading**: "The Range" eyebrow + "Only three flavours. Zero filler formulas." + description
- **Grid**: 3 columns (`repeat(3,1fr)`, `gap: 28px`), responsive to 1 column on mobile
- **Product Cards** (`.p-card`):
  - Border: `1px solid var(--line)`, transparent background
  - Hover: `translateY(-8px)`, border becomes `rgba(255,209,0,0.5)`
  - **Flavor tag**: Mono font, 11px, yellow, uppercase
  - **Image**: `tub-orange.png` / `tub-fruit-punch.png` / `tub-rocket.png` (transparent PNGs)
    - Container: `280px` height, flex centered
    - Image: `objectFit: contain`, `maxHeight: 280px`, `drop-shadow(0 8px 30px rgba(0,0,0,0.5))`
    - **3D rotation animation**: `tubSpinCard` — oscillates `rotateY(-10deg)` to `rotateY(10deg)` over 6s
    - On hover: Animation pauses, `scale(1.05)` with glow shadow
  - **Title**: "Prime X - {Flavour}" — Anton font, 28px, yellow → white on hover, underline grows from left
  - **Description**: 14px, `rgba(255,255,255,0.6)`, `line-height: 1.6`
  - **Meta row**: "80 SERVINGS · 280G" (mono, muted) + "View Details" ghost button
  - **Click entire card** → navigates to `/product/{slug}` (PDP page)
  - **Tilt effect**: On mousemove, `perspective(900px) rotateY/rotateX` up to 8deg, `translateZ(6px)` for 3D feel

### 4.8 Bestseller Strip
- **Transparent** background with yellow top/bottom borders (`rgba(255,209,0,0.15)`)
- **Layout**: Horizontal flex with "Best Sellers" label + scrollable chips
- **Chips**: Dark graphite background, border, contain: "01 PRIME X Fruit Punch — Flagship", etc.
- **No scroll JS** — pure CSS `overflow-x: auto`, hidden scrollbar

### 4.9 Category Cards
- **Grid**: 3 columns, `gap: 20px`
- **Card** (`.category-card`):
  - `aspect-ratio: 3/4`, overflow hidden, border `var(--line)`, background `var(--graphite-2)`
  - **Image**: Next.js `<Image fill>` with `objectFit: cover` (fills entire card), wrapped in `.category-card-img-wrap`
  - **Hover**: Image wrapper scales 1.05x
  - **Overlay**: Gradient from transparent top to `rgba(0,0,0,0.8)` bottom, darkens on hover
  - **Content** (hidden by default, shows on hover):
    - `.card-eyebrow`: Mono, 10px, yellow (fades in with delay)
    - `.card-title`: Anton, 22-32px, white
    - `.card-desc`: 13px, `rgba(255,255,255,0.7)` (fades in with delay)
  - **Arrow**: Top-right, circle with blur, slides in on hover
  - **Click card** → navigates to `/product/{slug}` (PDP page)
  - **Mobile**: 1 column, `aspect-ratio: 16/9`

### 4.10 Image + Text Split — Formula
- **Layout**: 2-column grid (`1fr 1fr`), 500px min-height
- **Left**: Product tub image (`tub-orange.png`) with `objectFit: contain`, padding 40px, subtle yellow radial glow background
- **Right**: "The Formula" eyebrow + "Every milligram, on the **label**." + description + "See the Science" yellow CTA → `#science`
- **Reveal**: `reveal-on-scroll="fade"`
- **Hover on image**: `scale(1.03)` transition
- **Mobile**: Stacks to single column

### 4.11 Science / Ingredients Section
- **Padding**: `100px 0`
- **Heading**: "Power Performance Nutrients Blend" eyebrow (yellow) + "Every milligram, on the label." + description
- **Grid**: 4 columns (`repeat(4,1fr)`, `gap: 16px`), responsive to 2 col → 1 col
- **Ingredient Cards** (`.sci-cell`):
  - **Front state** (`.sci-cell-front`):
    - `linear-gradient(145deg, #1a1a1a, #111)` background
    - `border: 1px solid rgba(255,209,0,0.12)`
    - 3D embossed effect: `box-shadow: 0 6px 0 0 #0a0a0a, 0 8px 20px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05)`
    - Value: Mono font, 38px, white
    - Unit: Mono, 16px, yellow
    - Name: 11px, uppercase, `rgba(255,255,255,0.45)`
  - **Hover state** (`.sci-cell-hover`):
    - Absolute positioned, covers entire card
    - `linear-gradient(145deg, #FFD100, #E8BE00)` yellow background
    - Name: Anton, 18px, black
    - Dose: Mono, 13px, `rgba(0,0,0,0.5)`
    - Description: 13px, `rgba(0,0,0,0.78)`, `line-height: 1.6`
    - **Transition**: 0.45s cubic-bezier, front fades out + scales down, hover fades in + scales up
  - **8 Ingredients with descriptions**:
    1. Beta-Alanine (1.5g) — Buffers lactic acid, delays fatigue
    2. Arginine HCl (750mg) — Boosts nitric oxide, blood flow
    3. L-Citrulline (500mg) — Converts to arginine, reduces soreness
    4. L-Carnitine (250mg) — Transports fatty acids for energy
    5. L-Tyrosine (125mg) — Precursor to dopamine, mental clarity
    6. Encapsulated Caffeine (50mg) — Sustained-release, no crash
    7. Coffee Bean Extract (45mg) — Natural caffeine + antioxidants
    8. Garcinia Cambogia (37.5mg) — Supports fat metabolism
  - **Stagger**: Each card delays 0.06s more than previous

### 4.12 Parallax Break 2 — "Built Different"
- Same structure as Parallax Break 1
- Floating product image: `Fruit Punch.png` (200x220px) with drop-shadow
- Content: "Built **Different**" + FSSAI/banned-substance text
- Product floats up/down with slight rotation (`parallaxProductFloat` keyframe)

### 4.13 Why PURE Section
- **Padding**: `100px 0`
- **Header**: "Why PURE" eyebrow + "Built different, by design."
- **3 rows** alternating layout (text left/image right, then reversed):
  1. **01 — Full Transparency**: Text about label transparency + `tub-orange.png`
  2. **02 — Science-Backed Dosing**: Clinical doses + `tub-fruit-punch.png`
  3. **03 — Clean Formula**: Banned-substance free + `tub-rocket.png`
- **Row layout**: 2-column grid (`1fr 1fr`, `gap: 80px`), borders between rows
- **Number**: Anton, 72px, yellow, 80% opacity
- **Heading**: Anton, 28-40px, uppercase
- **Description**: 16px, `rgba(255,255,255,0.65)`, max-width 480px
- **Image**: `objectFit: contain`, `max-width: 320px`, `drop-shadow(0 20px 60px rgba(0,0,0,0.7))`
- **Hover on row**: Image `scale(1.05) rotate(-3deg)`
- **Reveal**: Rows alternate `reveal-on-scroll="left"` and `"right"`
- **Trust Panel** at bottom:
  - Dark graphite background, border
  - "Trust, Verified." heading
  - 7 rows of key-value pairs (FSSAI Licence, Banned Substance, Sucralose, Shelf Life, Serving Size, Manufactured, Allergen)
  - Keys: muted text. Values: mono, yellow, bold
  - Tilt effect on hover

### 4.14 Image + Text Split — Trust (Reverse)
- Same as Formula split but reversed layout (image right, text left via `direction: rtl`)
- Image: `tub-rocket.png`
- Content: "Trust, Verified" + FSSAI/banned-substance text + "Why PURE" CTA → `#why`

### 4.15 Bundle Section
- **Transparent** background with yellow top/bottom borders
- **Grid**: 2 columns (`1fr 1fr`, `gap: 48px`)
- **Left — Visual**:
  - 3 product images (Orange, Fruit Punch, Rocket Lollipop) overlapping
  - Staggered rotations: left `-8deg translateX(20px)`, center `scale(1.08)`, right `8deg translateX(-20px)`
  - On hover: Rotations intensify, center scales more
- **Right — Copy**:
  - "Stack & Save" eyebrow
  - "All three flavours. One tray." heading
  - Description about Trainer's Tray
  - Price: ₹3,299 (yellow, 44px) / ₹3,897 (strikethrough, muted)
  - "Order Bundle" yellow CTA → `https://www.puresupps.site`

### 4.16 Parallax Break 3 — "Never Finished"
- Same structure as other parallax breaks
- Floating product: `Rocket Lolli pop.png` (180x200px)
- Content: "Never **Finished**" + focus/crash text

### 4.17 Athlete Banner
- **Background**: Dark gradient with yellow radial glow on right side
- **Content**: "For the working athlete" eyebrow + "You clock in at the office. You clock in at the gym too." + description about working athletes + "Get PRIME X" yellow CTA
- **Max-width**: 620px, left-aligned
- **Reveal**: Staggered — eyebrow fade, heading up, paragraph up, CTA up

### 4.18 Journal Section
- **Transparent** background
- **Grid**: 2 columns (`1.1fr 0.9fr`, `gap: 60px`)
- **Left**: "The PURE Performance Journal" eyebrow (on-light) + "Why we only ship three SKUs." + 2 paragraphs about transparent dosing + "Read the Full Story" ghost button → `/blog`
- **Right**: 3 stacked cards:
  - Dark background, yellow left border (3px)
  - Each: Bold heading (Anton, 15px) + description (13px, muted)
  - Topics: Transparent Dosing, FSSAI Licensed, Banned Substance Free
  - Tilt effect on hover

### 4.19 Testimonials Section
- **Transparent** background
- **Heading**: "Real Training, Real Feedback" eyebrow (yellow) + "What the floor is saying." + "Early feedback..." subtext
- **Grid**: 3 columns, `gap: 24px`
- **Card** (`.t-card`): Dark background, padding 30px
  - Stars: Mono, yellow, letter-spacing 2px
  - Quote: 15px, `rgba(255,255,255,0.82)`, `line-height: 1.65`
  - Author: Avatar (yellow square, first letter) + Name (bold) + Role (mono, 12px, muted)
- **Stagger**: 0.1s between cards

### 4.20 Instagram Section
- **Transparent** background
- **Header**: "@puresupps.site" eyebrow + "Follow the training." + "Follow on Instagram" ghost button → `https://instagram.com/puresupps.site`
- **Grid**: 5 columns, `gap: 6px`
- **Cell**: Square aspect-ratio, dark background, product image (`objectFit: contain`, padding 12px), border
- **Hover**: Dark overlay + Instagram icon fades in
- **5 items**: tub-orange, tub-fruit-punch, tub-rocket, Orange.png, Fruit Punch.png
- **Stagger**: 0.08s between cells

### 4.21 Newsletter Section
- **Transparent** background
- **Layout**: Flex between heading and form
- **Heading**: "Get early access to new flavours & drops." (Anton, 28-42px)
- **Form**: Email input (border: `var(--ink)`, transparent bg) + "Notify Me" button (dark bg, yellow text → yellow bg, dark text on hover)
- **Note**: Form `alert()` on submit — no actual backend

### 4.22 Footer
- **Background**: `var(--ink)` (solid black)
- **Border-top**: `1px solid var(--line)`
- **Grid**: 4 columns (`1.4fr 1fr 1fr 1fr`)
- **Column 1 — Brand**: "PURE" text (28px) + description (14px, muted)
- **Column 2 — Shop**: PRIME X Orange, Rocket Lollipop, Fruit Punch, Trainer's Tray Bundle
- **Column 3 — Company**: Why PURE, The Formula, Journal, Reviews
- **Column 4 — Contact**: puresupps.site, email, phone, Instagram
- **Bottom bar**: Copyright + FSSAI licence + "IG" social link
- **Link hover**: Yellow

## 5. JavaScript Effects (page.tsx useEffect)

### 5.1 Nav Scroll
- Adds `.scrolled` class to `#siteNav` when `scrollY > 40`

### 5.2 Hero Grid Parallax
- `.hero-grid` translates Y at `scrollY * 0.15` speed

### 5.3 Hero Mouse Tracking
- Updates `--mx` and `--my` CSS custom properties on hero element based on mouse position
- Used by `::before` radial gradient for interactive yellow glow

### 5.4 Canvas Particles
- Yellow dots (`#FFD100`) floating upward in hero
- Count: `Math.round((width * height) / 24000)`, minimum 20
- Each particle: random position, radius 0.5-2.3px, velocity upward + slight horizontal drift, alpha 0.12-0.57
- Resets to bottom when reaching top

### 5.5 Scroll Reveal System
- **Two observers**:
  1. `[reveal-on-scroll]` — individual elements, threshold 0.1, rootMargin `-50px` bottom
  2. `[data-reveal-items]` — container, threshold 0.05, rootMargin `-60px` bottom
- Adds `.is-revealed` class on intersection, then disconnects
- **Reveal types** (via attribute value):
  - `"up"` — translateY(24px) → 0
  - `"fade"` — opacity 0 → 1
  - `"scale"` — scale(0.96) → 1
  - `"left"` — translateX(-24px) → 0
  - `"right"` — translateX(24px) → 0
- **Stagger**: `data-delay` attribute on children, each adds 0.05-0.08s transition-delay

### 5.6 Parallax Break Scroll
- `.parallax-bg-js` elements translate Y based on viewport intersection progress
- Formula: `(progress - 0.5) * 80` pixels offset, with `scale(1.15)` base

### 5.7 Tilt Effect
- Applied to `.tilt` elements (product cards, trust panel, journal cards)
- On mousemove: `perspective(900px) rotateY(dx * 8deg) rotateX(-dy * 8deg) translateZ(6px)`
- On mouseleave: Resets transform

### 5.8 Custom Cursor
- `.cursor-dot` follows mouse instantly
- `.cursor-ring` follows with lerp (0.16 factor) via `requestAnimationFrame`
- Both use `translate(-50%, -50%)` centering
- Cleanup: Removes all event listeners and cancels animation frame

### 5.9 Hero Scroll Reveal
- `.hero-reveal` overlay at `z-index: 5` covers hero initially at full opacity
- On scroll: opacity fades from 1 → 0 over 65% of viewport height
- `heroRevealed` flag: Once overlay reaches 0 opacity, it stays hidden even on scroll-up
- Prevents the "jarring reveal" effect — smooth transition from black to hero image

## 6. Component Architecture

### 6.1 Files
- `src/app/page.tsx` — Homepage (~700 lines), 'use client', single component
- `src/app/globals.css` — All styles (~1750+ lines)
- `src/app/layout.tsx` — Root layout with Google Fonts `<link>` tags
- `src/app/product/[slug]/page.tsx` — Product Detail Page (Ghost Lifestyle-inspired), dynamic route
- `src/app/api/send-discount/route.ts` — Nodemailer SMTP API endpoint
- `src/components/WelcomePopup.tsx` — Dynamic import (SSR disabled), full-screen popup with API integration
- `src/components/AnnouncementBar.tsx` — Contains `PARTNER_URL` export
- `src/types/custom-elements.d.ts` — JSX declarations for `split-lines` and `reveal-items` custom elements
- `src/lib/store.ts` — Product data (products array with variants, nutrition, images)

### 6.2 Product Data (INGREDIENTS array)
```typescript
const INGREDIENTS = [
  { value: '1.5', unit: 'g', name: 'Beta-Alanine', desc: '...' },
  { value: '750', unit: 'mg', name: 'Arginine HCl', desc: '...' },
  { value: '500', unit: 'mg', name: 'L-Citrulline', desc: '...' },
  { value: '250', unit: 'mg', name: 'L-Carnitine', desc: '...' },
  { value: '125', unit: 'mg', name: 'L-Tyrosine', desc: '...' },
  { value: '50', unit: 'mg', name: 'Encapsulated Caffeine', desc: '...' },
  { value: '45', unit: 'mg', name: 'Coffee Bean Extract', desc: '...' },
  { value: '37.5', unit: 'mg', name: 'Garcinia Cambogia', desc: '...' },
];
```

### 6.3 Product Data (PRODUCTS array)
```typescript
const PRODUCTS = [
  { flavor: 'orange', label: 'Flavour 01 — Orange', name: 'Orange', img: '/products/Orange.png', tubImg: '/products/tub-orange.png', desc: '...', delay: '1' },
  { flavor: 'rocket', label: 'Flavour 02 — Rocket Lollipop', name: 'Rocket Lollipop', img: '/products/Rocket Lolli pop.png', tubImg: '/products/tub-rocket.png', desc: '...', delay: '2' },
  { flavor: 'fruit', label: 'Flavour 03 — Fruit Punch', name: 'Fruit Punch', img: '/products/Fruit Punch.png', tubImg: '/products/tub-fruit-punch.png', desc: '...', delay: '3' },
];
```

## 7. Assets (public/products/)
- `BG3.jpg` — Body background texture (light/warm, overlaid with 82% dark)
- `hero-slide.png` — Hero + parallax breaks background (product/fruit imagery)
- `product-3flavours.png` — Combined 3-tub image for popup
- `Orange.png` — Yellow-bg product image (used in category cards, bundle)
- `Fruit Punch.png` — Yellow-bg product image
- `Rocket Lolli pop.png` — Yellow-bg product image
- `tub-orange.png` — Transparent-bg tub image (used in products, why section)
- `tub-fruit-punch.png` — Transparent-bg tub image
- `tub-rocket.png` — Transparent-bg tub image

## 8. External Links
- `https://www.puresupps.site` — All "Order Now" / "Order Bundle" / "Get PRIME X" CTAs
- `https://instagram.com/puresupps.site` — Instagram link in footer + header
- `mailto:puresupps.site@gmail.com` — Footer email
- `tel:+919557513017` — Footer phone

## 9. Product Detail Pages (PDP)
- **Route**: `/product/[slug]` — Dynamic route, slug maps to product data in `src/lib/store.ts`
- **Design**: Ghost Lifestyle-inspired dark theme layout
- **Layout**: 2-column grid — left 45% image gallery, right 55% product details
- **Image Gallery**:
  - Large main image with thumbnails below
  - Thumbnails: yellow-bg product images (Orange.png, Fruit Punch.png, Rocket Lolli pop.png)
  - Click thumbnail to swap main image
- **Product Details** (right column):
  - Breadcrumb: HOME / SHOP / {Product Name}
  - Flavor name (Anton, uppercase)
  - Product title ("PRIME X {Flavour} — Pre-Workout")
  - Star rating (★★★★★)
  - Price display (₹699 MRP)
  - Flavor variant selector (pill buttons)
  - Format selector (Capsules / Powder tabs)
  - Quantity selector (− / count / +)
  - "ADD TO CART" yellow CTA
  - "BUY NOW ON PURE SUPPS" ghost button → puresupps.site
  - Trust badges (FSSAI Certified, Banned Substance Free, Lab Tested)
- **Accordion Sections**:
  - Suggested Use — usage instructions
  - Supplement Facts — full ingredient table (1.5g Beta-Alanine, 750mg Arginine HCl, etc.)
  - FAQ — expandable questions (How to take, Safety, Servings, Stacking, Taste)
- **Cross-sell**: "Try Another Flavour" section showing other products as clickable cards
- **State**: `openAccordion` supports 'suggested' | 'ingredients' | 'faq' | null

## 10. API Routes

### 10.1 /api/send-discount
- **Method**: POST
- **Purpose**: Send discount code email via Nodemailer
- **Request body**: `{ name, email, phone }`
- **Response**: `{ ok: true }` on success, `{ ok: false, error: '...' }` on failure
- **SMTP config**: Reads from env vars (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`)
- **Graceful fallback**: Returns `{ ok: true }` even when SMTP not configured (logs warning)
- **Email template**: Branded HTML email with PURE branding, sends `PRIME-X` code
- **Dependencies**: `nodemailer` + `@types/nodemailer`

## 11. Assets (public/products/)
- `BG3.jpg` — Body background texture (light/warm, overlaid with 82% dark)
- `hero-slide.png` — Hero + parallax breaks background (product/fruit imagery)
- `popup-bg.png` — Full-screen popup background image
- `product-3flavours.png` — Combined 3-tub image (used in old popup, may be unused now)
- `Orange.png` — Yellow-bg product image (used in category cards, bundle, PDP gallery)
- `Fruit Punch.png` — Yellow-bg product image
- `Rocket Lolli pop.png` — Yellow-bg product image
- `tub-orange.png` — Transparent-bg tub image (used in products, why section)
- `tub-fruit-punch.png` — Transparent-bg tub image
- `tub-rocket.png` — Transparent-bg tub image

## 12. Known Production Blockers
1. No admin authentication (admin page at `/admin` is wide open)
2. Razorpay integration uses hardcoded `rzp_test_demo` key
3. No `/privacy` or `/terms` pages (linked nowhere, but standard requirement)
4. Contact form and newsletter form do nothing (just `alert()`)
5. `images.unoptimized: true` in next.config.mjs
6. Shop page has products at `opacity: 0` with no scroll observer
7. No git history — project is gitignored
8. SMTP not configured — email sending skipped until env vars set in `.env.local`

## 13. Design Principles (Jacked Factory Inspired)
- Numbered sections (01, 02, 03) for "Why PURE" rows
- Scroll-triggered animations (reveal-on-scroll system)
- Parallax breaks between content sections
- Category cards with hover-reveal text overlay
- Product-focused hero with transparent tub images
- Trust signals prominently displayed (FSSAI, banned-substance free)
- Consistent yellow accent on dark background
- Typography hierarchy: Anton (display) > Space Grotesk (body) > JetBrains Mono (data)
- Clip-path buttons with angled bottom-right corner
- 3D tilt effects on interactive elements
