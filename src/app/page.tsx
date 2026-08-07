'use client';

import React, { useState, useEffect, useRef, Suspense } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { ArrowRight, ChevronDown, ExternalLink, Shield, Award, Beaker, Truck, RotateCcw, Star, ShoppingBag, Menu, X } from 'lucide-react';
import { useShop } from '../lib/store';
import Image from '../components/Image';
import CartDrawer from '../components/CartDrawer';
import BackToTop from '../components/BackToTop';
import WelcomePopup from '../components/WelcomePopup';
import { PARTNER_URL } from '../components/AnnouncementBar';

const EASE = [0.23, 1, 0.32, 1] as const;

const INGREDIENTS = [
  { value: '1.5', unit: 'g', name: 'Beta-Alanine', desc: 'Buffers lactic acid, delays fatigue. Pushes the wall back so you squeeze out reps when your body says quit.' },
  { value: '750', unit: 'mg', name: 'Arginine HCl', desc: 'Boosts nitric oxide, blood flow. More blood flow, more oxygen, more pump — every set counts.' },
  { value: '500', unit: 'mg', name: 'L-Citrulline', desc: 'Converts to arginine, reduces soreness. Pump that lasts long after your session ends.' },
  { value: '250', unit: 'mg', name: 'L-Carnitine', desc: 'Transports fatty acids for energy. Burns cleaner, supports endurance, helps maintain lean muscle.' },
  { value: '125', unit: 'mg', name: 'L-Tyrosine', desc: 'Precursor to dopamine, mental clarity. Focus stays sharp when the weights get heavy.' },
  { value: '50', unit: 'mg', name: 'Encapsulated Caffeine', desc: 'Sustained-release, no crash. Clean energy over 2-3 hours — you finish as strong as you started.' },
  { value: '45', unit: 'mg', name: 'Coffee Bean Extract', desc: 'Natural caffeine + antioxidants. Smooths the energy curve and keeps you locked in.' },
  { value: '37.5', unit: 'mg', name: 'Garcinia Cambogia', desc: 'Supports fat metabolism. Complements the energy blend for a leaner training experience.' },
];

const PRODUCTS = [
  { flavor: 'orange', label: 'Flavour 01 — Orange', name: 'Orange', img: '/products/Orange.png', tubImg: '/products/tub-orange.png', desc: 'Bright citrus energy that hits clean and lasts. 80 servings of focused, sustained performance.', delay: '1' },
  { flavor: 'fruit', label: 'Flavour 02 — Fruit Punch', name: 'Fruit Punch', img: '/products/Fruit Punch.png', tubImg: '/products/tub-fruit-punch.png', desc: 'Our flagship blend for max-intensity training days. A full mixed-fruit hit backed by 8 clinically dosed ingredients.', delay: '2' },
  { flavor: 'rocket', label: 'Flavour 03 — Rocket Lollipop', name: 'Rocket Lollipop', img: '/products/Rocket Lolli pop.png', tubImg: '/products/tub-rocket.png', desc: 'Sweet candy nostalgia meets clinical performance. Same 8-ingredient formula in a flavour that makes you look forward to scoop day.', delay: '3' },
];

const TRUST_ROWS = [
  { key: 'FSSAI Licence', val: '10824999000028' },
  { key: 'Banned Substance', val: 'FREE' },
  { key: 'Proprietary Blend', val: 'ZERO' },
  { key: 'Shelf Life', val: '18 MONTHS' },
  { key: 'Serving Size', val: '3.5g' },
  { key: 'Servings Per Tub', val: '80' },
  { key: 'Country of Origin', val: 'INDIA' },
];

