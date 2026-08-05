'use client';

import React, { useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { Star, ExternalLink } from 'lucide-react';
import Image from '@/components/Image';
import { PARTNER_URL } from './AnnouncementBar';

interface ProductCard3DProps {
  name: string;
  flavour: string;
  price: number;
  originalPrice: number;
  image: string;
  rating?: number;
  href?: string;
}

export default function ProductCard3D({
  name,
  flavour,
  price,
  originalPrice,
  image,
  rating = 5,
  href = '/shop',
}: ProductCard3DProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseXSpring = useSpring(x, { stiffness: 150, damping: 15 });
  const mouseYSpring = useSpring(y, { stiffness: 150, damping: 15 });

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ['12deg', '-12deg']);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ['-12deg', '12deg']);

  const glareX = useTransform(mouseXSpring, [-0.5, 0.5], [0, 100]);
  const glareY = useTransform(mouseYSpring, [-0.5, 0.5], [0, 100]);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const xPct = (e.clientX - rect.left) / rect.width - 0.5;
    const yPct = (e.clientY - rect.top) / rect.height - 0.5;
    x.set(xPct);
    y.set(yPct);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    x.set(0);
    y.set(0);
  };

  const discount = Math.round(((originalPrice - price) / originalPrice) * 100);

  return (
    <motion.div
      ref={ref}
      className="relative group cursor-pointer"
      style={{
        rotateX,
        rotateY,
        transformStyle: 'preserve-3d',
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      whileHover={{ z: 50 }}
    >
      <a href={href} className="block">
        <div className="relative rounded-3xl bg-gradient-to-b from-pure-dark to-pure-black border border-white/5 overflow-hidden transition-all duration-500 group-hover:border-pure-yellow/30 group-hover:shadow-2xl group-hover:shadow-pure-yellow/10">
          
          {/* Glare overlay */}
          <motion.div
            className="absolute inset-0 z-10 pointer-events-none rounded-3xl"
            style={{
              background: `radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255, 215, 0, 0.2) 0%, transparent 50%)`,
              opacity: isHovered ? 1 : 0,
            }}
          />

          {/* Product image */}
          <div className="relative h-64 overflow-hidden">
            <Image
              src={image}
              alt={name}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-700"
              sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
              quality={85}
            />
            
            {/* Discount badge */}
            <div className="absolute top-4 right-4 bg-pure-yellow text-pure-black text-xs font-black px-3 py-1 rounded-full">
              -{discount}%
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-4">
            {/* Rating */}
            <div className="flex gap-1">
              {Array.from({ length: rating }).map((_, i) => (
                <Star key={i} className="w-4 h-4 fill-pure-yellow text-pure-yellow" />
              ))}
            </div>

            {/* Name */}
            <div>
              <h3 className="text-xl font-black uppercase tracking-tight text-white group-hover:text-pure-yellow transition-colors">
                {name}
              </h3>
              <p className="text-sm text-pure-gray mt-1">{flavour}</p>
            </div>

            {/* Price */}
            <div className="flex items-baseline gap-3">
              <span className="text-2xl font-black text-pure-yellow">
                ₹{price.toLocaleString('en-IN')}
              </span>
              <span className="text-sm text-pure-gray line-through">
                ₹{originalPrice.toLocaleString('en-IN')}
              </span>
            </div>

            {/* View Products button → redirected to upgraded.co.in */}
            <a
              href={PARTNER_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full py-3 rounded-xl bg-pure-yellow text-pure-black font-bold uppercase tracking-wider text-sm flex items-center justify-center gap-2 btn-press text-center"
            >
              <ExternalLink className="w-4 h-4" />
              View Products
            </a>
          </div>

          {/* Bottom glow on hover */}
          <motion.div
            className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-pure-yellow/10 to-transparent pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 1 : 0 }}
          />
        </div>
      </a>
    </motion.div>
  );
}