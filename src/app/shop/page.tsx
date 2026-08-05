'use client';

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, SlidersHorizontal, X, Star, ShoppingBag, Eye, Heart, ChevronDown, Package, Zap, ExternalLink } from 'lucide-react';
import Image from 'next/image';
import { useShop, Product } from '@/lib/store';
import ScrollReveal from '@/components/ScrollReveal';
import { PARTNER_URL } from '@/components/AnnouncementBar';

const EASE = [0.23, 1, 0.32, 1] as const;

const SORT_OPTIONS = [
  { value: 'popular', label: 'Most Popular' },
  { value: 'price-low', label: 'Price: Low → High' },
  { value: 'price-high', label: 'Price: High → Low' },
  { value: 'rating', label: 'Highest Rated' },
  { value: 'newest', label: 'Newest' },
];

const CATEGORIES = ['All', 'Pre-Workout', 'Protein', 'Vitamins', 'Recovery', 'Hydration'];

export default function ShopPage() {
  const { products, addToCart, toggleWishlist, isInWishlist, setQuickViewProduct } = useShop();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [sort, setSort] = useState('popular');
  const [showFilters, setShowFilters] = useState(false);
  const [addedId, setAddedId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    let items = [...products];

    // Search
    if (search) {
      const q = search.toLowerCase();
      items = items.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.flavour.toLowerCase().includes(q)
      );
    }

    // Category
    if (category !== 'All') {
      items = items.filter(p => p.category === category);
    }

    // Sort
    switch (sort) {
      case 'price-low': items.sort((a, b) => a.price - b.price); break;
      case 'price-high': items.sort((a, b) => b.price - a.price); break;
      case 'rating': items.sort((a, b) => b.rating - a.rating); break;
      default: items.sort((a, b) => (b.isBestseller ? 1 : 0) - (a.isBestseller ? 1 : 0));
    }

    return items;
  }, [products, search, category, sort]);

  const handleAdd = (product: Product) => {
    const variant = product.variants[0];
    addToCart(product, variant, 1);
    setAddedId(product.id);
    setTimeout(() => setAddedId(null), 1500);
  };

  return (
    <div className="bg-pure-black min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <ScrollReveal>
          <div className="text-center mb-12">
            <motion.div
              className="inline-flex items-center gap-2 bg-pure-yellow/10 border border-pure-yellow/20 rounded-full px-4 py-1.5 mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Zap className="w-3.5 h-3.5 text-pure-yellow" />
              <span className="text-[11px] font-bold text-pure-yellow uppercase tracking-wider">Fuel Your Potential</span>
            </motion.div>
            <h1 className="text-5xl sm:text-6xl font-black text-white uppercase tracking-tighter">
              Shop <span className="text-pure-yellow">PURE</span>
            </h1>
            <p className="text-gray-500 mt-3 max-w-md mx-auto">Premium sports nutrition. Every ingredient. Every flavour. Built for athletes.</p>
          </div>
        </ScrollReveal>

        {/* Search + Filters Bar */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search products, flavours, categories..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:border-pure-yellow/50 transition-colors"
            />
            {search && (
              <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Sort */}
          <div className="relative">
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="appearance-none px-4 py-3 pr-10 bg-white/5 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-pure-yellow/50 transition-colors cursor-pointer"
            >
              {SORT_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value} className="bg-pure-black text-white">{opt.label}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
          </div>

          {/* Filter toggle */}
          <button onClick={() => setShowFilters(!showFilters)} className={`p-3 rounded-xl border transition-all ${showFilters ? 'bg-pure-yellow text-pure-black border-pure-yellow' : 'bg-white/5 border-white/10 text-gray-500 hover:text-white'}`}>
            <SlidersHorizontal className="w-4 h-4" />
          </button>
        </div>

        {/* Category Pills */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden mb-8"
            >
              <div className="flex flex-wrap gap-2 pb-4">
                {CATEGORIES.map(cat => (
                  <button
                    key={cat}
                    onClick={() => setCategory(cat)}
                    className={`px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-all ${
                      category === cat
                        ? 'bg-pure-yellow text-pure-black'
                        : 'bg-white/5 text-gray-500 border border-white/10 hover:border-white/30'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Count */}
        <div className="flex items-center justify-between mb-6">
          <span className="text-xs text-gray-500">
            {filtered.length} {filtered.length === 1 ? 'product' : 'products'} found
          </span>
        </div>

        {/* Product Grid */}
        {filtered.length === 0 ? (
          <div className="text-center py-20">
            <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">No products found</h3>
            <p className="text-sm text-gray-500">Try adjusting your search or filters.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((product, index) => (
              <ScrollReveal key={product.id} delay={index * 50}>
                <motion.div
                  className="group glass rounded-3xl overflow-hidden border border-white/5 hover:border-pure-yellow/30 transition-all duration-500"
                  whileHover={{ y: -4 }}
                  transition={{ ease: EASE }}
                >
                  {/* Product image */}
                  <div className="relative aspect-[4/5] overflow-hidden">
                    <Image
                      src={product.image}
                      alt={product.name}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-700"
                      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                      quality={80}
                      loading="lazy"
                    />

                    {/* Badges */}
                    <div className="absolute top-3 left-3 flex flex-col gap-1.5">
                      {product.isBestseller && (
                        <span className="bg-pure-yellow text-pure-black text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1">
                          <Star className="w-3 h-3 fill-pure-black" /> Bestseller
                        </span>
                      )}
                      {product.originalPrice > product.price && (
                        <span className="bg-green-500 text-white text-[10px] font-bold px-2 py-1 rounded-full">
                          {Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)}% OFF
                        </span>
                      )}
                    </div>

                    {/* Hover Actions */}
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-3">
                      <motion.button
                        onClick={() => setQuickViewProduct(product)}
                        className="p-3 bg-white rounded-xl text-pure-black hover:bg-pure-yellow transition-colors"
                        whileTap={{ scale: 0.9 }}
                      >
                        <Eye className="w-5 h-5" />
                      </motion.button>
                      <motion.button
                        onClick={() => toggleWishlist(product.id)}
                        className={`p-3 rounded-xl transition-colors ${isInWishlist(product.id) ? 'bg-red-500 text-white' : 'bg-white text-pure-black hover:bg-red-500 hover:text-white'}`}
                        whileTap={{ scale: 0.9 }}
                      >
                        <Heart className={`w-5 h-5 ${isInWishlist(product.id) ? 'fill-white' : ''}`} />
                      </motion.button>
                    </div>
                  </div>

                  {/* Info */}
                  <div className="p-5">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-[10px] font-bold text-pure-yellow bg-pure-yellow/10 px-2 py-0.5 rounded-full uppercase">{product.category}</span>
                      <div className="flex items-center gap-0.5">
                        <Star className="w-3 h-3 fill-pure-yellow text-pure-yellow" />
                        <span className="text-[10px] font-bold text-white">{product.rating}</span>
                      </div>
                    </div>

                    <h3 className="text-lg font-bold text-white mb-1 group-hover:text-pure-yellow transition-colors">{product.name}</h3>
                    <p className="text-xs text-gray-500 line-clamp-2 mb-3">{product.tagline}</p>

                    {/* Flavour badge */}
                    {product.flavour && (
                      <div className="mb-4">
                        <span className="text-[10px] font-bold text-pure-yellow bg-pure-yellow/10 px-2 py-0.5 rounded-full uppercase">{product.flavour}</span>
                      </div>
                    )}

                    {/* Price + CTA */}
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xl font-black text-pure-yellow">₹{product.price.toLocaleString('en-IN')}</span>
                        {product.originalPrice > product.price && (
                          <span className="text-xs text-gray-500 line-through ml-1">₹{product.originalPrice.toLocaleString('en-IN')}</span>
                        )}
                      </div>
                      <a
                        href={PARTNER_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 bg-pure-yellow text-pure-black hover:bg-pure-yellow-light transition-all text-center"
                      >
                        <ExternalLink className="w-3.5 h-3.5" /> View Products
                      </a>
                    </div>
                  </div>
                </motion.div>
              </ScrollReveal>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
