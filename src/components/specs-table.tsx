'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface SpecsTableProps {
  variant?: string;
}

const EASE = [0.23, 1, 0.32, 1] as const;

const SPECS = [
  {
    category: 'Performance',
    specs: [
      { label: 'Beta-Alanine', value: '1.5g', note: 'Muscular endurance' },
      { label: 'L-Citrulline', value: '500mg', note: 'Blood flow & pumps' },
      { label: 'Arginine Alpha-Ketoglutarate', value: '750mg', note: 'Nitric oxide boost' },
      { label: 'Caffeine Anhydrous', value: '200mg', note: 'Clean energy' },
    ],
  },
  {
    category: 'Recovery',
    specs: [
      { label: 'BCAA 2:1:1', value: '2.5g', note: 'Muscle repair' },
      { label: 'L-Glutamine', value: '1g', note: 'Recovery support' },
      { label: 'Taurine', value: '500mg', note: 'Endurance & focus' },
    ],
  },
  {
    category: 'Nutrition',
    specs: [
      { label: 'Calories', value: '5 kcal', note: 'Per serving' },
      { label: 'Carbohydrates', value: '0g', note: 'Zero sugar' },
      { label: 'Servings Per Container', value: '80', note: 'Value pack' },
    ],
  },
];

export default function SpecsTable({ variant = 'default' }: SpecsTableProps) {
  const [activeCategory, setActiveCategory] = useState(0);

  return (
    <section className="py-16 md:py-20 bg-[#faf9f7]">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <motion.div
          className="text-center mb-10"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: EASE }}
        >
          <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#B08900] mb-2 block">
            Detailed Specs
          </span>
          <h2 className="text-3xl sm:text-4xl font-black uppercase tracking-tight text-[#0a0a0a]">
            What's <span className="text-[#B08900]">Inside</span>
          </h2>
        </motion.div>

        {/* Category tabs */}
        <div className="flex justify-center gap-2 mb-8">
          {SPECS.map((cat, i) => (
            <button
              key={cat.category}
              onClick={() => setActiveCategory(i)}
              className={`px-5 py-2.5 text-xs font-bold uppercase tracking-wider transition-all ${
                activeCategory === i
                  ? 'bg-[#0a0a0a] text-[#ffd100]'
                  : 'bg-white border border-black/10 text-[#0a0a0a]/60 hover:border-[#B08900]/30'
              }`}
            >
              {cat.category}
            </button>
          ))}
        </div>

        {/* Specs grid */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeCategory}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="bg-white border border-black/5 overflow-hidden"
          >
            {SPECS[activeCategory].specs.map((spec, i) => (
              <div
                key={spec.label}
                className={`flex items-center justify-between px-6 py-4 ${
                  i < SPECS[activeCategory].specs.length - 1 ? 'border-b border-black/5' : ''
                }`}
              >
                <div>
                  <p className="text-sm font-bold text-[#0a0a0a]">{spec.label}</p>
                  <p className="text-xs text-[#0a0a0a]/50 mt-0.5">{spec.note}</p>
                </div>
                <span className="text-lg font-black text-[#0a0a0a]">{spec.value}</span>
              </div>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  );
}