/* ═══════════════════════════════════════════════════════════ */
/*  MARQUEE COMPONENT                                         */
/* ═══════════════════════════════════════════════════════════ */
function Marquee() {
  return (
    <div style={{ background: 'var(--ink)', borderTop: '1px solid rgba(255,209,0,0.15)', borderBottom: '1px solid rgba(255,209,0,0.15)', overflow: 'hidden', padding: '14px 0' }}>
      <div style={{ display: 'flex', width: '200%', animation: 'marquee 26s linear infinite' }}>
        {Array.from({ length: 8 }).map((_, i) => (
          <span key={i} style={{ fontFamily: 'var(--display)', fontSize: 26, textTransform: 'uppercase', color: 'var(--yellow)', whiteSpace: 'nowrap', padding: '0 24px', letterSpacing: '0.04em' }}>
            FOCUS ● PUMP ● ENERGY
          </span>
        ))}
      </div>
      <style>{`@keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }`}</style>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  HERO SECTION                                              */
/* ═══════════════════════════════════════════════════════════ */
function HeroSection() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] });
  const bgY = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95]);

  return (
    <section ref={ref} style={{ minHeight: '100svh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
      {/* Background — edge-to-edge lifestyle image, minimal overlay */}
      <motion.div style={{ position: 'absolute', inset: 0, y: bgY, scale }}>
        <Image src="/products/hero-slide.png" alt="" fill style={{ objectFit: 'cover' }} priority sizes="100vw" quality={90} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.35) 100%)' }} />
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2, duration: 1 }}
        style={{ position: 'absolute', bottom: 40, left: '50%', transform: 'translateX(-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, zIndex: 10 }}
      >
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.3)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>Scroll</span>
        <motion.div animate={{ y: [0, 8, 0] }} transition={{ duration: 1.5, repeat: Infinity }}>
          <ChevronDown size={18} style={{ color: 'rgba(255,255,255,0.3)' }} />
        </motion.div>
      </motion.div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  PRODUCT CARDS SECTION                                     */
/* ═══════════════════════════════════════════════════════════ */
function ProductsSection() {
  const { products, addToCart } = useShop();

  return (
    <section style={{ padding: '100px 0' }}>
      <div className="wrap">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: EASE }}
          style={{ marginBottom: 48 }}
        >
          <span className="eyebrow" style={{ marginBottom: 12, display: 'block' }}>The Range</span>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 4vw, 42px)', textTransform: 'uppercase', marginBottom: 8 }}>
            Only three flavours.<br />
            <span style={{ color: 'var(--yellow)' }}>Zero filler formulas.</span>
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: 16, maxWidth: 480 }}>
            Every ingredient and dose printed on the tub. No proprietary blends. No hidden fillers. Just performance.
          </p>
        </motion.div>

        <div className="product-grid">
          {PRODUCTS.map((p, i) => (
            <motion.div
              key={p.flavor}
              className="p-card"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.1, ease: EASE }}
            >
              <a href={`/product/${products[i]?.slug || 'primex-preworkout-' + p.flavor}`} style={{ textDecoration: 'none', color: 'inherit', display: 'flex', flexDirection: 'column', flex: 1 }}>
                <div className="p-flavor-tag">{p.label}</div>
                <div className="p-canvas-wrap">
                  <img src={p.img} alt={`PRIME X ${p.name}`} style={{ objectFit: 'contain', maxHeight: 240, width: 'auto', filter: 'drop-shadow(0 8px 30px rgba(0,0,0,0.5))' }} />
                </div>
                <h3 style={{ fontFamily: 'var(--heading)', fontSize: 22, textTransform: 'uppercase', padding: '0 20px' }}>Prime X — {p.name}</h3>
                <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', lineHeight: 1.6, padding: '6px 20px 0', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{p.desc}</p>
              </a>
              <div className="p-meta">
                <span className="servings">80 SERVINGS · 280G</span>
                <a href={`/product/${products[i]?.slug || 'primex-preworkout-' + p.flavor}`} style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                  View Details →
                </a>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  PARALLAX BREAK                                            */
/* ═══════════════════════════════════════════════════════════ */
function ParallaxBreak({ title, accent, subtext, productImg }: { title: string; accent: string; subtext: string; productImg?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] });
  const bgY = useTransform(scrollYProgress, [0, 1], ['-15%', '15%']);
  const contentOpacity = useTransform(scrollYProgress, [0.2, 0.5, 0.8], [0, 1, 0]);
  const contentY = useTransform(scrollYProgress, [0.2, 0.5, 0.8], [40, 0, -40]);

  return (
    <div ref={ref} style={{ position: 'relative', width: '100vw', marginLeft: 'calc(-50vw + 50%)', height: '70vh', minHeight: 500, overflow: 'hidden' }}>
      <motion.div style={{ position: 'absolute', inset: '-20% 0', y: bgY }}>
        <Image src="/products/hero-slide.png" alt="" fill style={{ objectFit: 'cover', transform: 'scale(1.15)' }} sizes="100vw" />
      </motion.div>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.72)' }} />

      <motion.div style={{ position: 'relative', zIndex: 10, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', opacity: contentOpacity, y: contentY, padding: '0 32px' }}>
        <div style={{ maxWidth: 600 }}>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(36px, 6vw, 56px)', textTransform: 'uppercase', lineHeight: 0.95 }}>
            {title.split(accent)[0]}
            <span style={{ color: 'var(--yellow)' }}>{accent}</span>
            {title.split(accent)[1]}
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: 16, marginTop: 16, lineHeight: 1.6 }}>{subtext}</p>
          {productImg && (
            <motion.img
              src={productImg}
              alt=""
              style={{ width: 160, height: 'auto', margin: '32px auto 0', filter: 'drop-shadow(0 20px 40px rgba(0,0,0,0.5))' }}
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            />
          )}
        </div>
      </motion.div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  SCIENCE / INGREDIENTS SECTION                             */
