'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ShoppingBag } from 'lucide-react';
import { Link } from 'react-router-dom';

interface CTASectionProps {
  variant?: string;
}

const EASE = [0.23, 1, 0.32, 1] as const;

export default function CTASection({ variant = 'default' }: CTASectionProps) {
  return (
    <section className="relative py-20 md:py-28 bg-[#0a0a0a] overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#ffd100]/5 rounded-full blur-[120px]" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: EASE }}
        >
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-black uppercase tracking-tighter text-white mb-6">
            Ready to Get <span className="text-[#ffd100]">Started</span>?
          </h2>
          <p className="text-lg text-gray-400 max-w-xl mx-auto mb-10">
            Shop our range of premium pre-workouts. Free shipping on all orders across India.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/shop"
              className="inline-flex items-center gap-2 px-8 py-4 bg-[#ffd100] text-[#0a0a0a] text-sm font-bold uppercase tracking-wider hover:bg-[#fbea9d] transition-colors"
            >
              <ShoppingBag className="w-4 h-4" /> Shop Now <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/contact"
              className="inline-flex items-center gap-2 px-8 py-4 border border-white/20 text-white text-sm font-bold uppercase tracking-wider hover:border-[#ffd100]/50 hover:text-[#ffd100] transition-colors"
            >
              Contact Us
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
