'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Menu, X } from 'lucide-react';
import Image from '@/components/Image';
import { PARTNER_URL } from '@/components/AnnouncementBar';
import CartDrawer from '../../components/CartDrawer';
const BackToTop = React.lazy(() => import('../../components/BackToTop'));

const INGREDIENTS = [
  { name: 'Beta-Alanine', dose: '1.5g', unit: 'g', color: '#FF6B00', desc: 'Delays the burn. Buffers lactic acid so you push harder when your body says quit.', science: 'Beta-Alanine increases carnosine levels in muscle tissue, which buffers hydrogen ions and delays the onset of muscular fatigue. Clinical studies show 1.5-3g per day improves endurance performance by 10-15%.', timing: 'Take 15-20 min before training. May cause harmless tingling (paresthesia) — that means it\'s working.' },
  { name: 'Arginine HCl', dose: '750', unit: 'mg', color: '#E8115A', desc: 'Floods your muscles with blood. More oxygen, more nutrients, more pump — every set counts.', science: 'L-Arginine is the direct precursor to nitric oxide (NO), a vasodilator that increases blood flow to working muscles. At 750mg, it supports meaningful increases in pump, nutrient delivery, and exercise capacity.', timing: 'Best absorbed on an empty stomach. Synergistic with L-Citrulline for extended nitric oxide support.' },
  { name: 'L-Citrulline', dose: '500', unit: 'mg', color: '#5B2EED', desc: 'The pump that lasts. Converts to Arginine in your kidneys for sustained blood flow long after your session.', science: 'L-Citrulline raises plasma arginine levels more effectively than arginine supplementation itself. It bypasses first-pass metabolism in the kidneys, providing sustained NO production for 2-3 hours post-ingestion.', timing: 'Works synergistically with Arginine HCl for extended nitric oxide support.' },
  { name: 'L-Carnitine', dose: '250', unit: 'mg', color: '#22c55e', desc: 'Turns fat into fuel. Shuttles fatty acids into your mitochondria so muscles burn cleaner, longer.', science: 'L-Carnitine transports long-chain fatty acids into the mitochondrial matrix for beta-oxidation. At 250mg, it supports fatty acid metabolism during prolonged exercise and may reduce muscle damage markers post-training.', timing: 'Consistent daily supplementation yields best results. Can be taken with food.' },
  { name: 'L-Tyrosine', dose: '125', unit: 'mg', color: '00BCD4', desc: 'Tunnel vision. Rebuilds the neurotransmitters heavy training drains — focus stays sharp when it matters.', science: 'L-Tyrosine is a conditionally essential amino acid and precursor to catecholamine neurotransmitters (dopamine, norepinephrine, epinephrine). Under physical stress, catecholamine depletion can impair focus and performance — L-Tyrosine supplementation helps maintain cognitive function.', timing: 'Best taken 30-60 min before training for peak cognitive benefits.' },
  { name: 'Encapsulated Caffeine', dose: '50', unit: 'mg', color: '#FFD100', desc: 'Slow-release energy that doesn\'t spike and crash. Coated to release over 2-3 hours so you finish strong.', science: 'Encapsulated caffeine uses enteric coating or matrix technology to release caffeine gradually over 2-3 hours, avoiding the spike-and-crash pattern of standard caffeine anhydrous. Produces sustained alertness without cardiovascular jitter.', timing: 'Takes 15-20 min to begin releasing. Effects last 2-3 hours.' },
  { name: 'Coffee Bean Extract', dose: '45', unit: 'mg', color: '#8D6E63', desc: 'Natural caffeine plus chlorogenic antioxidants. Smooths the energy curve and keeps you locked in.', science: 'Green coffee bean extract contains chlorogenic acids (CGA) that modulate caffeine absorption and provide antioxidant support. The combination with encapsulated caffeine produces a smoother energy curve than caffeine alone.', timing: 'Works best in combination with encapsulated caffeine for smooth energy release.' },
  { name: 'Garcinia Cambogia', dose: '37.5', unit: 'mg', color: '#FF9800', desc: 'Appetite support during training. HCA helps your body manage fat synthesis so you stay lean while you build.', science: 'Hydroxycitric acid (HCA) from Garcinia Cambogia inhibits citrate lyase, an enzyme involved in fatty acid synthesis. At 37.5mg, it provides a supportive role in fat metabolism without overstimulating.', timing: 'Take with food for better absorption. Synergistic with L-Carnitine.' },
];

