'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Menu, X, Instagram } from 'lucide-react';
import { PARTNER_URL } from '../../components/AnnouncementBar';
import CartDrawer from '../../components/CartDrawer';
const BackToTop = React.lazy(() => import('../../components/BackToTop'));

const ATHLETES = [
  { name: 'Sergi Constance', role: 'Brand Ambassador', img: '/products/sergi-constance.jpg', instagram: 'https://instagram.com/sergiconstance' },
  { name: 'Ryan Hughes', role: 'Athlete', img: '/products/product-gym.png', instagram: '#' },
  { name: 'Alex Rivera', role: 'Athlete', img: '/products/product-lifestyle.png', instagram: '#' },
];

export default function AthletesClient() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <Suspense fallback={null}><BackToTop /></Suspense>
      <div style={{ background: '#000', minHeight: '100vh', color: '#fff' }}>
        <header className={`nav ${scrolled ? 'scrolled' : ''}`}>
          <div className="wrap nav-inner">
            <a href="/" className="brand"><span className="brand-text">PURE</span></a>
            <nav className="nav-links">
              <a href="/">Home</a>
              <a href="/wholesale">Wholesale &amp; Retails</a>
              <a href="/contact">Contact Us</a>
              <a href="/athletes" style={{ color: 'var(--paper)' }}>Our Athletes</a>
            </nav>
            <div className="nav-right">
              <a href="/cart" className="nav-icon" style={{ position: 'relative' }}><ShoppingBag size={20} /></a>
              <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ fontSize: 11, padding: '10px 20px' }}>Shop PRIME X</a>
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

        {/* Hero */}
        <section style={{ maxWidth: 1000, margin: '0 auto', padding: '80px 32px 60px', textAlign: 'center' }}>
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 16 }}>Our Athletes</div>
            <h1 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 6vw, 56px)', textTransform: 'uppercase', lineHeight: 0.95, marginBottom: 20 }}>
              Meet The <span style={{ color: 'var(--yellow)' }}>Team</span>
            </h1>
            <p style={{ fontSize: 16, color: 'rgba(255,255,255,0.6)', lineHeight: 1.7, maxWidth: 600, margin: '0 auto' }}>
              The athletes who represent PURE. Driven, disciplined, and never finished.
            </p>
          </motion.div>
        </section>

        {/* Athletes Grid */}
        <section style={{ maxWidth: 1000, margin: '0 auto', padding: '0 32px 80px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
            {ATHLETES.map((athlete, i) => (
              <motion.div key={athlete.name} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6, delay: i * 0.1 }} style={{ position: 'relative', borderRadius: 12, overflow: 'hidden', aspectRatio: '3/4' }}>
                <img src={athlete.img} alt={athlete.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, transparent 40%, rgba(0,0,0,0.8) 100%)' }} />
                <div style={{ position: 'absolute', bottom: 20, left: 20, right: 20 }}>
                  <h3 style={{ fontFamily: 'var(--display)', fontSize: 22, textTransform: 'uppercase', marginBottom: 4 }}>{athlete.name}</h3>
                  <p style={{ fontSize: 13, color: 'var(--yellow)', fontFamily: 'var(--mono)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>{athlete.role}</p>
                  {athlete.instagram !== '#' && (
                    <a href={athlete.instagram} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, marginTop: 10, color: 'rgba(255,255,255,0.5)', fontSize: 13, textDecoration: 'none' }}>
                      <Instagram size={14} /> @profile
                    </a>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section style={{ textAlign: 'center', padding: '0 32px 80px' }}>
          <p style={{ fontSize: 15, color: 'rgba(255,255,255,0.5)', marginBottom: 24 }}>Want to represent PURE? Get in touch.</p>
          <a href="/contact" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '14px 32px', background: 'var(--yellow)', color: '#000', fontFamily: 'var(--display)', fontSize: 13, letterSpacing: '0.06em', textTransform: 'uppercase', textDecoration: 'none', borderRadius: 10, fontWeight: 700 }}>
            Contact Us
          </a>
        </section>

        <CartDrawer />
      </div>
    </>
  );
}
