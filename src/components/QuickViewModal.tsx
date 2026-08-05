'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { X, Star, Check, Minus, Plus, ShieldCheck, Truck, ExternalLink, Zap } from 'lucide-react';
import { useShop, ProductVariant } from '@/lib/store';
import { PARTNER_URL } from './AnnouncementBar';

export default function QuickViewModal() {
  const router = useRouter();
  const { quickViewProduct, setQuickViewProduct, addToCart } = useShop();
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [added, setAdded] = useState(false);

  if (!quickViewProduct) return null;

  const product = quickViewProduct;
  const variant = selectedVariant || product.variants[0];

  const handleAdd = () => {
    addToCart(product, variant, quantity);
    setAdded(true);
    setTimeout(() => {
      setAdded(false);
      setQuickViewProduct(null);
      router.push('/cart');
    }, 400);
  };

  return (
    <AnimatePresence>
      {quickViewProduct && (
        <>
          <motion.div
            className="fixed inset-0 z-[200] bg-black/80 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setQuickViewProduct(null)}
          />
          <motion.div
            className="fixed inset-0 z-[201] flex items-center justify-center p-4"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            <div className="bg-pure-black border border-white/10 rounded-3xl max-w-2xl w-full overflow-hidden shadow-2xl max-h-[90vh] flex flex-col md:flex-row" onClick={(e) => e.stopPropagation()}>
              <button onClick={() => setQuickViewProduct(null)} className="absolute top-4 right-4 z-10 p-2 bg-white/10 hover:bg-white/20 rounded-full text-white transition-colors">
                <X className="w-5 h-5" />
              </button>

              {/* Image */}
              <div className="w-full md:w-1/2 bg-pure-dark p-6 flex items-center justify-center relative">
                <motion.img
                  src={product.image}
                  alt={product.name}
                  className="w-full max-h-72 object-contain rounded-2xl"
                  initial={{ scale: 0.9 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.4 }}
                />
                {product.isBestseller && (
                  <span className="absolute top-4 left-4 bg-pure-yellow text-pure-black text-[10px] font-bold px-2.5 py-1 rounded-full uppercase">Bestseller</span>
                )}
              </div>

              {/* Info */}
              <div className="w-full md:w-1/2 p-6 flex flex-col justify-between overflow-y-auto">
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold bg-pure-yellow/10 text-pure-yellow px-2 py-0.5 rounded-full uppercase">{product.category}</span>
                    {product.flavour && <span className="text-[10px] text-gray-500">• {product.flavour}</span>}
                  </div>
                  
                  <h3 className="text-xl font-bold text-white">{product.name}</h3>
                  
                  <div className="flex items-center gap-2">
                    <div className="flex">{Array.from({ length: 5 }).map((_, i) => <Star key={i} className={`w-3.5 h-3.5 ${i < Math.floor(product.rating) ? 'fill-pure-yellow text-pure-yellow' : 'text-gray-600'}`} />)}</div>
                    <span className="text-xs font-bold text-white">{product.rating}</span>
                    <span className="text-[10px] text-gray-500">({product.reviewCount})</span>
                  </div>

                  <p className="text-xs text-gray-400 line-clamp-3 leading-relaxed">{product.description}</p>

                  {/* Variant */}
                  <div>
                    <label className="text-xs font-bold text-white block mb-2">Package</label>
                    <div className="space-y-1.5">
                      {product.variants.map((v) => (
                        <button key={v.id} onClick={() => setSelectedVariant(v)} className={`w-full p-2.5 rounded-xl border text-xs flex justify-between items-center transition-all ${v.id === variant.id ? 'bg-pure-yellow text-pure-black border-pure-yellow' : 'bg-white/5 text-white border-white/10 hover:border-white/30'}`}>
                          <span className="font-semibold">{v.name} ({v.weight})</span>
                          <span className="font-bold">₹{v.price.toLocaleString('en-IN')}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-3 pt-4 border-t border-white/10 mt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xl font-bold text-pure-yellow">₹{(variant.price * quantity).toLocaleString('en-IN')}</span>
                      {variant.originalPrice > variant.price && (
                        <span className="text-xs text-gray-500 line-through ml-2">₹{(variant.originalPrice * quantity).toLocaleString('en-IN')}</span>
                      )}
                      <span className="text-[10px] text-gray-500 block">18% GST Included</span>
                    </div>
                    <div className="flex items-center border border-white/20 rounded-xl overflow-hidden">
                      <button onClick={() => setQuantity(Math.max(1, quantity - 1))} className="px-2.5 py-1 text-white hover:bg-white/10"><Minus className="w-3 h-3" /></button>
                      <span className="px-3 py-1 text-sm font-bold text-white">{quantity}</span>
                      <button onClick={() => setQuantity(quantity + 1)} className="px-2.5 py-1 text-white hover:bg-white/10"><Plus className="w-3 h-3" /></button>
                    </div>
                  </div>

                  {/* Add to Cart → navigates to /cart */}
                  <motion.button
                    onClick={handleAdd}
                    className="w-full py-3 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 btn-pure text-center"
                    whileTap={{ scale: 0.97 }}
                  >
                    {added ? <><Check className="w-4 h-4" /> Added — Redirecting...</> : <><Zap className="w-4 h-4" /> Add to Cart</>}
                  </motion.button>

                  {/* Buy Now → upgraded.co.in */}
                  <a
                    href={PARTNER_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full py-3 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 btn-pure-outline text-center"
                  >
                    <ExternalLink className="w-4 h-4" /> Buy Now on Upgraded
                  </a>

                  <div className="flex items-center justify-center gap-4 text-[10px] text-gray-500">
                    <span className="flex items-center gap-1"><Truck className="w-3 h-3" /> Free Shipping 999+</span>
                    <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> FSSAI Certified</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
