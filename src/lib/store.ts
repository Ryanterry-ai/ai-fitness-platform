import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface ProductVariant {
  id: string;
  name: string;
  weight: string;
  price: number;
  originalPrice: number;
  stock: number;
}

export interface Product {
  id: string;
  slug: string;
  name: string;
  brand: string;
  tagline: string;
  category: string;
  flavour: string;
  description: string;
  image: string;
  galleryImages: string[];
  variants: ProductVariant[];
  nutritionFacts: { name: string; amount: string; unit: string }[];
  ingredients: string;
  badges: string[];
  rating: number;
  reviewCount: number;
  isBestseller: boolean;
  price: number;
  originalPrice: number;
  inStock: boolean;
}

export interface CartItem {
  product: Product;
  variant: ProductVariant;
  quantity: number;
}

export interface Coupon {
  code: string;
  discountType: 'percentage' | 'fixed';
  value: number;
  minOrder: number;
  description: string;
}

export interface Order {
  id: string;
  orderNumber: string;
  date: string;
  items: CartItem[];
  subtotal: number;
  discount: number;
  gst: number;
  shipping: number;
  total: number;
  paymentMethod: 'razorpay' | 'cod' | 'upi';
  paymentStatus: 'PAID' | 'PENDING' | 'FAILED';
  orderStatus: 'Processing' | 'Dispatched' | 'Delivered';
  shippingAddress: {
    name: string;
    phone: string;
    email: string;
    address: string;
    city: string;
    state: string;
    pincode: string;
  };
}

interface ShopState {
  products: Product[];
  cart: CartItem[];
  isCartOpen: boolean;
  wishlist: string[];
  coupons: Coupon[];
  appliedCoupon: Coupon | null;
  orders: Order[];
  quickViewProduct: Product | null;
  isSearchOpen: boolean;
  searchQuery: string;
  couponInput: string;
  setCouponInput: (val: string) => void;
  currentUser: { name: string; email: string; phone: string } | null;
  subtotal: number;
  discountAmount: number;
  shippingFee: number;
  gstAmount: number;
  grandTotal: number;

  addToCart: (product: Product, variant: ProductVariant, quantity?: number) => void;
  removeFromCart: (productId: string, variantId: string) => void;
  updateQuantity: (productId: string, variantId: string, delta: number) => void;
  clearCart: () => void;
  setCartOpen: (open: boolean) => void;
  toggleWishlist: (productId: string) => void;
  isInWishlist: (productId: string) => boolean;
  applyCoupon: (code: string) => { success: boolean; message: string };
  removeCoupon: () => void;
  setQuickViewProduct: (product: Product | null) => void;
  setSearchQuery: (query: string) => void;
  setSearchOpen: (open: boolean) => void;
  addOrder: (order: Order) => void;
  updateOrderStatus: (orderId: string, status: Order['orderStatus']) => void;
  loginUser: (email: string, name: string, phone: string) => void;
  logoutUser: () => void;
  recalculateTotals: () => void;
}

const NUTRITION_FACTS = [
  { name: 'Energy', amount: '1.24', unit: 'Kcal' },
  { name: 'Carbohydrate', amount: '0.28', unit: 'g' },
  { name: 'Total Sugar', amount: '0.11', unit: 'g' },
  { name: 'Beta Alanine', amount: '1.5', unit: 'g' },
  { name: 'Arginine HCL', amount: '750', unit: 'mg' },
  { name: 'L-Citrulline', amount: '500', unit: 'mg' },
  { name: 'L-Carnitine', amount: '250', unit: 'mg' },
  { name: 'L-Tyrosine', amount: '125', unit: 'mg' },
  { name: 'Caffeine', amount: '50', unit: 'mg' },
];

const INGREDIENTS = 'Beta Alanine, Arginine HCL, L-Citrulline, L-Carnitine, L-Tyrosine, Encapsulated Caffeine, Coffee Bean Extract, Garcinia Cambogia, Mucuna Pruriens';

