# NEED Supplements Website Clone - Complete Documentation

## Overview

This document details the complete process of cloning the NEED Supplements website (https://needsupps.site/) into a Next.js + Tailwind CSS application.

**Original Website:** https://needsupps.site/
**Tech Stack:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, shadcn/ui
**Deployed URL:** https://ai-fitness-platform-1kpr.onrender.com/

---

## 1. Website Technology Analysis

### 1.1 Platform & Framework

| Technology | Details |
|------------|---------|
| **E-commerce Platform** | Shopify (Shop ID: 1224048747) |
| **Theme** | Symmetry v7.3.0 (theme_store_id: 568) |
| **Theme Name** | Last_Version_Symmetry |
| **Shop Domain** | needsupps-site.myshopify.com |
| **Currency** | EUR (€) |
| **Locale** | English (en) |
| **Country** | Spain (ES) |

### 1.2 Third-Party Apps & Integrations

| App/Service | Purpose | CDN/Script |
|-------------|---------|------------|
| **Google Tag Manager** | Analytics tracking (GTM-5SGH89DT) | googletagmanager.com |
| **Shopify Payments** | Payment processing | shop.app |
| **Apple Pay** | Express checkout | Apple Pay JS |
| **PayPal** | Payment option | PayPal V4 |
| **Yotpo** | Product reviews widget | staticw2.yotpo.com |
| **Judge.me** | Reviews (alternative) | cdn.judge.me |
| **LeadDyno** | Affiliate tracking | collector.leaddyno.com |
| **Privy** | Popups/marketing | shopify.privy.com |
| **Booster EU Cookie** | Cookie consent | cdn.shopify.com |
| **Instafeed** | Instagram feed | cdn.nfcube.com |
| **Cart Bot** | Cart recovery | cart-bot.net |
| **Super Rewards** | Loyalty/referral | s3.amazonaws.com |
| **Weglot** | Multi-language | dashboard.weglot.com |
| **Locksmith** | Security/access control | Built-in Shopify |

### 1.3 Fonts

| Font | Weights | Usage |
|------|---------|-------|
| **Roboto** | 400, 500, 600, 700 (normal & italic) | Body text, navigation |
| **Oswald** | 400 | Headings, logo, navigation |

**Font URLs (CDN):**
- Roboto: `//needsupps.site/cdn/fonts/roboto/roboto_n4.2019d890f07b1852f56ce63ba45b2db45d852cba.woff2`
- Oswald: `//needsupps.site/cdn/fonts/oswald/oswald_n4.7760ed7a63e536050f64bb0607ff70ce07a480bd.woff2`

### 1.4 CSS Architecture

**CSS Files Loaded:**
- `main.css?v=155629054497702245621725442324` - Theme main styles
- `animate-on-scroll.css?v=116824741000487223811725442323` - Animation styles

**CSS Custom Properties (CSS Variables):**
```css
--page-container-width: 1100px
--reading-container-width: 720px
--gutter-large: 30px
--gutter-desktop: 20px
--gutter-mobile: 16px
--section-padding: 50px
--base-font-family: Roboto, sans-serif
--heading-font-family: Oswald, sans-serif
--base-text-size: 14px
--body-bg-color: 255 255 255
--header-bg-col: #1d1d1d
--main-nav-link-hover-col: #ffd100
--btn-bg-color: 255 209 0
```

---

## 3. Page Structure Analysis

### 3.1 All Discovered URLs

#### Collections (Product Categories)
1. `/collections/best-sellers` - Best Sellers
2. `/collections/proteins` - Proteins
3. `/collections/pre-training` - Pre-Training
4. `/collections/muscle-builder` - Build Muscle
5. `/collections/amino-acids` - Amino Acids
6. `/collections/vitality-and-health` - Vitamins & Minerals
7. `/collections/weight-loss` - Weight Loss
8. `/collections/need%C2%AE-packs` - NEED® Packs

#### Product Pages
- `/collections/[category]/products/[product-handle]`
- Examples: `/collections/best-sellers/products/need-pure-whey`

#### Blog/Content Pages
- `/blogs/the-health-project` - The Health Project (blog)

#### Static Pages
- `/pages/about-us` - About Us
- `/pages/contact-us` - Contact Us

#### Policy Pages
- `/policies/privacy-policy` - Privacy Policy
- `/policies/legal-notice` - Legal Notice
- `/policies/shipping-policy` - Shipping Policy
- `/policies/refund-policy` - Refund Policy
- `/policies/terms-of-service` - Terms of Service

#### System Pages
- `/cart` - Shopping Cart
- `/search` - Search (predictive search enabled)
- `/account/login` - Customer Login
- `/checkout` - Checkout (Shopify hosted)

### 2.2 Homepage Structure (/)

```
┌─────────────────────────────────────────────────────────────┐
│ TOP BAR (Yellow #ffcc00)                                   │
│ [Social Icons] [Scrolling Text] [Country/Language Selector] │
├─────────────────────────────────────────────────────────────┤
│ HEADER (Dark #1d1d1d)                                      │
│ [Mobile Menu] [Logo] [Nav Links] [Search] [Account] [Cart] │
├─────────────────────────────────────────────────────────────┤
│ MOBILE NAV (Dark #1d1d1d, horizontal scroll)               │
│ [Proteins] [Pre-Training] [Build Muscle] [Amino Acids] etc. │
├─────────────────────────────────────────────────────────────┤
│ HERO SLIDER                                                 │
│ [Full-width image with overlay text]                       │
├─────────────────────────────────────────────────────────────┤
│ BEST SELLERS CAROUSEL                                       │
│ [Section Title] [4-column carousel] [Navigation arrows]     │
│ Products: NEED PURE WHEY, DIURE6, PURE ISO, 0CARBS         │
├─────────────────────────────────────────────────────────────┤
│ CATEGORIES GRID (6 columns)                                │
│ [Proteins] [Pre-Training] [Amino Acids] [Vitamins] [Weight │
│  Loss] [Build Muscle]                                      │
├─────────────────────────────────────────────────────────────┤
│ BUILD MUSCLE CAROUSEL                                      │
│ [Section Title] [View All Link] [7-column carousel]        │
│ Products: PURE WHEY, POWER CREATINE, BCAAS, MASS GAINER... │
├─────────────────────────────────────────────────────────────┤
│ PACKS BANNER                                               │
│ [Full-width banner image linking to NEED® Packs]           │
├─────────────────────────────────────────────────────────────┤
│ FOOTER (Dark #1d1d1d)                                      │
│ [Shop Links] [Company Links] [Legal Links] [Newsletter]    │
│ [Social Icons] [Payment Icons] [Country/Language]          │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Collection Page Structure (/collections/[category])

```
┌─────────────────────────────────────────────────────────────┐
│ TOP BAR (Yellow #ffcc00) - Same as homepage                │
├─────────────────────────────────────────────────────────────┤
│ HEADER (Dark #1d1d1d) - Same as homepage                   │
├─────────────────────────────────────────────────────────────┤
│ BREADCRUMB                                                 │
│ Home > [Category Name]                                      │
├─────────────────────────────────────────────────────────────┤
│ HERO                                                       │
│ [Dark background #1d1d1d with category name in uppercase]  │
├─────────────────────────────────────────────────────────────┤
│ MAIN CONTENT                                               │
│ ┌──────────────────┬────────────────────────────────────┐   │
│ │ FILTER SIDEBAR   │ PRODUCT GRID                       │   │
│ │ (220px width)    │ (3-4 columns)                      │   │
│ │                  │                                    │   │
│ │ [Availability]   │ [Product Card]                     │   │
│ │  ☑ In stock      │  - Image (3/4 aspect)              │   │
│ │                  │  - Sale badge                      │   │
│ │ [Price Range]    │  - Sold out overlay               │   │
│ │  ○ All prices    │  - Title                          │   │
│ │  ○ Under €25     │  - Reviews stars                  │   │
│ │  ○ €25 - €50     │  - Price                          │   │
│ │  ○ Over €50      │                                    │   │
│ │                  │ [Product Card] x N                 │   │
│ │ [Sort Dropdown]  │                                    │   │
│ └──────────────────┴────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│ FOOTER (Dark #1d1d1d) - Same as homepage                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.4 Product Detail Page Structure (/products/[id])

```
┌─────────────────────────────────────────────────────────────┐
│ TOP BAR, HEADER, BREADCRUMB - Same as collection page       │
├─────────────────────────────────────────────────────────────┤
│ PRODUCT CONTENT                                            │
│ ┌─────────────────────────┬─────────────────────────────┐   │
│ │ PRODUCT IMAGES          │ PRODUCT INFO                │   │
│ │                         │                             │   │
│ │ [Main Image]            │ [Title]                     │   │
│ │ [Thumbnail Gallery]     │ [Price / Sale Price]        │   │
│ │                         │ [Reviews & Ratings]          │   │
│ │                         │ [Variant Selector]          │   │
│ │                         │ [Quantity]                  │   │
│ │                         │ [Add to Cart Button]         │   │
│ │                         │ [Stock Status]              │   │
│ │                         │ [Description Tabs]           │   │
│ └─────────────────────────┴─────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│ RELATED PRODUCTS / RECOMMENDATIONS                          │
│ [Horizontal carousel of related products]                  │
├─────────────────────────────────────────────────────────────┤
│ REVIEWS SECTION (Yotpo/Judge.me)                           │
│ [Customer reviews, ratings, photos]                         │
├─────────────────────────────────────────────────────────────┤
│ FOOTER                                                     │
└─────────────────────────────────────────────────────────────┘
```

### 2.5 Cart Page Structure (/cart)

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER                                                     │
├─────────────────────────────────────────────────────────────┤
│ CART CONTENT                                               │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ CART ITEMS                                             │  │
│ │ ┌─────────┬────────────┬──────────┬────────────────┐  │  │
│ │ │ Image   │ Product    │ Quantity │ Price          │  │  │
│ │ │         │ Name       │ +/-      │                │  │  │
│ │ │         │ Variant    │ [Remove] │                │  │  │
│ │ └─────────┴────────────┴──────────┴────────────────┘  │  │
│ └───────────────────────────────────────────────────────┘  │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ CART SUMMARY                                           │  │
│ │   Subtotal: €XX.XX                                     │  │
│ │   Shipping: Calculated at checkout                    │  │
│ │   [Checkout Button]                                   │  │
│ └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ FOOTER                                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Section-by-Section Detailed Analysis

### 4.1 Announcement Bar (Top Bar)

**CSS:** Background `#ffcc00`, Text `black`, Font size `11px`

**Elements:**
- Social media icons (Facebook, YouTube, Instagram) - left side
- Scrolling announcement text - center
- Country/Language selector - right side

**Layout:** Flexbox, max-width `1100px`, centered

### 4.2 Header

**CSS:** Background `#1d1d1d`, Padding `10px 20px`

**Layout:**
```
[Mobile Menu Button] [Logo (centered)] [Search] [Account] [Cart]
```

**Navigation Links (Desktop):**
- PROTEINS → /collections/proteins
- PRE-TRAINING → /collections/pre-training
- BUILD MUSCLE → /collections/muscle-builder
- AMINO ACIDS → /collections/amino-acids
- VITAMINS & MINERALS → /collections/vitality-and-health
- WEIGHT LOSS → /collections/weight-loss

**Mobile Navigation:** Horizontal scrollable list

### 4.3 Hero Section

- Full-width container
- Image dimensions: 1920x550px max
- Overlay text capability

### 4.4 Best Sellers Carousel

**Layout:** 4 products visible on desktop
**Navigation:** Left/right arrow buttons
**Product Card:**
- Image: 3/4 aspect ratio
- Badge: Sale percentage (yellow background)
- Overlay: "Sold out" when applicable
- Title: Oswald font, medium weight
- Rating: 5-star display with review count
- Price: Current price + original price (if on sale)

### 4.5 Categories Grid

**Layout:** 6 columns on desktop, 3 on tablet, 2 on mobile

**Categories:**
1. Proteins - `/collections/proteins`
2. Pre-training - `/collections/pre-training`
3. Amino acids - `/collections/amino-acids`
4. Vitamins & Minerals - `/collections/vitality-and-health`
5. Weight loss - `/collections/weight-loss`
6. Build Muscle - `/collections/muscle-builder`

**Card Style:** Square aspect ratio, image cover, dark overlay with white text

### 4.6 Footer

**Background:** `#1d1d1d`
**Columns:** 4 columns (Shop, Company, Legal, Newsletter)

**Shop Links:** All collections
**Company Links:** The Health Project, About us, Contact us
**Legal Links:** Privacy Policy, Legal Notice, Shipping Policy, Refund Policy, Terms of Service, Cookies

**Newsletter:** Email input + Subscribe button
**Payment Icons:** American Express, Apple Pay, Google Pay, Maestro, Mastercard, PayPal, Visa
**Bottom:** Copyright + Country/Language selectors

---

## 5. Component Analysis: Grids, Carousels, Galleries

### 5.1 GRID SYSTEMS

#### Product Grid (Collection Pages)
```
┌─────────────────────────────────────────────────────────────┐
│ GRID CONTAINER                                              │
│ display: grid                                                │
│ grid-template-columns: repeat(4, 1fr) // desktop             │
│ grid-template-columns: repeat(3, 1fr) // tablet              │
│ grid-template-columns: repeat(2, 1fr) // mobile              │
│ gap: 20px                                                    │
└─────────────────────────────────────────────────────────────┘
```
**Classes:** `.product-grid`, `.grid`, `.grid__inner`
**Breakpoints:**
- Mobile: 2 columns (< 768px)
- Tablet: 3 columns (768px - 1024px)
- Desktop: 4 columns (> 1024px)

#### Category Grid (Homepage)
```
┌─────────────────────────────────────────────────────────────┐
│ CATEGORY GRID                                              │
│ display: grid                                                │
│ grid-template-columns: repeat(6, 1fr) // desktop            │
│ grid-template-columns: repeat(3, 1fr) // tablet             │
│ grid-template-columns: repeat(2, 1fr) // mobile             │
│ aspect-ratio: 1 / 1 (square cards)                          │
└─────────────────────────────────────────────────────────────┘
```
**Classes:** `.custom-grid`, `.collection-grid`
**Categories:** 6 cards (Proteins, Pre-Training, Amino Acids, Vitamins, Weight Loss, Build Muscle)

#### Footer Grid
```
┌─────────────────────────────────────────────────────────────┐
│ FOOTER GRID (4 columns)                                     │
│ ┌─────────┬─────────┬─────────┬─────────┐                  │
│ │  SHOP   │ COMPANY │  LEGAL  │NEWSLETTER│                 │
│ └─────────┴─────────┴─────────┴─────────┘                  │
└─────────────────────────────────────────────────────────────┘
```
**Classes:** `.section-footer__row`, `.section-footer__row__col`

---

### 5.2 CAROUSEL SYSTEMS

#### Product Carousel (Best Sellers, Build Muscle)
```
┌─────────────────────────────────────────────────────────────┐
│ CAROUSEL CONTAINER                                         │
│ ┌──────┬────────────────────────────────────────────┬──────┐│
│ │  ◀   │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐      │   ▶  ││
│ │      │  │ P1 │ │ P2 │ │ P3 │ │ P4 │ │ P5 │      │      ││
│ │      │  └────┘ └────┘ └────┘ └────┘ └────┘      │      ││
│ └──────┴────────────────────────────────────────────┴──────┘│
└─────────────────────────────────────────────────────────────┘

Settings:
- Visible items: 4 (desktop), 2 (mobile)
- Scroll: 1 item per click
- Navigation: Arrow buttons (left/right)
- Auto-scroll: No (manual only)
```
**Classes:** `.slider`, `.slider__grid`, `.slider__item`, `.slider-nav`
**Scripts:** `slideshow.js`, `custom-slider.js`
**Interactions:**
- Click arrow → slide one position
- Touch/drag → swipe navigation
- Infinite loop: Yes

#### Product Detail Gallery (Media Gallery)
```
┌─────────────────────────────────────────────────────────────┐
│ MEDIA GALLERY                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │              MAIN IMAGE (large)                        │ │
│ │              540x680px default                          │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐        │
│ │img│img│img│img│img│img│img│img│img│img│img│img│        │
│ └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘        │
│        ← Thumbnail strip (scrollable) →                   │
└─────────────────────────────────────────────────────────────┘

Features:
- Main image: Large display with zoom capability
- Thumbnails: 12 visible images (flavors/variants)
- Click thumbnail → update main image
- Layout: "carousel-under" (thumbnails below main)
- Media type: Images (PNG, JPG)
```
**Classes:** `.media-gallery`, `.media-gallery__inner`, `.slider__grid`
**Gallery Types:** 
- Main: `.slider` with `.slider__item`
- Thumbnails: `.carousel` with `.thumbnails`
**Modal:** `.gallery-viewer-modal` for full-screen view

#### Image Gallery Modal (Product Page)
```
┌─────────────────────────────────────────────────────────────┐
│ GALLERY MODAL (Lightbox)                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  [◀]                                          [X]  [▶]  │ │
│ │                                                         │ │
│ │         ┌───────────────────────────────┐             │ │
│ │         │                               │             │ │
│ │         │      ZOOMED IMAGE              │             │ │
│ │         │      (click to zoom)          │             │ │
│ │         │                               │             │ │
│ │         └───────────────────────────────┘             │ │
│ │                                                         │ │
│ │  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐                  │ │
│ │  │  │ │  │ │  │ │  │ │  │ │  │ │  │  ← Thumbnails   │ │
│ │  └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘                  │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

Features:
- Modal dialog (fixed position, full screen)
- Zoom: Click image to open in full resolution
- Navigation: Previous/Next arrows
- Keyboard: Escape to close
- Thumbnails: Quick jump to any image
```
**Classes:** `.modal`, `.gallery-viewer`, `.gallery-viewer__zoom-container`
**Components:** `.gallery-viewer__prev`, `.gallery-viewer__next`, `.gallery-viewer__close`
**Trigger:** Click main image or "show-gallery" link

---

### 5.3 UI COMPONENTS

#### Product Card
```
┌─────────────────────────────┐
│  ┌───────────────────────┐  │
│  │                       │  │
│  │       IMAGE           │  │
│  │    (3:4 aspect)      │  │
│  │                       │  │
│  │  [SALE BADGE]         │  │
│  │  [SOLD OUT OVERLAY]   │  │
│  └───────────────────────┘  │
│  Product Name                │
│  ★★★★☆ (34 reviews)         │
│  €32.90                      │
│  €45.90 (original)           │
└─────────────────────────────┘

Styles:
- Image container: bg #fafafa, rounded
- Sale badge: bg #ffcc00, text black, font-bold
- Sold out: bg black/40%, centered text
- Title: Oswald font, 13-14px
- Price: Roboto, bold
```
**Classes:** `.product-block`, `.product-block__title`, `.product-block__price`

#### Filter Sidebar (Collection Page)
```
┌──────────────────────────┐
│ FILTERS                  │
│ ┌────────────────────┐   │
│ │ Availability      │   │
│ │ ☐ In stock only   │   │
│ └────────────────────┘   │
│ ┌────────────────────┐   │
│ │ Price Range        │   │
│ │ ○ All prices       │   │
│ │ ○ Under €25        │   │
│ │ ○ €25 - €50        │   │
│ │ ○ Over €50         │   │
│ └────────────────────┘   │
└──────────────────────────┘
```
**Classes:** `.filter-group`, `.filter-group__list`

#### Sort Dropdown
```
┌──────────────────────────┐
│ Sort by: [Featured  ▼] │
└──────────────────────────┘
Options:
- Featured
- Price: Low to High
- Price: High to Low
- Name
```
**Classes:** `.form-select`, `.sort-by-select`

#### Navigation Menu
```
┌─────────────────────────────────────────────────────────┐
│ MAIN NAV                                                │
│ [Proteins] [Pre-Training] [Build Muscle] [Amino Acids]  │
│ [Vitamins & Minerals] [Weight Loss]                     │
└─────────────────────────────────────────────────────────┘
Styles:
- Horizontal flex layout
- Oswald font, 13px, uppercase
- Hover: #ffd100 (yellow)
- Active: underline indicator
```
**Classes:** `.navigation`, `.navigation__item`, `.navigation__link`

#### Mobile Navigation
```
┌─────────────────────────────────────────────────────────┐
│ MOBILE NAV (horizontal scroll)                          │
│ [Proteins] [Pre-Training] [Build Muscle] [Amino Acids] │
│ [Vitamins] [Weight Loss] →                             │
└─────────────────────────────────────────────────────────┘
Styles:
- overflow-x: scroll
- white-space: nowrap
- Hide scrollbar
```

---

### 5.4 FORMS & INPUTS

#### Search Input
```
┌─────────────────────────────┐
│ 🔍  [Search products...]    │
└─────────────────────────────┘
Features:
- Predictive search (autocomplete)
- Icon: magnifying glass
- Placeholder: "Search products..."
```

#### Newsletter Signup
```
┌─────────────────────────────────────────────┐
│ Enter your email                      [SUBSCRIBE] │
└─────────────────────────────────────────────┘
```

#### Quantity Selector
```
┌─────────────────────────────────────────────┐
│ [−]  [1]  [+]                               │
└─────────────────────────────────────────────┘
```

#### Variant Selector (Product Page)
```
Flavor:
○ Strawberry  ○ Capuccino  ○ Chocolate  ○ Vanilla
```

---

### 5.5 ANIMATIONS & EFFECTS

| Effect | CSS | Trigger |
|--------|-----|---------|
| **Image Hover Scale** | `transform: scale(1.05)` over `0.5s` | Hover on product card |
| **Button Hover** | Color transition `0.3s ease` | Hover on buttons |
| **Link Hover** | Color `#ffd100` | Hover on nav links |
| **Carousel Slide** | Transform translateX | Click arrows |
| **Modal Open** | Fade in + scale | Click gallery |
| **Scroll Reveal** | AOS animate `0.6s` | Scroll into view |

**Scripts:** `animate-on-scroll.js`, `slideshow.js`

---

### 5.6 SECTION STRUCTURE (Product Detail Page)

The product page contains 16+ distinct sections:
```
Section 1:  Announcement Bar
Section 2:  Header
Section 3:  Breadcrumb
Section 4:  Product Media Gallery (main image + thumbnails)
Section 5:  Product Info (title, price, variants)
Section 6:  Add to Cart Form
Section 7:  Product Description Tabs
Section 8:  How to Take Section
Section 9:  FAQ Section
Section 10: Related Products (carousel)
Section 11: Reviews (Yotpo/Judge.me)
Section 12: Footer
```

---

## 6. Design Tokens Summary

### 4.1 Colors

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Primary Dark | `#1d1d1d` | 29 29 29 | Header, Footer, Hero background |
| Accent Yellow | `#ffcc00` | 255 204 0 | Top bar, buttons, sale badges |
| Accent Yellow Hover | `#ffd100` | 255 209 0 | Button hover, link hover |
| Muted Gray | `#737373` | 115 115 115 | Secondary text, links |
| White | `#ffffff` | 255 255 255 | Body background |
| Light Gray | `#fafafa` | 250 250 250 | Card backgrounds |

### 4.2 Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Headings | Oswald | 22-36px | Bold |
| Body | Roboto | 14px | 400 |
| Navigation | Roboto | 13px | 400 |
| Product Title | Oswald | 13-14px | Medium |
| Price | Roboto | 14px | Bold |
| Small Text | Roboto | 11-13px | 400 |

### 4.3 Spacing

| Token | Value |
|-------|-------|
| Container Max Width | 1100px |
| Section Padding | 50px (desktop), 60px (mobile) |
| Grid Gap | 20px |
| Card Padding | 16px |

### 4.4 Effects

| Effect | Value |
|--------|-------|
| Image Hover Scale | `scale(1.05)` over `0.5s` |
| Button Transition | `0.3s ease` |
| Link Hover Color | `#ffd100` |

## 7. Responsive Breakpoints

### 7.1 Grid Breakpoints
| Breakpoint | Width | Columns (Product) | Columns (Category) |
|-----------|-------|-------------------|--------------------|
| Mobile | < 768px | 2 | 2 |
| Tablet | 768px - 1024px | 3 | 3 |
| Desktop | > 1024px | 4 | 6 |

### 7.2 Navigation Breakpoints
- **Desktop:** > 768px - Full horizontal nav
- **Mobile:** < 768px - Hamburger menu + horizontal scroll list

### 7.3 Container Max Width
- **Main content:** 1100px
- **Reading content:** 720px
- **Gutters:** 30px (desktop), 20px (tablet), 16px (mobile)

---

## 8. Automated Website Cloning Process

### Phase 1: Website Analysis & URL Discovery

#### Step 1.1: Fetch Homepage & Discover All URLs

**PowerShell Command:**
```powershell
# Using webfetch to get homepage HTML
Invoke-WebRequest -Uri "https://needsupps.site/" -UseBasicParsing
```

**Purpose:** Fetches the homepage HTML to discover all internal links

### Phase 2: Asset Extraction

#### Step 2.1: Download Images

**PowerShell Command:**
```powershell
# Create images directory
New-Item -ItemType Directory -Force -Path "public\images\products"

# Download images (if site allows)
Invoke-WebRequest -Uri "IMAGE_URL" -OutFile "public\images\products\image.png"
```

**If Blocked:** Use Playwright/Puppeteer browser automation

#### Step 2.2: Extract Design Tokens

**Extract from CSS:**
- Colors (from CSS variables)
- Fonts (from @font-face rules)
- Spacing (from CSS variables)

### Phase 3: Project Setup

```powershell
# Initialize Next.js
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-turbopack

# Install dependencies
npm install
```

---

## 9. Development Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server (http://localhost:3000) |
| `npm run build` | Create production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run typecheck` | Run TypeScript check |
| `npm run check` | Run lint + typecheck + build |

---

## 10. Git Workflow

```powershell
git init
git add -A
git commit -m "Initial clone: [website] with Next.js, Tailwind"
git remote add origin https://github.com/USERNAME/REPO.git
git push origin main
```

---

## 11. Deployment

- Push to GitHub
- Connect to Render.com/Vercel
- Build: `npm run build`
- Start: `npm start`

---

## 12. Current Clone Status

### Implemented Pages:
| Route | Page | Status |
|-------|------|--------|
| `/` | Homepage | ✅ Complete |
| `/collections/[category]` | Collection pages (Proteins, Pre-Training, etc.) | ✅ Complete |
| `/products/[id]` | Product detail pages | ✅ Complete |
| `/cart` | Shopping cart | ✅ Complete |
| `/checkout` | Checkout flow | ✅ Complete |
| `/search` | Search functionality | ✅ Complete |
| `/admin` | Admin panel | ✅ Complete |
| `/pages/about-us` | About Us page | ✅ Complete |
| `/pages/contact-us` | Contact Us page | ✅ Complete |
| `/policies/privacy-policy` | Privacy Policy | ✅ Complete |
| `/policies/shipping-policy` | Shipping Policy | ✅ Complete |
| `/policies/refund-policy` | Refund Policy | ✅ Complete |
| `/policies/legal-notice` | Legal Notice | ✅ Complete |
| `/policies/terms-of-service` | Terms of Service | ✅ Complete |
| `/account/login` | Login/Register (toggle) | ✅ Complete |
| `/blogs/the-health-project` | Blog listing | ✅ Complete |
| `/blogs/the-health-project/[id]` | Blog post detail | ✅ Complete |
| `/api/products` | Products API | ✅ Complete |
| `/api/cart` | Cart API | ✅ Complete |
| `/api/newsletter` | Newsletter API | ✅ Complete |

### Completed Features:
- ✅ Homepage with all sections (Announcement bar, Header, Hero, Best Sellers, Categories, Muscle Products, Packs Banner, Footer)
- ✅ Collection pages with filters/sorting (Availability filter, Price range, Sort dropdown)
- ✅ Product detail pages with image gallery, variants, quantity selector
- ✅ Shopping cart with localStorage persistence
- ✅ Complete checkout flow (Cart → Info → Payment → Confirmation)
- ✅ Search functionality with product filtering
- ✅ Admin panel for product management
- ✅ REST API endpoints (products, cart, newsletter)
- ✅ About Us page with company story, values, products
- ✅ Contact Us page with form and contact info
- ✅ Policy pages (Privacy, Shipping, Refund, Legal, Terms)
- ✅ Account/Login page with Login/Register toggle and social login
- ✅ Blog pages (listing + detail with 6 full articles)
- ✅ Newsletter subscription with API and component
- ✅ Mobile responsive navigation

### All Tasks Complete!

## 13. Component Class Mapping (Shopify → Tailwind)

| Shopify Class | Purpose | Tailwind Equivalent |
|-------------|---------|---------------------|
| `.section-header` | Main header | `bg-[#1d1d1d] sticky top-0` |
| `.navigation__link` | Nav links | `text-white font-oswald hover:text-[#ffd100]` |
| `.product-block` | Product card | `group block rounded-md overflow-hidden` |
| `.product-block__title` | Product title | `font-oswald text-sm text-[#1d1d1d]` |
| `.product-block__price` | Price | `font-bold text-[#1d1d1d]` |
| `.slider` | Carousel container | `overflow-hidden` |
| `.slider__grid` | Carousel items | `flex transition-transform duration-300` |
| `.slider-nav__btn` | Carousel arrows | `absolute top-1/2 -translate-y-1/2` |
| `.media-gallery` | Product images | `relative` |
| `.gallery-viewer__thumb` | Gallery thumbnails | `w-20 h-20 object-cover` |
| `.form-input` | Input fields | `border border-gray-300 px-3 py-2` |
| `.form-select` | Dropdowns | `border px-2 py-1 rounded bg-white` |
| `.btn` | Buttons | `px-4 py-2 bg-[#ffcc00] text-black font-bold` |
| `.section-footer` | Footer | `bg-[#1d1d1d] text-white py-10` |
| `.announcement-bar` | Top bar | `bg-[#ffcc00] py-2` |

---

## 14. JavaScript & Interactive Features

### 14.1 Required Scripts
- `main.js` - Core theme functionality
- `slideshow.js` - Carousel/slider functionality
- `custom-select.js` - Custom dropdown selects
- `animate-on-scroll.js` - Scroll animations (AOS)

### 14.2 Interactive Features
| Feature | Script | Implementation |
|---------|--------|-----------------|
| Carousel Navigation | slideshow.js | Arrow click → translateX |
| Thumbnail Gallery | media-gallery.js | Click thumbnail → swap main image |
| Modal Gallery | modal.js | Click → open fullscreen |
| Predictive Search | theme.js | Input → AJAX fetch suggestions |
| Quantity Selector | product-form.js | +/- buttons → update input |
| Variant Selection | product-form.js | Radio/select → update price/image |
| Add to Cart | cart-add.js | Submit form → Shopify cart API |
| Filter/Sort | collection.js | URL params → filter products |

---

## 15. Project Structure (Next.js Clone)

```
src/
├── app/
│   ├── page.tsx                      # Homepage
│   ├── layout.tsx                    # Root layout (fonts, CartProvider)
│   ├── globals.css                   # Global styles & animations
│   ├── favicon.ico                   # Favicon
│   ├── cart/
│   │   └── page.tsx                  # Shopping cart
│   ├── checkout/
│   │   └── page.tsx                  # Checkout flow (info, payment, confirmation)
│   ├── search/
│   │   └── page.tsx                  # Search page
│   ├── admin/
│   │   └── page.tsx                  # Admin panel
│   ├── products/
│   │   └── [id]/
│   │       └── page.tsx              # Product detail
│   ├── collections/
│   │   └── [category]/
│   │       └── page.tsx              # Collection pages (dynamic)
│   ├── pages/
│   │   ├── about-us/
│   │   │   └── page.tsx              # About Us
│   │   └── contact-us/
│   │       └── page.tsx              # Contact Us
│   ├── policies/
│   │   ├── privacy-policy/
│   │   │   └── page.tsx              # Privacy Policy
│   │   ├── shipping-policy/
│   │   │   └── page.tsx              # Shipping Policy
│   │   ├── refund-policy/
│   │   │   └── page.tsx              # Refund Policy
│   │   ├── legal-notice/
│   │   │   └── page.tsx              # Legal Notice
│   │   └── terms-of-service/
│   │       └── page.tsx              # Terms of Service
│   ├── account/
│   │   └── login/
│   │       └── page.tsx              # Login/Register
│   ├── blogs/
│   │   └── the-health-project/
│   │       ├── page.tsx              # Blog listing
│   │       └── [id]/
│   │           └── page.tsx          # Blog post detail
│   └── api/
│       ├── products/
│       │   └── route.ts              # Products API
│       ├── cart/
│       │   └── route.ts              # Cart API
│       └── newsletter/
│           └── route.ts              # Newsletter API
├── components/
│   ├── BestSellers.tsx               # Best sellers carousel
│   ├── ProductCarousel.tsx           # Product carousel component
│   ├── ProductCard.tsx               # Reusable product card
│   ├── Newsletter.tsx                # Newsletter subscription form
│   └── ui/
│       └── button.tsx                # shadcn/ui button
├── lib/
│   ├── utils.ts                      # cn() utility
│   ├── data.ts                       # Products, categories, blog posts
│   └── cart-context.tsx              # Cart state (React Context)
├── types/
│   └── .gitkeep                      # TypeScript types placeholder
├── hooks/
│   └── .gitkeep                      # Custom hooks placeholder
└── public/
    └── images/                       # Downloaded images
        ├── products/                 # Product images
        ├── category-*.jpg             # Category images
        ├── logo.png                  # Logo
        ├── hero-slider.jpg           # Hero image
        └── packs-banner.jpg          # Packs banner
```

---

## 16. Design Tokens (Implemented)

### Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `--header-bg-col` | `#1d1d1d` | Header, Footer, Hero backgrounds |
| `--main-nav-link-hover-col` | `#ffd100` | Navigation hover, accent |
| `--btn-bg-color` | `#ffcc00` | Primary button background |
| `--body-bg-color` | `255 255 255` | Page background |
| `--base-text-size` | `14px` | Base font size |

### Typography
| Element | Font | Weight | Size |
|---------|------|--------|------|
| Headings | Oswald | Bold | 22-42px |
| Body | Roboto | 400 | 13-15px |
| Navigation | Oswald | Medium | 13px |
| Product Title | Oswald | Medium | 14px |

### Layout
| Token | Value |
|-------|-------|
| `--page-container-width` | 1100px |
| `--reading-container-width` | 720px |
| `--gutter-large` | 30px |
| `--gutter-desktop` | 20px |
| `--gutter-mobile` | 16px |
| `--section-padding` | 50px |

---

## 17. Build & Run Commands

### Development
```bash
npm run dev
# Starts development server at http://localhost:3000
```

### Production Build
```bash
npm run build
# Creates optimized production build

npm run start
# Starts production server
```

### Quality Checks
```bash
npm run lint        # ESLint check
npm run typecheck   # TypeScript check
npm run check       # lint + typecheck + build
```

---

## 18. Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript (strict mode) |
| UI Library | React 19 |
| Styling | Tailwind CSS v4 |
| UI Components | shadcn/ui (Radix primitives) |
| Icons | Lucide React + inline SVGs |
| Fonts | Google Fonts (Roboto, Oswald) |
| State | React Context (cart) |
| Data | Static JSON (data.ts) |
| Storage | localStorage (cart persistence) |
| Deployment | Vercel / Render.com |

---

*Document created: April 2026*
*Last updated: April 2026*