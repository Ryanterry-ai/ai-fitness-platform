'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Menu, X, Mail, Phone, MapPin } from 'lucide-react';
import { PARTNER_URL } from '../../components/AnnouncementBar';
import CartDrawer from '../../components/CartDrawer';
const BackToTop = React.lazy(() => import('../../components/BackToTop'));

export default function WholesaleClient() {
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
              <a href="/wholesale" style={{ color: 'var(--paper)' }}>Wholesale &amp; Retails</a>
              <a href="/contact">Contact Us</a>
              <a href="/athletes">Our Athletes</a>
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
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 16 }}>Wholesale &amp; Retails</div>
            <h1 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 6vw, 56px)', textTransform: 'uppercase', lineHeight: 0.95, marginBottom: 20 }}>
              Partner With <span style={{ color: 'var(--yellow)' }}>PURE</span>
            </h1>
            <p style={{ fontSize: 16, color: 'rgba(255,255,255,0.6)', lineHeight: 1.7, maxWidth: 600, margin: '0 auto' }}>
              We are looking for retail partners, gym owners, and distributors across India. Competitive margins, marketing support, and a brand that sells itself.
            </p>
          </motion.div>
        </section>

        {/* Benefits */}
        <section style={{ maxWidth: 1000, margin: '0 auto', padding: '0 32px 60px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 32 }}>
            {[
              { title: 'Competitive Margins', desc: 'Industry-leading wholesale pricing with volume-based tier discounts.' },
              { title: 'Marketing Support', desc: 'POS materials, social media assets, and co-branded campaigns.' },
              { title: 'Fast Logistics', desc: 'Direct-from-warehouse shipping with 3-5 day delivery across India.' },
            ].map((item, i) => (
              <motion.div key={item.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6, delay: i * 0.1 }} style={{ padding: '32px 24px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10 }}>
                <h3 style={{ fontFamily: 'var(--heading)', fontSize: 18, textTransform: 'uppercase', marginBottom: 10 }}>{item.title}</h3>
                <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)', lineHeight: 1.6 }}>{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Contact */}
        <section style={{ maxWidth: 600, margin: '0 auto', padding: '0 32px 80px', textAlign: 'center' }}>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 28, textTransform: 'uppercase', marginBottom: 24 }}>Get In Touch</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <a href="mailto:wholesale@puresupps.site" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, color: 'rgba(255,255,255,0.6)', textDecoration: 'none', fontSize: 15 }}><Mail size={18} style={{ color: 'var(--yellow)' }} /> wholesale@puresupps.site</a>
            <a href="tel:+919557513017" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, color: 'rgba(255,255,255,0.6)', textDecoration: 'none', fontSize: 15 }}><Phone size={18} style={{ color: 'var(--yellow)' }} /> +91 95575 13017</a>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, color: 'rgba(255,255,255,0.6)', fontSize: 15 }}><MapPin size={18} style={{ color: 'var(--yellow)' }} /> India</div>
          </div>
        </section>

        <CartDrawer />
      </div>
    </>
  );
}
