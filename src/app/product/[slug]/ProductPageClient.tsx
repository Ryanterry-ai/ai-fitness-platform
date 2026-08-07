'use client';

import React, { useState, useEffect, useRef, useCallback, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Menu, X } from 'lucide-react';
import Image from '@/components/Image';
import { useShop, Product, ProductVariant } from '@/lib/store';
import { PARTNER_URL } from '@/components/AnnouncementBar';
import CartDrawer from '../../../components/CartDrawer';
const StickyCtaBar = React.lazy(() => import('../../../components/StickyCtaBar'));
const BackToTop = React.lazy(() => import('../../../components/BackToTop'));

const BENEFITS = [
  { key: 'F', label: 'Focus', desc: 'L-Tyrosine + encapsulated caffeine for clean mental drive — no jitters, no crash mid-set.' },
  { key: 'P', label: 'Pump', desc: 'Arginine HCl + L-Citrulline push blood flow and vascularity through your hardest sessions.' },
  { key: 'E', label: 'Energy', desc: 'Beta-Alanine buffers fatigue while dosed caffeine keeps output high, rep after rep.' },
];

const INGREDIENTS_INFO = [
  { name: 'Beta-Alanine', dose: '1.5g', desc: 'Delays the burn by buffering lactic acid. Pushes the wall back so you squeeze out reps when your body says quit.' },
  { name: 'Arginine HCl', dose: '750mg', desc: 'Floods your muscles with nitric oxide. More blood flow, more oxygen, more pump — every set counts.' },
  { name: 'L-Citrulline', dose: '500mg', desc: 'Converts to Arginine in your kidneys for sustained blood flow. Pump that lasts long after your session ends.' },
  { name: 'L-Carnitine', dose: '250mg', desc: 'Transports fatty acids into your mitochondria for energy. Burns cleaner, supports endurance, helps maintain lean muscle.' },
  { name: 'L-Tyrosine', dose: '125mg', desc: 'Rebuilds the neurotransmitters heavy training drains. Focus stays sharp when the weights get heavy.' },
  { name: 'Encapsulated Caffeine', dose: '50mg', desc: 'Slow-release coating releases over 2-3 hours. Clean energy, no spike, no crash — you finish as strong as you started.' },
  { name: 'Coffee Bean Extract', dose: '45mg', desc: 'Natural caffeine plus chlorogenic antioxidants. Smooths the energy curve and keeps you locked in.' },
  { name: 'Garcinia Cambogia', dose: '37.5mg', desc: 'HCA supports fat metabolism and appetite management. Complements the energy blend for a leaner training experience.' },
];

const FAQS = [
  { q: 'How do I take PRIME X?', a: 'Mix 3.5g (half scoop) with 200-300ml cold water. Shake it up, drink 15-20 minutes before training. One serving per day — that\'s all you need.' },
  { q: 'Is it safe?', a: 'FSSAI certified, manufactured in a licensed facility, banned-substance free, and WADA compliant. Contains caffeine — don\'t stack it with your third espresso.' },
  { q: 'How many servings per tub?', a: '80 servings of 3.5g per 280g tub. Half a scoop is the recommended dose — one tub lasts over two months at 5 sessions a week.' },
  { q: 'Can I stack it with other supplements?', a: 'Absolutely. Pairs well with creatine, BCAAs, or whey. Just don\'t combine it with another pre-workout — the caffeine adds up.' },
  { q: 'What does it actually taste like?', a: 'Orange is bright and citrus-forward. Fruit Punch is a full mixed-fruit hit. Rocket Lollipop is sweet nostalgia. All smooth, no chalky aftertaste.' },
];

