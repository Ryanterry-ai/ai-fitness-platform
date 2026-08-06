'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Award, Target, Heart, Zap, Users, Factory, CheckCircle, ArrowRight, ShoppingBag, Menu, X } from 'lucide-react';
import CartDrawer from '../../components/CartDrawer';
import { PARTNER_URL } from '../../components/AnnouncementBar';

const EASE = [0.23, 1, 0.32, 1] as const;

const values = [
  { icon: Target, title: 'Transparency', desc: 'Every ingredient. Every dose. Every batch. We hide nothing because we have nothing to hide.' },
  { icon: Shield, title: 'Quality', desc: 'FSSAI licensed. Banned substance free. manufactured in ISO certified facilities.' },
  { icon: Heart, title: 'Athletes First', desc: 'Formulated for performance, not marketing. Every ingredient is clinically dosed.' },
  { icon: Zap, title: 'Innovation', desc: 'Continuously improving formulas based on the latest sports nutrition research.' },
];

const milestones = [
  { year: '2023', title: 'Founded', desc: 'PURE HEALTH SUPPS was born from a simple idea: India deserves world-class sports nutrition.' },
  { year: '2024', title: 'PRIME X Launch', desc: 'Launched our flagship pre-workout with 75 servings and transparent labeling.' },
  { year: '2024', title: 'FSSAI Certified', desc: 'Received FSSAI manufacturing license. Licensed facility. Quality guaranteed.' },
  { year: '2025', title: 'Pan-India', desc: 'Expanded to deliver across India. Free shipping on orders above ₹999.' },
];

