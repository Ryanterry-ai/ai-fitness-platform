'use client';

import React, { useState, useMemo, Suspense } from 'react';
import { Zap, Star, ChevronRight } from 'lucide-react';
import Image from '@/components/Image';
import { useShop, Product } from '@/lib/store';
import { motion } from 'framer-motion';
const BackToTop = React.lazy(() => import('../../components/BackToTop'));

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

  const filtered = useMemo(() => {
    if (flavour === 'all') return products;
    return products.filter(p => p.flavour === flavour);
  }, [products, flavour]);

  const handleAdd = (product: Product) => {
    const variant = product.variants[0];
    addToCart(product, variant, 1);
    setAddedId(product.id);
    setTimeout(() => setAddedId(null), 1500);
  };

  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

  return (
    <>
      <Suspense fallback={null}>
        <BackToTop />
      </Suspense>
      {/* ═══ NAV ═══ */}
      <header className="nav">
        <div className="wrap nav-inner">
          <a href="/" className="brand">
            <span className="brand-text">PURE</span>
          </a>
          <nav className="nav-links">
            <a href="/shop" style={{ color: 'var(--paper)' }}>Shop</a>
            <a href="/formula">Formula</a>
            <a href="/why-pure">Why PURE</a>
            <a href="/stack-save">Stack &amp; Save</a>
            <a href="/journal">Journal</a>
          </nav>
          <div className="nav-right">
            <a href="/cart" className="nav-icon" style={{ position: 'relative' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/>
              </svg>
            </a>
          </div>
        </div>
      </header>

      <div className="shop-header">
        <div className="wrap">
          <span className="eyebrow">PRIME X Pre-Workout</span>
          <h1>Shop <span style={{ color: 'var(--yellow)' }}>PURE</span></h1>
          <p>Three flavours. Zero compromise. Every ingredient and dose printed on the tub.</p>
        </div>
      </div>

      <div className="wrap" style={{ paddingBottom: 100 }}>
        {/* ═══ FLAVOUR FILTER TABS ═══ */}
        <div className="flavour-tabs-scroll" style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 40, flexWrap: 'wrap' }}>
          {FLAVOUR_TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setFlavour(tab.key)}
              style={{
                padding: '10px 20px',
                borderRadius: 999,
                fontFamily: 'var(--mono)',
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                background: flavour === tab.key ? (tab.color || 'var(--yellow)') : 'transparent',
                color: flavour === tab.key ? (tab.key === 'all' ? '#000' : '#fff') : 'rgba(255,255,255,0.45)',
                border: flavour === tab.key
                  ? `1.5px solid ${tab.color || 'var(--yellow)'}`
                  : '1.5px solid rgba(255,255,255,0.1)',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                minHeight: 44,
              }}
            >
              {tab.color && (
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: tab.color, flexShrink: 0 }} />
              )}
              {tab.label}
            </button>
          ))}
        </div>

        {/* ═══ PRODUCT GRID ═══ */}
        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <h3 style={{ fontFamily: 'var(--heading)', fontWeight: 700, fontSize: 22, textTransform: 'uppercase', marginBottom: 8 }}>No products found</h3>
            <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.4)' }}>Try selecting a different flavour.</p>
          </div>
        ) : (
          <div className="product-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
            {filtered.map((product) => {
              const discount = product.originalPrice > product.price
                ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
                : 0;

              return (
                <motion.div
                  key={product.id}
                  className="p-card"
                  whileHover={{ y: -4 }}
                  style={{ display: 'flex', flexDirection: 'column' }}
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
                    </div>
                    <h3>{product.name.split('—')[0]?.trim() || product.name}</h3>
                    <p className="p-desc">{product.description}</p>
                  </a>
                  <div className="p-meta">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span className="servings">80 SERVINGS</span>
                      {discount > 0 && (
                        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, color: 'var(--yellow)', background: 'rgba(255,209,0,0.1)', padding: '2px 8px', borderRadius: 999 }}>
                          {discount}% OFF
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontFamily: 'var(--heading)', fontWeight: 700, fontSize: 18, color: 'var(--yellow)' }}>{fmt(product.price)}</span>
                      {discount > 0 && (
                        <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'rgba(255,255,255,0.3)', textDecoration: 'line-through' }}>{fmt(product.originalPrice)}</span>
                      )}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
                    <a href={`/product/${product.slug}`} className="btn btn-ghost btn-sm" style={{ flex: 1, justifyContent: 'center' }}>
                      View <ChevronRight size={14} />
                    </a>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleAdd(product); }}
                      className="btn btn-yellow btn-sm"
                      style={{ flex: 1 }}
                    >
                      {addedId === product.id ? '✓ Added' : 'Add to Cart'}
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* ═══ BOTTOM CTA ═══ */}
        <div style={{ textAlign: 'center', marginTop: 64 }}>
          <p style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'rgba(255,255,255,0.3)', letterSpacing: '0.08em', marginBottom: 12 }}>
            EVERY INGREDIENT. EVERY DOSE. ZERO COMPROMISE.
          </p>
          <div style={{ width: 60, height: 2, background: 'var(--yellow)', margin: '0 auto' }} />
        </div>
      </div>

      {/* ═══ FOOTER ═══ */}
      <footer>
        <div className="wrap">
          <div className="foot-grid">
            <div>
              <div className="foot-brand"><span className="brand-text" style={{ fontSize: 24 }}>PURE</span></div>
              <p style={{ maxWidth: 240, color: 'rgba(255,255,255,0.5)', fontSize: 13, lineHeight: 1.7 }}>India&apos;s high-performance pre-workout. Transparent dosing, clinically backed formulas.</p>
            </div>
            <div className="foot-col">
              <h5>Shop</h5>
              <a href="/product/primex-preworkout-orange">PRIME X Orange</a>
              <a href="/product/primex-preworkout-rocket-lollipop">PRIME X Rocket Lollipop</a>
              <a href="/product/primex-preworkout-fruit-punch">PRIME X Fruit Punch</a>
            </div>
            <div className="foot-col">
              <h5>Company</h5>
              <a href="/why-pure">Why PURE</a>
              <a href="/formula">The Formula</a>
              <a href="/journal">Journal</a>
            </div>
            <div className="foot-col">
              <h5>Contact</h5>
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

      <style>{`
        @media(max-width: 900px) {
          .product-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 12px !important; }
        }
        @media(max-width: 480px) {
          .product-grid { grid-template-columns: 1fr !important; gap: 16px !important; }
        }
      `}</style>
    </>
  );
}
