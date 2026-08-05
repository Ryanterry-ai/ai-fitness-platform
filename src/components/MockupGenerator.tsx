'use client';

import React from 'react';
import { motion } from 'framer-motion';

const EASE = [0.23, 1, 0.32, 1] as const;

// ─────────────────────────────────────────────
// 1. PRODUCT ON STYLED BACKGROUND
// ─────────────────────────────────────────────

interface ProductOnBackgroundProps {
  productImage: string;
  variant?: 'dark-gym' | 'neon-energy' | 'minimal-white' | 'fire-gradient' | 'blue-ice' | 'gold-premium';
  className?: string;
  children?: React.ReactNode;
}

const BACKGROUNDS = {
  'dark-gym': {
    bg: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 40%, #16213e 70%, #0a0a0a 100%)',
    glow: 'rgba(255,215,0,0.2)',
    glowPos: '60% 40%',
  },
  'neon-energy': {
    bg: 'linear-gradient(160deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
    glow: 'rgba(139,92,246,0.25)',
    glowPos: '30% 60%',
  },
  'minimal-white': {
    bg: 'linear-gradient(180deg, #fafafa 0%, #f0f0f0 100%)',
    glow: 'rgba(255,215,0,0.1)',
    glowPos: '50% 50%',
  },
  'fire-gradient': {
    bg: 'linear-gradient(135deg, #1a0000 0%, #3d0000 30%, #6b1a1a 60%, #1a0000 100%)',
    glow: 'rgba(255,80,0,0.2)',
    glowPos: '70% 30%',
  },
  'blue-ice': {
    bg: 'linear-gradient(160deg, #0a1628 0%, #0d2847 40%, #1a3a5c 70%, #0a1628 100%)',
    glow: 'rgba(56,189,248,0.2)',
    glowPos: '40% 50%',
  },
  'gold-premium': {
    bg: 'linear-gradient(135deg, #0a0a0a 0%, #1a1500 30%, #2a2000 60%, #0a0a0a 100%)',
    glow: 'rgba(255,215,0,0.3)',
    glowPos: '50% 50%',
  },
};

export function ProductOnBackground({ productImage, variant = 'dark-gym', className = '', children }: ProductOnBackgroundProps) {
  const config = BACKGROUNDS[variant];

  return (
    <div className={`relative overflow-hidden rounded-3xl ${className}`} style={{ background: config.bg }}>
      {/* Glow orb */}
      <div
        className="absolute w-[300px] h-[300px] rounded-full blur-[80px] opacity-60"
        style={{
          background: `radial-gradient(circle, ${config.glow} 0%, transparent 70%)`,
          left: config.glowPos,
          transform: 'translate(-50%, -50%)',
        }}
      />

      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,215,0,0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,215,0,0.3) 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
        }}
      />

      {/* Product image */}
      <motion.img
        src={productImage}
        alt="Product"
        className="relative z-10 w-full h-full object-contain drop-shadow-[0_20px_60px_rgba(0,0,0,0.5)]"
        whileHover={{ scale: 1.03, y: -5 }}
        transition={{ ease: EASE }}
      />

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-black/40 to-transparent z-20 pointer-events-none" />

      {children}
    </div>
  );
}

// ─────────────────────────────────────────────
// 2. HERO IMAGE COMPOSER
// ─────────────────────────────────────────────

interface HeroComposerProps {
  productImage: string;
  logoImage?: string;
  tagline?: string;
  variant?: 'explosion' | 'split' | 'centered' | 'diagonal';
  className?: string;
}

