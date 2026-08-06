'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Menu, X } from 'lucide-react';
import { PARTNER_URL } from '../../components/AnnouncementBar';
import CartDrawer from '../../components/CartDrawer';
const BackToTop = React.lazy(() => import('../../components/BackToTop'));

const DEPARTMENTS = [
  { title: 'Customer Support', desc: 'Order issues, product questions, returns', email: 'puresupps.site@gmail.com' },
  { title: 'Dealer Enquiry', desc: 'Wholesale and distribution partnerships', email: 'dealers@puresupps.site' },
  { title: 'Wholesale', desc: 'Bulk orders and gym partnerships', email: 'wholesale@puresupps.site' },
  { title: 'General', desc: 'Brand collaborations, media, everything else', email: 'hello@puresupps.site' },
];

export default function ContactClient() {
  const [formData, setFormData] = useState({ name: '', email: '', subject: 'support', message: '' });
  const [submitted, setSubmitted] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
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
            <a href="/shop">Products</a>
            <a href="/formula">Formula</a>
            <a href="/why-pure">Why PURE</a>
            <a href="/stack-save">Stack & Save</a>
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
            <a href="/shop" onClick={() => setMobileMenuOpen(false)}>Products</a>
            <a href="/formula" onClick={() => setMobileMenuOpen(false)}>Formula</a>
            <a href="/why-pure" onClick={() => setMobileMenuOpen(false)}>Why PURE</a>
            <a href="/stack-save" onClick={() => setMobileMenuOpen(false)}>Stack & Save</a>
            <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ marginTop: 16 }}>Shop PRIME X</a>
          </motion.div>
        )}
      </AnimatePresence>

      <div style={{ background: '#000', minHeight: '100vh', color: '#fff', paddingTop: 0 }}>
      {/* ═══ HERO ═══ */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 32px 60px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(255,209,0,0.1)', border: '1px solid rgba(255,209,0,0.2)', borderRadius: 999, padding: '6px 18px', marginBottom: 20 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>Contact</span>
        </div>
        <h1 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(40px, 7vw, 72px)', textTransform: 'uppercase', lineHeight: 1, letterSpacing: '-0.02em', marginBottom: 16 }}>
          Get in <span style={{ color: 'var(--yellow)' }}>touch</span>.
        </h1>
        <p style={{ fontFamily: 'var(--body)', fontSize: 17, color: 'rgba(255,255,255,0.5)', lineHeight: 1.7, maxWidth: 480 }}>
          Questions about PRIME X? Wholesale pricing? We&apos;re here to help.
        </p>
      </section>

      {/* ═══ CONTACT METHODS ═══ */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px 60px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
          {[
            { icon: '📞', label: 'Phone', value: '+91 95575 13017', href: 'tel:+919557513017' },
            { icon: '✉️', label: 'Email', value: 'puresupps.site@gmail.com', href: 'mailto:puresupps.site@gmail.com' },
            { icon: '📍', label: 'Location', value: 'India', href: '#' },
            { icon: '⏰', label: 'Response', value: 'Within 24 hours', href: '#' },
          ].map((m) => (
            <a key={m.label} href={m.href} style={{ padding: '24px 20px', background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, textDecoration: 'none', color: '#fff', transition: 'all 0.2s ease', display: 'block' }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'rgba(255,209,0,0.2)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'; }}
            >
              <div style={{ fontSize: 24, marginBottom: 10 }}>{m.icon}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>{m.label}</div>
              <div style={{ fontFamily: 'var(--body)', fontSize: 13, fontWeight: 600 }}>{m.value}</div>
            </a>
          ))}
        </div>
      </section>

      {/* ═══ MAIN CONTENT ═══ */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px 80px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: 48, alignItems: 'start' }}>
          {/* LEFT — Departments */}
          <div>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 24, textTransform: 'uppercase', marginBottom: 24 }}>Departments</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {DEPARTMENTS.map((d) => (
                <div key={d.title} style={{ padding: '20px', background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10 }}>
                  <div style={{ fontFamily: 'var(--body)', fontSize: 15, fontWeight: 700, marginBottom: 4 }}>{d.title}</div>
                  <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 8 }}>{d.desc}</div>
                  <a href={`mailto:${d.email}`} style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--yellow)', textDecoration: 'none' }}>{d.email}</a>
                </div>
              ))}
            </div>
          </div>

          {/* RIGHT — Form */}
          <div style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, padding: '36px 32px' }}>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 24, textTransform: 'uppercase', marginBottom: 28 }}>Send a Message</h2>

            {submitted ? (
              <div style={{ textAlign: 'center', padding: '60px 0' }}>
                <div style={{ fontSize: 40, marginBottom: 12 }}>✓</div>
                <h3 style={{ fontFamily: 'var(--display)', fontSize: 22, textTransform: 'uppercase', marginBottom: 8 }}>Message Sent!</h3>
                <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.45)' }}>We will get back to you within 24 hours.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div>
                    <label style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>Name</label>
                    <input type="text" required value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      style={{ width: '100%', padding: '14px 16px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontFamily: 'var(--body)', fontSize: 14, outline: 'none', borderRadius: 6 }}
                      placeholder="Your name" />
                  </div>
                  <div>
                    <label style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>Email</label>
                    <input type="email" required value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      style={{ width: '100%', padding: '14px 16px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontFamily: 'var(--body)', fontSize: 14, outline: 'none', borderRadius: 6 }}
                      placeholder="your@email.com" />
                  </div>
                </div>

                <div>
                  <label style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>Department</label>
                  <select value={formData.subject} onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    style={{ width: '100%', padding: '14px 16px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontFamily: 'var(--body)', fontSize: 14, outline: 'none', borderRadius: 6 }}>
                    <option value="support">Customer Support</option>
                    <option value="dealer">Dealer Enquiry</option>
                    <option value="wholesale">Wholesale</option>
                    <option value="general">General</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>Message</label>
                  <textarea required rows={5} value={formData.message} onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    style={{ width: '100%', padding: '14px 16px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontFamily: 'var(--body)', fontSize: 14, outline: 'none', borderRadius: 6, resize: 'none' }}
                    placeholder="How can we help?" />
                </div>

                <button type="submit" style={{ padding: '16px 32px', background: 'var(--yellow)', color: '#000', fontFamily: 'var(--display)', fontSize: 14, letterSpacing: '0.06em', textTransform: 'uppercase', border: 'none', cursor: 'pointer', borderRadius: 6, fontWeight: 700, alignSelf: 'flex-start', transition: 'all 0.25s ease' }}>
                  Send Message
                </button>
              </form>
            )}
          </div>
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
