'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';

export default function WelcomePopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState<'form' | 'success'>('form');
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const dismissed = localStorage.getItem('pure_popup_dismissed');
    if (!dismissed) {
      const timer = setTimeout(() => setIsOpen(true), 2500);
      return () => clearTimeout(timer);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  // Block Escape — user must fill form
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        e.preventDefault();
        e.stopPropagation();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleEsc, true);
    }
    return () => window.removeEventListener('keydown', handleEsc, true);
  }, [isOpen]);

  // Block back/forward navigation
  useEffect(() => {
    if (isOpen) {
      const handler = () => { history.pushState(null, '', location.href); };
      window.addEventListener('popstate', handler);
      history.pushState(null, '', location.href);
      return () => window.removeEventListener('popstate', handler);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim() || !mobile.trim() || !email.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setIsSubmitting(true);

    try {
      const res = await fetch('/api/send-discount', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), mobile: mobile.trim(), email: email.trim() }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || 'Something went wrong. Please try again.');
        setIsSubmitting(false);
        return;
      }

      setStep('success');
      localStorage.setItem('pure_popup_dismissed', 'true');
    } catch {
      setError('Network error. Please try again.');
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="popup-overlay">
      <div className="popup-fullscreen">
        {/* Full-screen background image */}
        <div className="popup-bg-image">
          <Image
            src="/products/popup-bg.png"
            alt="PRIME X All Flavours"
            fill
            style={{ objectFit: 'cover', objectPosition: 'center center' }}
            priority
          />
        </div>

        {/* Dark gradient panel with form */}
        <div className="popup-form-panel">
          <div className="popup-brand-text">PURE</div>

          {step === 'form' ? (
            <>
              <h2 className="popup-title">
                SUBSCRIBE &amp; GET<br />
                <span className="popup-highlight">20% OFF</span><br />
                ON BUNDLE
              </h2>
              <p className="popup-subtitle">
                Enter your details to receive your exclusive discount code for the Trainer&apos;s Tray Bundle.
              </p>
              <form className="popup-form" onSubmit={handleSubmit}>
                <input
                  type="text"
                  placeholder="Your Name"
                  value={name}
                  onChange={(e) => { setName(e.target.value); setError(''); }}
                  required
                  className="popup-input"
                  autoFocus
                />
                <input
                  type="tel"
                  placeholder="Mobile Number"
                  value={mobile}
                  onChange={(e) => { setMobile(e.target.value); setError(''); }}
                  required
                  className="popup-input"
                />
                <input
                  type="email"
                  placeholder="Email Address"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setError(''); }}
                  required
                  className="popup-input"
                />
                {error && <p className="popup-error">{error}</p>}
                <button type="submit" className="popup-btn" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <span className="popup-spinner" />
                  ) : (
                    'SEND DISCOUNT CODE'
                  )}
                </button>
              </form>
            </>
          ) : (
            <div className="popup-success">
              <div className="popup-success-icon">
                <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="var(--yellow)" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              </div>
              <h2 className="popup-title" style={{ fontSize: 'clamp(22px, 3vw, 30px)' }}>CODE SENT!</h2>
              <p className="popup-subtitle">
                Your exclusive 20% discount code has been sent to your email and WhatsApp. Check your inbox!
              </p>
              <button className="popup-btn" onClick={() => setIsOpen(false)} style={{ marginTop: 20 }}>
                START SHOPPING
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
