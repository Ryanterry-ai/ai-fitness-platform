'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, Minus, Plus, Tag, ShoppingBag, ArrowLeft, ShieldCheck, Truck, X, Check, ArrowRight, ExternalLink } from 'lucide-react';
import Image from '@/components/Image';
import { useShop, CartItem } from '@/lib/store';
import ScrollReveal from '@/components/ScrollReveal';
import { PARTNER_URL } from '@/components/AnnouncementBar';

const EASE = [0.23, 1, 0.32, 1] as const;

export default function CartPage() {
  const { cart, removeFromCart, updateQuantity, clearCart, couponInput, setCouponInput, applyCoupon, removeCoupon, appliedCoupon, subtotal, discountAmount, shippingFee, gstAmount, grandTotal } = useShop();
  const [couponError, setCouponError] = useState('');
  const [couponSuccess, setCouponSuccess] = useState('');

  const handleApplyCoupon = () => {
    const result = applyCoupon(couponInput);
    if (result.success) {
      setCouponSuccess(result.message);
      setCouponError('');
    } else {
      setCouponError(result.message);
      setCouponSuccess('');
    }
  };

  if (cart.length === 0) {
    return (
      <div className="bg-pure-black min-h-screen pt-24 pb-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <img src="/products/empty-cart.svg" alt="Empty Cart" className="w-48 h-48 mx-auto mb-6 opacity-60" />
          <h1 className="text-3xl font-black text-white uppercase mb-3">Your Cart is Empty</h1>
          <p className="text-gray-500 mb-8">Looks like you haven&apos;t added any supplements to your cart yet.</p>
          <a href="/shop" className="btn-pure inline-flex items-center gap-2 px-8 py-3">
            <ShoppingBag className="w-4 h-4" /> Start Shopping
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-pure-black min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl sm:text-4xl font-black text-white uppercase tracking-tight">Your Cart</h1>
            <p className="text-sm text-gray-500 mt-1">{cart.length} {cart.length === 1 ? 'item' : 'items'}</p>
          </div>
          <a href="/shop" className="text-sm text-gray-500 hover:text-pure-yellow transition-colors flex items-center gap-1">
            <ArrowLeft className="w-4 h-4" /> Continue Shopping
          </a>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            <AnimatePresence>
              {cart.map((item, index) => (
                <ScrollReveal key={`${item.product.id}-${item.variant.id}`} delay={Math.min(index * 0.06, 0.4)}>
                  <motion.div
                    className="glass rounded-2xl p-4 sm:p-6 flex flex-col sm:flex-row gap-4 border border-white/5 hover:border-white/10 transition-colors"
                    layout
                    exit={{ opacity: 0, x: -100, scale: 0.9 }}
                    transition={{ ease: EASE }}
                  >
                    {/* Image */}
                    <div className="w-full sm:w-28 h-28 bg-pure-dark rounded-xl overflow-hidden shrink-0 relative">
                      <Image src={item.product.image} alt={item.product.name} fill className="object-cover" sizes="112px" />
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h3 className="text-sm font-bold text-white truncate">{item.product.name}</h3>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {item.variant.name} • {item.variant.weight}
                          </p>
                        </div>
                        <button onClick={() => removeFromCart(item.product.id, item.variant.id)} className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors shrink-0">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="flex items-center justify-between mt-3">
                        {/* Quantity */}
                        <div className="flex items-center border border-white/10 rounded-lg overflow-hidden">
                          <button onClick={() => updateQuantity(item.product.id, item.variant.id, -1)} className="px-3 py-1.5 text-gray-500 hover:bg-white/10 transition-colors"><Minus className="w-3 h-3" /></button>
                          <span className="px-4 py-1.5 text-sm font-bold text-white min-w-[40px] text-center">{item.quantity}</span>
                          <button onClick={() => updateQuantity(item.product.id, item.variant.id, 1)} className="px-3 py-1.5 text-gray-500 hover:bg-white/10 transition-colors"><Plus className="w-3 h-3" /></button>
                        </div>

                        {/* Price */}
                        <div className="text-right">
                          <span className="text-lg font-black text-pure-yellow">₹{(item.variant.price * item.quantity).toLocaleString('en-IN')}</span>
                          {item.variant.originalPrice > item.variant.price && (
                            <span className="text-xs text-gray-500 line-through block">₹{(item.variant.originalPrice * item.quantity).toLocaleString('en-IN')}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </ScrollReveal>
              ))}
            </AnimatePresence>

            {/* Clear Cart */}
            <div className="flex justify-end pt-2">
              <button onClick={clearCart} className="text-xs text-gray-500 hover:text-red-400 transition-colors flex items-center gap-1">
                <Trash2 className="w-3 h-3" /> Clear Cart
              </button>
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="glass rounded-2xl p-6 border border-white/5 sticky top-24 space-y-5">
              <h2 className="text-lg font-bold text-white">Order Summary</h2>

              {/* Coupon */}
              <div>
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-2">Coupon Code</label>
                {appliedCoupon ? (
                  <div className="flex items-center justify-between bg-pure-yellow/10 border border-pure-yellow/30 rounded-xl px-3 py-2">
                    <div className="flex items-center gap-2">
                      <Tag className="w-3.5 h-3.5 text-pure-yellow" />
                      <span className="text-sm font-bold text-pure-yellow">{appliedCoupon.code}</span>
                    </div>
                    <button onClick={removeCoupon} className="text-gray-500 hover:text-white"><X className="w-4 h-4" /></button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Enter code"
                      value={couponInput}
                      onChange={(e) => { setCouponInput(e.target.value.toUpperCase()); setCouponError(''); setCouponSuccess(''); }}
                      className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none focus:border-pure-yellow/50"
                    />
                    <button onClick={handleApplyCoupon} className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs font-bold text-white hover:bg-white/10 transition-colors">Apply</button>
                  </div>
                )}
                {couponError && <p className="text-xs text-red-400 mt-1">{couponError}</p>}
                {couponSuccess && <p className="text-xs text-green-400 mt-1">{couponSuccess}</p>}
              </div>

              {/* Breakdown */}
              <div className="space-y-3 pt-3 border-t border-white/10">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Subtotal</span>
                  <span className="font-bold text-white">₹{subtotal.toLocaleString('en-IN')}</span>
                </div>
                {discountAmount > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Discount</span>
                    <span className="font-bold text-green-400">-₹{discountAmount.toLocaleString('en-IN')}</span>
                  </div>
                )}
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Shipping</span>
                  <span className={`font-bold ${shippingFee === 0 ? 'text-green-400' : 'text-white'}`}>
                    {shippingFee === 0 ? 'FREE' : `₹${shippingFee}`}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">GST (18% incl.)</span>
                  <span className="font-bold text-white">₹{gstAmount.toLocaleString('en-IN')}</span>
                </div>
              </div>

              {/* Total */}
              <div className="flex justify-between items-baseline pt-3 border-t border-white/10">
                <span className="text-sm font-bold text-white">Total</span>
                <span className="text-2xl font-black text-pure-yellow">₹{grandTotal.toLocaleString('en-IN')}</span>
              </div>

              {/* Free Shipping Bar */}
              {subtotal < 999 && (
                <div className="bg-white/5 rounded-xl p-3">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="text-gray-400 flex items-center gap-1"><Truck className="w-3 h-3" /> Free shipping at ₹999</span>
                    <span className="font-bold text-pure-yellow">{Math.round((subtotal / 999) * 100)}%</span>
                  </div>
                  <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-pure-yellow rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(100, (subtotal / 999) * 100)}%` }}
                      transition={{ duration: 0.5, ease: EASE }}
                    />
                  </div>
                </div>
              )}

              {/* View Products → upgraded.co.in */}
              <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure w-full py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 text-center">
                View Products on Upgraded <ExternalLink className="w-4 h-4" />
              </a>

              {/* Trust */}
              <div className="flex items-center justify-center gap-4 text-[10px] text-gray-500 pt-2">
                <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> Official Partner</span>
                <span className="flex items-center gap-1"><Truck className="w-3 h-3" /> PAN India Delivery</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