/* ═══════════════════════════════════════════════════════════ */
function ScienceSection() {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  return (
    <section style={{ padding: '100px 0' }}>
      <div className="wrap">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: EASE }}
          style={{ textAlign: 'center', marginBottom: 56 }}
        >
          <span className="eyebrow" style={{ marginBottom: 12, display: 'block' }}>Power Performance Nutrients Blend</span>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 4vw, 42px)', textTransform: 'uppercase', marginBottom: 8 }}>
            Every milligram, on the <span style={{ color: 'var(--yellow)' }}>label</span>.
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: 16, maxWidth: 500, margin: '0 auto' }}>
            No proprietary blends. No hidden doses. Every ingredient and its exact amount printed on the tub.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
          {INGREDIENTS.map((ing, i) => (
            <motion.div
              key={ing.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.06, ease: EASE }}
              onMouseEnter={() => setHoveredIdx(i)}
              onMouseLeave={() => setHoveredIdx(null)}
              style={{
                position: 'relative',
                background: hoveredIdx === i ? 'var(--yellow)' : 'linear-gradient(145deg, #1a1a1a, #111)',
                border: `1px solid ${hoveredIdx === i ? 'var(--yellow)' : 'rgba(255,209,0,0.12)'}`,
                borderRadius: 12,
                padding: 28,
                cursor: 'pointer',
                transition: 'all 0.45s cubic-bezier(0.23, 1, 0.32, 1)',
                boxShadow: hoveredIdx === i ? '0 0 40px rgba(255,209,0,0.3)' : '0 6px 0 0 #0a0a0a, 0 8px 20px rgba(0,0,0,0.5)',
                minHeight: 160,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                textAlign: 'center',
                overflow: 'hidden',
              }}
            >
              {/* Front state */}
              <div style={{ opacity: hoveredIdx === i ? 0 : 1, transform: hoveredIdx === i ? 'scale(0.9)' : 'scale(1)', transition: 'all 0.45s cubic-bezier(0.23, 1, 0.32, 1)', position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: 28 }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 36, fontWeight: 700, color: '#fff', lineHeight: 1 }}>{ing.value}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 14, color: 'var(--yellow)', marginTop: 4 }}>{ing.unit}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase', marginTop: 12 }}>{ing.name}</div>
              </div>
              {/* Hover state */}
              <div style={{ opacity: hoveredIdx === i ? 1 : 0, transform: hoveredIdx === i ? 'scale(1)' : 'scale(0.9)', transition: 'all 0.45s cubic-bezier(0.23, 1, 0.32, 1)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
                <div style={{ fontFamily: 'var(--heading)', fontSize: 18, textTransform: 'uppercase', color: '#000', fontWeight: 400 }}>{ing.name}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'rgba(0,0,0,0.5)', marginTop: 4 }}>{ing.value}{ing.unit} per serving</div>
                <div style={{ fontFamily: 'var(--body)', fontSize: 13, color: 'rgba(0,0,0,0.7)', marginTop: 8, lineHeight: 1.5 }}>{ing.desc}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <style>{`
        @media (max-width: 900px) {
          div[style*="grid-template-columns: repeat(4"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }
        @media (max-width: 480px) {
          div[style*="grid-template-columns: repeat(4"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  WHY PURE SECTION                                          */
/* ═══════════════════════════════════════════════════════════ */
function WhyPureSection() {
  return (
    <section style={{ background: '#000' }}>
      {/* Hero — Ghost Story style */}
      <div style={{ position: 'relative', width: '100%', height: '85vh', minHeight: 500, overflow: 'hidden' }}>
        <Image
          src="/products/product-gym.png"
          alt="PURE athlete in the gym"
          fill
          style={{ objectFit: 'cover', objectPosition: 'center 20%' }}
        />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.15) 40%, rgba(0,0,0,0.65) 100%)' }} />
        <div style={{ position: 'relative', zIndex: 2, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', padding: '0 24px', textAlign: 'center' }}>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
          >
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 16 }}>
              The PURE Story
            </div>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(40px, 9vw, 72px)', textTransform: 'uppercase', lineHeight: 0.92, color: '#fff' }}>
              Why We<br /><span style={{ color: 'var(--yellow)' }}>Exist</span>
            </h2>
          </motion.div>
        </div>
      </div>

      {/* Editorial story — two-column Ghost style */}
      <div className="wrap" style={{ padding: '80px 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 64, alignItems: 'center' }}>
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7, ease: [0.23, 1, 0.32, 1] }}
          >
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 12 }}>
              Our Mission
            </div>
            <h3 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 4vw, 42px)', textTransform: 'uppercase', lineHeight: 1.05, marginBottom: 20 }}>
              Transparency is not a<br />marketing <span style={{ color: 'var(--yellow)' }}>strategy</span>.
            </h3>
            <p style={{ fontSize: 16, color: 'rgba(255,255,255,0.6)', lineHeight: 1.7, maxWidth: 480 }}>
              When we started PURE, we were tired of supplements hiding behind proprietary blends and underdosed ingredients. We believed Indian athletes deserved better — clinically dosed formulas, fully transparent labels, and zero shortcuts.
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7, delay: 0.15, ease: [0.23, 1, 0.32, 1] }}
            style={{ display: 'flex', justifyContent: 'center' }}
          >
            <div style={{ position: 'relative', width: '100%', maxWidth: 440, aspectRatio: '4/5', borderRadius: 12, overflow: 'hidden' }}>
              <Image src="/products/product-lifestyle.png" alt="PURE lifestyle" fill style={{ objectFit: 'cover' }} />
              <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, transparent 50%, rgba(0,0,0,0.6) 100%)' }} />
              <div style={{ position: 'absolute', bottom: 24, left: 24, right: 24 }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 4 }}>Founded</div>
                <div style={{ fontFamily: 'var(--display)', fontSize: 20, textTransform: 'uppercase', color: '#fff' }}>2024, India</div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Values — editorial grid */}
      <div className="wrap" style={{ padding: '0 24px 80px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 1 }}>
          {[
            { num: '01', title: 'Full Transparency', desc: 'Every ingredient and its exact dose printed on the tub. No proprietary blends. No hidden fillers.' },
            { num: '02', title: 'Clinical Dosing', desc: 'Every ingredient at its clinically studied dose. 1.5g Beta-Alanine means 1.5g — not a dusting for the label.' },
            { num: '03', title: 'Zero Compromises', desc: 'Banned substance free. FSSAI licensed. Manufactured in a certified facility. No artificial colours.' },
          ].map((item, i) => (
            <motion.div
              key={item.num}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.1, ease: [0.23, 1, 0.32, 1] }}
              style={{
                padding: '40px 32px',
                background: i === 1 ? 'rgba(255,209,0,0.04)' : 'transparent',
                borderLeft: i > 0 ? '1px solid rgba(255,255,255,0.06)' : 'none',
              }}
            >
              <div style={{ fontFamily: 'var(--display)', fontSize: 48, color: 'var(--yellow)', opacity: 0.7, lineHeight: 1, marginBottom: 12 }}>{item.num}</div>
              <h4 style={{ fontFamily: 'var(--heading)', fontSize: 18, textTransform: 'uppercase', marginBottom: 10, color: '#fff' }}>{item.title}</h4>
              <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)', lineHeight: 1.65 }}>{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Trust strip */}
      <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div className="wrap" style={{ display: 'flex', justifyContent: 'space-between', padding: '24px', gap: 16, flexWrap: 'wrap' }}>
          {TRUST_ROWS.map((row) => (
            <div key={row.key} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>{row.key}</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.05em' }}>{row.val}</span>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          div[style*="grid-template-columns: 1.1fr"] {
            grid-template-columns: 1fr !important;
            gap: 40px !important;
          }
          div[style*="grid-template-columns: repeat(3"] {
            grid-template-columns: 1fr !important;
            gap: 0 !important;
          }
          div[style*="grid-template-columns: repeat(3"] > div {
            border-left: none !important;
            border-bottom: 1px solid rgba(255,255,255,0.06);
          }
        }
      `}</style>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  BUNDLE SECTION                                            */
