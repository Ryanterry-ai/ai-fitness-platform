'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CreditCard, Smartphone, Banknote, ShieldCheck, Lock, Check, Loader2 } from 'lucide-react';
import { useShop } from '@/lib/store';

declare global {
  interface Window {
    Razorpay: any;
  }
}

interface RazorpayPaymentProps {
  amount: number;
  name: string;
  email: string;
  phone: string;
  onSuccess: (paymentId: string) => void;
  onFailure: (error: string) => void;
}

export function initRazorpay() {
  return new Promise((resolve) => {
    if (typeof window !== 'undefined' && window.Razorpay) {
      resolve(true);
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}

export async function handleRazorpayPayment({
  amount,
  name,
  email,
  phone,
  onSuccess,
  onFailure,
}: RazorpayPaymentProps) {
  const res = await initRazorpay();
  if (!res) {
    onFailure('Razorpay SDK failed to load. Check your internet connection.');
    return;
  }

  // In production, this would call your backend to create an order
  // For demo, we simulate the order creation
  const orderId = `order_${Date.now()}`;

  const options = {
    key: (window as any).PureSuppsWPConfig?.razorpayKeyId || import.meta.env?.VITE_RAZORPAY_KEY_ID || 'rzp_test_demo',
    amount: amount * 100, // Razorpay expects paise
    currency: 'INR',
    name: 'PURE HEALTH SUPPS',
    description: `Order for ${name}`,
    image: '/products/logo.png',
    order_id: orderId,
    handler: function (response: any) {
      onSuccess(response.razorpay_payment_id);
    },
    prefill: {
      name,
      email,
      contact: phone,
    },
    notes: {
      address: 'PURE HEALTH SUPPS, India',
    },
    theme: {
      color: '#FFD700',
      backdrop_color: 'rgba(10,10,11,0.8)',
    },
    modal: {
      ondismiss: function () {
        onFailure('Payment cancelled by user.');
      },
      confirm_close: true,
      escape: false,
    },
    config: {
      display: {
        blocks: {
          utib: {
            name: 'Pay using UPI',
            instruments: [
              { method: 'upi' },
            ],
          },
        },
        sequence: ['block.utib'],
        preferences: {
          show_default_blocks: true,
        },
      },
    },
  };

  try {
    const rzp = new window.Razorpay(options);
    rzp.on('payment.failed', function (response: any) {
      onFailure(response.error?.description || 'Payment failed. Please try again.');
    });
    rzp.open();
  } catch (err) {
    onFailure('Payment initialization failed. Please try again.');
  }
}

interface PaymentButtonProps {
  total: number;
  address: { name: string; email: string; phone: string };
  onPaymentSuccess: (paymentId: string) => void;
  onPaymentFailure: (error: string) => void;
}

export function RazorpayButton({ total, address, onPaymentSuccess, onPaymentFailure }: PaymentButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    await handleRazorpayPayment({
      amount: total,
      name: address.name,
      email: address.email,
      phone: address.phone,
      onSuccess: (paymentId) => {
        setLoading(false);
        onPaymentSuccess(paymentId);
      },
      onFailure: (error) => {
        setLoading(false);
        onPaymentFailure(error);
      },
    });
  };

  return (
    <motion.button
      onClick={handleClick}
      disabled={loading}
      className="w-full py-4 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 bg-pure-yellow text-pure-black hover:bg-pure-yellow-light transition-all disabled:opacity-50"
      whileTap={{ scale: 0.98 }}
    >
      {loading ? (
        <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</>
      ) : (
        <><Lock className="w-4 h-4" /> Pay ₹{total.toLocaleString('en-IN')} via Razorpay</>
      )}
    </motion.button>
  );
}

interface UPIPaymentProps {
  total: number;
  onSuccess: (upiId: string) => void;
}

export function UPIPayment({ total, onSuccess }: UPIPaymentProps) {
  const [upiId, setUpiId] = useState('');
  const [verifying, setVerifying] = useState(false);

  const handlePay = async () => {
    if (!upiId || !upiId.includes('@')) return;
    setVerifying(true);
    // Simulate UPI verification
    await new Promise(r => setTimeout(r, 1500));
    setVerifying(false);
    onSuccess(upiId);
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="your@upi-id"
          value={upiId}
          onChange={(e) => setUpiId(e.target.value)}
          className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none focus:border-pure-yellow/50 transition-colors"
        />
        <motion.button
          onClick={handlePay}
          disabled={verifying || !upiId.includes('@')}
          className="px-6 py-3 bg-pure-yellow text-pure-black rounded-xl text-sm font-bold flex items-center gap-2 disabled:opacity-50"
          whileTap={{ scale: 0.95 }}
        >
          {verifying ? <Loader2 className="w-4 h-4 animate-spin" /> : <Smartphone className="w-4 h-4" />}
          Pay
        </motion.button>
      </div>
      <p className="text-[10px] text-gray-500 flex items-center gap-1">
        <ShieldCheck className="w-3 h-3" /> You will receive a payment request on your UPI app
      </p>
    </div>
  );
}

interface CODConfirmationProps {
  onConfirm: () => void;
}

export function CODConfirmation({ onConfirm }: CODConfirmationProps) {
  return (
    <div className="space-y-3">
      <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
        <p className="text-sm text-yellow-400 font-bold flex items-center gap-2 mb-1">
          <Banknote className="w-4 h-4" /> Cash on Delivery
        </p>
        <p className="text-xs text-gray-400">
          Pay ₹{`{amount}`} when your order arrives. Please keep exact change ready.
          COD orders may take 1-2 additional days to process.
        </p>
      </div>
      <motion.button
        onClick={onConfirm}
        className="w-full py-3 bg-white/5 border border-white/10 rounded-xl text-sm font-bold text-white hover:bg-white/10 transition-colors flex items-center justify-center gap-2"
        whileTap={{ scale: 0.98 }}
      >
        <Check className="w-4 h-4" /> Confirm COD Order
      </motion.button>
    </div>
  );
}
