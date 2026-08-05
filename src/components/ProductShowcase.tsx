'use client';

import React from 'react';
import { Star } from 'lucide-react';
import Image from '@/components/Image';

const PRODUCTS = [
  { slug: 'primex-preworkout-orange', name: 'PRIME X Pre-Workout', flavour: 'Orange', price: 1299, originalPrice: 1599, image: '/products/prime-x-orange.png', badge: '25% off', rating: 4.8, reviews: 34 },
  { slug: 'primex-preworkout-fruit-punch', name: 'PRIME X Pre-Workout', flavour: 'Fruit Punch', price: 1299, originalPrice: 1599, image: '/products/prime-x-fruit-punch.png', badge: '20% off', rating: 4.6, reviews: 28 },
  { slug: 'primex-preworkout-rocket-lollipop', name: 'PRIME X Pre-Workout', flavour: 'Rocket Lollipop', price: 1299, originalPrice: 1599, image: '/products/prime-x-rocket.png', badge: '17% off', rating: 4.7, reviews: 22 },
];

export default function ProductShowcase() {
  return (
    <section className="py-12 bg-white">
      <div className="max-w-[1100px] mx-auto px-4 sm:px-5">
        <div className="text-center mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold uppercase tracking-wider text-[#1d1d1d] font-heading">
            NEED BEST SELLERS
          </h2>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
          {PRODUCTS.map((product) => (
            <a
              key={product.slug}
              href={`/product/${product.slug}`}
              className="group block text-center"
            >
              <div className="relative aspect-[4/5] overflow-hidden bg-[#f6f6f6] mb-3">
                <Image
                  src={product.image}
                  alt={product.name}
                  fill
                  className="object-contain p-4 group-hover:scale-105 transition-transform duration-500"
                  sizes="(max-width: 640px) 50vw, (max-width: 1024px) 25vw, 20vw"
                  quality={80}
                  loading="lazy"
                />
                {product.badge && (
                  <span className="absolute top-2 left-2 bg-[#E53E3E] text-white text-[9px] font-bold px-1.5 py-0.5 rounded">
                    {product.badge}
                  </span>
                )}
              </div>
              <h3 className="text-[11px] font-bold text-[#1d1d1d] uppercase tracking-wide">
                {product.name}
              </h3>
              {product.flavour && (
                <p className="text-[10px] text-gray-500 mt-0.5">{product.flavour}</p>
              )}
              <div className="flex items-center justify-center gap-0.5 mt-1.5">
                {Array.from({ length: 5 }, (_, j) => (
                  <Star
                    key={j}
                    className={`w-2.5 h-2.5 ${
                      j < Math.floor(product.rating)
                        ? 'text-[#F6A52A] fill-[#F6A52A]'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
                <span className="text-[9px] text-gray-500 ml-1">
                  ({product.reviews})
                </span>
              </div>
              <div className="flex items-center justify-center gap-1.5 mt-1.5">
                <span className="text-sm font-bold text-[#1d1d1d]">
                  ₹{product.price.toLocaleString('en-IN')}
                </span>
                {product.originalPrice > product.price && (
                  <span className="text-[10px] text-gray-400 line-through">
                    ₹{product.originalPrice.toLocaleString('en-IN')}
                  </span>
                )}
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