const FAQS = [
  { q: 'Why are the doses printed on the tub?', a: 'Most brands use "proprietary blends" to hide under-dosed ingredients. You never know if you\'re getting 50mg or 500mg. We print every ingredient and every dose because you deserve to know exactly what you\'re putting in your body.' },
  { q: 'Is 1.5g Beta-Alanine enough?', a: 'Clinical research shows 1.5-3g per day of Beta-Alanine improves muscular endurance. Our 1.5g dose is at the lower end of the clinical range — effective for most athletes. For higher doses, take a full scoop (7g) instead of the recommended half scoop.' },
  { q: 'Why encapsulated caffeine instead of regular?', a: 'Regular caffeine anhydrous hits fast and crashes hard. Encapsulated caffeine releases gradually over 2-3 hours, giving you sustained energy without jitters or crashes. It\'s more expensive but delivers a better training experience.' },
  { q: 'Can I take more than one scoop?', a: 'Start with half a scoop (3.5g) to assess tolerance. If you need more, increase to one full scoop (7g). Do not exceed one scoop per day. Total caffeine per full scoop is approximately 95mg — less than a strong cup of coffee.' },
  { q: 'What does "banned substance free" mean?', a: 'Every batch is screened against the WADA banned substance list. If you compete in any sport that drug tests, you can use PRIME X with confidence. We hold FSSAI Licence No. 10824999000028.' },
];

