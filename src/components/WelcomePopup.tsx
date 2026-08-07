'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Copy, Check } from 'lucide-react';
import { PARTNER_URL } from './AnnouncementBar';
import Image from './Image';

const COUPON_CODE = 'PRIMEX10';

export default function WelcomePopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const dismissed = sessionStorage.getItem('welcome-popup-dismissed');
    if (!dismissed) {
      const timer = setTimeout(() => setIsOpen(true), 3000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(COUPON_CODE);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name && mobile && email) setSubmitted(true);
  };

  const handleClose = () => {
    setIsOpen(false);
    sessionStorage.setItem('welcome-popup-dismissed', '1');
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
            justifyContent: 'center',
            background: 'rgba(0,0,0,0.75)',
            backdropFilter: 'blur(6px)',
          }}
        >
          {/* Outer wrapper — handles logo + card together */}
          <div style={{ position: 'relative', width: '92%', maxWidth: 820 }}>

            {/* Logo — centered above the card */}
            <div style={{
              position: 'absolute',
              top: -52,
              left: '50%',
              marginLeft: -52,
              zIndex: 30,
              width: 104,
              height: 104,
              borderRadius: '50%',
              background: 'var(--yellow)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 40px rgba(255,209,0,0.4)',
            }}>
              <span style={{
                fontFamily: 'var(--display)',
                fontSize: 38,
                color: '#000',
                letterSpacing: '0.04em',
                lineHeight: 1,
              }}>PURE</span>
            </div>

            {/* Card */}
            <motion.div
              initial={{ scale: 0.92, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.15, ease: [0.23, 1, 0.32, 1] }}
              style={{
                position: 'relative',
                width: '100%',
                minHeight: 460,
                borderRadius: 16,
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'row',
                boxShadow: '0 30px 80px rgba(0,0,0,0.6)',
              }}
            >
              {/* LEFT — Form panel */}
              <div style={{
                flex: '0 0 42%',
                background: '#111',
                padding: '72px 36px 36px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
              }}>
                {!submitted ? (
                  <>
                    <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 10 }}>
                      Welcome to PURE
                    </div>
                    <h2 style={{
                      fontFamily: 'var(--display)',
                      fontSize: 'clamp(26px, 4vw, 34px)',
                      textTransform: 'uppercase',
                      lineHeight: 1.05,
                      marginBottom: 12,
                      color: '#fff',
                    }}>
                      Subscribe &amp; Get<br />
                      <span style={{ color: 'var(--yellow)' }}>10% OFF</span><br />
                      On First Order
                    </h2>
                    <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', lineHeight: 1.6, marginBottom: 24 }}>
                      Enter your details to receive your exclusive discount code.
                    </p>

                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      <input
                        type="text"
                        placeholder="Your Name"
                        required
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '13px 14px',
                          background: 'rgba(255,255,255,0.06)',
                          border: '1px solid rgba(255,255,255,0.12)',
                          borderRadius: 8,
                          color: '#fff',
                          fontFamily: 'var(--body)',
                          fontSize: 13,
                          outline: 'none',
                          transition: 'border-color 0.2s',
                        }}
                        onFocus={(e) => (e.target.style.borderColor = 'var(--yellow)')}
                        onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.12)')}
                      />
                      <input
                        type="tel"
                        placeholder="Mobile Number"
                        required
                        value={mobile}
                        onChange={(e) => setMobile(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '13px 14px',
                          background: 'rgba(255,255,255,0.06)',
                          border: '1px solid rgba(255,255,255,0.12)',
                          borderRadius: 8,
                          color: '#fff',
                          fontFamily: 'var(--body)',
                          fontSize: 13,
                          outline: 'none',
                          transition: 'border-color 0.2s',
                        }}
                        onFocus={(e) => (e.target.style.borderColor = 'var(--yellow)')}
                        onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.12)')}
                      />
                      <input
                        type="email"
                        placeholder="Email Address"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '13px 14px',
                          background: 'rgba(255,255,255,0.06)',
                          border: '1px solid rgba(255,255,255,0.12)',
                          borderRadius: 8,
                          color: '#fff',
                          fontFamily: 'var(--body)',
                          fontSize: 13,
                          outline: 'none',
                          transition: 'border-color 0.2s',
                        }}
                        onFocus={(e) => (e.target.style.borderColor = 'var(--yellow)')}
                        onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.12)')}
                      />
                      <button
                        type="submit"
                        style={{
                          width: '100%',
                          padding: '14px 24px',
                          background: 'var(--yellow)',
                          color: '#000',
                          fontFamily: 'var(--display)',
                          fontSize: 12,
                          letterSpacing: '0.06em',
                          textTransform: 'uppercase',
                          border: 'none',
                          borderRadius: 8,
                          cursor: 'pointer',
                          fontWeight: 700,
                          marginTop: 4,
                          transition: 'transform 0.2s, box-shadow 0.2s',
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.02)'; e.currentTarget.style.boxShadow = '0 0 20px rgba(255,209,0,0.3)'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = 'none'; }}
                      >
                        Send Discount Code
                      </button>
                    </form>
                  </>
                ) : (
                  /* After submit — reveal coupon */
                  <div>
                    <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 10 }}>
                      Your Exclusive Code
                    </div>
                    <h3 style={{ fontFamily: 'var(--display)', fontSize: 28, textTransform: 'uppercase', marginBottom: 16, color: '#fff' }}>
                      You&apos;re In, {name.split(' ')[0]}!
                    </h3>

                    <div
                      onClick={handleCopy}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '16px 20px',
                        background: 'rgba(255,209,0,0.08)',
                        border: '2px dashed rgba(255,209,0,0.4)',
                        borderRadius: 10,
                        cursor: 'pointer',
                        marginBottom: 20,
                        transition: 'border-color 0.2s',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(255,209,0,0.8)')}
                      onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'rgba(255,209,0,0.4)')}
                    >
                      <span style={{ fontFamily: 'var(--display)', fontSize: 30, letterSpacing: '0.1em', color: 'var(--yellow)' }}>
                        {COUPON_CODE}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.5)' }}>
                        {copied ? <><Check size={14} style={{ color: '#22c55e' }} /> Copied</> : <><Copy size={14} /> Copy</>}
                      </span>
                    </div>

                    <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 20 }}>
                      Use this code at checkout on puresupps.site.
                    </p>

                    <a
                      href={PARTNER_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={handleClose}
                      style={{
                        display: 'block',
                        width: '100%',
                        textAlign: 'center',
                        padding: '14px 24px',
                        background: 'var(--yellow)',
                        color: '#000',
                        fontFamily: 'var(--display)',
                        fontSize: 12,
                        letterSpacing: '0.06em',
                        textTransform: 'uppercase',
                        textDecoration: 'none',
                        borderRadius: 8,
                        fontWeight: 700,
                      }}
                    >
                      Continue Shopping
                    </a>
                  </div>
                )}
              </div>

              {/* RIGHT — Product image (all 3 flavours) */}
              <div style={{
                flex: '1 1 58%',
                background: '#000',
                position: 'relative',
                minHeight: 460,
              }}>
                <Image
                  src="/products/product-3flavours.png"
                  alt="PRIME X Pre-Workout — All 3 Flavours"
                  fill
                  style={{ objectFit: 'contain', objectPosition: 'center center' }}
                />
              </div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
