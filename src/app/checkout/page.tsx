'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CreditCard, Smartphone, Banknote, ShieldCheck, Truck, Lock, Check, ArrowLeft, ArrowRight, MapPin, User, Phone, Mail, Building } from 'lucide-react';
import { useShop, Order } from '@/lib/store';
import ScrollReveal from '@/components/ScrollReveal';

const EASE = [0.23, 1, 0.32, 1] as const;

const PAYMENT_METHODS = [
  { id: 'razorpay', label: 'Razorpay (UPI / Card / Netbanking)', icon: CreditCard, description: 'Pay securely via Razorpay' },
  { id: 'upi', label: 'UPI Direct', icon: Smartphone, description: 'Google Pay, PhonePe, Paytm' },
  { id: 'cod', label: 'Cash on Delivery', icon: Banknote, description: 'Pay when you receive' },
];

const INDIAN_STATES = [
  'Andhra Pradesh', 'Bihar', 'Chandigarh', 'Chhattisgarh', 'Delhi', 'Goa', 'Gujarat', 'Haryana',
  'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
  'Odisha', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telangana', 'Uttar Pradesh', 'West Bengal',
];

export default function CheckoutPage() {
  const { cart, subtotal, discountAmount, shippingFee, gstAmount, grandTotal, appliedCoupon, clearCart, addOrder } = useShop();
  const [step, setStep] = useState<'address' | 'payment' | 'confirm'>('address');
  const [paymentMethod, setPaymentMethod] = useState('razorpay');
  const [isProcessing, setIsProcessing] = useState(false);
  const [orderComplete, setOrderComplete] = useState(false);
  const [orderNumber, setOrderNumber] = useState('');

  const [address, setAddress] = useState({
    name: '', phone: '', email: '', address: '', city: '', state: 'Maharashtra', pincode: '', landmark: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateAddress = () => {
    const errs: Record<string, string> = {};
    if (!address.name.trim()) errs.name = 'Name is required';
    if (!address.phone.trim() || !/^\d{10}$/.test(address.phone.replace(/\D/g, ''))) errs.phone = 'Valid 10-digit phone required';
    if (!address.email.trim() || !/\S+@\S+\.\S+/.test(address.email)) errs.email = 'Valid email required';
    if (!address.address.trim()) errs.address = 'Address is required';
    if (!address.city.trim()) errs.city = 'City is required';
    if (!address.pincode.trim() || !/^\d{6}$/.test(address.pincode)) errs.pincode = 'Valid 6-digit pincode required';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handlePlaceOrder = async () => {
    if (!validateAddress()) return;
    setStep('confirm');
  };

  const handleConfirmOrder = async () => {
    setIsProcessing(true);

    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 2000));

    const ord: Order = {
      id: `ord-${Date.now()}`,
      orderNumber: `PHS-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 9999)).padStart(4, '0')}`,
      date: new Date().toISOString(),
      items: [...cart],
      subtotal,
      discount: discountAmount,
      gst: gstAmount,
      shipping: shippingFee,
      total: grandTotal,
      paymentMethod: paymentMethod as Order['paymentMethod'],
      paymentStatus: paymentMethod === 'cod' ? 'PENDING' : 'PAID',
      orderStatus: 'Processing',
      shippingAddress: { name: address.name, phone: address.phone, email: address.email, address: address.address, city: address.city, state: address.state, pincode: address.pincode },
    };

    addOrder(ord);
    setOrderNumber(ord.orderNumber);
    setOrderComplete(true);
    setIsProcessing(false);
  };

  if (cart.length === 0 && !orderComplete) {
    return (
      <div className="bg-pure-black min-h-screen pt-24 pb-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h1 className="text-3xl font-black text-white uppercase mb-3">Nothing to Checkout</h1>
          <p className="text-gray-500 mb-8">Add items to your cart first.</p>
          <a href="/shop" className="btn-pure inline-flex items-center gap-2 px-8 py-3">Go to Shop</a>
        </div>
      </div>
    );
  }

  if (orderComplete) {
    return (
      <div className="bg-pure-black min-h-screen pt-24 pb-20">
        <div className="max-w-lg mx-auto px-4 text-center">
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', damping: 15, stiffness: 200 }}>
            <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <Check className="w-10 h-10 text-white" />
            </div>
          </motion.div>
          <h1 className="text-3xl font-black text-white uppercase mb-3">Order Placed!</h1>
          <p className="text-gray-400 mb-2">Your order number is</p>
          <p className="text-2xl font-black text-pure-yellow mb-4">{orderNumber}</p>
          <p className="text-sm text-gray-500 mb-8">We&apos;ll send a confirmation to {address.email}. You can track your order in the app.</p>
          <div className="flex gap-3 justify-center">
            <a href="/" className="px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-sm font-bold text-white hover:bg-white/10 transition-colors">Home</a>
            <a href="/shop" className="btn-pure px-6 py-3 rounded-xl text-sm font-bold">Continue Shopping</a>
          </div>
        </div>
      </div>
    );
  }

  const inputClass = (field: string) =>
    `w-full px-4 py-3 bg-white/5 border rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none transition-colors ${
      errors[field] ? 'border-red-500 focus:border-red-500' : 'border-white/10 focus:border-pure-yellow/50'
    }`;

  return (
    <div className="bg-pure-black min-h-screen pt-24 pb-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back */}
        <a href="/cart" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-pure-yellow transition-colors mb-6">
          <ArrowLeft className="w-4 h-4" /> Back to Cart
        </a>

        {/* Progress */}
        <div className="flex items-center gap-4 mb-10">
          {(['address', 'payment', 'confirm'] as const).map((s, i) => (
            <React.Fragment key={s}>
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  step === s ? 'bg-pure-yellow text-pure-black' : i < ['address', 'payment', 'confirm'].indexOf(step) ? 'bg-green-500 text-white' : 'bg-white/10 text-gray-500'
                }`}>
                  {i < ['address', 'payment', 'confirm'].indexOf(step) ? <Check className="w-4 h-4" /> : i + 1}
                </div>
                <span className={`text-xs font-bold uppercase tracking-wider hidden sm:block ${step === s ? 'text-pure-yellow' : 'text-gray-500'}`}>
                  {s === 'address' ? 'Shipping' : s === 'payment' ? 'Payment' : 'Confirm'}
                </span>
              </div>
              {i < 2 && <div className={`flex-1 h-0.5 rounded-full ${i < ['address', 'payment', 'confirm'].indexOf(step) ? 'bg-green-500' : 'bg-white/10'}`} />}
            </React.Fragment>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main */}
          <div className="lg:col-span-2">
            <AnimatePresence mode="wait">
              {/* Address Step */}
              {step === 'address' && (
                <motion.div key="address" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="space-y-6">
                  <h2 className="text-xl font-bold text-white flex items-center gap-2"><MapPin className="w-5 h-5 text-pure-yellow" /> Shipping Address</h2>

                  <div className="grid sm:grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Full Name *</label>
                      <input type="text" placeholder="Rahul Sharma" value={address.name} onChange={(e) => setAddress({ ...address, name: e.target.value })} className={inputClass('name')} />
                      {errors.name && <p className="text-xs text-red-400 mt-1">{errors.name}</p>}
                    </div>
                    <div>
                      <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Phone *</label>
                      <input type="tel" placeholder="98765 43210" value={address.phone} onChange={(e) => setAddress({ ...address, phone: e.target.value })} className={inputClass('phone')} />
                      {errors.phone && <p className="text-xs text-red-400 mt-1">{errors.phone}</p>}
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Email *</label>
                    <input type="email" placeholder="rahul@example.com" value={address.email} onChange={(e) => setAddress({ ...address, email: e.target.value })} className={inputClass('email')} />
                    {errors.email && <p className="text-xs text-red-400 mt-1">{errors.email}</p>}
                  </div>

                  <div>
                    <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Address *</label>
                    <input type="text" placeholder="123 Gym Street, Andheri West" value={address.address} onChange={(e) => setAddress({ ...address, address: e.target.value })} className={inputClass('address')} />
                    {errors.address && <p className="text-xs text-red-400 mt-1">{errors.address}</p>}
                  </div>

                  <div>
                    <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Landmark (optional)</label>
                    <input type="text" placeholder="Near Infinity Mall" value={address.landmark} onChange={(e) => setAddress({ ...address, landmark: e.target.value })} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none focus:border-pure-yellow/50 transition-colors" />
                  </div>

                  <div className="grid sm:grid-cols-3 gap-4">
                    <div>
                      <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1.5">City *</label>
                      <input type="text" placeholder="Mumbai" value={address.city} onChange={(e) => setAddress({ ...address, city: e.target.value })} className={inputClass('city')} />
                      {errors.city && <p className="text-xs text-red-400 mt-1">{errors.city}</p>}
                    </div>
                    <div>
                      <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1.5">State *</label>
                      <select value={address.state} onChange={(e) => setAddress({ ...address, state: e.target.value })} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-pure-yellow/50 transition-colors cursor-pointer">
                        {INDIAN_STATES.map(s => <option key={s} value={s} className="bg-pure-black">{s}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Pincode *</label>
                      <input type="text" placeholder="400001" value={address.pincode} onChange={(e) => setAddress({ ...address, pincode: e.target.value })} className={inputClass('pincode')} />
                      {errors.pincode && <p className="text-xs text-red-400 mt-1">{errors.pincode}</p>}
                    </div>
                  </div>

                  <button onClick={handlePlaceOrder} className="btn-pure px-8 py-3 rounded-xl font-bold text-sm flex items-center gap-2">
                    Continue to Payment <ArrowRight className="w-4 h-4" />
                  </button>
                </motion.div>
              )}

              {/* Payment Step */}
              {step === 'payment' && (
                <motion.div key="payment" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="space-y-6">
                  <h2 className="text-xl font-bold text-white flex items-center gap-2"><CreditCard className="w-5 h-5 text-pure-yellow" /> Payment Method</h2>

                  <div className="space-y-3">
                    {PAYMENT_METHODS.map((pm) => (
                      <button key={pm.id} onClick={() => setPaymentMethod(pm.id)} className={`w-full p-4 rounded-xl border-2 text-left flex items-center gap-4 transition-all ${paymentMethod === pm.id ? 'border-pure-yellow bg-pure-yellow/10' : 'border-white/10 hover:border-white/30 bg-white/5'}`}>
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${paymentMethod === pm.id ? 'bg-pure-yellow text-pure-black' : 'bg-white/10 text-gray-400'}`}>
                          <pm.icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1">
                          <span className="text-sm font-bold text-white block">{pm.label}</span>
                          <span className="text-xs text-gray-500">{pm.description}</span>
                        </div>
                        {paymentMethod === pm.id && <div className="w-5 h-5 bg-pure-yellow rounded-full flex items-center justify-center"><Check className="w-3 h-3 text-pure-black" /></div>}
                      </button>
                    ))}
                  </div>

                  {/* Address Summary */}
                  <div className="glass rounded-xl p-4 border border-white/5">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Shipping to</p>
                    <p className="text-sm text-white">{address.name}</p>
                    <p className="text-xs text-gray-500">{address.address}, {address.city}, {address.state} - {address.pincode}</p>
                    <p className="text-xs text-gray-500">{address.phone} • {address.email}</p>
                  </div>

                  <div className="flex gap-3">
                    <button onClick={() => setStep('address')} className="px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-sm font-bold text-white hover:bg-white/10 transition-colors flex items-center gap-2">
                      <ArrowLeft className="w-4 h-4" /> Back
                    </button>
                    <button onClick={() => setStep('confirm')} className="btn-pure px-8 py-3 rounded-xl font-bold text-sm flex items-center gap-2">
                      Review Order <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Confirm Step */}
              {step === 'confirm' && (
                <motion.div key="confirm" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="space-y-6">
                  <h2 className="text-xl font-bold text-white flex items-center gap-2"><ShieldCheck className="w-5 h-5 text-pure-yellow" /> Review & Confirm</h2>

                  {/* Items */}
                  <div className="glass rounded-xl p-4 border border-white/5 space-y-3">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Order Items</p>
                    {cart.map((item) => (
                      <div key={`${item.product.id}-${item.variant.id}`} className="flex items-center gap-3 py-2 border-b border-white/5 last:border-0">
                        <img src={item.product.image} alt="" className="w-12 h-12 rounded-lg object-cover bg-pure-dark" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-bold text-white truncate">{item.product.name}</p>
                          <p className="text-xs text-gray-500">{item.variant.name} • {item.variant.weight} × {item.quantity}</p>
                        </div>
                        <span className="text-sm font-bold text-pure-yellow">₹{(item.variant.price * item.quantity).toLocaleString('en-IN')}</span>
                      </div>
                    ))}
                  </div>

                  {/* Address */}
                  <div className="glass rounded-xl p-4 border border-white/5">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Shipping Address</p>
                    <p className="text-sm text-white">{address.name}, {address.address}</p>
                    <p className="text-xs text-gray-500">{address.city}, {address.state} - {address.pincode}</p>
                    <p className="text-xs text-gray-500">{address.phone}</p>
                  </div>

                  {/* Payment */}
                  <div className="glass rounded-xl p-4 border border-white/5">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Payment Method</p>
                    <p className="text-sm text-white flex items-center gap-2">
                      {paymentMethod === 'razorpay' && <><CreditCard className="w-4 h-4 text-pure-yellow" /> Razorpay</>}
                      {paymentMethod === 'upi' && <><Smartphone className="w-4 h-4 text-pure-yellow" /> UPI Direct</>}
                      {paymentMethod === 'cod' && <><Banknote className="w-4 h-4 text-pure-yellow" /> Cash on Delivery</>}
                    </p>
                  </div>

                  <div className="flex gap-3">
                    <button onClick={() => setStep('payment')} className="px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-sm font-bold text-white hover:bg-white/10 transition-colors flex items-center gap-2">
                      <ArrowLeft className="w-4 h-4" /> Back
                    </button>
                    <motion.button
                      onClick={handleConfirmOrder}
                      disabled={isProcessing}
                      className="btn-pure px-8 py-3.5 rounded-xl font-bold text-sm flex items-center gap-2 flex-1 justify-center"
                      whileTap={{ scale: 0.98 }}
                    >
                      {isProcessing ? (
                        <span className="flex items-center gap-2">
                          <motion.span className="w-4 h-4 border-2 border-pure-black border-t-transparent rounded-full" animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }} />
                          Processing...
                        </span>
                      ) : (
                        <><Lock className="w-4 h-4" /> Place Order — ₹{grandTotal.toLocaleString('en-IN')}</>
                      )}
                    </motion.button>
                  </div>

                  <p className="text-[10px] text-gray-500 text-center flex items-center justify-center gap-1">
                    <ShieldCheck className="w-3 h-3" /> Your payment is secured with 256-bit SSL encryption
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Sidebar Summary */}
          <div className="lg:col-span-1">
            <div className="glass rounded-2xl p-6 border border-white/5 sticky top-24 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Order Summary</h3>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-gray-400">Subtotal</span><span className="font-bold text-white">₹{subtotal.toLocaleString('en-IN')}</span></div>
                {discountAmount > 0 && <div className="flex justify-between"><span className="text-gray-400">Discount</span><span className="font-bold text-green-400">-₹{discountAmount.toLocaleString('en-IN')}</span></div>}
                <div className="flex justify-between"><span className="text-gray-400">Shipping</span><span className={`font-bold ${shippingFee === 0 ? 'text-green-400' : 'text-white'}`}>{shippingFee === 0 ? 'FREE' : `₹${shippingFee}`}</span></div>
                <div className="flex justify-between"><span className="text-gray-400">GST (18% incl.)</span><span className="font-bold text-white">₹{gstAmount.toLocaleString('en-IN')}</span></div>
              </div>

              <div className="flex justify-between items-baseline pt-3 border-t border-white/10">
                <span className="text-sm font-bold text-white">Total</span>
                <span className="text-xl font-black text-pure-yellow">₹{grandTotal.toLocaleString('en-IN')}</span>
              </div>

              {appliedCoupon && (
                <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-3 text-xs text-green-400 flex items-center gap-2">
                  <Check className="w-3.5 h-3.5" /> {appliedCoupon.code} applied
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
