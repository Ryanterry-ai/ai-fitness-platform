'use client';

import React, { useRef, useState, useEffect, Suspense } from 'react';
import { motion, useScroll, useTransform, useMotionValue, useSpring } from 'framer-motion';
import { Zap, ArrowRight, ChevronDown, ExternalLink } from 'lucide-react';
import { HeroComposer, ProductOnBackground } from './MockupGenerator';
import { PARTNER_URL } from './AnnouncementBar';

const ParticleHero = React.lazy(() => import('./ParticleHero'));

const EASE = [0.23, 1, 0.32, 1] as const;

// Pre-computed particle positions
const particles = Array.from({ length: 60 }, (_, i) => ({
  left: `${((i * 17 + 13) % 100)}%`,
  top: `${((i * 23 + 7) % 100)}%`,
  duration: 3 + (i % 5),
  delay: (i % 8) * 0.6,
  size: 1 + (i % 4),
}));

export default function HeroSection() {
  const ref = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end start'],
  });

  const y = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.9]);

  // Mouse parallax for product
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const mouseXSpring = useSpring(mouseX, { stiffness: 50, damping: 20 });
  const mouseYSpring = useSpring(mouseY, { stiffness: 50, damping: 20 });

  const productX = useTransform(mouseXSpring, [-0.5, 0.5], [-30, 30]);
  const productY = useTransform(mouseYSpring, [-0.5, 0.5], [-20, 20]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const xPct = (e.clientX / window.innerWidth - 0.5) * 2;
      const yPct = (e.clientY / window.innerHeight - 0.5) * 2;
      mouseX.set(xPct);
      mouseY.set(yPct);
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [mouseX, mouseY]);

  return (
    <section ref={ref} className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background gradient */}
      <motion.div
        className="absolute inset-0"
        style={{ y, scale }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-pure-black via-pure-dark to-pure-black" />
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top_right,_rgba(255,215,0,0.1)_0%,_transparent_60%)]" />
        <div className="absolute bottom-0 right-0 w-full h-full bg-[radial-gradient(ellipse_at_bottom_left,_rgba(255,215,0,0.05)_0%,_transparent_60%)]" />
      </motion.div>

      {/* Particles */}
      <div className="absolute inset-0 overflow-hidden">
        {particles.map((p, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-pure-yellow"
            style={{
              left: p.left,
              top: p.top,
              width: `${p.size}px`,
              height: `${p.size}px`,
            }}
            animate={{
              opacity: [0, 0.6, 0],
              scale: [0, 1.5, 0],
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

      {/* Dynamic glow that follows mouse */}
      <motion.div
        className="absolute pointer-events-none"
        style={{
          x: useTransform(mouseXSpring, [-1, 1], [-200, 200]),
          y: useTransform(mouseYSpring, [-1, 1], [-200, 200]),
          width: 600,
          height: 600,
          background: 'radial-gradient(circle, rgba(255, 215, 0, 0.15) 0%, transparent 70%)',
          borderRadius: '50%',
          filter: 'blur(60px)',
        }}
      />

      {/* Hero Content */}
      <motion.div
        className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid lg:grid-cols-2 gap-12 items-center"
        style={{ opacity }}
      >
        {/* Left: Copy */}
        <div className="space-y-8">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: EASE }}
          >
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-yellow text-pure-yellow text-xs font-bold uppercase tracking-widest">
              <Zap className="w-3 h-3" /> High-Intensity Pre-Workout
            </span>
          </motion.div>

          <motion.h1
            className="text-6xl sm:text-7xl lg:text-8xl font-black uppercase leading-[0.85] tracking-tighter"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.1, ease: EASE }}
          >
            <span className="block text-white">FUEL</span>
            <span className="block text-white">FOR</span>
            <span className="block text-pure-yellow relative">
              ATHLETES
              <motion.span
                className="absolute -bottom-2 left-0 h-1 bg-pure-yellow"
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ duration: 0.8, delay: 0.8, ease: EASE }}
              />
            </span>
          </motion.h1>

          <motion.p
            className="text-lg text-pure-gray max-w-md leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3, ease: EASE }}
          >
            PRIME X delivers explosive energy, massive pumps, and laser-sharp focus.
            75 servings. 3 flavours. No compromise.
          </motion.p>

          {/* Highlight Pills */}
          <motion.div
            className="flex flex-wrap gap-3"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.4, ease: EASE }}
          >
            {['1.5G Beta-Alanine', '750MG Arginine', '500MG L-Citrulline'].map((h, i) => (
              <motion.div
                key={i}
                className="glass rounded-full px-4 py-2 flex items-center gap-2"
                whileHover={{ scale: 1.05, backgroundColor: 'rgba(255, 215, 0, 0.1)' }}
              >
                <Zap className="w-4 h-4 text-pure-yellow" />
                <span className="text-sm font-bold text-white">{h}</span>
              </motion.div>
            ))}
          </motion.div>

          {/* CTAs */}
          <motion.div
            className="flex flex-wrap gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5, ease: EASE }}
          >
            <motion.a
              href={PARTNER_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-pure text-lg px-8 py-4 inline-flex items-center gap-2"
              whileHover={{ scale: 1.02, boxShadow: '0 0 40px rgba(255, 215, 0, 0.4)' }}
              whileTap={{ scale: 0.98 }}
            >
              View Products <ExternalLink className="w-5 h-5" />
            </motion.a>
            <motion.a
              href="/shop"
              className="btn-pure-outline text-lg px-8 py-4"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              View Product
            </motion.a>
          </motion.div>

          {/* Price */}
          <motion.div
            className="flex items-baseline gap-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.6 }}
          >
            <span className="text-4xl font-black text-pure-yellow">₹1,299</span>
            <span className="text-lg text-pure-gray line-through">₹1,599</span>
            <span className="text-sm font-bold text-green-400 bg-green-400/10 px-3 py-1 rounded-full">SAVE 19%</span>
          </motion.div>
        </div>

        {/* Right: Product Visual with mouse parallax + 3D particles */}
        <motion.div
          className="relative flex justify-center lg:justify-end"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.3, ease: EASE }}
        >
          {/* 3D Particle Background */}
          <div className="absolute inset-0 -m-20 z-0">
            <Suspense fallback={null}>
              <ParticleHero />
            </Suspense>
          </div>

          <motion.div
            className="relative z-10"
            style={{ x: productX, y: productY }}
          >
            {/* Generated hero mockup instead of raw image */}
            <HeroComposer
              productImage="/products/hero-product.png"
              logoImage="/products/logo.png"
              variant="explosion"
              className="w-80 h-80 sm:w-96 sm:h-96 rounded-3xl"
            />

            {/* Floating accent elements */}
            <motion.div
              className="absolute -top-10 -right-10 glass rounded-2xl px-4 py-3"
              animate={{ y: [0, -10, 0], rotate: [0, 5, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
            >
              <span className="text-2xl font-black text-pure-yellow">75</span>
              <span className="text-xs text-pure-gray block">Servings</span>
            </motion.div>

            <motion.div
              className="absolute -bottom-5 -left-10 glass rounded-2xl px-4 py-3"
              animate={{ y: [0, 10, 0], rotate: [0, -5, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
            >
              <span className="text-2xl font-black text-green-400">19%</span>
              <span className="text-xs text-pure-gray block">OFF</span>
            </motion.div>
          </motion.div>
        </motion.div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <span className="text-[10px] tracking-[0.3em] uppercase text-pure-gray">Scroll</span>
        <motion.div
          className="w-6 h-10 rounded-full border-2 border-pure-gray/30 flex items-start justify-center pt-2"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <motion.div
            className="w-1 h-2 rounded-full bg-pure-yellow"
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          />
        </motion.div>
      </motion.div>
    </section>
  );
}