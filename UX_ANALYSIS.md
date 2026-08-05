# Milestone 1: UX Analysis — Reference Site vs PURE HEALTH SUPPS

## Reference Site (Avabyaish) — UX Patterns Extracted

### 1. NAVIGATION & HEADER
- **Sticky header** with backdrop blur (not solid — translucent)
- **Announcement bar** at top: promo text + coupon code badge
- **Logo** with tagline underneath
- **Search bar** with instant search dropdown (live results as you type)
- **Action buttons**: Skin Quiz, Account, Admin, Settings, Wishlist (with badge count), Cart (with badge count)
- **Desktop nav** row below logo with active state underline
- **Mobile hamburger** menu with slide-down drawer
- **Mobile search** input inside drawer

### 2. HERO SECTION
- **Two-column layout**: Left = copy + CTAs, Right = product image
- **Badge pill** at top ("45-Day Cold-Processed Artisanal Soaps")
- **Headline** with serif font + italic accent color on key word
- **Subtext** paragraph describing brand story
- **Two CTAs**: Primary (solid) + Secondary (outline with icon)
- **Stats row** at bottom: 3 key metrics (100% Herbs, 45 Days, 4.9★)
- **Product image** with floating card overlay showing price + product name

### 3. CATEGORY FILTERING (Homepage)
- **Horizontal scrollable pill buttons** for category filtering
- Active state: filled background + ring
- "View All" link on right side

### 4. PRODUCT CARD
- **Image stage** with hover zoom effect (scale 1.05)
- **Badges**: Bestseller sparkle, Discount % OFF
- **Wishlist heart** button (top-right, toggles fill)
- **Quick View** floating button on hover (bottom-center)
- **Category pill** + skin type text
- **Product name** (clickable)
- **Hindi name** in italic
- **Star rating** with count
- **Price** with original strikethrough
- **"Add" button** with shopping bag icon

### 5. QUICK VIEW MODAL
- **Backdrop blur** overlay
- **Two-column layout**: Image left, Info right
- **Close button** (X, top-right)
- **Category badge** + batch number
- **Product name** + Hindi name
- **Star rating**
- **Description** (line-clamped)
- **Variant selector** (list of radio-style buttons)
- **Quantity stepper** (+/- buttons)
- **Price** with GST note
- **"Add to Cart" button** with success state animation
- **"View Full Details"** link

### 6. CART DRAWER
- **Slide-in from right** with backdrop overlay
- **Header**: Icon + title + item count badge + close button
- **Free shipping progress bar** with percentage + message
- **Cart items list** with:
  - Product image (thumbnail)
  - Name + variant + weight
  - Remove button (trash icon)
  - Quantity stepper (+/-)
  - Price with original strikethrough
- **Coupon form**: Input + Apply button
- **Summary**: Subtotal, Discount, GST (included note), Shipping, Total
- **Checkout button** with arrow + security badge
- **Empty state** with illustration + explore button

### 7. SHOP PAGE
- **Header banner** with title + subtitle
- **Filter toolbar**: Mobile filter button, result count, sort dropdown
- **Mobile filter drawer** (slide-in)
- **Filter options**: Category pills, Skin type pills, Price range
- **Sort options**: Bestseller, Price Low-High, Price High-Low, Rating
- **Product grid** (responsive: 1-2-4 columns)

### 8. PRODUCT DETAIL PAGE
- **Breadcrumbs** navigation
- **Two-column layout**: Gallery left, Info right
- **Gallery**: Main image + thumbnail strip (clickable)
- **Badges**: Bestseller
- **Variant selector** (visual cards)
- **Quantity stepper**
- **Price** with discount badge
- **"Add to Cart" + "Buy Now"** buttons
- **Trust badges**: Free Shipping, FSSAI, Banned Substance Free
- **Tabs**: Ingredients, Scent Profile, Usage
- **Reviews section** with:
  - Average rating display
  - "Write Review" button
  - Review cards with author, location, rating, title, comment, verified badge
- **Share button** (copy link)
- **Related products** grid

