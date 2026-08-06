'use client';

import React from 'react';
import { motion } from 'framer-motion';

const EASE = [0.23, 1, 0.32, 1] as const;

interface GradientHeroProps {
  className?: string;
}

export function AnimatedGradientHero({ className = '' }: GradientHeroProps) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      {/* Animated gradient background */}
      <motion.div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(135deg, #0A0A0B 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #0A0A0B 100%)',
          backgroundSize: '400% 400%',
        }}
        animate={{
          backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'],
        }}
        transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
      />

      {/* Yellow accent glow */}
      <motion.div
        className="absolute -top-1/2 -right-1/4 w-[600px] h-[600px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(255,215,0,0.15) 0%, transparent 70%)',
        }}
        animate={{
          scale: [1, 1.2, 1],
          x: [0, 30, 0],
          y: [0, -20, 0],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Secondary glow */}
      <motion.div
        className="absolute -bottom-1/3 -left-1/4 w-[500px] h-[500px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(255,215,0,0.08) 0%, transparent 70%)',
        }}
        animate={{
          scale: [1.2, 1, 1.2],
          x: [0, -20, 0],
          y: [0, 30, 0],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Grid lines overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,215,0,0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,215,0,0.5) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />

      {/* Noise texture */}
      <div className="absolute inset-0 opacity-[0.04] mix-blend-overlay" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.5'/%3E%3C/svg%3E")`,
      }} />
    </div>
  );
}

interface ProductDisplayProps {
  image: string;
  name: string;
  className?: string;
}

export function AnimatedProductDisplay({ image, name, className = '' }: ProductDisplayProps) {
  return (
    <div className={`relative ${className}`}>
      {/* Rotating glow ring */}
      <motion.div
        className="absolute inset-0 rounded-3xl"
        style={{
          background: 'conic-gradient(from 0deg, transparent, rgba(255,215,0,0.3), transparent, rgba(255,215,0,0.1), transparent)',
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      />

      {/* Product image with float */}
      <motion.img
        src={image}
        alt={name}
        className="relative z-10 w-full h-full object-contain drop-shadow-[0_20px_60px_rgba(255,215,0,0.3)]"
        animate={{
          y: [0, -12, 0],
          rotateY: [0, 5, 0, -5, 0],
        }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  );
}

interface ParticleFieldProps {
  count?: number;
  className?: string;
}

export function CSSParticleField({ count = 30, className = '' }: ParticleFieldProps) {
  const particles = React.useMemo(() =>
    Array.from({ length: count }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 3 + 1,
      duration: Math.random() * 10 + 10,
      delay: Math.random() * 5,
    })), [count]);

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-pure-yellow/20"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
          }}
          animate={{
            y: [0, -100, 0],
            opacity: [0, 0.8, 0],
            scale: [0.5, 1, 0.5],
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

interface GlowCardProps {
  children: React.ReactNode;
  className?: string;
}

export function GlowCard({ children, className = '' }: GlowCardProps) {
  return (
    <motion.div
      className={`relative group ${className}`}
      whileHover={{ y: -4 }}
      transition={{ ease: EASE }}
    >
      {/* Hover glow */}
      <div className="absolute -inset-1 bg-gradient-to-r from-pure-yellow/20 via-transparent to-pure-yellow/10 rounded-3xl opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500" />
      <div className="relative glass rounded-3xl border border-white/5 group-hover:border-pure-yellow/20 transition-all duration-500 overflow-hidden">
        {children}
      </div>
    </motion.div>
  );
}

interface AnimatedCounterProps {
  value: number;
  suffix?: string;
  prefix?: string;
  className?: string;
}

export function AnimatedCounter({ value, suffix = '', prefix = '', className = '' }: AnimatedCounterProps) {
  const [count, setCount] = React.useState(0);

  React.useEffect(() => {
    let start = 0;
    const duration = 2000;
    const increment = value / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [value]);

  return (
    <span className={className}>
      {prefix}{count.toLocaleString('en-IN')}{suffix}
    </span>
  );
}
