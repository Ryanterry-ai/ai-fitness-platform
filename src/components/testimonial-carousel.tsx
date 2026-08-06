'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Star } from 'lucide-react';

interface TestimonialCarouselProps {
  testimonials?: Array<{ quote: string; author: string; role?: string; rating?: number; image?: string }>;
}

const EASE = [0.23, 1, 0.32, 1] as const;

const defaultTestimonials = [
  {
    quote: 'Amazing nutrition service! Highly recommend.',
    author: 'Rohit A.',
    role: 'Working Professional',
    rating: 5,
  },
  {
    quote: 'Professional and reliable. Will use again.',
    author: 'Simran K.',
    role: 'Strength Training',
    rating: 5,
  },
  {
    quote: 'Best nutrition in the area.',
    author: 'Arjun P.',
    role: 'Fitness Enthusiast',
    rating: 5,
  },
];

export default function TestimonialCarousel({
  testimonials = defaultTestimonials,
}: TestimonialCarouselProps) {
  const [current, setCurrent] = useState(0);
  const [direction, setDirection] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setDirection(1);
      setCurrent((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [testimonials.length]);

  const next = () => {
    setDirection(1);
    setCurrent((prev) => (prev + 1) % testimonials.length);
  };

  const prev = () => {
    setDirection(-1);
    setCurrent((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  const variants = {
    enter: (dir: number) => ({
      x: dir > 0 ? 100 : -100,
      opacity: 0,
    }),
    center: {
      x: 0,
      opacity: 1,
    },
    exit: (dir: number) => ({
      x: dir > 0 ? -100 : 100,
      opacity: 0,
    }),
  };

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
            Customer Reviews
          </span>
          <h2 className="text-3xl sm:text-4xl font-black uppercase tracking-tight text-[#0a0a0a]">
            What Athletes <span className="text-[#B08900]">Say</span>
          </h2>
        </motion.div>

        <div className="relative">
          <AnimatePresence mode="wait" custom={direction}>
            <motion.div
              key={current}
              custom={direction}
              variants={variants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.4, ease: EASE }}
              className="bg-white border border-black/5 p-8 md:p-12 text-center"
            >
              {/* Stars */}
              <div className="flex justify-center gap-1 mb-6">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${
                      i < (testimonials[current].rating || 5)
                        ? 'fill-[#ffd100] text-[#ffd100]'
                        : 'fill-gray-200 text-gray-200'
                    }`}
                  />
                ))}
              </div>

              {/* Quote */}
              <p className="text-xl md:text-2xl font-medium text-[#0a0a0a] leading-relaxed mb-8 max-w-2xl mx-auto">
                "{testimonials[current].quote}"
              </p>

              {/* Author */}
              <div>
                <p className="font-bold text-[#0a0a0a]">{testimonials[current].author}</p>
                {testimonials[current].role && (
                  <p className="text-sm text-[#0a0a0a]/50 mt-1">{testimonials[current].role}</p>
                )}
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Navigation */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <button
              onClick={prev}
              className="p-2 bg-white border border-black/10 text-[#0a0a0a] hover:border-[#B08900]/30 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div className="flex gap-2">
              {testimonials.map((_, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setDirection(i > current ? 1 : -1);
                    setCurrent(i);
                  }}
                  className={`w-2 h-2 rounded-full transition-all ${
                    i === current ? 'bg-[#B08900] w-6' : 'bg-[#0a0a0a]/20'
                  }`}
                />
              ))}
            </div>
            <button
              onClick={next}
              className="p-2 bg-white border border-black/10 text-[#0a0a0a] hover:border-[#B08900]/30 transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