### 9. CHECKOUT PAGE
- **Two-column layout**: Form left, Summary right
- **Contact form**: Name, Email, Phone
- **Address form**: Line 1, Line 2, Landmark, Pincode (with auto-lookup), City, State, Address Type
- **GSTIN input** (optional, for B2B)
- **Payment method**: Razorpay / COD toggle
- **Order summary**: Items, Subtotal, Discount, GST breakdown (CGST/SGST), Shipping, COD fee, Total
- **Place Order button** with loading state
- **Security badges**

### 10. CART PAGE
- **Back to Shop** link
- **Item count** badge
- **Cart items** with full details
- **Coupon section** with available coupons list
- **Summary panel** (sticky on desktop)
- **Proceed to Checkout** button

### 11. STATE MANAGEMENT
- **React Context** (ShopContext) with:
  - Products, Cart, Wishlist, Orders, Coupons
  - User auth (login/register/logout)
  - Store settings
  - Razorpay config
  - localStorage persistence for all state
- **Actions**: addToCart, removeFromCart, updateQuantity, clearCart, toggleWishlist, applyCoupon, addOrder, etc.

### 12. ADMIN CMS
- **Product CRUD**: Add, Edit, Delete products
- **Order Management**: View orders, update status, add tracking
- **Coupon CRUD**: Add, Edit, Delete coupons
- **Review Moderation**: Approve/Delete reviews
- **Store Settings**: Edit store name, tagline, contact info, shipping rates

---

## PURE HEALTH SUPPS — What's Built vs What's Missing

### BUILT (Visual Only)
| Component | Status | Notes |
|---|---|---|
| Navbar | ✅ Visual | No search, no cart badge, no mobile drawer |
| Hero | ✅ Visual | No stats row, no floating product card |
| Product Cards | ✅ Visual | No hover zoom, no wishlist, no quick view |
| Benefits | ✅ Visual | Basic grid, no interactions |
| Nutrition | ✅ Visual | No tabs, no accordion |
| Testimonials | ✅ Visual | No review form |
| Footer | ✅ Visual | No working newsletter |
| Image Gallery | ✅ Visual | Lightbox works |

### MISSING (Functional)
| Feature | Priority | Complexity |
|---|---|---|
| Zustand Store | P0 | Medium |
| Cart Drawer | P0 | High |
| Add to Cart Logic | P0 | Low |
| Quick View Modal | P0 | High |
| Product Detail Page | P0 | High |
| Checkout Flow | P0 | High |
| Razorpay Integration | P0 | High |
| GST Calculation | P1 | Medium |
| Coupon System | P1 | Medium |
| Wishlist | P1 | Low |
| Search (instant) | P1 | Medium |
| Category Filtering | P1 | Low |
| Sort Options | P1 | Low |
| Quantity Stepper | P1 | Low |
| Auth/Account | P2 | High |
| Admin CMS | P2 | Very High |
| Order Tracking | P2 | Medium |
| Pincode Lookup | P2 | Medium |
| FAQ Page | P2 | Low |
| Policy Pages | P2 | Low |
| Announcement Bar | P3 | Low |
| Breadcrumbs | P3 | Low |
| Recently Viewed | P3 | Low |
| Skin Quiz | P3 | Medium |

---

## INTERACTIONS NEEDED (from Reference)

### Hover Effects
1. Product card image zoom (scale 1.05)
2. Product card shadow elevation on hover
3. Wishlist heart fill animation
4. Quick View button fade-in on card hover
5. Button color transitions
6. Nav link underline animation
7. Search result hover background

### Scroll Animations
1. Hero fade-in on load
2. Section reveal on scroll (fade up)
3. Product cards stagger reveal
4. Stats counter animation
5. Testimonial cards slide-in

### Modal/Drawer Animations
1. Cart drawer slide-in from right
2. Quick view modal scale-in
3. Backdrop fade + blur
4. Close button hover rotation

### Micro-interactions
1. Quantity +/- button feedback
2. Add to cart success animation (checkmark)
3. Coupon apply/remove feedback
4. Wishlist toggle heart fill
5. Share link copy confirmation
6. Form field focus ring

### Page Transitions
1. Route change fade
2. Scroll to top on navigation
3. Loading states between pages
