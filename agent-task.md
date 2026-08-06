# Build Task: NUFUIX

## Business Context
**Industry:** nutrition
**Transaction type:** product-purchase
**Currency:** USD
**Locale:** US

## Business Discovery

**Signal confidence: 0.80 — discovery questions SKIPPED.**
The prompt contains enough explicit signals (products, prices, CTA, theme) to build without asking.

### Auto-filled from prompt signals:
| Question | Answer (auto-extracted) |
|---|---|
| What is the business goal? | Sell nutrition products |
| What should visitors do on this site? | Browse and purchase products |
| What defines success for this business? | Revenue from nutrition sales |
| Who are the ideal customers? | nutrition enthusiasts |
| What problems does this business solve? | Need for quality nutrition |
| Who is the business owner/team? | NUFUIX team |
| What do customers need most? | Quality nutrition at fair prices |
| Why should people trust this business? | Expert curation and quality guarantee |
| What action should users take? | Shop Now |
| What makes this business different? | Curated selection and expert knowledge |
| What content does this business need? | Product catalog, pricing, testimonials |

**These answers drive EVERY piece of copy, every CTA, every testimonial, every feature list.**
**Generic filler is NOT an option. Real answers = real content.**

## What This Business Does

This is a **nutrition** business.
It sells products online.

**Example business:** A nutrition company that offers detailed specs, technical info, comparison charts, photo gallery, before & after, portfolio.

## Industry Vocabulary

**USE these terms** (industry-specific, real, concrete):
- shop
- buy
- cart
- checkout
- order
- price
- discount
- sale
- new arrival
- in stock
- collection
- range
- lineup
- selection
- variety
- options
- models
- styles
- specifications
- features

**NEVER use these terms** (generic filler):
- solutions
- services
- features
- products
- offerings
- capabilities
- synergy
- leverage
- optimize
- streamline
- enhance
- maximize
- utilize
- facilitate

**Example CTAs** (use these patterns, customize for the business):
- Shop Now
- View Collection
- Add to Cart
- Buy Now
- See Prices

**Example features** (real capabilities, not abstract categories):
- Detailed Specs
- Technical Info
- Comparison Charts
- Photo Gallery
- Before & After
- Portfolio

**Customer roles** (who buys from this business):
- Customer
- Shopper
- Buyer

## Primitive Reasoning Output
*(These signals drove every decision below — honor them in your output)*

- **Transaction type:** product-purchase
- **Value object:** nutrition
- **Aesthetic signals:** dark-theme, light-theme, glassmorphism, scroll-motion, animated-visual
- **Emotional intent:** futuristic, premium, energy, natural, authentic
- **Content shape:** multiple-products, specs-table, image-gallery, blog-feed, client-logos, pricing-table, reviews

## Components to Generate

Generate each component below with REAL business content. NO generic filler.

### SoundwaveHero
**Category:** hero
**Reason:** aestheticSignals includes animated/immersive element

**Content to use:**
- Use real nutrition content from the vocabulary above

### CTASection
**Category:** conversion
**Reason:** standard conversion element

**Content to use:**
- Headline: Ready to Get Started?
- Subtext: Contact us today for a free consultation
- CTA: Shop Now

### GlobalFooter
**Category:** footer
**Reason:** standard footer

**Content to use:**
- Use real nutrition content from the vocabulary above

### ProductShowcase
**Category:** showcase
**Reason:** transactionType is product-purchase — show products with specs and pricing

**Content to use:**
- Use real nutrition content from the vocabulary above

### SpecsTable
**Category:** content
**Reason:** contentShape includes specs-table — detailed product specifications

**Content to use:**
- Use real nutrition content from the vocabulary above

### GallerySection
**Category:** content
**Reason:** contentShape includes image-gallery — product images

**Content to use:**
- Use real nutrition content from the vocabulary above

### TestimonialCarousel
**Category:** content
**Reason:** contentShape includes reviews — customer testimonials

**Content to use:**
- "Amazing nutrition service! Highly recommend." — Customer
- "Professional and reliable. Will use again." — Shopper

### PricingTable
**Category:** conversion
**Reason:** contentShape includes pricing-table — pricing tiers

**Content to use:**
- Basic: $29/mo — Detailed Specs
- Standard: $49/mo — Detailed Specs + Technical Info
- Premium: $79/mo — All features included

### FeatureGrid
**Category:** content
**Reason:** aestheticSignals includes glassmorphism — glass card design

