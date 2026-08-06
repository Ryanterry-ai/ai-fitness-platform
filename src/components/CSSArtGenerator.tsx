'use client';

import React from 'react';
import { motion } from 'framer-motion';

const EASE = [0.23, 1, 0.32, 1] as const;

// ─────────────────────────────────────────────
// 1. CSS PRODUCT JAR — pure CSS art, no images
// ─────────────────────────────────────────────

interface CSSJarProps {
  variant?: 'preworkout' | 'shaker';
  size?: number;
  className?: string;
  animate?: boolean;
}

export function CSSJar({ variant = 'preworkout', size = 200, className = '', animate = true }: CSSJarProps) {
  const isPreworkout = variant === 'preworkout';

  return (
    <motion.div
      className={`relative ${className}`}
      style={{ width: size, height: size * 1.4 }}
      animate={animate ? { y: [0, -10, 0] } : undefined}
      transition={animate ? { duration: 4, repeat: Infinity, ease: 'easeInOut' } : undefined}
    >
      {/* Jar body */}
      <div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 rounded-2xl overflow-hidden"
        style={{
          width: size * 0.7,
          height: size * 1.1,
          background: isPreworkout
            ? 'linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 40%, #1a1a1a 60%, #0a0a0a 100%)'
            : 'linear-gradient(180deg, #222 0%, #1a1a1a 50%, #111 100%)',
          boxShadow: `
            inset 2px 0 8px rgba(255,255,255,0.05),
            inset -2px 0 8px rgba(0,0,0,0.3),
            8px 8px 30px rgba(0,0,0,0.5),
            -4px -4px 15px rgba(255,255,255,0.02)
          `,
        }}
      >
        {/* Label area */}
        <div
          className="absolute left-1/2 -translate-x-1/2 rounded-lg overflow-hidden"
          style={{
            top: '25%',
            width: '85%',
            height: '50%',
            background: 'linear-gradient(180deg, #FFD700 0%, #F5C518 50%, #E6B800 100%)',
            boxShadow: '0 2px 10px rgba(255,215,0,0.3)',
          }}
        >
          {/* Label content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center p-2">
            <div
              className="font-black text-black uppercase tracking-wider leading-none"
              style={{ fontSize: size * 0.08 }}
            >
              PURE
            </div>
            <div
              className="text-black/60 uppercase tracking-widest"
              style={{ fontSize: size * 0.035 }}
            >
              HEALTH SUPPS
            </div>
            <div
              className="mt-1 px-2 py-0.5 bg-black/10 rounded text-black font-bold uppercase"
              style={{ fontSize: size * 0.04 }}
            >
              {isPreworkout ? 'PRIME X' : 'SHAKER'}
            </div>
            {isPreworkout && (
              <div className="mt-1 text-black/50 uppercase" style={{ fontSize: size * 0.03 }}>
                280g • 75 Servings
              </div>
            )}
          </div>

          {/* Label shine */}
          <div className="absolute top-0 left-0 w-1/3 h-full bg-gradient-to-r from-white/20 to-transparent" />
        </div>

        {/* Jar shine */}
        <div className="absolute top-0 left-0 w-1/4 h-full bg-gradient-to-r from-white/8 to-transparent" />
      </div>

      {/* Lid */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 rounded-t-xl"
        style={{
          width: size * 0.74,
          height: size * 0.12,
          background: 'linear-gradient(180deg, #333 0%, #222 50%, #1a1a1a 100%)',
          boxShadow: '0 -2px 10px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.15)',
        }}
      >
        {/* Lid ridges */}
        <div className="absolute inset-x-2 top-1/2 -translate-y-1/2 flex gap-[2px]">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="flex-1 h-[2px] bg-white/5 rounded-full" />
          ))}
        </div>
      </div>

      {/* Shadow */}
      <div
        className="absolute -bottom-4 left-1/2 -translate-x-1/2 bg-black/20 rounded-full blur-xl"
        style={{ width: size * 0.6, height: size * 0.1 }}
      />
    </motion.div>
  );
}

// ─────────────────────────────────────────────
// 2. CSS SHAKER BOTTLE — pure CSS art
// ─────────────────────────────────────────────

interface CSSShakerProps {
  size?: number;
  className?: string;
}

