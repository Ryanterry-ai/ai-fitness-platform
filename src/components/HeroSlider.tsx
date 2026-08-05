'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react';
import Image from 'next/image';
import { PARTNER_URL } from './AnnouncementBar';

interface Slide {
  id: number;
  image: string;
  title: string;
  subtitle: string;
  cta: string;
  accentColor: string;
}

const SLIDES: Slide[] = [
  {
    id: 1,
    image: '/products/prime-x-orange.png',
    title: 'PRIME X PRE-WORKOUT',
    subtitle: 'High-Intensity Pre-Workout for Relentless Results.',
    cta: 'Shop Now',
    accentColor: '#FFD100',
  },
  {
    id: 2,
    image: '/products/prime-x-fruit-punch.png',
    title: 'PRIME X PRE-WORKOUT',
    subtitle: 'Unstoppable Pre-Workout. Unmatched Performance.',
    cta: 'Shop Now',
    accentColor: '#FFD100',
  },
  {
    id: 3,
    image: '/products/prime-x-rocket.png',
    title: 'PRIME X PRE-WORKOUT',
    subtitle: 'Dominate Every Rep. Crush Every Goal.',
    cta: 'Shop Now',
    accentColor: '#FFD100',
  },
];

export default function HeroSlider() {
  const [current, setCurrent] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const next = useCallback(() => {
    if (isTransitioning) return;
    setIsTransitioning(true);
    setCurrent((prev) => (prev + 1) % SLIDES.length);
    setTimeout(() => setIsTransitioning(false), 700);
  }, [isTransitioning]);

  const prev = useCallback(() => {
    if (isTransitioning) return;
    setIsTransitioning(true);
    setCurrent((prev) => (prev - 1 + SLIDES.length) % SLIDES.length);
    setTimeout(() => setIsTransitioning(false), 700);
  }, [isTransitioning]);

  useEffect(() => {
    const timer = setInterval(next, 7000);
    return () => clearInterval(timer);
  }, [next]);

  const slide = SLIDES[current];

  return (
    <section className="relative h-[60vh] sm:h-[70vh] md:h-[80vh] lg:h-[90vh] overflow-hidden bg-[#111]">
      {/* Background Image - full bleed */}
      {SLIDES.map((s, i) => (
        <div
          key={s.id}
          className="absolute inset-0 transition-opacity duration-700"
          style={{ opacity: i === current ? 1 : 0 }}
        >
          <Image
            src={s.image}
            alt={s.title}
            fill
            className="object-cover object-center"
            priority={i === 0}
            sizes="100vw"
            quality={85}
          />
          <div className="absolute inset-0 bg-black/20" />
        </div>
      ))}

      {/* Content - Left aligned */}
      <div className="relative z-10 h-full flex items-center">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 w-full">
          <div className="max-w-xl space-y-4">
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black uppercase leading-[0.9] tracking-tighter text-white font-heading">
              <span className="block">{slide.title}</span>
            </h1>

            <p className="text-sm sm:text-base text-white/90 max-w-md leading-relaxed font-sans">
              {slide.subtitle}
            </p>

            <div className="flex flex-wrap gap-3 pt-2">
              <a
                href={PARTNER_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-[#FFD100] text-black px-6 py-3 rounded text-xs font-bold uppercase tracking-wider transition-all hover:bg-[#E6B400] font-sans"
              >
                {slide.cta} <ExternalLink className="w-3.5 h-3.5" />
              </a>
              <a
                href="/shop"
                className="inline-flex items-center gap-2 border-2 border-white/40 text-white px-6 py-3 rounded text-xs font-bold uppercase tracking-wider hover:border-white hover:bg-white/10 transition-all font-sans"
              >
                View All Products
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="absolute bottom-6 left-0 right-0 z-20">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 flex items-center justify-between">
          <div className="flex gap-2">
            {SLIDES.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrent(i)}
                className="h-1 rounded-full transition-all duration-500"
                style={{
                  width: i === current ? '2rem' : '0.5rem',
                  backgroundColor: i === current ? '#FFD100' : 'rgba(255,255,255,0.3)',
                }}
              />
            ))}
          </div>
          <div className="flex gap-2">
            <button
              onClick={prev}
              className="w-10 h-10 rounded-full bg-black/30 backdrop-blur-sm border border-white/20 flex items-center justify-center text-white hover:bg-black/50 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={next}
              className="w-10 h-10 rounded-full bg-black/30 backdrop-blur-sm border border-white/20 flex items-center justify-center text-white hover:bg-black/50 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
