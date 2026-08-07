'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Menu, X } from 'lucide-react';
import Image from '@/components/Image';
import { PARTNER_URL } from '../../components/AnnouncementBar';
import CartDrawer from '../../components/CartDrawer';
const BackToTop = React.lazy(() => import('../../components/BackToTop'));

const POSTS = [
  {
    id: 1,
    title: 'Why We Only Ship Three SKUs',
    excerpt: 'Most brands launch with twenty half-baked products. We launched with three we\'d stake our reputation on — each carrying the same clinically dosed Power Performance Nutrients Blend.',
    category: 'Brand',
    date: 'Aug 2026',
    readTime: '5 min',
    image: '/products/tub-orange.png',
    featured: true,
  },
  {
    id: 2,
    title: 'The Science of the Pump: Arginine vs Citrulline',
    excerpt: 'Which nitric oxide booster actually works? We compare Arginine HCl and L-Citrulline with clinical data — and explain why we use both.',
    category: 'Science',
    date: 'Jul 2026',
    readTime: '7 min',
    image: '/products/tub-fruit-punch.png',
  },
  {
    id: 3,
    title: 'Beta-Alanine: Why 1.5g Is the Sweet Spot',
    excerpt: 'Beta-Alanine is one of the most researched pre-workout ingredients. Here\'s why 1.5g per serving is the optimal dose for real endurance gains.',
    category: 'Ingredients',
    date: 'Jul 2026',
    readTime: '6 min',
    image: '/products/tub-rocket.png',
  },
  {
    id: 4,
    title: '5 Training Mistakes That Are Killing Your Gains',
    excerpt: 'Stop making these common errors. Science-backed strategies to maximize muscle growth and strength every single session.',
    category: 'Training',
    date: 'Jun 2026',
    readTime: '10 min',
    image: '/products/Orange.png',
  },
  {
    id: 5,
    title: 'Pre-Workout Timing: When to Take Your Supplement',
    excerpt: 'Timing matters. The optimal window to take your pre-workout for maximum energy, focus, and performance across your entire session.',
    category: 'Nutrition',
    date: 'Jun 2026',
    readTime: '5 min',
    image: '/products/Fruit Punch.png',
  },
  {
    id: 6,
    title: 'Recovery 101: What to Do After Your Workout',
    excerpt: 'The workout is only half the equation. Recovery is where gains actually happen. The protocols that work — no broscience.',
    category: 'Recovery',
    date: 'May 2026',
    readTime: '9 min',
    image: '/products/Rocket Lolli pop.png',
  },
];

const CATEGORIES = ['All', 'Brand', 'Science', 'Ingredients', 'Training', 'Nutrition', 'Recovery'];

