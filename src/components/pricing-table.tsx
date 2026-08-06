'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Check, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface PricingTableProps {
  columns?: string;
  highlight?: string;
  variant?: string;
  tiers?: Array<{ name: string; price: string; features: string[]; highlighted?: boolean }>;
}

const EASE = [0.23, 1, 0.32, 1] as const;

const defaultTiers = [
  {
    name: 'Basic',
    price: '₹1,299',
    features: ['PRIME X Orange (80 servings)', 'Free shipping', 'Standard delivery'],
    highlighted: false,
  },
  {
    name: 'Standard',
    price: '₹2,399',
    features: ['PRIME X Orange + Rocket Lollipop (160 servings)', 'Free shipping', 'Priority delivery', 'Shaker bottle included'],
    highlighted: true,
  },
  {
    name: 'Premium',
    price: '₹3,299',
    features: ['All 3 Flavours (240 servings)', 'Free shipping', 'Priority delivery', 'Shaker bottle + accessories', 'Exclusive merch'],
    highlighted: false,
  },
];

export default function PricingTable({
  columns = '3',
  highlight = '1',
  variant = 'default',
  tiers = defaultTiers,
}: PricingTableProps) {
  return (
    <section className="py-16 md:py-20 bg-[#0a0a0a]">
      <div className="max-w-[1100px] mx-auto px-4 sm:px-6">
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: EASE }}
        >
          <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#ffd100] mb-2 block">
            Pricing
          </span>
          <h2 className="text-3xl sm:text-4xl font-black uppercase tracking-tight text-white">
            Choose Your <span className="text-[#ffd100]">Stack</span>
          </h2>
        </motion.div>

        <div className={`grid grid-cols-1 md:grid-cols-${columns} gap-4`}>
          {tiers.map((tier, i) => (
            <motion.div
              key={tier.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className={`relative p-6 md:p-8 border transition-all ${
                tier.highlighted
                  ? 'bg-[#ffd100] text-[#0a0a0a] border-[#ffd100] scale-105'
                  : 'bg-[#1a1a1a] text-white border-white/10 hover:border-[#ffd100]/30'
              }`}
            >
              {tier.highlighted && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#0a0a0a] text-[#ffd100] text-[10px] font-bold uppercase tracking-wider px-4 py-1">
                  Best Value
                </span>
              )}

              <h3 className="text-lg font-bold uppercase tracking-wider mb-2">{tier.name}</h3>
              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-4xl font-black">{tier.price}</span>
              </div>

              <ul className="space-y-3 mb-8">
                {tier.features.map((feature, j) => (
                  <li key={j} className="flex items-start gap-3">
                    <Check className={`w-4 h-4 mt-0.5 flex-shrink-0 ${tier.highlighted ? 'text-[#0a0a0a]' : 'text-[#ffd100]'}`} />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <Link
                to="/shop"
                className={`w-full inline-flex items-center justify-center gap-2 py-3 text-sm font-bold uppercase tracking-wider transition-colors ${
                  tier.highlighted
                    ? 'bg-[#0a0a0a] text-[#ffd100] hover:bg-[#1a1a1a]'
                    : 'bg-[#ffd100] text-[#0a0a0a] hover:bg-[#fbea9d]'
                }`}
              >
                Shop Now <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