export function HeroComposer({ productImage, logoImage, tagline, variant = 'explosion', className = '' }: HeroComposerProps) {
  if (variant === 'explosion') {
    return (
      <div className={`relative overflow-hidden ${className}`} style={{ background: 'linear-gradient(135deg, #0a0a0b 0%, #1a1a2e 50%, #0a0a0b 100%)' }}>
        {/* Radial burst lines */}
        <div className="absolute inset-0 flex items-center justify-center">
          {Array.from({ length: 12 }).map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-[2px] origin-center"
              style={{
                height: '120%',
                background: `linear-gradient(to bottom, transparent, rgba(255,215,0,${0.03 + (i % 3) * 0.01}), transparent)`,
                transform: `rotate(${i * 30}deg)`,
              }}
              animate={{ opacity: [0.3, 0.6, 0.3] }}
              transition={{ duration: 3, delay: i * 0.2, repeat: Infinity }}
            />
          ))}
        </div>

        {/* Central glow */}
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(255,215,0,0.15) 0%, transparent 60%)' }}
          animate={{ scale: [1, 1.15, 1] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Product */}
        <motion.img
          src={productImage}
          alt="Product"
          className="relative z-10 w-full h-full object-contain"
          initial={{ scale: 0.85, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, ease: EASE }}
        />

        {/* Floating accent particles */}
        {Array.from({ length: 8 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1.5 h-1.5 rounded-full bg-pure-yellow/40"
            style={{
              left: `${15 + Math.random() * 70}%`,
              top: `${10 + Math.random() * 80}%`,
            }}
            animate={{
              y: [0, -20, 0],
              opacity: [0.2, 0.8, 0.2],
              scale: [0.8, 1.2, 0.8],
            }}
            transition={{ duration: 3 + Math.random() * 2, delay: Math.random() * 2, repeat: Infinity }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'split') {
    return (
      <div className={`relative overflow-hidden flex ${className}`} style={{ background: '#0a0a0b' }}>
        {/* Left half - product */}
        <div className="w-1/2 relative">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent to-pure-yellow/5" />
          <img src={productImage} alt="Product" className="w-full h-full object-cover" />
        </div>

        {/* Right half - brand */}
        <div className="w-1/2 flex flex-col items-center justify-center p-8" style={{ background: 'linear-gradient(135deg, #0a0a0b 0%, #1a1500 100%)' }}>
          {logoImage && <img src={logoImage} alt="PURE" className="h-16 mb-6" />}
          <div className="space-y-3 text-center">
            <motion.h2
              className="text-4xl font-black text-white uppercase tracking-tighter"
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              FUEL YOUR<br /><span className="text-pure-yellow">POTENTIAL</span>
            </motion.h2>
            {tagline && (
              <motion.p
                className="text-sm text-gray-400"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                {tagline}
              </motion.p>
            )}
          </div>
        </div>

        {/* Center divider glow */}
        <div className="absolute left-1/2 top-0 bottom-0 w-[2px] -translate-x-1/2" style={{ background: 'linear-gradient(to bottom, transparent, rgba(255,215,0,0.5), transparent)' }} />
      </div>
    );
  }

  if (variant === 'diagonal') {
    return (
      <div className={`relative overflow-hidden ${className}`} style={{ background: '#0a0a0b' }}>
        {/* Diagonal split */}
        <div className="absolute inset-0" style={{
          background: 'linear-gradient(135deg, #0a0a0b 45%, rgba(255,215,0,0.08) 45%, rgba(255,215,0,0.08) 55%, #0a0a0b 55%)',
        }} />

        <img src={productImage} alt="Product" className="relative z-10 w-full h-full object-contain" />

        {/* Corner accents */}
        <div className="absolute top-0 left-0 w-24 h-24 border-l-2 border-t-2 border-pure-yellow/30" />
        <div className="absolute bottom-0 right-0 w-24 h-24 border-r-2 border-b-2 border-pure-yellow/30" />
      </div>
    );
  }

  // centered
  return (
    <div className={`relative overflow-hidden ${className}`} style={{ background: 'radial-gradient(ellipse at center, #1a1500 0%, #0a0a0b 70%)' }}>
      <img src={productImage} alt="Product" className="relative z-10 w-full h-full object-contain" />

      {/* Corner glows */}
      <div className="absolute top-0 left-0 w-32 h-32 rounded-full bg-pure-yellow/5 blur-[60px]" />
      <div className="absolute bottom-0 right-0 w-32 h-32 rounded-full bg-pure-yellow/5 blur-[60px]" />
    </div>
  );
}

// ─────────────────────────────────────────────
// 3. PACKAGING / LABEL MOCKUP
// ─────────────────────────────────────────────

interface PackagingMockupProps {
  productImage: string;
  labelImage?: string;
  variant?: 'jar' | 'pouch' | 'tub';
  className?: string;
}

export function PackagingMockup({ productImage, labelImage, variant = 'jar', className = '' }: PackagingMockupProps) {
  return (
    <div className={`relative flex items-center justify-center ${className}`} style={{ perspective: '1000px' }}>
      <motion.div
        className="relative"
        style={{ transformStyle: 'preserve-3d' }}
        whileHover={{ rotateY: 12, rotateX: -5 }}
        transition={{ ease: EASE, duration: 0.6 }}
      >
        {/* 3D Jar body */}
        <div
          className="relative w-48 h-64 rounded-2xl overflow-hidden"
          style={{
            background: 'linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 50%, #0f0f0f 100%)',
            boxShadow: '20px 20px 60px rgba(0,0,0,0.5), -5px -5px 20px rgba(255,255,255,0.03), inset 0 1px 0 rgba(255,255,255,0.1)',
            transform: 'rotateY(-8deg)',
          }}
        >
          {/* Label area */}
          {labelImage ? (
            <img src={labelImage} alt="Label" className="absolute inset-0 w-full h-full object-cover" />
          ) : (
            <div className="absolute inset-4 flex flex-col items-center justify-center bg-gradient-to-b from-pure-yellow/20 to-transparent rounded-xl border border-pure-yellow/20">
              <img src={productImage} alt="Product" className="w-24 h-24 object-contain mb-2" />
              <div className="text-center">
                <p className="text-[8px] font-black text-pure-yellow uppercase tracking-widest">PURE</p>
                <p className="text-[6px] text-gray-400 uppercase">Health Supps</p>
              </div>
            </div>
          )}

          {/* Shine effect */}
          <div className="absolute top-0 left-0 w-1/3 h-full bg-gradient-to-r from-white/10 to-transparent pointer-events-none" />
        </div>

        {/* Lid */}
        <div
          className="absolute -top-3 -left-1 -right-1 h-8 rounded-t-2xl"
          style={{
            background: 'linear-gradient(180deg, #333 0%, #222 100%)',
            boxShadow: '0 -2px 10px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.15)',
            transform: 'translateZ(5px)',
          }}
        />

        {/* Shadow */}
        <div className="absolute -bottom-6 left-4 right-4 h-8 bg-black/30 rounded-full blur-xl" />
      </motion.div>
    </div>
  );
}

// ─────────────────────────────────────────────
// 4. SOCIAL MEDIA POST GENERATOR
// ─────────────────────────────────────────────

interface SocialPostProps {
  productImage: string;
  logoImage?: string;
  variant?: 'promo' | 'lifestyle' | 'nutrition' | 'testimonial' | 'story';
  headline?: string;
  subtext?: string;
  className?: string;
}

export function SocialPost({ productImage, logoImage, variant = 'promo', headline, subtext, className = '' }: SocialPostProps) {
  if (variant === 'story') {
    return (
      <div className={`relative overflow-hidden aspect-[9/16] max-h-[600px] ${className}`} style={{ background: 'linear-gradient(180deg, #0a0a0b 0%, #1a1500 50%, #0a0a0b 100%)' }}>
        <img src={productImage} alt="Product" className="absolute inset-0 w-full h-full object-cover opacity-40" />
        <div className="absolute inset-0 flex flex-col items-center justify-end p-8 pb-16">
          {logoImage && <img src={logoImage} alt="PURE" className="h-10 mb-4" />}
          <h3 className="text-2xl font-black text-white uppercase text-center mb-2 whitespace-pre-line">{headline || 'FUEL YOUR\nPOTENTIAL'}</h3>
          <p className="text-xs text-gray-400 text-center">{subtext || 'PRIME X Pre-Workout'}</p>
        </div>
        {/* Swipe up indicator */}
        <motion.div
          className="absolute bottom-4 left-1/2 -translate-x-1/2"
          animate={{ y: [0, -8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center pt-2">
            <div className="w-1 h-2 bg-white/50 rounded-full" />
          </div>
        </motion.div>
      </div>
    );
  }

  if (variant === 'nutrition') {
    return (
      <div className={`relative overflow-hidden aspect-square ${className}`} style={{ background: 'linear-gradient(135deg, #0a0a0b 0%, #0f1a0f 100%)' }}>
        <div className="absolute inset-0 flex items-center justify-center opacity-10">
          <div className="text-[200px] font-black text-green-500/20">+</div>
        </div>
        <div className="relative z-10 p-6 h-full flex flex-col justify-between">
          <div>
            {logoImage && <img src={logoImage} alt="PURE" className="h-6 mb-4" />}
            <h3 className="text-lg font-black text-white uppercase">{headline || 'Key Ingredients'}</h3>
          </div>
          <div className="space-y-2">
            {['Beta-Alanine 1.5g', 'L-Citrulline 500mg', 'Caffeine 50mg'].map((item, i) => (
              <div key={i} className="flex items-center gap-2 bg-white/5 rounded-lg px-3 py-2">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span className="text-xs font-bold text-white">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'testimonial') {
    return (
      <div className={`relative overflow-hidden aspect-square ${className}`} style={{ background: 'linear-gradient(135deg, #0a0a0b 0%, #1a1500 100%)' }}>
        <div className="absolute top-0 right-0 w-1/2 h-full">
          <img src={productImage} alt="Product" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-r from-pure-black to-transparent" />
        </div>
        <div className="relative z-10 p-6 h-full flex flex-col justify-center">
          <div className="text-6xl text-pure-yellow/30 font-serif mb-2">&ldquo;</div>
          <p className="text-sm text-white font-medium leading-relaxed mb-4">{headline || 'Best pre-workout I\'ve used. insane pumps and energy.'}</p>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-pure-yellow/20" />
            <div>
              <p className="text-xs font-bold text-white">{subtext || 'Rahul S.'}</p>
              <div className="flex gap-0.5">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="w-2.5 h-2.5 fill-pure-yellow text-pure-yellow">★</div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'lifestyle') {
    return (
      <div className={`relative overflow-hidden aspect-square ${className}`}>
        <img src={productImage} alt="Product" className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-6">
          {logoImage && <img src={logoImage} alt="PURE" className="h-6 mb-3" />}
          <h3 className="text-xl font-black text-white uppercase">{headline || 'Built for Athletes'}</h3>
          <p className="text-xs text-gray-300 mt-1">{subtext || 'Performance. Focus. Energy.'}</p>
        </div>
      </div>
    );
  }

  // promo (default)
  return (
    <div className={`relative overflow-hidden aspect-square ${className}`} style={{ background: 'linear-gradient(135deg, #0a0a0b 0%, #2a2000 50%, #0a0a0b 100%)' }}>
      {/* Corner accents */}
      <div className="absolute top-4 left-4 w-12 h-12 border-l-2 border-t-2 border-pure-yellow/40" />
      <div className="absolute bottom-4 right-4 w-12 h-12 border-r-2 border-b-2 border-pure-yellow/40" />

      <div className="relative z-10 p-6 h-full flex flex-col items-center justify-center text-center">
        <img src={productImage} alt="Product" className="w-2/3 h-2/3 object-contain mb-4" />
        {logoImage && <img src={logoImage} alt="PURE" className="h-5 mb-3" />}
        <h3 className="text-xl font-black text-white uppercase">{headline || 'PRIME X Pre-Workout'}</h3>
        <p className="text-xs text-pure-yellow font-bold mt-1">{subtext || '₹1,299 • 75 Servings'}</p>
      </div>

      {/* Animated border */}
      <motion.div
        className="absolute inset-2 border border-pure-yellow/20 rounded-xl pointer-events-none"
        animate={{ opacity: [0.2, 0.5, 0.2] }}
        transition={{ duration: 3, repeat: Infinity }}
      />
    </div>
  );
}

// ─────────────────────────────────────────────
// 5. LIFESTYLE SCENE COMPOSER
// ─────────────────────────────────────────────

interface LifestyleSceneProps {
  productImage: string;
  scene?: 'gym' | 'outdoor' | 'kitchen' | 'desk' | 'studio';
  className?: string;
}

const SCENE_CONFIGS = {
  gym: {
    bg: 'linear-gradient(135deg, #1a1a1a 0%, #2d1f1f 50%, #1a1a1a 100%)',
    overlay: 'rgba(255,80,0,0.05)',
    accent: '#ff5000',
    icon: '🏋️',
  },
  outdoor: {
    bg: 'linear-gradient(135deg, #0a1a0a 0%, #1a2f1a 50%, #0a1a0a 100%)',
    overlay: 'rgba(34,197,94,0.05)',
    accent: '#22c55e',
    icon: '🌿',
  },
  kitchen: {
    bg: 'linear-gradient(135deg, #1a1510 0%, #2a2015 50%, #1a1510 100%)',
    overlay: 'rgba(255,215,0,0.05)',
    accent: '#FFD700',
    icon: '🥤',
  },
  desk: {
    bg: 'linear-gradient(135deg, #0a0a1a 0%, #15152a 50%, #0a0a1a 100%)',
    overlay: 'rgba(56,189,248,0.05)',
    accent: '#38bdf8',
    icon: '💻',
  },
  studio: {
    bg: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%)',
    overlay: 'rgba(255,255,255,0.03)',
    accent: '#ffffff',
    icon: '📸',
  },
};

export function LifestyleScene({ productImage, scene = 'gym', className = '' }: LifestyleSceneProps) {
  const config = SCENE_CONFIGS[scene];

  return (
    <div className={`relative overflow-hidden rounded-3xl ${className}`} style={{ background: config.bg }}>
      {/* Scene ambient light */}
      <div
        className="absolute inset-0"
        style={{ background: `radial-gradient(ellipse at 50% 30%, ${config.overlay}, transparent 70%)` }}
      />

      {/* Product */}
      <motion.img
        src={productImage}
        alt="Product"
        className="relative z-10 w-full h-full object-contain"
        whileHover={{ scale: 1.05, y: -8 }}
        transition={{ ease: EASE }}
      />

      {/* Scene-specific elements */}
      {scene === 'gym' && (
        <>
          <div className="absolute bottom-0 left-0 right-0 h-1/4 bg-gradient-to-t from-red-900/10 to-transparent" />
          <div className="absolute top-4 right-4 text-2xl opacity-20">🏋️</div>
        </>
      )}
      {scene === 'outdoor' && (
        <div className="absolute top-0 left-0 right-0 h-1/3 bg-gradient-to-b from-green-900/10 to-transparent" />
      )}
      {scene === 'kitchen' && (
        <div className="absolute bottom-4 left-4 text-xl opacity-20">🥤</div>
      )}

      {/* Reflection */}
      <div className="absolute bottom-0 left-0 right-0 h-1/3" style={{
        background: `linear-gradient(to top, ${config.accent}08, transparent)`,
      }} />
    </div>
  );
}
