'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Trash2, Plus, Minus, ShoppingBag, ArrowRight, Tag, Truck, ShieldCheck, Check, ExternalLink } from 'lucide-react';
import { useShop } from '@/lib/store';
import { PARTNER_URL } from './AnnouncementBar';
import { purchaseProduct } from '../lib/purchase';

export default function CartDrawer() {
  const { cart, isCartOpen, setCartOpen, updateQuantity, removeFromCart, subtotal, discountAmount, shippingFee, gstAmount, grandTotal, appliedCoupon, applyCoupon, removeCoupon } = useShop();
  const [couponInput, setCouponInput] = useState('');
  const [couponMsg, setCouponMsg] = useState('');
  const [couponError, setCouponError] = useState('');

  const cartCount = cart.reduce((a, b) => a + b.quantity, 0);
  const freeShippingProgress = Math.min(100, (subtotal / 999) * 100);
  const amountToFreeShipping = Math.max(0, 999 - subtotal);

  const handleApplyCoupon = (e: React.FormEvent) => {
    e.preventDefault();
    setCouponError('');
    setCouponMsg('');
    if (!couponInput.trim()) return;
    const res = applyCoupon(couponInput);
    if (res.success) { setCouponMsg(res.message); setCouponInput(''); }
    else { setCouponError(res.message); }
  };

  return (
    <AnimatePresence>
      {isCartOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setCartOpen(false)}
          />
          
          {/* Drawer */}
          <motion.div
            className="fixed inset-y-0 right-0 z-[101] w-full max-w-md bg-pure-black border-l border-white/10 flex flex-col"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          >
            {/* Header */}
            <div className="p-4 border-b border-white/10 flex items-center justify-between bg-pure-dark">
              <div className="flex items-center gap-3">
                <ShoppingBag className="w-5 h-5 text-pure-yellow" />
                <h3 className="text-lg font-bold text-white">Your Cart</h3>
                <span className="bg-pure-yellow text-pure-black text-xs font-bold px-2 py-0.5 rounded-full">{cartCount}</span>
              </div>
              <button onClick={() => setCartOpen(false)} className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Free Shipping Bar */}
            <div className="p-3 border-b border-white/10 bg-pure-dark/50">
              <div className="flex justify-between items-center text-xs mb-2">
                <span className="flex items-center gap-1 text-gray-300">
                  <Truck className="w-3.5 h-3.5 text-pure-yellow" />
                  {subtotal >= 999 ? (
                    <span className="text-green-400 font-bold">Free Shipping Unlocked!</span>
                  ) : (
                    <span>Add <span className="text-pure-yellow font-bold">₹{amountToFreeShipping}</span> more for Free Shipping</span>
                  )}
                </span>
                <span className="text-pure-yellow font-bold">{Math.round(freeShippingProgress)}%</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
                <motion.div
                  className="bg-pure-yellow h-full rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${freeShippingProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>

            {/* Cart Items */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {cart.length === 0 ? (
                <div className="text-center py-16 space-y-4">
                  <div className="w-20 h-20 mx-auto rounded-full bg-white/5 flex items-center justify-center">
                    <ShoppingBag className="w-10 h-10 text-gray-600" />
                  </div>
                  <h4 className="text-lg font-bold text-white">Your cart is empty</h4>
                  <p className="text-sm text-gray-500">Add some fuel for your training.</p>
                  <button onClick={() => setCartOpen(false)} className="btn-pure">Explore Products</button>
                </div>
              ) : (
                <AnimatePresence>
                  {cart.map((item) => (
                    <motion.div
                      key={`${item.product.id}-${item.variant.id}`}
                      layout
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, x: 100 }}
                      className="flex gap-3 p-3 rounded-xl bg-white/5 border border-white/5"
                    >
                      <img src={item.product.image} alt={item.product.name} className="w-16 h-16 object-cover rounded-lg" />
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="text-sm font-bold text-white truncate">{item.product.name}</h4>
                            <p className="text-xs text-gray-400">{item.variant.name} • {item.variant.weight}</p>
                          </div>
                          <button onClick={() => removeFromCart(item.product.id, item.variant.id)} className="text-gray-500 hover:text-red-400 transition-colors p-1">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        <div className="flex justify-between items-center mt-2">
                          <div className="flex items-center border border-white/20 rounded-lg overflow-hidden">
                            <button onClick={() => updateQuantity(item.product.id, item.variant.id, -1)} className="px-2 py-1 text-white hover:bg-white/10 transition-colors">
                              <Minus className="w-3 h-3" />
                            </button>
                            <span className="px-3 py-1 text-sm font-bold text-white">{item.quantity}</span>
                            <button onClick={() => updateQuantity(item.product.id, item.variant.id, 1)} className="px-2 py-1 text-white hover:bg-white/10 transition-colors">
                              <Plus className="w-3 h-3" />
                            </button>
                          </div>
                          <div className="text-right">
                            <span className="text-sm font-bold text-pure-yellow">₹{(item.variant.price * item.quantity).toLocaleString('en-IN')}</span>
                            {item.variant.originalPrice > item.variant.price && (
                              <span className="text-xs text-gray-500 line-through block">₹{(item.variant.originalPrice * item.quantity).toLocaleString('en-IN')}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              )}
            </div>

            {/* Footer */}
            {cart.length > 0 && (
              <div className="p-4 border-t border-white/10 bg-pure-dark space-y-3">
                {/* Coupon */}
                {appliedCoupon ? (
                  <div className="flex items-center justify-between bg-green-500/10 border border-green-500/30 p-2.5 rounded-xl">
                    <div className="flex items-center gap-2 text-green-400 text-xs font-bold">
                      <Tag className="w-4 h-4" />
                      <span>{appliedCoupon.code} Applied!</span>
                    </div>
                    <button onClick={removeCoupon} className="text-xs text-red-400 font-bold hover:underline">Remove</button>
                  </div>
                ) : (
                  <form onSubmit={handleApplyCoupon} className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Coupon Code"
                      value={couponInput}
                      onChange={(e) => setCouponInput(e.target.value)}
                      className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-pure-yellow/50 uppercase font-mono"
                    />
                    <button type="submit" className="bg-pure-yellow text-pure-black px-4 py-2 rounded-lg text-xs font-bold hover:bg-white transition-colors">Apply</button>
                  </form>
                )}
                {couponError && <p className="text-xs text-red-400">{couponError}</p>}
                {couponMsg && <p className="text-xs text-green-400">{couponMsg}</p>}

                {/* Summary */}
                <div className="space-y-1.5 text-xs pt-2 border-t border-white/10">
                  <div className="flex justify-between text-gray-400"><span>Subtotal</span><span className="text-white">₹{subtotal.toLocaleString('en-IN')}</span></div>
                  {discountAmount > 0 && <div className="flex justify-between text-green-400"><span>Discount</span><span>-₹{discountAmount.toLocaleString('en-IN')}</span></div>}
                  <div className="flex justify-between text-gray-400"><span>GST (18% inclusive)</span><span className="text-gray-500">Included</span></div>
                  <div className="flex justify-between text-gray-400"><span>Shipping</span><span className={shippingFee === 0 ? 'text-green-400 font-bold' : 'text-white'}>{shippingFee === 0 ? 'FREE' : `₹${shippingFee}`}</span></div>
                  <div className="flex justify-between text-sm font-bold text-white pt-2 border-t border-white/10"><span>Total</span><span className="text-pure-yellow">₹{grandTotal.toLocaleString('en-IN')}</span></div>
                </div>

                {/* View Products → upgraded.co.in */}
                <button
                  onClick={() => purchaseProduct('default', { showLoading: true })}
                  className="w-full btn-pure flex items-center justify-center gap-2 text-center"
                >
                  <span>View Products on Upgraded</span>
                  <ExternalLink className="w-4 h-4" />
                </button>
                <div className="flex items-center justify-center gap-1 text-[10px] text-gray-500">
                  <ShieldCheck className="w-3 h-3" />
                  <span>Official PAN India Authorised Partner</span>
                </div>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