export function CSSShaker({ size = 160, className = '' }: CSSShakerProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      style={{ width: size, height: size * 1.6 }}
      animate={{ y: [0, -8, 0], rotate: [0, 2, 0, -2, 0] }}
      transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
    >
      {/* Bottle body */}
      <div
        className="absolute bottom-0 left-1/2 -translate-x-1/2"
        style={{
          width: size * 0.55,
          height: size * 1.2,
          background: 'linear-gradient(180deg, rgba(30,30,30,0.9) 0%, rgba(20,20,20,0.95) 50%, rgba(15,15,15,0.9) 100%)',
          borderRadius: `${size * 0.08}px ${size * 0.08}px ${size * 0.12}px ${size * 0.12}px`,
          boxShadow: `
            inset 3px 0 10px rgba(255,255,255,0.05),
            inset -3px 0 10px rgba(0,0,0,0.3),
            6px 6px 25px rgba(0,0,0,0.5)
          `,
          border: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        {/* PURE brand mark */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 text-center">
          <div className="font-black text-pure-yellow uppercase" style={{ fontSize: size * 0.1 }}>PURE</div>
          <div className="text-white/30 uppercase tracking-widest" style={{ fontSize: size * 0.03 }}>SHAKER</div>
        </div>

        {/* Measurement lines */}
        <div className="absolute right-2 top-[20%] bottom-[15%] flex flex-col justify-between">
          {['600ml', '500ml', '400ml', '300ml', '200ml'].map((ml, i) => (
            <div key={i} className="flex items-center gap-1">
              <div className="w-3 h-[1px] bg-white/15" />
              <span className="text-white/20" style={{ fontSize: size * 0.025 }}>{ml}</span>
            </div>
          ))}
        </div>

        {/* Liquid fill */}
        <div
          className="absolute bottom-0 left-0 right-0 rounded-b-[inherit]"
          style={{
            height: '45%',
            background: 'linear-gradient(180deg, rgba(255,140,0,0.15) 0%, rgba(255,100,0,0.25) 100%)',
          }}
        />

        {/* Shine */}
        <div className="absolute top-0 left-0 w-1/3 h-full bg-gradient-to-r from-white/5 to-transparent rounded-l-[inherit]" />
      </div>

      {/* Cap */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2"
        style={{
          width: size * 0.4,
          height: size * 0.18,
          background: 'linear-gradient(180deg, #FFD700 0%, #E6B800 100%)',
          borderRadius: `${size * 0.06}px ${size * 0.06}px 0 0`,
          boxShadow: '0 -2px 8px rgba(255,215,0,0.2)',
        }}
      >
        {/* Spout */}
        <div
          className="absolute -top-1 left-1/2 -translate-x-1/2"
          style={{
            width: size * 0.15,
            height: size * 0.08,
            background: '#E6B800',
            borderRadius: `${size * 0.04}px ${size * 0.04}px 0 0`,
          }}
        />
      </div>

      {/* Shadow */}
      <div
        className="absolute -bottom-3 left-1/2 -translate-x-1/2 bg-black/20 rounded-full blur-lg"
        style={{ width: size * 0.5, height: size * 0.08 }}
      />
    </motion.div>
  );
}

// ─────────────────────────────────────────────
// 3. CSS PRODUCT SCENE — abstract gradient scene
// ─────────────────────────────────────────────

interface CSSSceneProps {
  variant?: 'energy' | 'focus' | 'power' | 'calm' | 'premium';
  children?: React.ReactNode;
  className?: string;
}

const SCENE_GRADIENTS = {
  energy: {
    bg: 'linear-gradient(135deg, #1a0500 0%, #3d0f00 25%, #6b2000 50%, #3d0f00 75%, #1a0500 100%)',
    orbs: ['rgba(255,100,0,0.15)', 'rgba(255,50,0,0.1)', 'rgba(255,150,0,0.08)'],
    accent: '#ff5000',
  },
  focus: {
    bg: 'linear-gradient(135deg, #0a0a1a 0%, #15153a 25%, #1a1a4a 50%, #15153a 75%, #0a0a1a 100%)',
    orbs: ['rgba(100,100,255,0.12)', 'rgba(80,80,255,0.08)', 'rgba(120,120,255,0.06)'],
    accent: '#6366f1',
  },
  power: {
    bg: 'linear-gradient(135deg, #0a0a0a 0%, #1a0a1a 25%, #2a0a2a 50%, #1a0a1a 75%, #0a0a0a 100%)',
    orbs: ['rgba(168,85,247,0.12)', 'rgba(139,92,246,0.08)', 'rgba(192,132,252,0.06)'],
    accent: '#a855f7',
  },
  calm: {
    bg: 'linear-gradient(135deg, #0a1a0a 0%, #0f2f0f 25%, #153f15 50%, #0f2f0f 75%, #0a1a0a 100%)',
    orbs: ['rgba(34,197,94,0.12)', 'rgba(22,163,74,0.08)', 'rgba(74,222,128,0.06)'],
    accent: '#22c55e',
  },
  premium: {
    bg: 'linear-gradient(135deg, #0a0a0a 0%, #1a1500 25%, #2a2000 50%, #1a1500 75%, #0a0a0a 100%)',
    orbs: ['rgba(255,215,0,0.15)', 'rgba(245,197,24,0.1)', 'rgba(230,184,0,0.08)'],
    accent: '#FFD700',
  },
};

export function CSSScene({ variant = 'premium', children, className = '' }: CSSSceneProps) {
  const config = SCENE_GRADIENTS[variant];

  return (
    <div className={`relative overflow-hidden ${className}`} style={{ background: config.bg }}>
      {/* Animated orbs */}
      {config.orbs.map((orb, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full blur-[80px]"
          style={{
            background: `radial-gradient(circle, ${orb}, transparent 70%)`,
            width: `${200 + i * 80}px`,
            height: `${200 + i * 80}px`,
            left: `${20 + i * 25}%`,
            top: `${15 + i * 20}%`,
          }}
          animate={{
            x: [0, 20 + i * 10, 0],
            y: [0, -15 + i * 5, 0],
            scale: [1, 1.1 + i * 0.05, 1],
          }}
          transition={{ duration: 5 + i * 2, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}

      {/* Grid lines */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(${config.accent}33 1px, transparent 1px),
            linear-gradient(90deg, ${config.accent}33 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// 4. CSS FLOATING PARTICLES — brand colored
// ─────────────────────────────────────────────

interface CSSParticlesProps {
  count?: number;
  color?: string;
  className?: string;
}

export function CSSParticles({ count = 20, color = '#FFD700', className = '' }: CSSParticlesProps) {
  const particles = React.useMemo(() =>
    Array.from({ length: count }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: 2 + Math.random() * 4,
      duration: 4 + Math.random() * 8,
      delay: Math.random() * 4,
      opacity: 0.2 + Math.random() * 0.4,
    })), [count]);

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
            background: color,
            opacity: p.opacity,
          }}
          animate={{
            y: [0, -60 - Math.random() * 40, 0],
            opacity: [0, p.opacity, 0],
            scale: [0.5, 1.2, 0.5],
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────
// 5. CSS GLOW RING — animated ring
// ─────────────────────────────────────────────

interface CSSGlowRingProps {
  size?: number;
  color?: string;
  className?: string;
}

export function CSSGlowRing({ size = 300, color = '#FFD700', className = '' }: CSSGlowRingProps) {
  return (
    <div className={`relative ${className}`} style={{ width: size, height: size }}>
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          border: `2px solid ${color}33`,
          boxShadow: `0 0 30px ${color}15, inset 0 0 30px ${color}08`,
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      />
      <motion.div
        className="absolute inset-4 rounded-full"
        style={{
          border: `1px solid ${color}22`,
        }}
        animate={{ rotate: -360 }}
        transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
      />
      <motion.div
        className="absolute inset-8 rounded-full"
        style={{
          border: `1px solid ${color}15`,
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
      />
    </div>
  );
}

// ─────────────────────────────────────────────
// 6. CSS HERO COMPOSITION — generated hero visual
// ─────────────────────────────────────────────

interface CSSHeroVisualProps {
  variant?: 'explosion' | 'split' | 'diagonal' | 'radial';
  className?: string;
  children?: React.ReactNode;
}

export function CSSHeroVisual({ variant = 'explosion', className = '', children }: CSSHeroVisualProps) {
  if (variant === 'explosion') {
    return (
      <div className={`relative overflow-hidden ${className}`} style={{ background: 'linear-gradient(135deg, #0a0a0b 0%, #1a1a2e 50%, #0a0a0b 100%)' }}>
        {/* Radial burst lines */}
        <div className="absolute inset-0 flex items-center justify-center">
          {Array.from({ length: 16 }).map((_, i) => (
            <motion.div
              key={i}
              className="absolute origin-center"
              style={{
                width: '1px',
                height: '120%',
                background: `linear-gradient(to bottom, transparent, rgba(255,215,0,${0.02 + (i % 4) * 0.008}), transparent)`,
                transform: `rotate(${i * 22.5}deg)`,
              }}
              animate={{ opacity: [0.2, 0.5, 0.2] }}
              transition={{ duration: 3, delay: i * 0.15, repeat: Infinity }}
            />
          ))}
        </div>

        {/* Central glow */}
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(255,215,0,0.12) 0%, transparent 60%)' }}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
        />

        <div className="relative z-10">{children}</div>
      </div>
    );
  }

  if (variant === 'split') {
    return (
      <div className={`relative overflow-hidden ${className}`} style={{ background: '#0a0a0b' }}>
        <div className="absolute inset-0" style={{
          background: 'linear-gradient(135deg, #0a0a0b 45%, rgba(255,215,0,0.06) 45%, rgba(255,215,0,0.06) 55%, #0a0a0b 55%)',
        }} />
        <div className="absolute left-1/2 top-0 bottom-0 w-[1px] -translate-x-1/2" style={{
          background: 'linear-gradient(to bottom, transparent, rgba(255,215,0,0.3), transparent)',
        }} />
        <div className="relative z-10">{children}</div>
      </div>
    );
  }

  if (variant === 'diagonal') {
    return (
      <div className={`relative overflow-hidden ${className}`} style={{ background: '#0a0a0b' }}>
        <div className="absolute inset-0" style={{
          background: 'linear-gradient(135deg, #0a0a0b 40%, rgba(255,215,0,0.05) 40%, rgba(255,215,0,0.05) 60%, #0a0a0b 60%)',
        }} />
        <div className="absolute top-0 left-0 w-20 h-20 border-l-2 border-t-2 border-pure-yellow/20" />
        <div className="absolute bottom-0 right-0 w-20 h-20 border-r-2 border-b-2 border-pure-yellow/20" />
        <div className="relative z-10">{children}</div>
      </div>
    );
  }

  // radial
  return (
    <div className={`relative overflow-hidden ${className}`} style={{ background: 'radial-gradient(ellipse at center, #1a1500 0%, #0a0a0b 70%)' }}>
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(255,215,0,0.08) 0%, transparent 60%)' }}
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
