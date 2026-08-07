'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Menu, X } from 'lucide-react';
import Image from '@/components/Image';
import { PARTNER_URL } from '@/components/AnnouncementBar';
import { useShop } from '@/lib/store';
import CartDrawer from '../../components/CartDrawer';
const BackToTop = React.lazy(() => import('../../components/BackToTop'));

const BUNDLE_TIERS = [
  {
    id: 'single',
    label: 'Single Tub',
    servings: '80 Servings',
    weight: '280g',
    price: 1299,
    originalPrice: 1599,
    saving: 300,
    perServing: '₹16.24',
    popular: false,
    images: ['/products/Orange.png'],
  },
  {
    id: 'trainer-tray',
    label: "Trainer's Tray",
    servings: '240 Servings',
    weight: '3 × 280g',
    price: 3499,
    originalPrice: 4797,
    saving: 1298,
    perServing: '₹14.58',
    popular: true,
    images: ['/products/Orange.png', '/products/Fruit Punch.png', '/products/Rocket Lolli pop.png'],
  },
  {
    id: 'duo',
    label: 'Duo Pack',
    servings: '160 Servings',
    weight: '2 × 280g',
    price: 2399,
    originalPrice: 3198,
    saving: 799,
    perServing: '₹14.99',
    popular: false,
    images: ['/products/Fruit Punch.png', '/products/Rocket Lolli pop.png'],
  },
];

const BENEFITS = [
  { icon: '📦', title: 'Never Run Out', desc: 'One order covers 2+ months of training. No scrambling for a reorder mid-cycle.' },
  { icon: '💰', title: 'Save More', desc: 'Bundle pricing drops your cost per serving by up to 10%. The more you stack, the less you pay.' },
  { icon: '🚚', title: 'Free Shipping', desc: 'All bundles ship free across India. No hidden fees, no checkout surprises.' },
  { icon: '🔄', title: 'Mix & Match', desc: 'Try all three flavours or double up on your favourite. Your training, your choice.' },
];

