'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, ArrowRight, Tag } from 'lucide-react';
import Image from 'next/image';

const EASE = [0.23, 1, 0.32, 1] as const;

const posts = [
  {
    id: 1,
    title: 'The Ultimate Guide to Pre-Workout Supplements',
    excerpt: 'Everything you need to know about pre-workout ingredients, dosing, and timing. Learn what actually works and what is just marketing.',
    category: 'Nutrition',
    date: 'Jan 15, 2025',
    readTime: '8 min',
    image: '/products/blog-preworkout-guide.svg',
  },
  {
    id: 2,
    title: 'Beta-Alanine: Why 1.5g is the Sweet Spot',
    excerpt: 'Beta-Alanine is one of the most researched pre-workout ingredients. We break down why 1.5g per serving is the optimal dose for performance.',
    category: 'Ingredients',
    date: 'Jan 10, 2025',
    readTime: '6 min',
    image: '/products/blog-beta-alanine.svg',
  },
  {
    id: 3,
    title: '5 Training Mistakes That Are Killing Your Gains',
    excerpt: 'Stop making these common training errors. Learn the science-backed strategies to maximize muscle growth and strength.',
    category: 'Training',
    date: 'Jan 5, 2025',
    readTime: '10 min',
    image: '/products/blog-training-mistakes.svg',
  },
  {
    id: 4,
    title: 'The Science of the Pump: Arginine vs Citrulline',
    excerpt: 'Which nitric oxide booster is better? We compare Arginine HCL and L-Citrulline with clinical data to help you decide.',
    category: 'Science',
    date: 'Dec 28, 2024',
    readTime: '7 min',
    image: '/products/blog-arginine-citrulline.svg',
  },
  {
    id: 5,
    title: 'Pre-Workout Timing: When to Take Your Supplement',
    excerpt: 'Timing matters. Learn the optimal window to take your pre-workout for maximum energy, focus, and performance.',
    category: 'Nutrition',
    date: 'Dec 20, 2024',
    readTime: '5 min',
    image: '/products/blog-preworkout-timing.svg',
  },
  {
    id: 6,
    title: 'Recovery 101: What to Do After Your Workout',
    excerpt: 'The workout is only half the equation. Proper recovery is where gains happen. Learn the protocols that work.',
    category: 'Recovery',
    date: 'Dec 15, 2024',
    readTime: '9 min',
    image: '/products/blog-training-mistakes.svg',
  },
];

const categories = ['All', 'Nutrition', 'Training', 'Ingredients', 'Science', 'Recovery'];

export default function BlogPage() {
  return (
    <div className="bg-pure-black min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: EASE }}
        >
          <h1 className="text-5xl sm:text-6xl font-black uppercase tracking-tighter">
            THE <span className="text-pure-yellow">BLOG</span>
          </h1>
          <p className="text-pure-gray mt-4 max-w-xl">
            Training tips, nutrition science, and athlete stories. Learn from the experts.
          </p>
        </motion.div>

        {/* Categories */}
        <motion.div
          className="flex gap-3 mb-12 flex-wrap"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1, ease: EASE }}
        >
          {categories.map((c, i) => (
            <button
              key={c}
              className={`px-5 py-2.5 rounded-full text-xs font-bold uppercase tracking-wider transition-all ${
                i === 0
                  ? 'bg-pure-yellow text-pure-black'
                  : 'glass text-pure-gray hover:text-white hover:bg-white/5'
              }`}
            >
              {c}
            </button>
          ))}
        </motion.div>

        {/* Featured Post */}
        <motion.div
          className="glass rounded-3xl overflow-hidden mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: EASE }}
        >
          <div className="grid md:grid-cols-2">
            <div className="aspect-video bg-pure-dark overflow-hidden relative">
              <Image
                src={posts[0].image}
                alt={posts[0].title}
                fill
                className="object-cover group-hover:scale-105 transition-transform duration-700"
                sizes="(max-width: 768px) 100vw, 50vw"
                quality={85}
              />
            </div>
            <div className="p-8 md:p-12 flex flex-col justify-center">
              <span className="text-pure-yellow text-xs font-bold uppercase tracking-wider mb-3">{posts[0].category}</span>
              <h2 className="text-3xl font-black uppercase tracking-tight mb-4">{posts[0].title}</h2>
              <p className="text-pure-gray leading-relaxed mb-6">{posts[0].excerpt}</p>
              <div className="flex items-center gap-4 text-xs text-pure-gray mb-6">
                <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {posts[0].date}</span>
                <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {posts[0].readTime}</span>
              </div>
              <a href="/blog" className="btn-pure w-fit">
                Read Article <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        </motion.div>

        {/* Posts Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.slice(1).map((post, i) => (
            <motion.article
              key={post.id}
              className="glass rounded-2xl overflow-hidden group hover:border-pure-yellow/20 transition-all duration-500"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.5, delay: i * 0.1, ease: EASE }}
              whileHover={{ y: -4 }}
            >
              <div className="h-48 bg-pure-dark overflow-hidden relative">
                <Image
                  src={post.image}
                  alt={post.title}
                  fill
                  className="object-cover group-hover:scale-105 transition-transform duration-700"
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  quality={80}
                  loading="lazy"
                />
              </div>
              <div className="p-6">
                <div className="flex items-center gap-4 text-xs text-pure-gray mb-3">
                  <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {post.date}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {post.readTime}</span>
                </div>
                <h3 className="text-lg font-black uppercase tracking-tight mb-2 group-hover:text-pure-yellow transition-colors">
                  {post.title}
                </h3>
                <p className="text-sm text-pure-gray leading-relaxed line-clamp-3">{post.excerpt}</p>
                <a href="/blog" className="inline-flex items-center gap-2 text-sm font-bold text-pure-yellow mt-4 group-hover:gap-3 transition-all">
                  Read More <ArrowRight className="w-3 h-3" />
                </a>
              </div>
            </motion.article>
          ))}
        </div>
      </div>
    </div>
  );
}