/* ═══════════════════════════════════════════════════════════ */
function BundleSection() {
  return (
    <section style={{ padding: '80px 0', borderTop: '1px solid rgba(255,209,0,0.15)', borderBottom: '1px solid rgba(255,209,0,0.15)' }}>
      <div className="wrap">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48, alignItems: 'center' }}>
          {/* Left: Product images */}
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', position: 'relative', height: 350 }}>
            <motion.img src="/products/tub-orange.png" alt="Orange" style={{ position: 'absolute', left: 40, width: 150, objectFit: 'contain', transform: 'rotate(-8deg)', filter: 'drop-shadow(0 15px 30px rgba(0,0,0,0.5))' }} whileHover={{ rotate: -12, scale: 1.05 }} />
            <motion.img src="/products/tub-fruit-punch.png" alt="Fruit Punch" style={{ position: 'relative', zIndex: 2, width: 180, objectFit: 'contain', transform: 'scale(1.08)', filter: 'drop-shadow(0 20px 40px rgba(0,0,0,0.6))' }} whileHover={{ scale: 1.12 }} />
            <motion.img src="/products/tub-rocket.png" alt="Rocket" style={{ position: 'absolute', right: 40, width: 150, objectFit: 'contain', transform: 'rotate(8deg)', filter: 'drop-shadow(0 15px 30px rgba(0,0,0,0.5))' }} whileHover={{ rotate: 12, scale: 1.05 }} />
          </div>

          {/* Right: Copy */}
          <div>
            <span className="eyebrow" style={{ marginBottom: 12, display: 'block' }}>Stack & Save</span>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 4vw, 40px)', textTransform: 'uppercase', marginBottom: 12 }}>
              All three flavours. <span style={{ color: 'var(--yellow)' }}>One tray.</span>
            </h2>
            <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: 16, lineHeight: 1.65, marginBottom: 24 }}>
              The Trainer's Tray. All three PRIME X flavours in one bundle. Save ₹598 compared to buying individually.
            </p>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 14, marginBottom: 28 }}>
              <span style={{ fontFamily: 'var(--display)', fontSize: 44, color: 'var(--yellow)', lineHeight: 1 }}>₹3,299</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 16, color: 'rgba(255,255,255,0.3)', textDecoration: 'line-through' }}>₹3,897</span>
            </div>
            <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ fontSize: 14, padding: '16px 36px' }}>
              Order Bundle <ExternalLink size={16} />
            </a>
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  ATHLETE BANNER                                            */
/* ═══════════════════════════════════════════════════════════ */
function AthleteBanner() {
  return (
    <section style={{ padding: '100px 0', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, rgba(0,0,0,1) 0%, rgba(10,10,10,1) 50%, rgba(0,0,0,1) 100%)' }} />
      <div style={{ position: 'absolute', top: '50%', right: 0, width: 500, height: 500, background: 'radial-gradient(circle, rgba(255,209,0,0.08) 0%, transparent 70%)', transform: 'translateY(-50%)', filter: 'blur(40px)' }} />

      <div className="wrap" style={{ position: 'relative', zIndex: 10 }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: EASE }}
          style={{ maxWidth: 620 }}
        >
          <span className="eyebrow" style={{ marginBottom: 12, display: 'block' }}>For the working athlete</span>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 4vw, 40px)', textTransform: 'uppercase', marginBottom: 16, lineHeight: 1.05 }}>
            You clock in at the office.<br />
            You clock in at the <span style={{ color: 'var(--yellow)' }}>gym</span> too.
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: 16, lineHeight: 1.65, marginBottom: 32 }}>
            PRIME X is built for the 9-to-5 athlete. The one who trains before sunrise or after sunset.
            Who demands performance from every supplement. Who refuses to compromise.
          </p>
          <a href="/shop" className="btn-pure" style={{ fontSize: 14, padding: '16px 32px' }}>
            Get PRIME X <ArrowRight size={16} />
          </a>
        </motion.div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  TESTIMONIALS SECTION                                      */
