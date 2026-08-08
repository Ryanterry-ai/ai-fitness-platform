'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag } from 'lucide-react';
import { purchaseProduct } from '../lib/purchase';

interface StickyCtaBarProps {
  price: number;
  originalPrice?: number;
  productSlug?: string;
}

export default function StickyCtaBar({ price, originalPrice, productSlug = 'default' }: StickyCtaBarProps) {
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);

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

  const handlePurchase = async () => {
    setLoading(true);
    await purchaseProduct(productSlug, { showLoading: true });
    setLoading(false);
  };

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
          className={`sticky-cta-btn ${loading ? 'loading' : ''}`}
          onClick={handlePurchase}
          disabled={loading}
        >
          <ShoppingBag className="w-4 h-4" />
          {loading ? 'Redirecting...' : 'Buy Now'}
        </button>
      </div>
    </div>
  );
}