/* ────────────────────────────────────────────── */
/*  Ghost-inspired PDP Component                 */
/* ────────────────────────────────────────────── */
export default function ProductPageClient({ slug }: { slug: string }) {
  const { products, addToCart } = useShop();
  const product = products.find((p) => p.slug === slug);

  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(product?.variants[0] || null);
  const [selectedImage, setSelectedImage] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [added, setAdded] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [openAccordion, setOpenAccordion] = useState<'suggested' | 'ingredients' | 'faq' | null>('ingredients');
  const [isSubscribe, setIsSubscribe] = useState(false);
  const [subscribeFreq, setSubscribeFreq] = useState<'1 month' | '2 months' | '3 months'>('1 month');
  const [activeTab, setActiveTab] = useState<'details' | 'nutrition' | 'ingredients'>('details');
  const [stickyVisible, setStickyVisible] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const stickyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [slug]);

  const handleScroll = useCallback(() => {
    setScrolled(window.scrollY > 40);
    if (!stickyRef.current) return;
    const rect = stickyRef.current.getBoundingClientRect();
    setStickyVisible(rect.bottom < 0);
  }, []);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  if (!product || !selectedVariant) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000', color: '#fff' }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontFamily: 'var(--display)', fontSize: 42, textTransform: 'uppercase', marginBottom: 16 }}>Product Not Found</h1>
          <a href="/shop" style={{ color: 'var(--yellow)', fontWeight: 700, textDecoration: 'underline' }}>Back to Shop</a>
        </div>
      </div>
    );
  }

  const handleAddToCart = () => {
    addToCart(product, selectedVariant, quantity);
    setAdded(true);
    setTimeout(() => setAdded(false), 1800);
  };

  const otherFlavours = products.filter((p) => p.id !== product.id);
  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

  /* ── Flavour colour dots ── */
  const flavourColour: Record<string, string> = {
    Orange: '#FF6B00',
    'Fruit Punch': '#E8115A',
    'Rocket Lollipop': '#5B2EED',
  };
  const currentFlavour = selectedVariant.name;

  /* ── Tabs for Supplement Facts section ── */
  const tabs = [
    { id: 'details' as const, label: 'DETAILS' },
    { id: 'nutrition' as const, label: 'SUPPLEMENT FACTS' },
    { id: 'ingredients' as const, label: 'INGREDIENTS' },
  ];

  return (
    <div style={{ background: '#000', minHeight: '100vh', color: '#fff' }}>
      <Suspense fallback={null}>
        <BackToTop />
        <StickyCtaBar
          price={selectedVariant?.price || product.price}
          originalPrice={selectedVariant?.originalPrice || product.originalPrice}
          onAddToCart={handleAddToCart}
          added={added}
        />
      </Suspense>
      {/* ═══ NAV ═══ */}
      <header className={`nav ${scrolled ? 'scrolled' : ''}`}>
        <div className="wrap nav-inner">
          <a href="/" className="brand"><span className="brand-text">PURE</span></a>
          <nav className="nav-links">
            <a href="/">Home</a>
            <a href="/wholesale">Wholesale &amp; Retails</a>
            <a href="/contact">Contact Us</a>
            <a href="/athletes">Our Athletes</a>
          </nav>
          <div className="nav-right">
            <a href="/cart" className="nav-icon" style={{ position: 'relative' }}>
              <ShoppingBag size={20} />
            </a>
            <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ fontSize: 11, padding: '10px 20px' }}>
              Shop PRIME X
            </a>
            <button className="nav-mobile-toggle" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            className="mobile-menu"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <a href="/" onClick={() => setMobileMenuOpen(false)}>Home</a>
            <a href="/wholesale" onClick={() => setMobileMenuOpen(false)}>Wholesale &amp; Retails</a>
            <a href="/contact" onClick={() => setMobileMenuOpen(false)}>Contact Us</a>
            <a href="/athletes" onClick={() => setMobileMenuOpen(false)}>Our Athletes</a>
            <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ marginTop: 16 }}>Shop PRIME X</a>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ═══ BREADCRUMB ═══ */}
      <div className="pdp-container" style={{ maxWidth: 1200, margin: '0 auto', padding: '100px 32px 0' }}>
        <nav style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', fontFamily: 'var(--mono)', letterSpacing: '0.05em' }}>
          <a href="/" style={{ color: 'rgba(255,255,255,0.4)', textDecoration: 'none' }}>HOME</a>
          <span style={{ margin: '0 8px' }}>/</span>
          <a href="/shop" style={{ color: 'rgba(255,255,255,0.4)', textDecoration: 'none' }}>SHOP</a>
          <span style={{ margin: '0 8px' }}>/</span>
          <span style={{ color: '#fff' }}>{product.name}</span>
        </nav>
      </div>

      {/* ═══ HERO — FULL-WIDTH IMAGE CAROUSEL ═══ */}
      <div className="pdp-container" style={{ maxWidth: 1200, margin: '32px auto 0', padding: '32px 32px 0' }}>
        <div className="pdp-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 60, alignItems: 'start' }}>
          {/* LEFT — Large Gallery */}
          <div>
            {/* Main Image */}
            <div
              ref={stickyRef}
              className="pdp-gallery-main"
              style={{
                position: 'relative',
                aspectRatio: '4/5',
                background: 'var(--graphite-2)',
                borderRadius: 'var(--r-lg)',
                overflow: 'hidden',
                border: '1px solid var(--line)',
              }}
            >
              <Image
                src={product.galleryImages[selectedImage]}
                alt={product.name}
                fill
                style={{ objectFit: 'contain', padding: 40 }}
                priority
              />
              {product.isBestseller && (
                <div
                  style={{
                    position: 'absolute',
                    top: 20,
                    left: 20,
                    background: 'var(--yellow)',
                    color: '#000',
                    fontFamily: 'var(--mono)',
                    fontSize: 10,
                    fontWeight: 700,
                    padding: '6px 14px',
                    letterSpacing: '0.12em',
                    textTransform: 'uppercase',
                  }}
                >
                  BESTSELLER
                </div>
              )}
              {selectedVariant.originalPrice > selectedVariant.price && (
                <div
                  style={{
                    position: 'absolute',
                    top: 20,
                    right: 20,
                    background: '#E8115A',
                    color: '#fff',
                    fontFamily: 'var(--mono)',
                    fontSize: 10,
                    fontWeight: 700,
                    padding: '6px 14px',
                    letterSpacing: '0.12em',
                  }}
                >
                  {Math.round(((selectedVariant.originalPrice - selectedVariant.price) / selectedVariant.originalPrice) * 100)}% OFF
                </div>
              )}
            </div>

            {/* Thumbnails — horizontal scroll */}
            <div
              className="pdp-thumbnails"
              style={{
                display: 'flex',
                gap: 10,
                marginTop: 14,
                overflowX: 'auto',
                scrollbarWidth: 'none',
                paddingBottom: 4,
              }}
            >
              {product.galleryImages.map((img, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedImage(i)}
                  style={{
                    width: 80,
                    height: 80,
                    position: 'relative',
                    borderRadius: 'var(--r)',
                    overflow: 'hidden',
                    flexShrink: 0,
                    border: i === selectedImage ? '2px solid var(--yellow)' : '1px solid var(--line)',
                    background: 'var(--graphite-2)',
                    cursor: 'pointer',
                    opacity: i === selectedImage ? 1 : 0.45,
                    transition: 'all 0.2s ease',
                  }}
                >
                  <Image src={img} alt="" fill style={{ objectFit: 'contain', padding: 8 }} sizes="80px" />
                </button>
              ))}
            </div>
          </div>

          {/* RIGHT — Product Info */}
          <div style={{ position: 'sticky', top: 100 }}>
            {/* Title + Subtitle */}
            <p
              style={{
                fontFamily: 'var(--mono)',
                fontSize: 11,
                color: 'var(--yellow)',
                letterSpacing: '0.16em',
                textTransform: 'uppercase',
                marginBottom: 8,
                fontWeight: 700,
              }}
            >
              PRE-WORKOUT
            </p>
            <h1
              style={{
                fontFamily: 'var(--display)',
                fontSize: 'clamp(36px, 4vw, 52px)',
                textTransform: 'uppercase',
                lineHeight: 1.02,
                marginBottom: 4,
                letterSpacing: '-0.01em',
              }}
            >
              {product.name.split('—')[0]?.trim() || 'PRIME X'}
            </h1>
            <p
              style={{
                fontFamily: 'var(--body)',
                fontSize: 16,
                color: 'rgba(255,255,255,0.55)',
                lineHeight: 1.5,
                marginBottom: 8,
              }}
            >
              {product.tagline}
            </p>

            {/* New launch + trust indicator (no fabricated ratings — brand is newly launched) */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24 }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.1em', border: '1px solid rgba(255,209,0,0.35)', padding: '5px 12px', textTransform: 'uppercase' }}>
                New Launch
              </span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
                FSSAI Certified · Banned Substance Free
              </span>
            </div>

            {/* Price */}
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 14, marginBottom: 28 }}>
              <span style={{ fontFamily: 'var(--display)', fontSize: 42, color: '#fff', lineHeight: 1 }}>
                {fmt(selectedVariant.price)}
              </span>
              {selectedVariant.originalPrice > selectedVariant.price && (
                <>
                  <span
                    style={{
                      fontFamily: 'var(--mono)',
                      fontSize: 18,
                      color: 'rgba(255,255,255,0.3)',
                      textDecoration: 'line-through',
                    }}
                  >
                    {fmt(selectedVariant.originalPrice)}
                  </span>
                  <span
                    style={{
                      fontFamily: 'var(--mono)',
                      fontSize: 12,
                      color: '#22c55e',
                      fontWeight: 700,
                      background: 'rgba(34,197,94,0.1)',
                      padding: '4px 10px',
                      letterSpacing: '0.05em',
                    }}
                  >
                    SAVE {fmt(selectedVariant.originalPrice - selectedVariant.price)}
                  </span>
                </>
              )}
            </div>

            {/* ── FLAVOUR SELECTOR ── */}
            <div style={{ marginBottom: 28 }}>
              <label
                style={{
                  fontFamily: 'var(--mono)',
                  fontSize: 11,
                  color: 'rgba(255,255,255,0.5)',
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  display: 'block',
                  marginBottom: 12,
                }}
              >
                FLAVOUR — <span style={{ color: '#fff', fontWeight: 700 }}>{currentFlavour}</span>
              </label>
              <div style={{ display: 'flex', gap: 10 }}>
                {product.variants.map((v) => {
                  const isActive = selectedVariant.id === v.id;
                  const dot = flavourColour[v.name] || '#888';
                  return (
                    <button
                      key={v.id}
                      onClick={() => setSelectedVariant(v)}
                      title={v.name}
                      style={{
                        width: 48,
                        height: 48,
                        borderRadius: '50%',
                        background: dot,
                        border: isActive ? '3px solid #fff' : '3px solid transparent',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        boxShadow: isActive ? `0 0 0 2px var(--yellow)` : 'none',
                        position: 'relative',
                        flexShrink: 0,
                      }}
                    >
                      {isActive && (
                        <span
                          style={{
                            position: 'absolute',
                            inset: 0,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 16,
                            color: '#fff',
                            fontWeight: 700,
                            textShadow: '0 1px 3px rgba(0,0,0,0.5)',
                          }}
                        >
                          ✓
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* ── SIZE / FORMAT SELECTOR ── */}
            <div style={{ marginBottom: 28 }}>
              <label
                style={{
                  fontFamily: 'var(--mono)',
                  fontSize: 11,
                  color: 'rgba(255,255,255,0.5)',
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  display: 'block',
                  marginBottom: 12,
                }}
              >
                SIZE
              </label>
              <div style={{ display: 'flex', gap: 10 }}>
                {product.variants.map((v) => {
                  const isActive = selectedVariant.id === v.id;
                  return (
                    <button
                      key={v.id}
                      onClick={() => setSelectedVariant(v)}
                      style={{
                        flex: 1,
                        padding: '16px 8px',
                        textAlign: 'center',
                        background: isActive ? 'rgba(255,209,0,0.08)' : 'rgba(255,255,255,0.03)',
                        border: isActive ? '1.5px solid var(--yellow)' : '1.5px solid rgba(255,255,255,0.08)',
                        color: isActive ? 'var(--yellow)' : 'rgba(255,255,255,0.5)',
                        fontFamily: 'var(--mono)',
                        fontSize: 13,
                        fontWeight: 700,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        letterSpacing: '0.04em',
                      }}
                    >
                      {v.weight}
                      <div style={{ fontSize: 11, marginTop: 4, opacity: 0.55, fontWeight: 400 }}>
                        {v.name}
                      </div>
                      <div style={{ fontSize: 12, marginTop: 4, color: isActive ? '#fff' : 'rgba(255,255,255,0.35)' }}>
                        {fmt(v.price)}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* ── SUBSCRIBE & SAVE ── */}
            <div
              style={{
                marginBottom: 24,
                padding: '18px 20px',
                background: 'rgba(255,209,0,0.04)',
                border: '1px solid rgba(255,209,0,0.12)',
                borderRadius: 'var(--r)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: isSubscribe ? 14 : 0 }}>
                <div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 14, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    SUBSCRIBE & SAVE
                  </div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.45)', marginTop: 2 }}>
                    Never run out — auto-delivered to your door
                  </div>
                </div>
                {/* Toggle */}
                <button
                  onClick={() => setIsSubscribe(!isSubscribe)}
                  style={{
                    width: 48,
                    height: 26,
                    borderRadius: 13,
                    background: isSubscribe ? 'var(--yellow)' : 'rgba(255,255,255,0.12)',
                    border: 'none',
                    cursor: 'pointer',
                    position: 'relative',
                    transition: 'background 0.2s ease',
                    flexShrink: 0,
                  }}
                >
                  <span
                    style={{
                      position: 'absolute',
                      top: 3,
                      left: isSubscribe ? 25 : 3,
                      width: 20,
                      height: 20,
                      borderRadius: '50%',
                      background: isSubscribe ? '#000' : '#fff',
                      transition: 'left 0.2s ease',
                    }}
                  />
                </button>
              </div>
              {isSubscribe && (
                <div style={{ display: 'flex', gap: 8 }}>
                  {(['1 month', '2 months', '3 months'] as const).map((f) => (
                    <button
                      key={f}
                      onClick={() => setSubscribeFreq(f)}
                      style={{
                        flex: 1,
                        padding: '10px 6px',
                        background: subscribeFreq === f ? 'var(--yellow)' : 'transparent',
                        color: subscribeFreq === f ? '#000' : 'rgba(255,255,255,0.5)',
                        border: subscribeFreq === f ? '1px solid var(--yellow)' : '1px solid rgba(255,255,255,0.1)',
                        fontFamily: 'var(--mono)',
                        fontSize: 11,
                        fontWeight: 700,
                        cursor: 'pointer',
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em',
                        transition: 'all 0.2s ease',
                      }}
                    >
                      Every {f}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* ── QUANTITY + ADD TO CART ── */}
            <div style={{ display: 'flex', gap: 12, marginBottom: 14 }}>
              <div
                style={{
                  display: 'flex',
                  border: '1.5px solid var(--line)',
                  borderRadius: 'var(--r-button)',
                  overflow: 'hidden',
                }}
              >
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  style={{ width: 52, minHeight: 52, background: 'transparent', border: 'none', color: '#fff', fontSize: 22, cursor: 'pointer' }}
                >
                  −
                </button>
                <span
                  style={{
                    width: 52,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'var(--mono)',
                    fontSize: 16,
                    fontWeight: 700,
                    borderLeft: '1px solid rgba(255,255,255,0.08)',
                    borderRight: '1px solid rgba(255,255,255,0.08)',
                  }}
                >
                  {quantity}
                </span>
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  style={{ width: 52, minHeight: 52, background: 'transparent', border: 'none', color: '#fff', fontSize: 22, cursor: 'pointer' }}
                >
                  +
                </button>
              </div>

              <motion.button
                onClick={handleAddToCart}
                whileTap={{ scale: 0.96 }}
                transition={{ duration: 0.15 }}
                style={{
                  flex: 1,
                  padding: '18px 24px',
                  background: added ? '#22c55e' : 'var(--yellow)',
                  color: added ? '#fff' : '#000',
                  fontFamily: 'var(--display)',
                  fontSize: 17,
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  border: 'none',
                  cursor: 'pointer',
                  borderRadius: 'var(--r-button)',
                  transition: 'background 0.25s ease, color 0.25s ease',
                  fontWeight: 700,
                  minHeight: 52,
                }}
              >
                {added ? '✓ ADDED TO CART' : isSubscribe ? 'SUBSCRIBE NOW' : 'ADD TO CART'}
              </motion.button>
            </div>

            {/* Buy Now */}
            <a
              href={PARTNER_URL}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                padding: '16px 24px',
                textAlign: 'center',
                border: '1.5px solid rgba(255,255,255,0.2)',
                background: 'transparent',
                color: '#fff',
                fontFamily: 'var(--display)',
                fontSize: 14,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                textDecoration: 'none',
                marginBottom: 28,
                borderRadius: 'var(--r-button)',
                transition: 'all 0.25s ease',
                minHeight: 52,
              }}
            >
              BUY NOW ON PURE SUPPS
            </a>

            {/* ── TRUST BADGES ── */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: 12,
                paddingTop: 24,
                borderTop: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              {[
                { icon: '🛡️', label: 'FSSAI\nCertified' },
                { icon: '✓', label: 'Banned Substance\nFree' },
                { icon: '🇮🇳', label: 'Made in\nIndia' },
              ].map((b) => (
                <div
                  key={b.label}
                  style={{
                    padding: '14px 10px',
                    background: 'var(--graphite-2)',
                    border: '1px solid var(--line)',
                    textAlign: 'center',
                    borderRadius: 'var(--r)',
                  }}
                >
                  <div style={{ fontSize: 22, marginBottom: 6 }}>{b.icon}</div>
                  <div
                    style={{
                      fontFamily: 'var(--mono)',
                      fontSize: 9,
                      color: 'rgba(255,255,255,0.45)',
                      letterSpacing: '0.06em',
                      lineHeight: 1.5,
                      whiteSpace: 'pre-line',
                      textTransform: 'uppercase',
                    }}
                  >
                    {b.label}
                  </div>
                </div>
              ))}
            </div>

            {/* ── KEY BENEFITS ── */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 24 }}>
              {[
                { label: '80 SERVINGS', sub: 'Per 280g Tub' },
                { label: 'HALF SCOOP', sub: '3.5g Is All You Need' },
                { label: 'ZERO CRASH', sub: 'Slow-Release Caffeine' },
                { label: 'CLINICAL DOSES', sub: 'Every Ingredient, Fully Dosed' },
              ].map((b) => (
                <div
                  key={b.label}
                  style={{
                    padding: '14px 16px',
                    background: 'var(--graphite-2)',
                    border: '1px solid var(--line)',
                    borderRadius: 'var(--r)',
                  }}
                >
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.08em' }}>{b.label}</div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 4 }}>{b.sub}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ═══ BENEFITS — FOCUS / PUMP / ENERGY (scannable, visual) ═══ */}
      <div className="pdp-container" style={{ maxWidth: 1200, margin: '56px auto 0', padding: '0 32px' }}>
        <div className="pdp-benefits-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
          {BENEFITS.map((b) => (
            <div
              key={b.key}
                style={{
                  padding: '26px 22px',
                  background: 'var(--graphite-2)',
                  border: '1px solid var(--line)',
                  borderRadius: 'var(--r)',
                }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  border: '1.5px solid var(--yellow)',
                  transform: 'rotate(45deg)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: 16,
                }}
              >
                <span style={{ transform: 'rotate(-45deg)', fontFamily: 'var(--display)', color: 'var(--yellow)', fontSize: 16 }}>{b.key}</span>
              </div>
              <div style={{ fontFamily: 'var(--display)', fontSize: 19, textTransform: 'uppercase', marginBottom: 8, letterSpacing: '0.01em' }}>{b.label}</div>
              <div style={{ fontSize: 13.5, lineHeight: 1.6, color: 'rgba(255,255,255,0.55)' }}>{b.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ═══ SUPPLEMENT FACTS — TABS ═══ */}
      <div className="pdp-container" style={{ maxWidth: 1200, margin: '60px auto 0', padding: '0 32px' }}>
        {/* Tab bar */}
        <div className="pdp-tabs" style={{ display: 'flex', borderBottom: '1px solid rgba(255,255,255,0.08)', marginBottom: 32, overflowX: 'auto', scrollbarWidth: 'none' }}>
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              style={{
                padding: '16px 28px',
                background: 'transparent',
                border: 'none',
                borderBottom: activeTab === t.id ? '2px solid var(--yellow)' : '2px solid transparent',
                color: activeTab === t.id ? '#fff' : 'rgba(255,255,255,0.35)',
                fontFamily: 'var(--display)',
                fontSize: 15,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                whiteSpace: 'nowrap',
                minHeight: 48,
                flexShrink: 0,
              }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {activeTab === 'details' && (
          <div style={{ maxWidth: 800 }}>
            <h3 style={{ fontFamily: 'var(--display)', fontSize: 24, textTransform: 'uppercase', marginBottom: 16 }}>
              PRODUCT <span style={{ color: 'var(--yellow)' }}>DETAILS</span>
            </h3>
            <p style={{ fontSize: 15, lineHeight: 1.8, color: 'rgba(255,255,255,0.6)', marginBottom: 20 }}>
              {product.description}
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 24 }}>
              <div style={{ padding: '18px 20px', background: 'var(--graphite-2)', border: '1px solid var(--line)', borderRadius: 'var(--r)' }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--yellow)', letterSpacing: '0.12em', marginBottom: 6 }}>SUGGESTED USE</div>
                <div style={{ fontSize: 13, lineHeight: 1.6, color: 'rgba(255,255,255,0.55)' }}>
                  Mix 3.5g (half scoop) with 200-300ml cold water. Consume 15-20 minutes before your workout. Do not exceed 1 serving per day.
                </div>
              </div>
              <div style={{ padding: '18px 20px', background: 'var(--graphite-2)', border: '1px solid var(--line)', borderRadius: 'var(--r)' }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--yellow)', letterSpacing: '0.12em', marginBottom: 6 }}>WARNINGS</div>
                <div style={{ fontSize: 13, lineHeight: 1.6, color: 'rgba(255,255,255,0.55)' }}>
                  For healthy adults 18+. Do not use if pregnant or nursing. Contains caffeine — avoid combining with other caffeinated products.
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'nutrition' && (
          <div style={{ maxWidth: 800 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
              {INGREDIENTS_INFO.map((ing) => (
                <div
                  key={ing.name}
                  style={{
                    padding: '22px 18px',
                    background: 'var(--graphite-2)',
                    border: '1px solid var(--line)',
                    borderRadius: 'var(--r)',
                    transition: 'all 0.3s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'rgba(255,209,0,0.25)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'rgba(255,209,0,0.08)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 28, fontWeight: 700, color: '#fff', lineHeight: 1 }}>
                    {ing.dose.replace(/[^0-9.]/g, '')}
                    <span style={{ fontSize: 13, color: 'var(--yellow)', marginLeft: 3 }}>{ing.dose.replace(/[0-9.]/g, '')}</span>
                  </div>
                  <div
                    style={{
                      fontFamily: 'var(--mono)',
                      fontSize: 10,
                      color: 'rgba(255,255,255,0.4)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em',
                      marginTop: 8,
                    }}
                  >
                    {ing.name}
                  </div>
                </div>
              ))}
            </div>
            <div
              style={{
                marginTop: 20,
                padding: '18px 22px',
                background: 'rgba(255,209,0,0.04)',
                border: '1px solid rgba(255,209,0,0.1)',
                fontSize: 13,
                color: 'rgba(255,255,255,0.5)',
                lineHeight: 1.7,
                borderRadius: 8,
              }}
            >
              <strong style={{ color: 'var(--yellow)' }}>Power Performance Nutrients Blend</strong> — Every ingredient, every dose, printed on the tub. No proprietary blends, no pixie-dusted token amounts. Third-party tested, FSSAI compliant, banned-substance free.
            </div>
          </div>
        )}

        {activeTab === 'ingredients' && (
          <div style={{ maxWidth: 800 }}>
            <h3 style={{ fontFamily: 'var(--display)', fontSize: 24, textTransform: 'uppercase', marginBottom: 16 }}>
              FULL <span style={{ color: 'var(--yellow)' }}>INGREDIENTS</span> LIST
            </h3>
            <p style={{ fontSize: 14, lineHeight: 1.8, color: 'rgba(255,255,255,0.55)', marginBottom: 24 }}>
              {product.ingredients}
            </p>
            <div
              style={{
                padding: '16px 20px',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid rgba(255,255,255,0.05)',
                fontSize: 12,
                color: 'rgba(255,255,255,0.35)',
                lineHeight: 1.7,
              }}
            >
              Allergen: Milk · Soy · Nuts · Barley. FSSAI Licence No. 10824999000028
            </div>
          </div>
        )}
      </div>

      {/* ═══ FAQ — ACCORDION ═══ */}
      <div className="pdp-container" style={{ maxWidth: 800, margin: '60px auto 0', padding: '0 32px' }}>
        <h2 style={{ fontFamily: 'var(--display)', fontSize: 28, textTransform: 'uppercase', marginBottom: 28 }}>
          FREQUENTLY ASKED <span style={{ color: 'var(--yellow)' }}>QUESTIONS</span>
        </h2>
        <div>
          {FAQS.map((faq, i) => (
            <div key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <button
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
                style={{
                  width: '100%',
                  padding: '20px 0',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: 'transparent',
                  border: 'none',
                  color: 'rgba(255,255,255,0.85)',
                  cursor: 'pointer',
                  fontFamily: 'var(--body)',
                  fontSize: 15,
                  fontWeight: 600,
                  textAlign: 'left',
                  minHeight: 56,
                }}
              >
                {faq.q}
                <span
                  style={{
                    fontSize: 22,
                    color: 'var(--yellow)',
                    flexShrink: 0,
                    marginLeft: 20,
                    transition: 'transform 0.3s',
                    transform: openFaq === i ? 'rotate(45deg)' : 'rotate(0)',
                  }}
                >
                  +
                </span>
              </button>
              <AnimatePresence initial={false}>
                {openFaq === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: [0.23, 1, 0.32, 1] }}
                    style={{ overflow: 'hidden' }}
                  >
                    <p style={{ paddingBottom: 20, fontSize: 14, lineHeight: 1.75, color: 'rgba(255,255,255,0.5)' }}>{faq.a}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </div>

      {/* ═══ STACKS WELL WITH — CROSS-SELL ═══ */}
      {otherFlavours.length > 0 && (
        <div className="pdp-container" style={{ maxWidth: 1200, margin: '70px auto 0', padding: '0 32px' }}>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 3.5vw, 40px)', textTransform: 'uppercase', marginBottom: 8 }}>
            STACKS WELL <span style={{ color: 'var(--yellow)' }}>WITH</span>
          </h2>
          <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.4)', marginBottom: 32 }}>
            Same formula, different flavour. Try the full range.
          </p>
          <div className="pdp-cross-sell" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
            {otherFlavours.map((p) => (
              <a
                key={p.id}
                href={`/product/${p.slug}`}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 24,
                  alignItems: 'center',
                  padding: 28,
                  background: 'var(--graphite-2)',
                  border: '1px solid var(--line)',
                  textDecoration: 'none',
                  color: '#fff',
                  transition: 'all 0.3s ease',
                  borderRadius: 'var(--r)',
                  minHeight: 120,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255,209,0,0.2)';
                  e.currentTarget.style.background = 'rgba(255,209,0,0.04)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)';
                  e.currentTarget.style.background = 'rgba(255,255,255,0.025)';
                }}
              >
                <div style={{ position: 'relative', aspectRatio: '1/1' }}>
                  <Image src={p.image} alt={p.name} fill style={{ objectFit: 'contain', padding: 16 }} />
                </div>
                <div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 18, textTransform: 'uppercase', marginBottom: 6 }}>
                    {p.name.split('—')[1]?.trim() || p.name}
                  </div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.08em' }}>
                    80 SERVINGS · 280G
                  </div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 24, color: 'var(--yellow)', marginTop: 10 }}>
                    {fmt(p.price)}
                  </div>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* ═══ STICKY ADD-TO-CART BAR (MOBILE) ═══ */}
      <div
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          background: 'rgba(0,0,0,0.95)',
          backdropFilter: 'blur(16px)',
          borderTop: '1px solid var(--line)',
          padding: '14px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          zIndex: 900,
          transform: stickyVisible ? 'translateY(0)' : 'translateY(100%)',
          transition: 'transform 0.3s ease',
        }}
      >
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: 'var(--display)', fontSize: 16, textTransform: 'uppercase' }}>PRIME X</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 14, color: 'var(--yellow)', fontWeight: 700 }}>
            {fmt(selectedVariant.price)}
          </div>
        </div>
        <button
          onClick={handleAddToCart}
          style={{
            padding: '14px 32px',
            background: added ? '#22c55e' : 'var(--yellow)',
            color: added ? '#fff' : '#000',
            fontFamily: 'var(--display)',
            fontSize: 15,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
            border: 'none',
            cursor: 'pointer',
            borderRadius: 'var(--r-button)',
            fontWeight: 700,
            transition: 'all 0.25s ease',
          }}
        >
          {added ? '✓ ADDED' : 'ADD TO CART'}
        </button>
      </div>

      {/* ═══ RESPONSIVE ═══ */}
      <style>{`
        @media(max-width:900px) {
          .pdp-grid {
            grid-template-columns: 1fr !important;
            gap: 32px !important;
          }
          .pdp-grid > div:last-child {
            position: static !important;
          }
          .pdp-benefits-grid {
            grid-template-columns: 1fr !important;
            gap: 12px !important;
          }
        }
        @media(max-width:600px) {
          .pdp-container {
            padding-left: 18px !important;
            padding-right: 18px !important;
          }
          .pdp-gallery-main {
            aspect-ratio: 1/1 !important;
            border-radius: 12px !important;
          }
          .pdp-gallery-main > div {
            padding: 24px !important;
          }
          .pdp-thumbnails {
            gap: 8px !important;
          }
          .pdp-thumbnails button {
            width: 64px !important;
            height: 64px !important;
          }
          .pdp-cross-sell {
            grid-template-columns: 1fr !important;
          }
          .pdp-tabs {
            gap: 0 !important;
          }
        }
      `}</style>
      <CartDrawer />
    </div>
  );
}
