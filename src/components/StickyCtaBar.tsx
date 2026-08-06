'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag } from 'lucide-react';

interface StickyCtaBarProps {
  price: number;
  originalPrice?: number;
  onAddToCart: () => void;
  added: boolean;
}

export default function StickyCtaBar({ price, originalPrice, onAddToCart, added }: StickyCtaBarProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      const scrollY = window.scrollY;
      const windowH = window.innerHeight;
      setVisible(scrollY > windowH * 0.5);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

  return (
    <div className={`sticky-cta-bar ${visible ? 'visible' : ''}`}>
      <div className="sticky-cta-bar-inner">
        <div className="sticky-cta-price">
          <span className="now">{fmt(price)}</span>
          {originalPrice && originalPrice > price && (
            <span className="was">{fmt(originalPrice)}</span>
          )}
        </div>
        <button
          className={`sticky-cta-btn ${added ? 'added' : ''}`}
          onClick={onAddToCart}
        >
          <ShoppingBag className="w-4 h-4" />
          {added ? '✓ Added' : 'Add to Cart'}
        </button>
      </div>
    </div>
  );
}
