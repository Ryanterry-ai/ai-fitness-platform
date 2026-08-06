'use client';

import React from 'react';
import { ShoppingBag } from 'lucide-react';
import Image from '@/components/Image';
import { useShop } from '@/lib/store';

export default function ProductShowcase() {
  const { products, addToCart } = useShop();

  return (
    <section className="py-14 md:py-16 bg-white">
      <div className="max-w-[1100px] mx-auto px-4 sm:px-5">
        <div className="flex items-end justify-between mb-6 md:mb-8">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#B08900] mb-1.5">The Range</p>
            <h2 className="text-2xl sm:text-3xl font-bold uppercase tracking-wide text-[#0a0a0a] font-heading">
              Shop PRIME X
            </h2>
          </div>
          <a href="/shop" className="hidden sm:block text-[13px] font-semibold uppercase tracking-wide text-[#0a0a0a] border-b border-[#0a0a0a]/30 hover:border-[#0a0a0a] pb-0.5 transition-colors">
            View All
          </a>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 md:gap-5">
          {products.map((product) => {
            const variant = product.variants[0];
            const pct = Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100);
            return (
              <div key={product.id} className="group relative bg-[#faf9f7] border border-black/5 flex flex-col">
                <a href={`/product/${product.slug}`} className="block">
                  <div className="relative aspect-square overflow-hidden bg-[#f2f1ee]">
                    <Image
                      src={product.image}
                      alt={`${product.name} — ${product.flavour}`}
                      fill
                      className="object-contain p-5 md:p-7 group-hover:scale-105 transition-transform duration-500"
                      sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
                      quality={82}
                      loading="lazy"
                    />
                    {pct > 0 && (
                      <span className="absolute top-2.5 left-2.5 bg-[#0a0a0a] text-[#ffd100] text-[10px] font-bold px-2 py-1 uppercase tracking-wide">
                        {pct}% Off
                      </span>
                    )}
                    {product.isBestseller && (
                      <span className="absolute top-2.5 right-2.5 bg-[#ffd100] text-[#0a0a0a] text-[9px] font-bold px-2 py-1 uppercase tracking-wide">
                        Bestseller
                      </span>
                    )}
                  </div>
                </a>

                <div className="p-3.5 md:p-4 flex flex-col flex-1">
                  <a href={`/product/${product.slug}`} className="block mb-2">
                    <h3 className="text-[13px] md:text-[15px] font-bold text-[#0a0a0a] uppercase tracking-wide leading-snug">
                      {product.flavour}
                    </h3>
                    <p className="text-[11px] text-[#0a0a0a]/50 mt-0.5">PRIME X Pre-Workout &middot; 80 Servings</p>
                  </a>

                  <div className="flex items-baseline gap-2 mb-3">
                    <span className="text-[15px] md:text-[17px] font-bold text-[#0a0a0a]">
                      ₹{product.price.toLocaleString('en-IN')}
                    </span>
                    {product.originalPrice > product.price && (
                      <span className="text-[12px] text-[#0a0a0a]/35 line-through">
                        ₹{product.originalPrice.toLocaleString('en-IN')}
                      </span>
                    )}
                  </div>

                  <button
                    onClick={() => addToCart(product, variant, 1)}
                    aria-label={`Add ${product.flavour} to cart`}
                    className="mt-auto h-11 flex items-center justify-center gap-1.5 bg-[#0a0a0a] text-white text-[12px] font-bold uppercase tracking-wide hover:bg-[#ffd100] hover:text-[#0a0a0a] active:scale-[0.97] transition-all"
                  >
                    <ShoppingBag className="w-3.5 h-3.5" />
                    Add to Cart
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        <a href="/shop" className="sm:hidden mt-6 flex items-center justify-center h-12 border border-[#0a0a0a]/20 text-[13px] font-semibold uppercase tracking-wide text-[#0a0a0a]">
          View All Products
        </a>
      </div>
    </section>
  );
}
