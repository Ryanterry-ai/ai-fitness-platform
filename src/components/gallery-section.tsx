'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

interface GallerySectionProps {
  columns?: number;
  lightbox?: string;
  images?: Array<{ src: string; alt: string; caption?: string }>;
}

const EASE = [0.23, 1, 0.32, 1] as const;

const defaultImages = [
  { src: '/products/Orange.png', alt: 'PRIME X Orange', caption: 'Orange Flavour' },
  { src: '/products/Rocket Lolli pop.png', alt: 'PRIME X Rocket Lollipop', caption: 'Rocket Lollipop' },
  { src: '/products/Fruit Punch.png', alt: 'PRIME X Fruit Punch', caption: 'Fruit Punch' },
  { src: '/products/product-3flavours.png', alt: '3 Flavours Collection', caption: 'All 3 Flavours' },
  { src: '/products/hero-slide.png', alt: 'PRIME X Hero', caption: 'Built for Performance' },
];

export default function GallerySection({
  columns = 3,
  lightbox = 'true',
  images = defaultImages,
}: GallerySectionProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  const openLightbox = (index: number) => setSelectedIndex(index);
  const closeLightbox = () => setSelectedIndex(null);
  const nextImage = () => {
    if (selectedIndex !== null) setSelectedIndex((selectedIndex + 1) % images.length);
  };
  const prevImage = () => {
    if (selectedIndex !== null) setSelectedIndex((selectedIndex - 1 + images.length) % images.length);
  };

  return (
    <>
      <section className="py-16 md:py-20 bg-[#0a0a0a]">
        <div className="max-w-[1100px] mx-auto px-4 sm:px-6">
          <motion.div
            className="text-center mb-10"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: EASE }}
          >
            <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#ffd100] mb-2 block">
              Photo Gallery
            </span>
            <h2 className="text-3xl sm:text-4xl font-black uppercase tracking-tight text-white">
              See the <span className="text-[#ffd100]">Product</span>
            </h2>
          </motion.div>

          <div className={`grid grid-cols-2 md:grid-cols-${columns} gap-3`}>
            {images.map((image, i) => (
              <motion.div
                key={i}
                className={`relative overflow-hidden cursor-pointer group ${
                  i === 0 ? 'md:col-span-2 md:row-span-2' : ''
                }`}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                whileHover={{ scale: 1.02 }}
                onClick={() => lightbox === 'true' && openLightbox(i)}
              >
                <div className={`relative ${i === 0 ? 'h-64 md:h-96' : 'h-48 md:h-64'}`}>
                  <img
                    src={image.src}
                    alt={image.alt}
                    className="w-full h-full object-contain bg-[#1a1a1a] p-4 transition-transform duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  {image.caption && (
                    <div className="absolute bottom-0 left-0 right-0 p-4 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
                      <p className="text-white font-bold text-sm">{image.caption}</p>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Lightbox */}
      <AnimatePresence>
        {selectedIndex !== null && (
          <motion.div
            className="fixed inset-0 z-[10000] flex items-center justify-center bg-black/95 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeLightbox}
          >
            <button
              className="absolute top-6 right-6 p-2 bg-white/10 rounded-full text-white hover:text-[#ffd100] transition-colors z-10"
              onClick={closeLightbox}
            >
              <X className="w-6 h-6" />
            </button>
            <button
              className="absolute left-4 p-2 bg-white/10 rounded-full text-white hover:text-[#ffd100] transition-colors z-10"
              onClick={(e) => { e.stopPropagation(); prevImage(); }}
            >
              <ChevronLeft className="w-8 h-8" />
            </button>
            <button
              className="absolute right-4 p-2 bg-white/10 rounded-full text-white hover:text-[#ffd100] transition-colors z-10"
              onClick={(e) => { e.stopPropagation(); nextImage(); }}
            >
              <ChevronRight className="w-8 h-8" />
            </button>
            <motion.div
              className="relative max-w-4xl max-h-[80vh] mx-4"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={images[selectedIndex].src}
                alt={images[selectedIndex].alt}
                className="max-w-full max-h-[80vh] object-contain"
              />
              {images[selectedIndex].caption && (
                <div className="absolute bottom-4 left-4 right-4 text-center">
                  <p className="text-white font-bold text-lg">{images[selectedIndex].caption}</p>
                  <p className="text-gray-400 text-sm mt-1">{selectedIndex + 1} / {images.length}</p>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