/* ═══════════════════════════════════════════════════════════ */
function TestimonialsSection() {
  const testimonials = [
    { quote: 'The pump is insane. Beta-Alanine kicks in within minutes and the energy lasts through my entire 90-minute session. Best pre-workout I have used in India.', author: 'Rahul M.', role: 'Powerlifter', stars: 5 },
    { quote: 'Finally a pre-workout that is transparent about what is inside. No proprietary blends, no BS. The Orange flavour tastes amazing too.', author: 'Arjun K.', role: 'CrossFit Athlete', stars: 5 },
    { quote: 'I was sceptical about Indian pre-workouts until I tried PRIME X. The clinical dosing is legit — 1.5g Beta-Alanine actually makes a difference.', author: 'Vikram S.', role: 'Working Professional', stars: 5 },
  ];

  return (
    <section style={{ padding: '100px 0' }}>
      <div className="wrap">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: EASE }}
          style={{ textAlign: 'center', marginBottom: 56 }}
        >
          <span className="eyebrow" style={{ marginBottom: 12, display: 'block' }}>Real Training, Real Feedback</span>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 4vw, 42px)', textTransform: 'uppercase' }}>
            What the floor is <span style={{ color: 'var(--yellow)' }}>saying</span>.
          </h2>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
          {testimonials.map((t, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1, ease: EASE }}
              style={{ background: 'linear-gradient(145deg, #1a1a1a, #111)', border: '1px solid var(--line)', borderRadius: 12, padding: 32 }}
            >
              <div style={{ fontFamily: 'var(--mono)', fontSize: 14, color: 'var(--yellow)', letterSpacing: 4, marginBottom: 16 }}>
                {'★'.repeat(t.stars)}
              </div>
              <p style={{ fontSize: 15, color: 'rgba(255,255,255,0.82)', lineHeight: 1.65, marginBottom: 24 }}>{t.quote}</p>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 8, background: 'var(--yellow)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--display)', fontSize: 16, color: '#000' }}>
                  {t.author[0]}
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 14 }}>{t.author}</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>{t.role}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          div[style*="grid-template-columns: repeat(3"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  NEWSLETTER SECTION                                        */
/* ═══════════════════════════════════════════════════════════ */
function NewsletterSection() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      setSubmitted(true);
      setEmail('');
    }
  };

  return (
    <section style={{ padding: '80px 0', borderTop: '1px solid var(--line)' }}>
      <div className="wrap" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 32 }}>
        <div>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(24px, 3vw, 36px)', textTransform: 'uppercase', marginBottom: 8 }}>
            Get early access to new flavours & <span style={{ color: 'var(--yellow)' }}>drops</span>.
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 14 }}>No spam. Just performance updates.</p>
        </div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {submitted ? (
            <div style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--yellow)', padding: '14px 20px' }}>You are in. Watch your inbox.</div>
          ) : (
            <>
              <input
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ padding: '14px 20px', background: 'transparent', border: '1px solid var(--line)', color: '#fff', fontFamily: 'var(--body)', fontSize: 14, outline: 'none', minWidth: 260, transition: 'border-color 0.25s' }}
                onFocus={(e) => (e.target.style.borderColor = 'var(--yellow)')}
                onBlur={(e) => (e.target.style.borderColor = 'var(--line)')}
              />
              <button type="submit" className="btn-pure" style={{ fontSize: 12, padding: '14px 24px' }}>
                Notify Me
              </button>
            </>
          )}
        </form>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/*  MAIN HOMEPAGE                                             */
