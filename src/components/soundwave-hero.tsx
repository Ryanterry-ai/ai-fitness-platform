'use client';

import React, { useRef, useEffect } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Zap, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface SoundwaveHeroProps {
  title?: string;
  subtitle?: string;
  cta?: string;
}

const EASE = [0.23, 1, 0.32, 1] as const;

export default function SoundwaveHero({
  title = 'Professional Nutrition Services',
  subtitle = 'Detailed Specs | Technical Info | Comparison Charts',
  cta = 'Shop Now',
}: SoundwaveHeroProps) {
  const ref = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end start'],
  });

  const y = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  // Soundwave animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animFrame: number;
    let time = 0;

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };

    const draw = () => {
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      ctx.clearRect(0, 0, w, h);

      const bars = 64;
      const barWidth = w / bars;
      const centerY = h / 2;

      for (let i = 0; i < bars; i++) {
        const frequency = 0.02 + (i / bars) * 0.03;
        const amplitude = 20 + Math.sin(time * 0.02 + i * 0.3) * 15;
        const barHeight = Math.abs(Math.sin(time * frequency + i * 0.2)) * amplitude;

        const x = i * barWidth;
        const alpha = 0.3 + (i / bars) * 0.4;

        ctx.fillStyle = `rgba(255, 209, 0, ${alpha})`;
        ctx.fillRect(x + 1, centerY - barHeight, barWidth - 2, barHeight * 2);
      }

      time++;
      animFrame = requestAnimationFrame(draw);
    };

    resize();
    draw();
    window.addEventListener('resize', resize);

    return () => {
      cancelAnimationFrame(animFrame);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <section ref={ref} className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#0a0a0a]">
      {/* Soundwave Canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full opacity-30"
      />

      {/* Gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a] via-transparent to-[#0a0a0a]" />
      <div className="absolute inset-0 bg-gradient-to-r from-[#0a0a0a]/80 via-transparent to-[#0a0a0a]/80" />

      {/* Content */}
      <motion.div
        className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 text-center"
        style={{ y, opacity }}
      >
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: EASE }}
        >
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#ffd100]/10 text-[#ffd100] text-xs font-bold uppercase tracking-widest mb-6">
            <Zap className="w-3 h-3" /> High-Intensity Pre-Workout
          </span>
        </motion.div>

        <motion.h1
          className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black uppercase leading-[0.9] tracking-tighter mb-6"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.1, ease: EASE }}
        >
          <span className="block text-white">{title.split(' ').slice(0, 2).join(' ')}</span>
          <span className="block text-[#ffd100]">{title.split(' ').slice(2).join(' ')}</span>
        </motion.h1>

        <motion.p
          className="text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: EASE }}
        >
          {subtitle}
        </motion.p>

        <motion.div
          className="flex flex-wrap items-center justify-center gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5, ease: EASE }}
        >
          <Link
            to="/shop"
            className="inline-flex items-center gap-2 px-8 py-4 bg-[#ffd100] text-[#0a0a0a] text-sm font-bold uppercase tracking-wider hover:bg-[#fbea9d] transition-colors"
          >
            {cta} <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/formula"
            className="inline-flex items-center gap-2 px-8 py-4 border border-white/20 text-white text-sm font-bold uppercase tracking-wider hover:border-[#ffd100]/50 hover:text-[#ffd100] transition-colors"
          >
            View Formula
          </Link>
        </motion.div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        animate={{ opacity: [0.4, 0.8, 0.4] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="w-6 h-10 rounded-full border-2 border-white/20 flex items-start justify-center pt-2">
          <motion.div
            className="w-1 h-2 rounded-full bg-[#ffd100]"
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          />
        </div>
      </motion.div>
    </section>
  );
}