const DEFAULT_PRODUCTS: Product[] = [
  {
    id: 'primex-orange',
    slug: 'primex-preworkout-orange',
    name: 'PRIME X Pre-Workout — Orange',
    brand: 'PURE HEALTH SUPPS',
    tagline: '8 Clinically Dosed Ingredients. Zero Crash.',
    category: 'Pre-Workout',
    flavour: 'Orange',
    description: 'Bright citrus energy that hits clean and lasts. 1.5g Beta-Alanine pushes the burn back, 750mg Arginine HCl floods the pump, and encapsulated caffeine keeps you locked in without the crash. 80 servings of focused, sustained performance.',
    image: '/products/Orange.png',
    galleryImages: ['/products/Orange.png', '/products/tub-orange.png'],
    variants: [
      { id: 'single', name: 'Single Jar', weight: '280g', price: 1299, originalPrice: 1599, stock: 100 },
      { id: 'bundle-2', name: 'Bundle of 2', weight: '560g', price: 2399, originalPrice: 3198, stock: 50 },
      { id: 'bundle-3', name: 'Bundle of 3', weight: '840g', price: 3499, originalPrice: 4797, stock: 30 },
    ],
    nutritionFacts: NUTRITION_FACTS,
    ingredients: INGREDIENTS,
    badges: ['Banned Substance Free', 'Contains Caffeine', 'FSSAI Certified'],
    rating: 0,
    reviewCount: 0,
    isBestseller: true,
    price: 1299,
    originalPrice: 1599,
    inStock: true,
  },
  {
    id: 'primex-fruit-punch',
    slug: 'primex-preworkout-fruit-punch',
    name: 'PRIME X Pre-Workout — Fruit Punch',
    brand: 'PURE HEALTH SUPPS',
    tagline: 'The Flagship Formula. Full-Spectrum Performance.',
    category: 'Pre-Workout',
    flavour: 'Fruit Punch',
    description: 'Our flagship blend for max-intensity training days. A full mixed-fruit hit backed by 8 clinically dosed ingredients — pumps, focus, and sustained energy from warm-up to last rep. 80 servings per tub.',
    image: '/products/Fruit Punch.png',
    galleryImages: ['/products/Fruit Punch.png', '/products/tub-fruit-punch.png'],
    variants: [
      { id: 'single', name: 'Single Jar', weight: '280g', price: 1299, originalPrice: 1599, stock: 100 },
      { id: 'bundle-2', name: 'Bundle of 2', weight: '560g', price: 2399, originalPrice: 3198, stock: 50 },
      { id: 'bundle-3', name: 'Bundle of 3', weight: '840g', price: 3499, originalPrice: 4797, stock: 30 },
    ],
    nutritionFacts: NUTRITION_FACTS,
    ingredients: INGREDIENTS,
    badges: ['Banned Substance Free', 'Contains Caffeine', 'FSSAI Certified'],
    rating: 0,
    reviewCount: 0,
    isBestseller: false,
    price: 1299,
    originalPrice: 1599,
    inStock: true,
  },
  {
    id: 'primex-rocket',
    slug: 'primex-preworkout-rocket-lollipop',
    name: 'PRIME X Pre-Workout — Rocket Lollipop',
    brand: 'PURE HEALTH SUPPS',
    tagline: 'Nostalgic Flavour. Serious Performance.',
    category: 'Pre-Workout',
    flavour: 'Rocket Lollipop',
    description: 'Sweet candy nostalgia meets clinical performance. Same 8-ingredient formula — Beta-Alanine, Arginine HCl, L-Citrulline, and slow-release caffeine — in a flavour that makes you look forward to scoop day. 80 servings.',
    image: '/products/Rocket Lolli pop.png',
    galleryImages: ['/products/Rocket Lolli pop.png', '/products/tub-rocket.png'],
    variants: [
      { id: 'single', name: 'Single Jar', weight: '280g', price: 1299, originalPrice: 1599, stock: 100 },
      { id: 'bundle-2', name: 'Bundle of 2', weight: '560g', price: 2399, originalPrice: 3198, stock: 50 },
      { id: 'bundle-3', name: 'Bundle of 3', weight: '840g', price: 3499, originalPrice: 4797, stock: 30 },
    ],
    nutritionFacts: NUTRITION_FACTS,
    ingredients: INGREDIENTS,
    badges: ['Banned Substance Free', 'Contains Caffeine', 'FSSAI Certified'],
    rating: 0,
    reviewCount: 0,
    isBestseller: false,
    price: 1299,
    originalPrice: 1599,
    inStock: true,
  },
];

const DEFAULT_COUPONS: Coupon[] = [
  { code: 'PURE10', discountType: 'percentage', value: 10, minOrder: 999, description: '10% off orders above ₹999' },
  { code: 'FIRSTORDER', discountType: 'percentage', value: 15, minOrder: 1499, description: '15% off your first order above ₹1,499' },
  { code: 'FLAT200', discountType: 'fixed', value: 200, minOrder: 1999, description: '₹200 off orders above ₹1,999' },
];

const SAMPLE_ORDERS: Order[] = [
  {
    id: 'ord-001',
    orderNumber: 'PHS-2026-001',
    date: '2026-08-01T10:30:00Z',
    items: [],
    subtotal: 1299,
    discount: 130,
    gst: 212,
    shipping: 0,
    total: 1381,
    paymentMethod: 'razorpay',
    paymentStatus: 'PAID',
    orderStatus: 'Dispatched',
    shippingAddress: { name: 'Rahul Sharma', phone: '+91 98765 43210', email: 'rahul@example.com', address: '123 Gym Street', city: 'Mumbai', state: 'Maharashtra', pincode: '400001' },
  }
];