**Content to use:**
- Use real nutrition content from the vocabulary above

## Component Prop Contracts

Every component MUST declare these props. Use REAL values, not placeholders.

### SoundwaveHero
```typescript
interface SoundwaveHeroProps {
  title?: string;
  subtitle?: string;
  cta?: string;
  title?: string;
  subtitle?: string;
  cta?: string;
}

### CTASection
```typescript
interface CTASectionProps {
  variant?: string;
  variant?: string;
}

### GlobalFooter
```typescript
interface GlobalFooterProps {
}

### ProductShowcase
```typescript
interface ProductShowcaseProps {
  columns?: string;
  gap?: string;
  items?: Array<{ name: string; price: string; description: string; image?: string; specs?: Array<{ label: string; value: string }> }>;
  columns?: number;
}

### SpecsTable
```typescript
interface SpecsTableProps {
  variant?: string;
}

### GallerySection
```typescript
interface GallerySectionProps {
  columns?: string;
  lightbox?: string;
  images?: Array<{ src: string; alt: string; caption?: string }>;
  columns?: number;
}

### TestimonialCarousel
```typescript
interface TestimonialCarouselProps {
  items?: string;
  testimonials?: Array<{ quote: string; author: string; role?: string; rating?: number; image?: string }>;
}

### PricingTable
```typescript
interface PricingTableProps {
  columns?: string;
  highlight?: string;
  variant?: string;
  tiers?: Array<{ name: string; price: string; features: string[]; highlighted?: boolean }>;
}

### FeatureGrid
```typescript
interface FeatureGridProps {
  columns?: string;
  variant?: string;
}

## Content Generation Rules

1. **NEVER use generic filler text** like "Features", "Everything you need", "Product Management".
2. **Use REAL business terms** for nutrition. Mention actual products, services, features.
3. **Hero section** must state the business goal from Business Discovery — what the business DOES and why it matters.
4. **Feature descriptions** must describe actual capabilities that solve the problems listed in Business Discovery.
5. **Testimonials** must sound like the ideal customers from Business Discovery — use their language, their pain points.
6. **CTA text** must match the action users should take from Business Discovery — "Book a Session", "Order Now", "Get a Quote".
7. **Pricing** must use realistic numbers for the nutrition industry (not $9.99 / $19.99 / $29.99 defaults).
8. **Trust signals** must reference what makes this business different — years of experience, certifications, unique approach.
9. **Every sentence** should answer: "Does this help the ideal customer understand why this business is the right choice?"

## Sample Content

Use this REAL content when building components. Do NOT use placeholder text.

### Hero Section
```
Title: Professional nutrition Services
Subtitle: Detailed Specs | Technical Info | Comparison Charts
CTA: Shop Now
```

### Service Menu
```
Detailed Specs — $36-146
Technical Info — $68-125
Comparison Charts — $21-50
```

### Testimonials
```
"Professional nutrition service. Highly recommend!" — Customer
"Reliable and experienced. Will use again." — Shopper
"Best nutrition in the area." — Customer
```

### CTA
```
Ready to Get Started?
Contact us today for a free consultation.
Shop Now
```

## Design System

**Colors:**
- Primary: #3b82f6
- Secondary: #10b981
- Accent: #8b5cf6

**Fonts:** heading=Inter, body=Inter

## Technical Requirements

- Every component file: `"use client";` at top
- Import React, useState, useEffect as needed
- Import icons from `lucide-react`
- Import motion from `framer-motion`
- Use Tailwind CSS classes — NO inline styles
- Export as `export default function ComponentName()`
- Use `Link` from `next/link` for all internal navigation
- Apply design tokens from the design system

## ⚡ Action Required

Write EVERY component file listed above to disk NOW.
Each file must:
1. Start with `"use client";`
2. Declare the exact interface from the Prop Contracts
3. Use Framer Motion for animations
4. Use lucide-react for icons
5. Use Tailwind CSS — no inline styles
6. Export as `export default function ComponentName()`
7. Use REAL business content from Sample Content section — NO generic filler

Output paths:
- `src/components/soundwave-hero.tsx`
- `src/components/ctasection.tsx`
- `src/components/global-footer.tsx`
- `src/components/product-showcase.tsx`
- `src/components/specs-table.tsx`
- `src/components/gallery-section.tsx`
- `src/components/testimonial-carousel.tsx`
- `src/components/pricing-table.tsx`
- `src/components/feature-grid.tsx`