export default function StackSaveClient() {
  const { addToCart } = useShop();
  const [addedId, setAddedId] = useState<string | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleAdd = (tier: typeof BUNDLE_TIERS[0]) => {
    const products = useShop.getState().products;
    // Add each image's product
    if (tier.id === 'trainer-tray') {
      products.forEach(p => addToCart(p, p.variants[2], 1)); // bundle of 3
    } else if (tier.id === 'duo') {
      addToCart(products[1], products[1].variants[1], 1);
      addToCart(products[2], products[2].variants[1], 1);
    } else {
      addToCart(products[0], products[0].variants[0], 1);
    }
    setAddedId(tier.id);
    setTimeout(() => setAddedId(null), 1800);
  };

  return (
    <>
      <Suspense fallback={null}>
        <BackToTop />
      </Suspense>
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

      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div className="mobile-menu" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
            <a href="/" onClick={() => setMobileMenuOpen(false)}>Home</a>
            <a href="/wholesale" onClick={() => setMobileMenuOpen(false)}>Wholesale &amp; Retails</a>
            <a href="/contact" onClick={() => setMobileMenuOpen(false)}>Contact Us</a>
            <a href="/athletes" onClick={() => setMobileMenuOpen(false)}>Our Athletes</a>
            <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ marginTop: 16 }}>Shop PRIME X</a>
          </motion.div>
        )}
      </AnimatePresence>

    <div style={{ background: '#000', minHeight: '100vh', color: '#fff' }}>
      {/* ═══ HERO ═══ */}
      <section style={{ position: 'relative', minHeight: '60vh', display: 'flex', alignItems: 'center', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'url(/products/hero-slide.png)', backgroundSize: 'cover', backgroundPosition: 'center' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, rgba(0,0,0,0.88) 0%, rgba(0,0,0,0.65) 100%)' }} />
        <div style={{ position: 'relative', maxWidth: 1200, margin: '0 auto', padding: '80px 32px', width: '100%' }}>
          <div style={{ maxWidth: 650 }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(255,209,0,0.1)', border: '1px solid rgba(255,209,0,0.2)', borderRadius: 999, padding: '6px 18px', marginBottom: 20 }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>Stack & Save</span>
            </div>
            <h1 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(40px, 7vw, 72px)', textTransform: 'uppercase', lineHeight: 1, letterSpacing: '-0.02em', marginBottom: 20 }}>
              All three flavours.<br />One <span style={{ color: 'var(--yellow)' }}>order</span>.
            </h1>
            <p style={{ fontFamily: 'var(--body)', fontSize: 18, color: 'rgba(255,255,255,0.6)', lineHeight: 1.7, maxWidth: 520, marginBottom: 32 }}>
              Never run out mid-cycle. The Trainer&apos;s Tray gives you all three flavours — Orange, Rocket Lollipop, and Fruit Punch — 240 servings, one delivery. Save ₹1,298 compared to buying individually.
            </p>
            <a href="#bundles" style={{ display: 'inline-block', padding: '16px 36px', background: 'var(--yellow)', color: '#000', fontFamily: 'var(--display)', fontSize: 15, letterSpacing: '0.06em', textTransform: 'uppercase', textDecoration: 'none', borderRadius: 6, fontWeight: 700 }}>
              See Bundles
            </a>
          </div>
        </div>
      </section>

      {/* ═══ BENEFITS STRIP ═══ */}
      <section style={{ borderTop: '1px solid rgba(255,255,255,0.06)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
          {BENEFITS.map((b) => (
            <div key={b.title} style={{ padding: '32px 24px', textAlign: 'center', borderRight: '1px solid rgba(255,255,255,0.06)' }}>
              <div style={{ fontSize: 28, marginBottom: 8 }}>{b.icon}</div>
              <div style={{ fontFamily: 'var(--display)', fontSize: 14, textTransform: 'uppercase', marginBottom: 4 }}>{b.title}</div>
              <div style={{ fontFamily: 'var(--body)', fontSize: 12, color: 'rgba(255,255,255,0.45)', lineHeight: 1.5 }}>{b.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ BUNDLE OPTIONS ═══ */}
      <section id="bundles" style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 32px' }}>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--yellow)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 12 }}>Choose Your Bundle</div>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 4vw, 48px)', textTransform: 'uppercase', lineHeight: 1.1 }}>
            The more you stack,<br />the more you <span style={{ color: 'var(--yellow)' }}>save</span>.
          </h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24, alignItems: 'start' }}>
          {BUNDLE_TIERS.map((tier) => (
            <div
              key={tier.id}
              style={{
                position: 'relative',
                background: tier.popular ? 'rgba(255,209,0,0.04)' : 'rgba(255,255,255,0.025)',
                border: tier.popular ? '2px solid var(--yellow)' : '1px solid rgba(255,255,255,0.06)',
                borderRadius: 16,
                overflow: 'hidden',
                transition: 'all 0.3s ease',
              }}
            >
              {tier.popular && (
                <div style={{ background: 'var(--yellow)', color: '#000', fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, textAlign: 'center', padding: '8px 0', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
                  Most Popular
                </div>
              )}

              {/* Images */}
              <div style={{ position: 'relative', aspectRatio: '4/3', background: 'linear-gradient(145deg, #161616, #0a0a0a)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
                <div style={{ display: 'flex', gap: tier.images.length > 1 ? -20 : 0, justifyContent: 'center' }}>
                  {tier.images.map((img, i) => (
                    <div key={i} style={{ position: 'relative', width: tier.images.length === 1 ? 160 : 120, height: tier.images.length === 1 ? 180 : 140 }}>
                      <Image src={img} alt="" fill style={{ objectFit: 'contain' }} />
                    </div>
                  ))}
                </div>
              </div>

              {/* Info */}
              <div style={{ padding: '24px 24px 28px' }}>
                <div style={{ fontFamily: 'var(--display)', fontSize: 22, textTransform: 'uppercase', marginBottom: 4 }}>{tier.label}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.08em', marginBottom: 16 }}>
                  {tier.servings} · {tier.weight}
                </div>

                {/* Price */}
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6 }}>
                  <span style={{ fontFamily: 'var(--display)', fontSize: 36, color: 'var(--yellow)' }}>₹{tier.price.toLocaleString('en-IN')}</span>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 14, color: 'rgba(255,255,255,0.25)', textDecoration: 'line-through' }}>₹{tier.originalPrice.toLocaleString('en-IN')}</span>
                </div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: '#22c55e', marginBottom: 20 }}>
                  Save ₹{tier.saving.toLocaleString('en-IN')} · {tier.perServing}/serving
                </div>

                {/* CTA */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <button
                    onClick={() => handleAdd(tier)}
                    style={{
                      width: '100%',
                      padding: '16px 24px',
                      background: addedId === tier.id ? '#22c55e' : 'var(--yellow)',
                      color: addedId === tier.id ? '#fff' : '#000',
                      fontFamily: 'var(--display)',
                      fontSize: 15,
                      letterSpacing: '0.06em',
                      textTransform: 'uppercase',
                      border: 'none',
                      cursor: 'pointer',
                      borderRadius: 6,
                      fontWeight: 700,
                      transition: 'all 0.25s ease',
                    }}
                  >
                    {addedId === tier.id ? '✓ ADDED' : 'ADD TO CART'}
                  </button>
                  <a
                    href={PARTNER_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'block',
                      width: '100%',
                      padding: '14px 24px',
                      textAlign: 'center',
                      border: '1.5px solid rgba(255,255,255,0.2)',
                      background: 'transparent',
                      color: '#fff',
                      fontFamily: 'var(--display)',
                      fontSize: 13,
                      letterSpacing: '0.06em',
                      textTransform: 'uppercase',
                      textDecoration: 'none',
                      borderRadius: 6,
                      transition: 'all 0.25s ease',
                    }}
                  >
                    Buy Now
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ FLAVOUR COMPARISON ═══ */}
      <section style={{ borderTop: '1px solid rgba(255,255,255,0.06)', background: 'rgba(255,209,0,0.02)' }}>
        <div style={{ maxWidth: 1000, margin: '0 auto', padding: '80px 32px' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--yellow)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 12 }}>All Three Flavours</div>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 4vw, 48px)', textTransform: 'uppercase', lineHeight: 1.1 }}>
              Same formula. Different <span style={{ color: 'var(--yellow)' }}>vibe</span>.
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {[
              { name: 'Orange', img: '/products/Orange.png', desc: 'Bright, citrus-forward. The early-session weapon for sharp focus from the first sip.', mood: 'Early Riser', bg: '#1a0f00' },
              { name: 'Rocket Lollipop', img: '/products/Rocket Lolli pop.png', desc: 'Nostalgic, electric, and unapologetically fun. The flavour that started conversations.', mood: 'Fan Favourite', bg: '#0f001a' },
              { name: 'Fruit Punch', img: '/products/Fruit Punch.png', desc: 'A full mixed-fruit hit. Our flagship formula for max-intensity training days.', mood: 'Flagship', bg: '#001a10' },
            ].map((f) => (
              <div key={f.name} style={{ padding: '28px 24px', background: f.bg, border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, textAlign: 'center' }}>
                <div style={{ position: 'relative', width: 120, height: 140, margin: '0 auto 16px' }}>
                  <Image src={f.img} alt={f.name} fill style={{ objectFit: 'contain' }} />
                </div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--yellow)', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 4 }}>{f.mood}</div>
                <div style={{ fontFamily: 'var(--display)', fontSize: 20, textTransform: 'uppercase', marginBottom: 8 }}>{f.name}</div>
                <p style={{ fontSize: 13, lineHeight: 1.6, color: 'rgba(255,255,255,0.5)' }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FINAL CTA ═══ */}
      <section style={{ maxWidth: 800, margin: '0 auto', padding: '100px 32px', textAlign: 'center' }}>
        <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(36px, 5vw, 56px)', textTransform: 'uppercase', lineHeight: 1.05, marginBottom: 20 }}>
          Stack up. <span style={{ color: 'var(--yellow)' }}>Save more</span>.
        </h2>
        <p style={{ fontFamily: 'var(--body)', fontSize: 17, color: 'rgba(255,255,255,0.5)', lineHeight: 1.7, maxWidth: 480, margin: '0 auto 36px' }}>
          Every flavour. Same 8-ingredient formula. Zero compromise. The Trainer&apos;s Tray is the best value way to fuel your training.
        </p>
        <a
          href={PARTNER_URL}
          target="_blank"
          rel="noopener noreferrer"
          style={{ display: 'inline-block', padding: '18px 44px', background: 'var(--yellow)', color: '#000', fontFamily: 'var(--display)', fontSize: 16, letterSpacing: '0.06em', textTransform: 'uppercase', textDecoration: 'none', borderRadius: 6, fontWeight: 700 }}
        >
          Order Trainer's Tray
        </a>
      </section>
      </div>

      <CartDrawer />

      <footer>
        <div className="wrap">
          <div className="foot-bottom">
            <span>© 2026 PURE HEALTH SUPPS®. FSSAI Lic. No. 10824999000028.</span>
          </div>
        </div>
      </footer>
    </>
  );
}