export const useShop = create<ShopState>()(
  persist(
    (set, get) => ({
      products: DEFAULT_PRODUCTS,
      cart: [],
      isCartOpen: false,
      wishlist: [],
      coupons: DEFAULT_COUPONS,
      appliedCoupon: null,
      orders: SAMPLE_ORDERS,
      quickViewProduct: null,
      isSearchOpen: false,
      searchQuery: '',
      couponInput: '',
      currentUser: null,
      subtotal: 0,
      discountAmount: 0,
      shippingFee: 0,
      gstAmount: 0,
      grandTotal: 0,

      addToCart: (product, variant, quantity = 1) => {
        set((state) => {
          const existingIndex = state.cart.findIndex(
            (item) => item.product.id === product.id && item.variant.id === variant.id
          );

          let newCart;
          if (existingIndex > -1) {
            newCart = [...state.cart];
            newCart[existingIndex].quantity += quantity;
          } else {
            newCart = [...state.cart, { product, variant, quantity }];
          }

          return { cart: newCart, isCartOpen: false };
        });
        get().recalculateTotals();
      },

      removeFromCart: (productId, variantId) => {
        set((state) => ({
          cart: state.cart.filter(
            (item) => !(item.product.id === productId && item.variant.id === variantId)
          ),
        }));
        get().recalculateTotals();
      },

      updateQuantity: (productId, variantId, delta) => {
        set((state) => ({
          cart: state.cart
            .map((item) => {
              if (item.product.id === productId && item.variant.id === variantId) {
                const newQty = item.quantity + delta;
                return newQty > 0 ? { ...item, quantity: newQty } : null;
              }
              return item;
            })
            .filter(Boolean) as CartItem[],
        }));
        get().recalculateTotals();
      },

      clearCart: () => set({ cart: [], appliedCoupon: null }),
      setCartOpen: (open) => set({ isCartOpen: open }),

      toggleWishlist: (productId) =>
        set((state) => ({
          wishlist: state.wishlist.includes(productId)
            ? state.wishlist.filter((id) => id !== productId)
            : [...state.wishlist, productId],
        })),

      isInWishlist: (productId) => get().wishlist.includes(productId),

      applyCoupon: (code) => {
        const coupon = get().coupons.find((c) => c.code === code.toUpperCase());
        if (!coupon) return { success: false, message: 'Invalid coupon code' };
        if (get().subtotal < coupon.minOrder) {
          return { success: false, message: `Minimum order ₹${coupon.minOrder} required` };
        }
        set({ appliedCoupon: coupon });
        get().recalculateTotals();
        return { success: true, message: `Coupon ${coupon.code} applied!` };
      },

      removeCoupon: () => {
        set({ appliedCoupon: null });
        get().recalculateTotals();
      },

      setQuickViewProduct: (product) => set({ quickViewProduct: product }),
      setSearchQuery: (query) => set({ searchQuery: query }),
      setSearchOpen: (open) => set({ isSearchOpen: open }),
      setCouponInput: (val) => set({ couponInput: val }),

      addOrder: (order) => set((state) => ({ orders: [order, ...state.orders], cart: [] })),
      updateOrderStatus: (orderId, status) =>
        set((state) => ({
          orders: state.orders.map((o) => (o.id === orderId ? { ...o, orderStatus: status } : o)),
        })),

      loginUser: (email, name, phone) => set({ currentUser: { name, email, phone } }),
      logoutUser: () => set({ currentUser: null }),

      recalculateTotals: () => {
        const { cart, appliedCoupon } = get();
        const subtotal = cart.reduce((acc, item) => acc + item.variant.price * item.quantity, 0);
        let discountAmount = 0;
        if (appliedCoupon) {
          discountAmount = appliedCoupon.discountType === 'percentage'
            ? Math.round((subtotal * appliedCoupon.value) / 100)
            : appliedCoupon.value;
        }
        const shippingFee = subtotal >= 999 ? 0 : 99;
        const taxableAmount = Math.max(0, subtotal - discountAmount);
        const gstAmount = Math.round(taxableAmount - taxableAmount / 1.18);
        const grandTotal = Math.max(0, subtotal - discountAmount + shippingFee);

        set({ subtotal, discountAmount, shippingFee, gstAmount, grandTotal });
      },
    }),
    {
      name: 'pure-health-supps-store',
      partialize: (state) => ({
        cart: state.cart,
        wishlist: state.wishlist,
        appliedCoupon: state.appliedCoupon,
        orders: state.orders,
        currentUser: state.currentUser,
      }),
    }
  )
);