export default function AboutPage() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <div className="bg-pure-black min-h-screen pt-24 pb-20">
      {/* Nav */}
      <header className={`nav ${scrolled ? 'scrolled' : ''}`}>
        <div className="wrap nav-inner">
          <a href="/" className="brand"><span className="brand-text">PURE</span></a>
          <nav className="nav-links">
            <a href="/shop">Products</a>
            <a href="/formula">Formula</a>
            <a href="/why-pure">Why PURE</a>
            <a href="/stack-save">Stack & Save</a>
          </nav>
          <div className="nav-right">
            <a href="/cart" className="nav-icon" style={{ position: 'relative' }}>
              <ShoppingBag size={20} />
            </a>
            <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ fontSize: 11, padding: '10px 20px' }}>
              Shop PRIME X
            </a>
            <button className="nav-mobile-toggle" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </header>

      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div className="mobile-menu" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
            <a href="/shop" onClick={() => setMobileMenuOpen(false)}>Products</a>
            <a href="/formula" onClick={() => setMobileMenuOpen(false)}>Formula</a>
            <a href="/why-pure" onClick={() => setMobileMenuOpen(false)}>Why PURE</a>
            <a href="/stack-save" onClick={() => setMobileMenuOpen(false)}>Stack & Save</a>
            <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ marginTop: 16 }}>Shop PRIME X</a>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hero */}
      <section className="section-padding">
        <div className="container-pure">
          <motion.div
            className="max-w-3xl"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: EASE }}
          >
            <span className="text-pure-yellow text-sm font-bold tracking-[0.3em] uppercase">About Us</span>
            <h1 className="text-5xl sm:text-7xl font-black uppercase mt-4 tracking-tighter">
              BUILT BY <span className="text-pure-yellow">ATHLETES</span>
            </h1>
            <p className="text-pure-gray text-lg mt-6 leading-relaxed max-w-2xl">
              PURE HEALTH SUPPS was founded with one mission: to give Indian athletes access to
              world-class sports nutrition. No proprietary blends. No hidden doses. Just honest,
              clinically dosed formulas that deliver real results.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Mission */}
      <section className="section-padding bg-gradient-to-b from-pure-dark/50 to-pure-black">
        <div className="container-pure">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, ease: EASE }}
            >
              <span className="text-pure-yellow text-sm font-bold tracking-[0.3em] uppercase">Our Mission</span>
              <h2 className="text-4xl sm:text-5xl font-black uppercase mt-4 tracking-tighter">
                FUEL EVERY <span className="text-pure-yellow">ATHLETE</span>
              </h2>
              <p className="text-pure-gray mt-6 leading-relaxed">
                We believe every athlete in India deserves access to premium, transparently labeled
                sports nutrition. No more guessing what is in your supplements. No more paying for
                proprietary blends that underdose key ingredients.
              </p>
              <p className="text-pure-gray mt-4 leading-relaxed">
                PRIME X is our answer. A pre-workout with clinically dosed ingredients, transparent
                labeling, and a price point that makes premium accessible.
              </p>
            </motion.div>

            <motion.div
              className="glass rounded-3xl p-8"
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7, delay: 0.2, ease: EASE }}
            >
              <div className="text-center mb-6">
                <Factory className="w-12 h-12 text-pure-yellow mx-auto mb-4" />
                <h3 className="text-xl font-black uppercase">Manufacturing</h3>
              </div>
              <div className="space-y-4">
                {[
                  'FSSAI Licensed Facility',
                  'ISO Certified Manufacturing',
                  'GMP Compliant',
                  'Regular Third-Party Testing',
                  'Banned Substance Free',
                  'WADA Compliant',
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <CheckCircle className="w-4 h-4 text-pure-yellow shrink-0" />
                    <span className="text-sm text-pure-gray">{item}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="section-padding">
        <div className="container-pure">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: EASE }}
          >
            <span className="text-pure-yellow text-sm font-bold tracking-[0.3em] uppercase">Our Values</span>
            <h2 className="text-4xl sm:text-5xl font-black uppercase mt-4 tracking-tighter">
              WHAT WE <span className="text-pure-yellow">STAND FOR</span>
            </h2>
          </motion.div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {values.map((v, i) => (
              <motion.div
                key={i}
                className="glass rounded-2xl p-8 text-center group hover:bg-pure-yellow/5 transition-all duration-500"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.3 }}
                transition={{ duration: 0.5, delay: i * 0.1, ease: EASE }}
              >
                <div className="w-14 h-14 rounded-2xl bg-pure-yellow/10 flex items-center justify-center mx-auto mb-4 group-hover:bg-pure-yellow/20 transition-colors">
                  <v.icon className="w-7 h-7 text-pure-yellow" />
                </div>
                <h3 className="text-lg font-black uppercase tracking-tight mb-2">{v.title}</h3>
                <p className="text-pure-gray text-sm leading-relaxed">{v.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="section-padding bg-gradient-to-b from-pure-black to-pure-dark/30">
        <div className="container-pure">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: EASE }}
          >
            <span className="text-pure-yellow text-sm font-bold tracking-[0.3em] uppercase">Our Journey</span>
            <h2 className="text-4xl sm:text-5xl font-black uppercase mt-4 tracking-tighter">
              THE <span className="text-pure-yellow">TIMELINE</span>
            </h2>
          </motion.div>

          <div className="relative">
            <div className="absolute left-4 md:left-1/2 top-0 bottom-0 w-px bg-pure-yellow/20" />
            {milestones.map((m, i) => (
              <motion.div
                key={i}
                className={`relative flex items-start gap-8 mb-12 ${i % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'}`}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1, ease: EASE }}
              >
                <div className="hidden md:block md:w-1/2" />
                <div className="absolute left-4 md:left-1/2 w-3 h-3 rounded-full bg-pure-yellow -translate-x-1.5 mt-2" />
                <div className="ml-12 md:ml-0 md:w-1/2 glass rounded-2xl p-6">
                  <span className="text-pure-yellow text-sm font-bold">{m.year}</span>
                  <h3 className="text-lg font-black uppercase mt-1">{m.title}</h3>
                  <p className="text-pure-gray text-sm mt-2">{m.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section-padding">
        <div className="container-pure text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: EASE }}
            className="space-y-8"
          >
            <h2 className="text-4xl sm:text-6xl font-black uppercase tracking-tighter">
              JOIN THE <span className="text-pure-yellow">MOVEMENT</span>
            </h2>
            <p className="text-pure-gray text-lg max-w-xl mx-auto">
              Fuel your ambition with PRIME X. Experience the difference of transparent, clinically dosed pre-workout.
            </p>
            <a href="/shop" className="btn-pure text-lg px-10 py-5">
              Shop PRIME X <ArrowRight className="w-5 h-5" />
            </a>
          </motion.div>
        </div>
      </section>

      <CartDrawer />

      <footer>
        <div className="wrap">
          <div className="foot-bottom">
            <span>© 2026 PURE HEALTH SUPPS®. FSSAI Lic. No. 10824999000028.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