/* ═══════════════════════════════════════════════════════════ */
export default function HomePage() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div style={{ background: '#000', minHeight: '100vh' }}>
      {/* Announcement Bar */}
      <div className="announce-bar">
        <div className="announce-inner">
          <div className="announce-track">
            <span>FREE SHIPPING ON ALL ORDERS ABOVE ₹999 ● PRIME X — 8 CLINICALLY DOSED INGREDIENTS ● ZERO PROPRIETARY BLENDS</span>
          </div>
          <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="announce-link">Shop Now</a>
        </div>
      </div>

      {/* Navigation */}
      <header className={`nav ${scrolled ? 'scrolled' : ''}`} style={{ top: 40 }}>
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

      {/* Hero */}
      <HeroSection />

      {/* Marquee */}
      <Marquee />

      {/* Products */}
      <ProductsSection />

      {/* Banner — Fruit Punch */}
      <section style={{ width: '100%', overflow: 'hidden' }}>
        <img
          src="/products/banner-fruit-punch.jpg"
          alt="PRIME X Fruit Punch — Explosive Energy, Enhanced Focus, Muscle Pump"
          style={{ width: '100%', height: 'auto', display: 'block' }}
        />
      </section>

      {/* Parallax Break 1 */}
      <ParallaxBreak
        title="Explosive Energy"
        accent="Energy"
        subtext="Clinically dosed for explosive power. Beta-Alanine, Arginine HCl, and L-Citrulline work together to push your limits."
      />

      {/* Science */}
      <ScienceSection />

      {/* Parallax Break 2 */}
      <ParallaxBreak
        title="Built Different"
        accent="Different"
        subtext="FSSAI licensed. Banned substance free. Manufactured in a certified facility. No shortcuts."
        productImg="/products/Fruit Punch.png"
      />

      {/* Why PURE */}
      <WhyPureSection />

      {/* Banner — Orange */}
      <section style={{ width: '100%', overflow: 'hidden' }}>
        <img
          src="/products/banner-orange.jpg"
          alt="PRIME X Orange — Light, Juicy & Refreshing"
          style={{ width: '100%', height: 'auto', display: 'block' }}
        />
      </section>

      {/* Bundle */}
      <BundleSection />

      {/* Parallax Break 3 */}
      <ParallaxBreak
        title="Never Finished"
        accent="Finished"
        subtext="Focus that lasts. Energy that does not crash. Pump that does not quit. Every rep, every set."
        productImg="/products/Rocket Lolli pop.png"
      />

      {/* Athlete Banner */}
      <AthleteBanner />

      {/* Testimonials */}
      <TestimonialsSection />

      {/* Newsletter */}
      <NewsletterSection />

      {/* Footer */}
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
              <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer">puresupps.site</a>
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
      <WelcomePopup />
    </div>
  );
}
