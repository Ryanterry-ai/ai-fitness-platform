'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { ChevronRight, ShoppingBag, Menu, X } from 'lucide-react';
import Image from '@/components/Image';
import { useShop, Product } from '@/lib/store';
import { motion, AnimatePresence } from 'framer-motion';
import CartDrawer from '@/components/CartDrawer';
import BackToTop from '@/components/BackToTop';
import { PARTNER_URL } from '@/components/AnnouncementBar';
import { purchaseProduct } from '@/lib/purchase';

const EASE = [0.23, 1, 0.32, 1] as const;

const FLAVOUR_TABS = [
  { key: 'all', label: 'All Flavours' },
  { key: 'Orange', label: 'Orange', color: '#FF6B00' },
  { key: 'Fruit Punch', label: 'Fruit Punch', color: '#E8115A' },
  { key: 'Rocket Lollipop', label: 'Rocket Lollipop', color: '#5B2EED' },
];

export default function ShopPage() {
  const { products, addToCart } = useShop();
  const [flavour, setFlavour] = useState('all');
  const [addedId, setAddedId] = useState<string | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const filtered = useMemo(() => {
    if (flavour === 'all') return products;
    return products.filter(p => p.flavour === flavour);
  }, [products, flavour]);

  const handleAdd = async (product: Product) => {
    await purchaseProduct(product.slug, { showLoading: true });
  };

  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

  return (
    <div style={{ background: '#000', minHeight: '100vh' }}>
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
            <button
              onClick={() => purchaseProduct('default', { showLoading: true })}
              className="btn-pure"
              style={{ fontSize: 11, padding: '10px 20px' }}
            >
              Shop PRIME X
            </button>
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
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                purchaseProduct('default', { showLoading: true });
              }}
              className="btn-pure"
              style={{ marginTop: 16, width: '100%', justifyContent: 'center' }}
            >
              Shop PRIME X
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ═══ HEADER ═══ */}
      <div className="shop-header">
        <div className="wrap">
          <motion.span
            className="eyebrow"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: EASE }}
            style={{ marginBottom: 12, display: 'block' }}
          >
            PRIME X Pre-Workout
          </motion.span>
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1, ease: EASE }}
          >
            Shop <span style={{ color: 'var(--yellow)' }}>PURE</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease: EASE }}
          >
            Three flavours. Zero compromise. Every ingredient and dose printed on the tub.
          </motion.p>
          {/* Trust Badges */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3, ease: EASE }}
            style={{ display: 'flex', gap: 24, justifyContent: 'center', marginTop: 24, flexWrap: 'wrap' }}
          >
            {[
              { text: 'FSSAI Licensed' },
              { text: '8 Ingredients' },
              { text: 'Zero Fillers' },
              { text: 'Free Shipping ₹999+' }
            ].map((badge, i) => (
              <div
                key={i}
                style={{
                  fontFamily: 'var(--mono)',
                  fontSize: 11,
                  color: 'rgba(255, 255, 255, 0.6)',
                  letterSpacing: '0.05em',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6
                }}
              >
                <span style={{ color: 'var(--yellow)' }}>✓</span>
                {badge.text}
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      <div className="wrap" style={{ paddingBottom: 100 }}>
        {/* ═══ FLAVOUR FILTER TABS ═══ */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 48, flexWrap: 'wrap' }}>
          {FLAVOUR_TABS.map((tab) => (
            <motion.button
              key={tab.key}
              onClick={() => setFlavour(tab.key)}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              style={{
                padding: '12px 24px',
                borderRadius: 999,
                fontFamily: 'var(--mono)',
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                cursor: 'pointer',
                transition: 'all 0.3s var(--ease-out)',
                background: flavour === tab.key ? (tab.color || 'var(--yellow)') : 'transparent',
                color: flavour === tab.key ? (tab.key === 'all' ? '#000' : '#fff') : 'rgba(255,255,255,0.45)',
                border: flavour === tab.key
                  ? `1.5px solid ${tab.color || 'var(--yellow)'}`
                  : '1.5px solid rgba(255,255,255,0.1)',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                minHeight: 44,
              }}
            >
              {tab.color && (
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: tab.color, flexShrink: 0 }} />
              )}
              {tab.label}
            </motion.button>
          ))}
        </div>

        {/* ═══ PRODUCT GRID ═══ */}
        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <h3 style={{ fontFamily: 'var(--heading)', fontSize: 22, textTransform: 'uppercase', marginBottom: 8 }}>No products found</h3>
            <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.4)' }}>Try selecting a different flavour.</p>
          </div>
        ) : (
          <div className="product-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
            {filtered.map((product, i) => {
              const discount = product.originalPrice > product.price
                ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
                : 0;

              return (
                <motion.div
                  key={product.id}
                  className="p-card"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: i * 0.1, ease: EASE }}
                  whileHover={{ y: -8 }}
                >
                  <a href={`/product/${product.slug}`} style={{ textDecoration: 'none', color: 'inherit', display: 'flex', flexDirection: 'column', flex: 1 }}>
                    <div className="p-flavor-tag">{product.flavour}</div>
                    <div className="p-canvas-wrap">
                      <Image
                        src={product.image}
                        alt={product.name}
                        width={260}
                        height={260}
                        style={{ objectFit: 'contain', maxHeight: 240, width: 'auto' }}
                        loading="lazy"
                      />
                      {discount > 0 && (
                        <span style={{
                          position: 'absolute', top: 16, right: 16,
                          fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700,
                          color: '#000', background: 'var(--yellow)',
                          padding: '4px 10px', letterSpacing: '0.08em',
                        }}>
                          {discount}% OFF
                        </span>
                      )}
                      {product.isBestseller && (
                        <span style={{
                          position: 'absolute', top: 16, left: 16,
                          fontFamily: 'var(--mono)', fontSize: 9, fontWeight: 700,
                          color: '#000', background: 'var(--yellow)',
                          padding: '4px 10px', letterSpacing: '0.1em', textTransform: 'uppercase',
                        }}>
                          Bestseller
                        </span>
                      )}
                    </div>
                    <h3>{product.name.split('—')[0]?.trim() || product.name}</h3>
                    <p className="p-desc">{product.description}</p>
                  </a>
                  <div className="p-meta">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="servings">80 SERVINGS</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                      <span style={{ fontFamily: 'var(--heading)', fontSize: 18, color: 'var(--yellow)' }}>{fmt(product.price)}</span>
                      {discount > 0 && (
                        <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'rgba(255,255,255,0.3)', textDecoration: 'line-through' }}>{fmt(product.originalPrice)}</span>
                      )}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, padding: '0 20px 20px' }}>
                    <a href={`/product/${product.slug}`} className="btn btn-ghost btn-sm" style={{ flex: 1, justifyContent: 'center' }}>
                      View Details <ChevronRight size={14} />
                    </a>
                    <motion.button
                      onClick={(e) => { e.stopPropagation(); handleAdd(product); }}
                      className="btn btn-yellow btn-sm"
                      style={{ flex: 1 }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Buy Now
                    </motion.button>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* ═══ BOTTOM CTA ═══ */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: EASE }}
          style={{ textAlign: 'center', marginTop: 64 }}
        >
          <p style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'rgba(255,255,255,0.3)', letterSpacing: '0.08em', marginBottom: 12 }}>
            EVERY INGREDIENT. EVERY DOSE. ZERO COMPROMISE.
          </p>
          <div style={{ width: 60, height: 2, background: 'var(--yellow)', margin: '0 auto' }} />
        </motion.div>
      </div>

      {/* ═══ FOOTER ═══ */}
      <footer>
        <div className="wrap">
          <div className="foot-grid">
            <div>
              <div className="foot-brand"><span className="brand-text" style={{ fontSize: 28 }}>PURE</span></div>
              <p style={{ maxWidth: 240, color: 'rgba(255,255,255,0.5)', fontSize: 13, lineHeight: 1.7, marginTop: 12 }}>India's high-performance pre-workout. Transparent dosing, clinically backed formulas.</p>
            </div>
            <div className="foot-col">
              <h5>Shop</h5>
              <a href="/product/primex-preworkout-orange">PRIME X Orange</a>
              <a href="/product/primex-preworkout-fruit-punch">PRIME X Fruit Punch</a>
              <a href="/product/primex-preworkout-rocket-lollipop">PRIME X Rocket Lollipop</a>
              <a href="/stack-save">Trainer's Tray Bundle</a>
            </div>
            <div className="foot-col">
              <h5>Company</h5>
              <a href="/why-pure">Why PURE</a>
              <a href="/wholesale">Wholesale</a>
              <a href="/athletes">Our Athletes</a>
              <a href="/about">About Us</a>
            </div>
            <div className="foot-col">
              <h5>Contact</h5>
              <a href="https://www.upgraded.co.in" target="_blank" rel="noopener noreferrer">Upgraded Health Store</a>
              <a href="mailto:puresupps.site@gmail.com">puresupps.site@gmail.com</a>
              <a href="tel:+919557513017">+91 95575 13017</a>
              <a href="https://instagram.com/puresupps.site" target="_blank" rel="noopener noreferrer">@puresupps.site</a>
            </div>
          </div>
          <div className="foot-bottom">
            <span>© 2026 PURE HEALTH SUPPS®. FSSAI Lic. No. 10824999000028.</span>
            <div className="foot-social">
              <a href="https://instagram.com/puresupps.site" target="_blank" rel="noopener noreferrer" aria-label="Instagram">IG</a>
            </div>
          </div>
        </div>
      </footer>

      <CartDrawer />
      <BackToTop />
    </div>
  );
}
