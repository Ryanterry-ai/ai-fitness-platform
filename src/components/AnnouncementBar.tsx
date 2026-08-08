'use client';

import React, { useState, useEffect } from 'react';
import { X, ExternalLink } from 'lucide-react';
import { purchaseProduct } from '../lib/purchase';

const PARTNER_URL = 'https://www.puresupps.site';

const PROMOS = [
  'FREE SHIPPING ON ALL ORDERS ABOVE ₹999',
  'PRIME X — 8 CLINICALLY DOSED INGREDIENTS',
  'ZERO PROPRIETARY BLENDS. FULL TRANSPARENCY.',
  'FSSAI LICENCED. BANNED SUBSTANCE FREE.',
  '80 SERVINGS PER TUB. EVERY FLAVOUR.',
];

export default function AnnouncementBar() {
  const [isVisible, setIsVisible] = useState(true);
  const [currentPromo, setCurrentPromo] = useState(0);

  useEffect(() => {
    if (!isVisible) return;
    const timer = setInterval(() => {
      setCurrentPromo((prev) => (prev + 1) % PROMOS.length);
    }, 3500);
    return () => clearInterval(timer);
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div className="announce-bar">
      <div className="announce-inner">
        <div className="announce-track" style={{ animation: 'none', transform: 'translateX(0)' }}>
          <span>{PROMOS[currentPromo]}</span>
        </div>
        <button
          onClick={() => purchaseProduct('default', { showLoading: true })}
          className="announce-link"
        >
          Shop Now
        </button>
        <button
          onClick={() => setIsVisible(false)}
          className="announce-close"
          aria-label="Close"
        >
          <X size={14} />
        </button>
      </div>
    </div>
  );
}

export { PARTNER_URL };
