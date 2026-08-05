'use client';

import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

interface FloatingProductProps {
  src: string;
  alt: string;
  className?: string;
}

export default function FloatingProduct({ src, alt, className = '' }: FloatingProductProps) {
  const ref = useRef<HTMLDivElement>(null);
  
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });

  const y = useTransform(scrollYProgress, [0, 1], [80, -80]);
  const rotate = useTransform(scrollYProgress, [0, 1], [-5, 5]);
  const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.9, 1.05, 0.9]);

  return (
    <motion.div
      ref={ref}
      className={`relative ${className}`}
      style={{ y, rotate, scale }}
    >
      <motion.div
        className="relative"
        whileHover={{ scale: 1.05, rotateY: 10 }}
        transition={{ type: 'spring', stiffness: 200, damping: 20 }}
      >
        <img
          src={src}
          alt={alt}
          className="w-full h-auto drop-shadow-2xl object-contain"
          style={{
            filter: 'drop-shadow(0 25px 50px rgba(255, 215, 0, 0.3))',
          }}
        />
      </motion.div>
    </motion.div>
  );
}