export default function FormulaClient() {
  const [activeIngredient, setActiveIngredient] = useState(0);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'dose' | 'science' | 'timing'>('dose');
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const ing = INGREDIENTS[activeIngredient];

  useEffect(() => {
    window.scrollTo(0, 0);
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <Suspense fallback={null}>
        <BackToTop />
      </Suspense>
      <header className={`nav ${scrolled ? 'scrolled' : ''}`}>
        <div className="wrap nav-inner">
          <a href="/" className="brand"><span className="brand-text">PURE</span></a>
          <nav className="nav-links">
            <a href="/shop">Products</a>
            <a href="/formula" style={{ color: 'var(--paper)' }}>Formula</a>
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

    <div style={{ background: '#000', minHeight: '100vh', color: '#fff' }}>
      {/* ═══ HERO ═══ */}
      <section style={{ position: 'relative', minHeight: '65vh', display: 'flex', alignItems: 'center', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'url(/products/hero-slide.png)', backgroundSize: 'cover', backgroundPosition: 'center' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.65) 100%)' }} />
        <div style={{ position: 'relative', maxWidth: 1200, margin: '0 auto', padding: '80px 32px', width: '100%' }}>
          <div style={{ maxWidth: 700 }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(255,209,0,0.1)', border: '1px solid rgba(255,209,0,0.2)', borderRadius: 999, padding: '6px 18px', marginBottom: 20 }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>The Formula</span>
            </div>
            <h1 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(40px, 7vw, 72px)', textTransform: 'uppercase', lineHeight: 1, letterSpacing: '-0.02em', marginBottom: 20 }}>
              Every milligram,<br />on the <span style={{ color: 'var(--yellow)' }}>tub</span>.
            </h1>
            <p style={{ fontFamily: 'var(--body)', fontSize: 18, color: 'rgba(255,255,255,0.6)', lineHeight: 1.7, maxWidth: 560, marginBottom: 32 }}>
              No proprietary blends hiding the dose. What&apos;s on the tub is what&apos;s in the scoop — third-party tested, FSSAI compliant, banned-substance free. 8 active ingredients, clinically dosed, zero filler.
            </p>
            <a href="#ingredients" style={{ display: 'inline-block', padding: '16px 36px', background: 'var(--yellow)', color: '#000', fontFamily: 'var(--display)', fontSize: 15, letterSpacing: '0.06em', textTransform: 'uppercase', textDecoration: 'none', borderRadius: 6, fontWeight: 700 }}>
              Explore Ingredients
            </a>
          </div>
        </div>
      </section>

      {/* ═══ QUICK STATS ═══ */}
      <section style={{ borderTop: '1px solid rgba(255,255,255,0.06)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
          {[
            { value: '8', label: 'Active Ingredients' },
            { value: '0', label: 'Proprietary Blends' },
            { value: '3.5g', label: 'Serving Size' },
            { value: '80', label: 'Servings Per Tub' },
          ].map((s) => (
            <div key={s.label} style={{ padding: '28px 20px', textAlign: 'center', borderRight: '1px solid rgba(255,255,255,0.06)' }}>
              <div style={{ fontFamily: 'var(--display)', fontSize: 32, color: 'var(--yellow)' }}>{s.value}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.45)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ INGREDIENT EXPLORER ═══ */}
      <section id="ingredients" style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 32px' }}>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--yellow)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 12 }}>Power Performance Nutrients Blend</div>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 4vw, 48px)', textTransform: 'uppercase', lineHeight: 1.1 }}>
            Ingredient <span style={{ color: 'var(--yellow)' }}>Explorer</span>.
          </h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 48, alignItems: 'start' }}>
          {/* LEFT — Ingredient List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {INGREDIENTS.map((item, i) => (
              <button
                key={item.name}
                onClick={() => { setActiveIngredient(i); setActiveTab('dose'); }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                  padding: '16px 20px',
                  background: i === activeIngredient ? 'rgba(255,209,0,0.06)' : 'transparent',
                  border: i === activeIngredient ? '1px solid rgba(255,209,0,0.2)' : '1px solid transparent',
                  borderRadius: 10,
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  width: '100%',
                }}
              >
                <div style={{ width: 44, height: 44, borderRadius: 10, background: `${item.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 14, fontWeight: 700, color: item.color }}>{item.dose}{item.unit === 'g' ? 'g' : ''}</span>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: 'var(--body)', fontSize: 14, fontWeight: 700, color: i === activeIngredient ? '#fff' : 'rgba(255,255,255,0.6)' }}>{item.name}</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.35)', marginTop: 2 }}>{item.dose} {item.unit}</div>
                </div>
                {i === activeIngredient && <div style={{ width: 4, height: 4, borderRadius: '50%', background: 'var(--yellow)' }} />}
              </button>
            ))}
          </div>

          {/* RIGHT — Detail Panel */}
          <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 16, padding: 36 }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
              <div style={{ width: 56, height: 56, borderRadius: 14, background: `${ing.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 20, fontWeight: 700, color: ing.color }}>{ing.dose}{ing.unit === 'g' ? 'g' : ''}</span>
              </div>
              <div>
                <h3 style={{ fontFamily: 'var(--display)', fontSize: 28, textTransform: 'uppercase' }}>{ing.name}</h3>
                <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)', marginTop: 2 }}>{ing.desc}</p>
              </div>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
              {(['dose', 'science', 'timing'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: '10px 20px',
                    background: activeTab === tab ? 'var(--yellow)' : 'rgba(255,255,255,0.04)',
                    color: activeTab === tab ? '#000' : 'rgba(255,255,255,0.4)',
                    border: activeTab === tab ? '1px solid var(--yellow)' : '1px solid rgba(255,255,255,0.08)',
                    fontFamily: 'var(--mono)',
                    fontSize: 11,
                    fontWeight: 700,
                    letterSpacing: '0.08em',
                    textTransform: 'uppercase',
                    cursor: 'pointer',
                    borderRadius: 6,
                    transition: 'all 0.2s ease',
                  }}
                >
                  {tab === 'dose' ? 'Dosage' : tab === 'science' ? 'Science' : 'Timing'}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div style={{ minHeight: 160 }}>
              {activeTab === 'dose' && (
                <div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 20 }}>
                    <div style={{ padding: '20px 16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, textAlign: 'center' }}>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 28, fontWeight: 700, color: ing.color }}>{ing.dose}<span style={{ fontSize: 14 }}>{ing.unit}</span></div>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.1em' }}>Per Half Scoop</div>
                    </div>
                    <div style={{ padding: '20px 16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, textAlign: 'center' }}>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 28, fontWeight: 700, color: '#fff' }}>{parseInt(ing.dose) * 2}<span style={{ fontSize: 14 }}>{ing.unit}</span></div>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.1em' }}>Per Full Scoop</div>
                    </div>
                    <div style={{ padding: '20px 16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, textAlign: 'center' }}>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 28, fontWeight: 700, color: '#22c55e' }}>✓</div>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.1em' }}>Clinical Dose</div>
                    </div>
                  </div>
                  <p style={{ fontSize: 14, lineHeight: 1.7, color: 'rgba(255,255,255,0.55)' }}>{ing.desc}</p>
                </div>
              )}
              {activeTab === 'science' && (
                <div>
                  <p style={{ fontSize: 15, lineHeight: 1.8, color: 'rgba(255,255,255,0.6)', marginBottom: 16 }}>{ing.science}</p>
                  <div style={{ padding: '14px 18px', background: 'rgba(255,209,0,0.04)', border: '1px solid rgba(255,209,0,0.1)', borderRadius: 8 }}>
                    <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', lineHeight: 1.6 }}>
                      <strong style={{ color: 'var(--yellow)' }}>Key insight:</strong> This ingredient is dosed at or above the clinical threshold shown in peer-reviewed research to produce meaningful performance benefits.
                    </p>
                  </div>
                </div>
              )}
              {activeTab === 'timing' && (
                <div>
                  <p style={{ fontSize: 15, lineHeight: 1.8, color: 'rgba(255,255,255,0.6)' }}>{ing.timing}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ FULL DOSE TABLE ═══ */}
      <section style={{ borderTop: '1px solid rgba(255,255,255,0.06)', background: 'rgba(255,209,0,0.02)' }}>
        <div style={{ maxWidth: 900, margin: '0 auto', padding: '80px 32px' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 3.5vw, 40px)', textTransform: 'uppercase', lineHeight: 1.1 }}>
              Full <span style={{ color: 'var(--yellow)' }}>Supplement Facts</span>
            </h2>
          </div>

          <div style={{ border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, overflow: 'hidden' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px 100px 100px', background: 'rgba(255,255,255,0.03)', padding: '14px 24px' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Ingredient</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase', textAlign: 'center' }}>Half Scoop</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase', textAlign: 'center' }}>Full Scoop</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase', textAlign: 'center' }}>Clinical?</span>
            </div>
            {INGREDIENTS.map((item, i) => (
              <div
                key={item.name}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 100px 100px 100px',
                  padding: '14px 24px',
                  borderTop: '1px solid rgba(255,255,255,0.06)',
                  background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.015)',
                }}
              >
                <span style={{ fontSize: 14, color: 'rgba(255,255,255,0.7)' }}>{item.name}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: '#fff', textAlign: 'center' }}>{item.dose}{item.unit}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'rgba(255,255,255,0.5)', textAlign: 'center' }}>{parseInt(item.dose) * 2}{item.unit}</span>
                <span style={{ textAlign: 'center', color: '#22c55e', fontWeight: 700 }}>✓</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <section style={{ maxWidth: 800, margin: '0 auto', padding: '80px 32px' }}>
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 3.5vw, 40px)', textTransform: 'uppercase' }}>
            Frequently Asked <span style={{ color: 'var(--yellow)' }}>Questions</span>
          </h2>
        </div>
        <div>
          {FAQS.map((faq, i) => (
            <div key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <button
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
                style={{
                  width: '100%', padding: '20px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.85)', cursor: 'pointer',
                  fontFamily: 'var(--body)', fontSize: 15, fontWeight: 600, textAlign: 'left',
                }}
              >
                {faq.q}
                <span style={{ fontSize: 22, color: 'var(--yellow)', flexShrink: 0, marginLeft: 20, transition: 'transform 0.3s', transform: openFaq === i ? 'rotate(45deg)' : 'rotate(0)' }}>+</span>
              </button>
              {openFaq === i && (
                <p style={{ paddingBottom: 20, fontSize: 14, lineHeight: 1.75, color: 'rgba(255,255,255,0.5)' }}>{faq.a}</p>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ═══ CTA ═══ */}
      <section style={{ maxWidth: 800, margin: '0 auto', padding: '80px 32px', textAlign: 'center' }}>
        <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 4vw, 48px)', textTransform: 'uppercase', lineHeight: 1.1, marginBottom: 20 }}>
          See the formula<br /><span style={{ color: 'var(--yellow)' }}>in action</span>?
        </h2>
        <p style={{ fontSize: 16, color: 'rgba(255,255,255,0.5)', marginBottom: 32 }}>Every ingredient. Every dose. Zero compromise. See what you&apos;re actually paying for.</p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-block', padding: '16px 36px', background: 'var(--yellow)', color: '#000', fontFamily: 'var(--display)', fontSize: 15, letterSpacing: '0.06em', textTransform: 'uppercase', textDecoration: 'none', borderRadius: 6, fontWeight: 700 }}>
            Shop PRIME X
          </a>
          <a href="/why-pure" style={{ display: 'inline-block', padding: '16px 36px', border: '1.5px solid rgba(255,255,255,0.25)', background: 'transparent', color: '#fff', fontFamily: 'var(--display)', fontSize: 15, letterSpacing: '0.06em', textTransform: 'uppercase', textDecoration: 'none', borderRadius: 6 }}>
            Why PURE
          </a>
        </div>
      </section>
      </div>

      <CartDrawer />

      <footer>
        <div className="wrap">
          <div className="foot-bottom">
            <span>© 2026 PURE HEALTH SUPPS®. FSSAI Lic. No. 10824999000028.</span>
          </div>
        </div>
      </footer>
    </>
  );
}
