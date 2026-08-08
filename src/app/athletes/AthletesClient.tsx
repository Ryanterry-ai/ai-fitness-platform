'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Menu, X, Instagram, Send, CheckCircle } from 'lucide-react';
import { purchaseProduct } from '../../lib/purchase';
import CartDrawer from '../../components/CartDrawer';
const BackToTop = React.lazy(() => import('../../components/BackToTop'));

const INSTAGRAM_POSTS = [
  { img: '/products/product-3flavours.png', link: 'https://www.instagram.com/p/puresupps.site', likes: '2.4K' },
  { img: '/products/banner-fruit-punch.jpg', link: 'https://www.instagram.com/p/puresupps.site', likes: '1.8K' },
  { img: '/products/explosive energy.png', link: 'https://www.instagram.com/p/puresupps.site', likes: '3.1K' },
  { img: '/products/Built different.png', link: 'https://www.instagram.com/p/puresupps.site', likes: '2.1K' },
  { img: '/products/banner-orange.jpg', link: 'https://www.instagram.com/p/puresupps.site', likes: '1.6K' },
  { img: '/products/Never Finished.png', link: 'https://www.instagram.com/p/puresupps.site', likes: '2.8K' },
];

export default function AthletesClient() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', phone: '', instagram: '', message: '' });
  const [formSubmitted, setFormSubmitted] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormSubmitted(true);
  };

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
              <button onClick={() => purchaseProduct('default', { showLoading: true })} className="btn-pure" style={{ fontSize: 11, padding: '10px 20px' }}>Shop PRIME X</button>
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
              <button onClick={() => purchaseProduct('default', { showLoading: true })} className="btn-pure" style={{ marginTop: 16 }}>Shop PRIME X</button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Hero */}
        <section style={{ maxWidth: 1000, margin: '0 auto', padding: '80px 32px 60px', textAlign: 'center' }}>
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 16 }}>Our Community</div>
            <h1 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 6vw, 56px)', textTransform: 'uppercase', lineHeight: 0.95, marginBottom: 20 }}>
              Follow <span style={{ color: 'var(--yellow)' }}>PURE</span>
            </h1>
            <p style={{ fontSize: 16, color: 'rgba(255,255,255,0.6)', lineHeight: 1.7, maxWidth: 600, margin: '0 auto' }}>
              Follow us on Instagram for training tips, athlete stories, and product drops.
            </p>
          </motion.div>
        </section>

        {/* Instagram Feed */}
        <section style={{ maxWidth: 1000, margin: '0 auto', padding: '0 32px 80px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
            {INSTAGRAM_POSTS.map((post, i) => (
              <motion.a
                key={i}
                href={post.link}
                target="_blank"
                rel="noopener noreferrer"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
                whileHover={{ scale: 1.02 }}
                style={{ position: 'relative', borderRadius: 12, overflow: 'hidden', aspectRatio: '1/1', cursor: 'pointer', textDecoration: 'none' }}
              >
                <img src={post.img} alt="PURE Instagram post" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, transparent 50%, rgba(0,0,0,0.7) 100%)', opacity: 0 }} className="ig-overlay" />
                <div style={{ position: 'absolute', top: 12, right: 12, background: 'rgba(0,0,0,0.6)', borderRadius: '50%', width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Instagram size={18} style={{ color: '#fff' }} />
                </div>
              </motion.a>
            ))}
          </div>
          <div style={{ textAlign: 'center', marginTop: 32 }}>
            <a
              href="https://instagram.com/puresupps.site"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-pure"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 8, textDecoration: 'none' }}
            >
              <Instagram size={18} /> Follow @puresupps.site
            </a>
          </div>
        </section>

        {/* Apply Form */}
        <section style={{ maxWidth: 600, margin: '0 auto', padding: '0 32px 80px' }}>
          <div style={{ background: 'var(--graphite)', borderRadius: 16, padding: '48px 32px', border: '1px solid var(--line)' }}>
            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(24px, 4vw, 36px)', textTransform: 'uppercase', marginBottom: 12 }}>
                Want to <span style={{ color: 'var(--yellow)' }}>Represent</span> PURE?
              </h2>
              <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)', lineHeight: 1.7 }}>
                Apply to join our team of athletes. We are looking for dedicated individuals who live the PURE lifestyle.
              </p>
            </div>

            {formSubmitted ? (
              <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} style={{ textAlign: 'center', padding: '40px 0' }}>
                <CheckCircle size={48} style={{ color: 'var(--yellow)', marginBottom: 16 }} />
                <h3 style={{ fontFamily: 'var(--display)', fontSize: 24, textTransform: 'uppercase', marginBottom: 8 }}>Application Received</h3>
                <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.6)' }}>We will review your application and get back to you within 48 hours.</p>
              </motion.div>
            ) : (
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <input
                    type="text"
                    placeholder="Full Name"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    style={{ padding: '14px 16px', background: 'rgba(255,255,255,0.06)', border: '1px solid var(--line)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none', transition: 'border-color 0.3s' }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--yellow)'}
                    onBlur={(e) => e.target.style.borderColor = 'var(--line)'}
                  />
                  <input
                    type="email"
                    placeholder="Email Address"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    style={{ padding: '14px 16px', background: 'rgba(255,255,255,0.06)', border: '1px solid var(--line)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none', transition: 'border-color 0.3s' }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--yellow)'}
                    onBlur={(e) => e.target.style.borderColor = 'var(--line)'}
                  />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <input
                    type="tel"
                    placeholder="Phone Number"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    style={{ padding: '14px 16px', background: 'rgba(255,255,255,0.06)', border: '1px solid var(--line)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none', transition: 'border-color 0.3s' }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--yellow)'}
                    onBlur={(e) => e.target.style.borderColor = 'var(--line)'}
                  />
                  <input
                    type="text"
                    placeholder="Instagram Handle"
                    value={formData.instagram}
                    onChange={(e) => setFormData({ ...formData, instagram: e.target.value })}
                    style={{ padding: '14px 16px', background: 'rgba(255,255,255,0.06)', border: '1px solid var(--line)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none', transition: 'border-color 0.3s' }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--yellow)'}
                    onBlur={(e) => e.target.style.borderColor = 'var(--line)'}
                  />
                </div>
                <textarea
                  placeholder="Tell us why you want to represent PURE..."
                  rows={4}
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  style={{ padding: '14px 16px', background: 'rgba(255,255,255,0.06)', border: '1px solid var(--line)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none', resize: 'vertical', transition: 'border-color 0.3s' }}
                  onFocus={(e) => e.target.style.borderColor = 'var(--yellow)'}
                  onBlur={(e) => e.target.style.borderColor = 'var(--line)'}
                />
                <button type="submit" className="btn-pure" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: '16px 32px' }}>
                  <Send size={16} /> Submit Application
                </button>
              </form>
            )}
          </div>
        </section>

        {/* Product CTA */}
        <section style={{ textAlign: 'center', padding: '0 32px 80px' }}>
          <p style={{ fontSize: 15, color: 'rgba(255,255,255,0.5)', marginBottom: 24 }}>Fuel your performance with PRIME X.</p>
          <button
            onClick={() => purchaseProduct('default', { showLoading: true })}
            className="btn-pure"
            style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
          >
            Shop PRIME X
          </button>
        </section>

        <CartDrawer />
      </div>
    </>
  );
}
