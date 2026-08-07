'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Copy, Check } from 'lucide-react';
import { PARTNER_URL } from './AnnouncementBar';
import Image from './Image';

const COUPON_CODE = 'PRIMEX10';

export default function WelcomePopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const dismissed = sessionStorage.getItem('welcome-popup-dismissed');
    if (!dismissed) {
      const timer = setTimeout(() => setIsOpen(true), 3000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleClose = () => {
    setIsOpen(false);
    sessionStorage.setItem('welcome-popup-dismissed', '1');
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(COUPON_CODE);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) setSubmitted(true);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            flexDirection: 'column',
          }}
        >
          {/* Background image */}
          <div style={{ position: 'absolute', inset: 0 }}>
            <Image src="/products/popup-bg.png" alt="" fill style={{ objectFit: 'cover' }} />
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.75) 40%, #000 78%)' }} />
          </div>

          {/* Close button */}
          <button
            onClick={handleClose}
            style={{
              position: 'absolute',
              top: 20,
              right: 20,
              zIndex: 20,
              width: 40,
              height: 40,
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.2)',
              color: '#fff',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.2)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.1)')}
          >
            <X size={20} />
          </button>

          {/* Form panel — slides up from bottom */}
          <motion.div
            initial={{ y: 60, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.23, 1, 0.32, 1] }}
            style={{
              position: 'relative',
              zIndex: 10,
              width: '100%',
              maxWidth: 520,
              margin: '0 auto',
              padding: '40px 32px calc(32px + env(safe-area-inset-bottom, 0px))',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'flex-end',
              maxHeight: '82vh',
            }}
          >
            {!submitted ? (
              <>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 12 }}>
                  Welcome to PURE
                </div>
                <h2 className="popup-title" style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 7vw, 44px)', textTransform: 'uppercase', lineHeight: 1, marginBottom: 16, color: '#fff' }}>
                  Get <span style={{ color: 'var(--yellow)' }}>10% OFF</span><br />Your First Order
                </h2>
                <p className="popup-subtitle" style={{ fontSize: 15, color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, marginBottom: 28 }}>
                  Enter your email to receive your exclusive discount code. Use it at checkout on puresupps.site.
                </p>

                {/* Coupon code */}
                <div
                  onClick={handleCopy}
                  className="popup-coupon"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '18px 24px',
                    background: 'rgba(255,209,0,0.06)',
                    border: '2px dashed rgba(255,209,0,0.3)',
                    borderRadius: 10,
                    cursor: 'pointer',
                    marginBottom: 24,
                    transition: 'border-color 0.2s',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(255,209,0,0.6)')}
                  onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'rgba(255,209,0,0.3)')}
                >
                  <span style={{ fontFamily: 'var(--display)', fontSize: 30, letterSpacing: '0.1em', color: 'var(--yellow)' }}>
                    {COUPON_CODE}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--mono)', fontSize: 12, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.05em' }}>
                    {copied ? <><Check size={14} style={{ color: '#22c55e' }} /> Copied</> : <><Copy size={14} /> Copy</>}
                  </span>
                </div>

                {/* Email form */}
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  <input
                    type="email"
                    placeholder="your@email.com"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '16px 18px',
                      background: 'rgba(255,255,255,0.06)',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: 10,
                      color: '#fff',
                      fontFamily: 'var(--body)',
                      fontSize: 15,
                      outline: 'none',
                      transition: 'border-color 0.2s',
                    }}
                    onFocus={(e) => (e.target.style.borderColor = 'rgba(255,209,0,0.4)')}
                    onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.12)')}
                  />
                  <button
                    type="submit"
                    style={{
                      width: '100%',
                      padding: '16px 24px',
                      background: 'var(--yellow)',
                      color: '#000',
                      fontFamily: 'var(--display)',
                      fontSize: 14,
                      letterSpacing: '0.06em',
                      textTransform: 'uppercase',
                      border: 'none',
                      borderRadius: 10,
                      cursor: 'pointer',
                      fontWeight: 700,
                      transition: 'transform 0.2s, box-shadow 0.2s',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.02)'; e.currentTarget.style.boxShadow = '0 0 24px rgba(255,209,0,0.3)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = 'none'; }}
                  >
                    Get My Discount
                  </button>
                </form>

                <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', textAlign: 'center', marginTop: 16 }}>
                  No spam. Just performance updates and exclusive offers.
                </p>
              </>
            ) : (
              <div className="popup-success" style={{ textAlign: 'center', padding: '24px 0' }}>
                <div className="popup-success-icon" style={{ fontSize: 56, marginBottom: 16 }}>✓</div>
                <h3 style={{ fontFamily: 'var(--display)', fontSize: 28, textTransform: 'uppercase', marginBottom: 10, color: '#fff' }}>
                  You&apos;re In!
                </h3>
                <p style={{ fontSize: 15, color: 'rgba(255,255,255,0.5)', marginBottom: 28 }}>
                  Your discount code <strong style={{ color: 'var(--yellow)' }}>{COUPON_CODE}</strong> is ready. Use it at checkout.
                </p>
                <a
                  href={PARTNER_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={handleClose}
                  style={{
                    display: 'inline-block',
                    padding: '16px 36px',
                    background: 'var(--yellow)',
                    color: '#000',
                    fontFamily: 'var(--display)',
                    fontSize: 14,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    textDecoration: 'none',
                    borderRadius: 10,
                    fontWeight: 700,
                  }}
                >
                  Shop Now
                </a>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
