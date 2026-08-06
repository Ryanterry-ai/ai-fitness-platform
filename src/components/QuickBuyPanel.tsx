'use client';

import React, { useState } from 'react';
import Image from '@/components/Image';
import { motion } from 'framer-motion';
import { useShop } from '@/lib/store';
import { PARTNER_URL } from './AnnouncementBar';

const FLAVOUR_COLOUR: Record<string, string> = {
  Orange: '#FF6B00',
  'Fruit Punch': '#E8115A',
  'Rocket Lollipop': '#5B2EED',
};

export default function QuickBuyPanel() {
  const { products, addToCart } = useShop();
  const bestseller = products.find((p) => p.isBestseller) || products[0];
  const [selectedId, setSelectedId] = useState(bestseller?.id);
  const [quantity, setQuantity] = useState(1);
  const [added, setAdded] = useState(false);

  const product = products.find((p) => p.id === selectedId) || bestseller;
  if (!product) return null;

  const variant = product.variants[0];

  const handleAdd = () => {
    addToCart(product, variant, quantity);
    setAdded(true);
    setTimeout(() => setAdded(false), 1600);
  };

  return (
    <section className="wrap">
      <div className="quickbuy" reveal-on-scroll="fade">
        {/* Image */}
        <div className="quickbuy-image">
          {product.isBestseller && <span className="quickbuy-badge">Bestseller</span>}
          <motion.div
            key={product.id}
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.35 }}
            style={{ position: 'absolute', inset: 0 }}
          >
            <Image src={product.image} alt={product.name} fill style={{ objectFit: 'contain', padding: 36 }} sizes="480px" />
          </motion.div>
        </div>

        {/* Buy Box */}
        <div>
          <div className="eyebrow quickbuy-eyebrow">Shop the Range</div>
          <h3>Prime X &mdash; {product.flavour}</h3>
          <p className="quickbuy-tagline">{product.tagline}</p>

          <div className="quickbuy-price">
            <span className="now">₹{variant.price.toLocaleString('en-IN')}</span>
            {variant.originalPrice > variant.price && (
              <span className="was">₹{variant.originalPrice.toLocaleString('en-IN')}</span>
            )}
          </div>

          {/* Flavour dots */}
          <div className="quickbuy-flavours">
            {products.map((p) => {
              const active = p.id === selectedId;
              const dot = FLAVOUR_COLOUR[p.flavour] || 'var(--yellow)';
              return (
                <button
                  key={p.id}
                  className={`quickbuy-dot${active ? ' active' : ''}`}
                  style={{ background: dot }}
                  title={p.flavour}
                  onClick={() => setSelectedId(p.id)}
                  aria-label={p.flavour}
                >
                  {active && (
                    <span style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 14, textShadow: '0 1px 3px rgba(0,0,0,0.5)' }}>
                      ✓
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="quickbuy-actions" style={{ marginBottom: 14 }}>
            <div className="quickbuy-qty">
              <button onClick={() => setQuantity(Math.max(1, quantity - 1))}>−</button>
              <span>{quantity}</span>
              <button onClick={() => setQuantity(quantity + 1)}>+</button>
            </div>
            <button className="btn btn-yellow" style={{ flex: 1 }} onClick={handleAdd}>
              {added ? '✓ Added to Cart' : 'Add to Cart'}
            </button>
          </div>

          <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn btn-ghost" style={{ width: '100%', textAlign: 'center' }}>
            Buy Now on PURE Supps
          </a>
        </div>
      </div>
    </section>
  );
}