export default function JournalClient() {
  const [activeCategory, setActiveCategory] = useState('All');
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const filtered = activeCategory === 'All' ? POSTS : POSTS.filter(p => p.category === activeCategory);
  const featured = POSTS.find(p => p.featured);
  const regular = filtered.filter(p => !p.featured);

  return (
    <>
      <Suspense fallback={null}>
        <BackToTop />
      </Suspense>
      <header className={`nav ${scrolled ? 'scrolled' : ''}`}>
        <div className="wrap nav-inner">
          <a href="/" className="brand"><span className="brand-text">PURE</span></a>
          <nav className="nav-links">
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
            <a href="/wholesale" onClick={() => setMobileMenuOpen(false)}>Wholesale &amp; Retails</a>
            <a href="/contact" onClick={() => setMobileMenuOpen(false)}>Contact Us</a>
            <a href="/athletes" onClick={() => setMobileMenuOpen(false)}>Our Athletes</a>
            <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ marginTop: 16 }}>Shop PRIME X</a>
          </motion.div>
        )}
      </AnimatePresence>

    <div style={{ background: '#000', minHeight: '100vh', color: '#fff' }}>
      {/* ═══ HERO ═══ */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 32px 60px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(255,209,0,0.1)', border: '1px solid rgba(255,209,0,0.2)', borderRadius: 999, padding: '6px 18px', marginBottom: 20 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>Journal</span>
        </div>
        <h1 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(40px, 7vw, 72px)', textTransform: 'uppercase', lineHeight: 1, letterSpacing: '-0.02em', marginBottom: 16 }}>
          The PURE Performance <span style={{ color: 'var(--yellow)' }}>Journal</span>.
        </h1>
        <p style={{ fontFamily: 'var(--body)', fontSize: 17, color: 'rgba(255,255,255,0.5)', lineHeight: 1.7, maxWidth: 560 }}>
          Training insights, ingredient deep-dives, and the thinking behind every formula decision.
        </p>
      </section>

      {/* ═══ CATEGORY FILTER ═══ */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px 40px' }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
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
                background: activeCategory === cat ? 'var(--yellow)' : 'transparent',
                color: activeCategory === cat ? '#000' : 'rgba(255,255,255,0.45)',
                border: activeCategory === cat ? '1.5px solid var(--yellow)' : '1.5px solid rgba(255,255,255,0.1)',
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </section>

      {/* ═══ FEATURED POST ═══ */}
      {featured && activeCategory === 'All' && (
        <section style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px 48px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, overflow: 'hidden' }}>
            <div style={{ position: 'relative', aspectRatio: '4/3', background: 'linear-gradient(145deg, #161616, #0a0a0a)' }}>
              <Image src={featured.image} alt={featured.title} fill style={{ objectFit: 'contain', padding: 48 }} />
            </div>
            <div style={{ padding: '48px 40px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, color: 'var(--yellow)', background: 'rgba(255,209,0,0.1)', padding: '4px 12px', letterSpacing: '0.1em', textTransform: 'uppercase' }}>{featured.category}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.35)' }}>{featured.date} · {featured.readTime}</span>
              </div>
              <h2 style={{ fontFamily: 'var(--display)', fontSize: 32, textTransform: 'uppercase', lineHeight: 1.15, marginBottom: 16 }}>{featured.title}</h2>
              <p style={{ fontSize: 15, lineHeight: 1.7, color: 'rgba(255,255,255,0.55)', marginBottom: 24 }}>{featured.excerpt}</p>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--yellow)', letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer' }}>
                Read Article →
              </span>
            </div>
          </div>
        </section>
      )}

      {/* ═══ POSTS GRID ═══ */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px 80px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
          {(activeCategory === 'All' ? regular : filtered).map((post) => (
            <div
              key={post.id}
              style={{
                background: 'rgba(255,255,255,0.025)',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: 12,
                overflow: 'hidden',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'rgba(255,209,0,0.2)'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div style={{ position: 'relative', aspectRatio: '16/10', background: 'linear-gradient(145deg, #161616, #0a0a0a)' }}>
                <Image src={post.image} alt={post.title} fill style={{ objectFit: 'contain', padding: 24 }} />
              </div>
              <div style={{ padding: '20px 22px 24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, color: 'var(--yellow)', background: 'rgba(255,209,0,0.08)', padding: '3px 10px', letterSpacing: '0.1em', textTransform: 'uppercase' }}>{post.category}</span>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.3)' }}>{post.readTime}</span>
                </div>
                <h3 style={{ fontFamily: 'var(--display)', fontSize: 18, textTransform: 'uppercase', lineHeight: 1.2, marginBottom: 8 }}>{post.title}</h3>
                <p style={{ fontSize: 13, lineHeight: 1.6, color: 'rgba(255,255,255,0.45)', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{post.excerpt}</p>
                <div style={{ marginTop: 14, fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.3)' }}>{post.date}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ NEWSLETTER ═══ */}
      <section style={{ borderTop: '1px solid rgba(255,255,255,0.06)', background: 'rgba(255,209,0,0.02)' }}>
        <div style={{ maxWidth: 600, margin: '0 auto', padding: '80px 32px', textAlign: 'center' }}>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 28, textTransform: 'uppercase', marginBottom: 12 }}>Stay in the loop</h2>
          <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.45)', marginBottom: 28 }}>New articles, training insights, and product drops — straight to your inbox.</p>
          <form onSubmit={(e) => { e.preventDefault(); alert('You\'re on the list — we\'ll be in touch.'); }} style={{ display: 'flex', gap: 8, justifyContent: 'center' }}>
            <input type="email" placeholder="you@email.com" required style={{ flex: 1, maxWidth: 320, padding: '14px 18px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontFamily: 'var(--body)', fontSize: 14, outline: 'none', borderRadius: 6 }} />
            <button type="submit" style={{ padding: '14px 28px', background: 'var(--yellow)', color: '#000', fontFamily: 'var(--display)', fontSize: 13, letterSpacing: '0.06em', textTransform: 'uppercase', border: 'none', cursor: 'pointer', borderRadius: 6, fontWeight: 700 }}>
              Subscribe
            </button>
          </form>
        </div>
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
