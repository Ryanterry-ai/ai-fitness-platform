'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Shield, Beaker, Award, Truck, RotateCcw } from 'lucide-react';

interface FeatureGridProps {
  columns?: string;
  variant?: string;
}

const EASE = [0.23, 1, 0.32, 1] as const;

const features = [
  {
    icon: Beaker,
    title: 'Detailed Specs',
    description: 'Every ingredient, every dose — printed on the tub. No proprietary blends.',
  },
  {
    icon: Zap,
    title: 'Technical Info',
    description: 'Clinically studied dosages. 1.5g Beta-Alanine means 1.5g.',
  },
  {
    icon: Shield,
    title: 'Banned Substance Free',
    description: 'TGRCO screened. Every batch tested for prohibited substances.',
  },
  {
    icon: Award,
    title: 'FSSAI Licensed',
    description: 'Manufactured in FSSAI licensed facility. Full traceability on every batch.',
  },
  {
    icon: Truck,
    title: 'Free Shipping',
    description: 'Free delivery across India on all orders. No hidden fees.',
  },
  {
    icon: RotateCcw,
    title: 'Easy Returns',
    description: '30-day return policy. If you are not satisfied, we got you.',
  },
];

export default function FeatureGrid({
  columns = '3',
  variant = 'default',
}: FeatureGridProps) {
  return (
    <section className="py-16 md:py-20 bg-[#faf9f7]">
      <div className="max-w-[1100px] mx-auto px-4 sm:px-6">
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: EASE }}
        >
          <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#B08900] mb-2 block">
            Why Choose Us
          </span>
          <h2 className="text-3xl sm:text-4xl font-black uppercase tracking-tight text-[#0a0a0a]">
            The PURE <span className="text-[#B08900]">Difference</span>
          </h2>
        </motion.div>

        <div className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-${columns} gap-4`}>
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="group bg-white border border-black/5 p-6 hover:border-[#B08900]/30 transition-all"
              >
                <div className="w-12 h-12 bg-[#ffd100]/10 flex items-center justify-center mb-4 group-hover:bg-[#ffd100]/20 transition-colors">
                  <Icon className="w-6 h-6 text-[#B08900]" />
                </div>
                <h3 className="text-lg font-bold text-[#0a0a0a] uppercase tracking-wide mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-[#0a0a0a]/60 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
