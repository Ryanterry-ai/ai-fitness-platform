# Flagship Optimization Sprint 1 - Homepage Implementation Plan

## Overview
**Goal:** Transform homepage into premium flagship brand experience
**Timeline:** Today (single session)
**Focus:** Homepage only - must remain deployable

---

## P0 (Never Break) ✅ Already Complete
- Business logic preserved
- Product data intact
- Navigation flow working
- SEO maintained
- All routes functional
- Performance verified
- Mobile responsiveness maintained

---

## P1 - Sprint 1 Implementation Tasks

### 1. Centralized Purchase Handler (CRITICAL)
**File:** `src/lib/purchase.ts`
- Create centralized purchase utility
- All CTAs redirect to: https://www.upgraded.co.in
- Add loading transition (200-400ms)
- Show "Redirecting to our Official PAN India Distribution Partner..."
- Future-proof: can switch to native checkout later

### 2. Premium Hero Section
**File:** `src/app/page.tsx` (hero section)
- GSAP entrance animation (text reveal, product float)
- Parallax background
- Improved typography hierarchy
- Clear CTA with purchase handler
- Mobile-first responsive design

### 3. Mobile Navigation Enhancement
**File:** `src/app/page.tsx` (mobile nav)
- Larger touch targets (min 44px)
- Thumb-friendly positioning
- Smooth drawer animation
- Cart badge with count

### 4. Product Cards Polish
**File:** `src/app/page.tsx` (products section)
- Ghost-inspired card design
- Hover effects (Framer Motion)
- Clear pricing and CTA
- Purchase handler integration

### 5. Typography & Spacing
**Files:** `src/app/globals.css`, `src/app/page.tsx`
- Consistent heading hierarchy
- Improved line heights
- Better section spacing
- Mobile-optimized font sizes

### 6. Trust Sections
**File:** `src/app/page.tsx`
- "Official PAN India Distribution Partner" messaging
- Trust badges
- Social proof elements

### 7. Motion System
**Files:** `src/app/page.tsx`, `src/components/ScrollReveal.tsx`
- GSAP: Hero entrance, section reveals, parallax
- Framer Motion: Button hovers, card interactions
- No conflicting animations on same element

### 8. Footer Polish
**File:** `src/app/page.tsx` (footer section)
- Clean layout
- Working links
- Brand messaging

---

## Implementation Order

1. **Create purchase utility** (`src/lib/purchase.ts`)
2. **Update homepage** (`src/app/page.tsx`) with:
   - Premium hero with GSAP
   - Mobile navigation improvements
   - Product cards with purchase handler
   - Trust sections
   - Typography/spacing fixes
   - Footer polish
3. **Update globals.css** with new utility classes
4. **Test and verify** build passes

---

## Critical Rules

- ✅ Every purchase CTA → Upgraded Health (https://www.upgraded.co.in)
- ✅ Mobile-first (90%+ visitors on phones)
- ✅ Keep existing CSS/Tailwind/Globals.css
- ✅ GSAP for hero/scroll, Framer Motion for micro-interactions
- ✅ No architecture refactors
- ✅ Website must remain deployable

---

## Success Criteria

- [ ] All CTAs redirect to Upgraded Health
- [ ] Hero has premium GSAP entrance
- [ ] Mobile navigation is thumb-friendly
- [ ] Product cards are polished
- [ ] Trust messaging is visible
- [ ] Motion system is consistent
- [ ] Build passes
- [ ] No regressions