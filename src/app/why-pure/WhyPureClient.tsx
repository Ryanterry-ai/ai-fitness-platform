'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Menu, X } from 'lucide-react';
import Image from '@/components/Image';
import { PARTNER_URL } from '@/components/AnnouncementBar';
import CartDrawer from '../../components/CartDrawer';
const BackToTop = React.lazy(() => import('../../components/BackToTop'));

const COMPARISON = [
  { feature: 'Transparent Dosing', pure: true, others: false, note: 'Every milligram on the label' },
  { feature: 'Proprietary Blend Free', pure: true, others: false, note: 'No hidden formulas' },
  { feature: 'FSSAI Licensed', pure: true, others: true, note: 'Licence No. 10824999000028' },
  { feature: 'Banned Substance Free', pure: true, others: true, note: 'TGRCO screened' },
  { feature: 'Clinical Doses', pure: true, others: false, note: '1.5g Beta-Alanine, 750mg Arginine' },
  { feature: 'Sustained-Release Caffeine', pure: true, others: false, note: 'Zero crash formula' },
  { feature: '80 Servings Per Tub', pure: true, others: false, note: 'Best value per serving' },
  { feature: 'Made in India', pure: true, others: true, note: 'Manufactured domestically' },
];

const PILLARS = [
  {
    num: '01',
    title: 'Full Transparency',
    subtitle: 'No Hiding. No Guessing.',
    desc: 'Every ingredient, every dose — printed on the tub. Most brands use "proprietary blends" to hide under-dosed ingredients. You never know if you\'re getting 50mg or 500mg. With PURE, 1.5g Beta-Alanine means 1.5g Beta-Alanine. Period.',
    detail: 'When a brand uses a proprietary blend, they can put 200mg in a 2g blend and call it "Energy Matrix." That\'s not transparency — that\'s a loophole. We print every milligram because you deserve to know exactly what you\'re paying for.',
    image: '/products/tub-orange.png',
  },
  {
    num: '02',
    title: 'Science-Backed Dosing',
    subtitle: 'Clinically Effective. Not Filler.',
    desc: '1.5g Beta-Alanine. 750mg Arginine HCl. 500mg L-Citrulline. These aren\'t random numbers — they\'re the thresholds where peer-reviewed research shows real results. Most pre-workouts use half these doses to save money. Half-doses don\'t work.',
    detail: 'Beta-Alanine at 1.5g buffers lactic acid for real endurance. Arginine at 750mg drives nitric oxide for visible pumps. L-Citrulline at 500mg sustains blood flow for your entire session. This is how performance supplements should be dosed.',
    image: '/products/tub-fruit-punch.png',
  },
  {
    num: '03',
    title: 'Clean Formula',
    subtitle: 'What\'s In the Scoop Is What\'s on the Tub.',
    desc: 'Banned-substance free. FSSAI licensed. Every batch screened against the WADA list. No fillers, no artificial colours for show, no pixie-dusted ingredients to make a label look impressive. Just performance, nothing else.',
    detail: 'Manufactured under FSSAI Licence No. 10824999000028 in a licensed facility. If you compete — or just care about what goes in your body — this is the standard.',
    image: '/products/tub-rocket.png',
  },
  {
    num: '04',
    title: 'Zero Crash Energy',
    subtitle: 'Sustained Release. Clean Focus.',
    desc: 'Encapsulated caffeine releases gradually over 2-3 hours. No 20-minute spike, no hard crash at your desk. Combined with Coffee Bean Extract for smooth antioxidants — focus that holds without the jitters.',
    detail: 'Most pre-workouts dump 300mg of cheap caffeine anhydrous for a quick high that fades fast. Our encapsulated technology gives you energy from warm-up to final set, then lets you transition back to your evening without the crash.',
    image: '/products/Orange.png',
  },
];

const PROBLEMS = [
  {
    problem: 'Proprietary Blends',
    what_others_do: 'Hide behind "Energy Blend" or "Performance Matrix" so you never know the actual dose of each ingredient.',
    what_pure_does: 'Every ingredient, every dose — printed on the tub. 1.5g Beta-Alanine means 1.5g, not "part of a 2g blend."',
  },
  {
    problem: 'Under-Dosed Ingredients',
    what_others_do: 'Use 250mg Beta-Alanine (clinical dose is 1.5-3g) and 100mg Arginine (effective dose is 600mg+) to cut costs.',
    what_pure_does: 'Clinical doses that match published research. 1.5g Beta-Alanine. 750mg Arginine HCl. 500mg L-Citrulline.',
  },
  {
    problem: 'Jitter & Crash',
    what_others_do: 'Dump 300mg of cheap caffeine anhydrous for a 20-minute spike followed by a hard crash at your desk.',
    what_pure_does: 'Sustained-release encapsulated caffeine (50mg) + Coffee Bean Extract (45mg) for smooth, crash-free energy.',
  },
  {
    problem: 'Filler Ingredients',
    what_others_do: 'Add maltodextrin, artificial colours, and anti-caking agents that dilute the active formula.',
    what_pure_does: 'Zero filler. Every ingredient serves a performance purpose. No unnecessary additives, no empty space.',
  },
  {
    problem: 'No Accountability',
    what_others_do: 'Manufactured in unregulated facilities with no third-party testing or banned substance screening.',
    what_pure_does: 'FSSAI licensed facility. TGRCO banned substance screening. Full traceability on every batch.',
  },
];

const TESTIMONIALS = [
  { name: 'Rohit A.', role: 'Working Professional', text: 'Half a scoop, fifteen minutes in, and I\'m locked in. No crash when I get back to my desk — just a productive evening ahead. This is the only pre-workout I trust for sessions before work.', avatar: 'R' },
  { name: 'Simran K.', role: 'Strength Training', text: 'Rocket Lollipop tastes insane. No chalky aftertaste, no weird chemical finish. Pump was dialed from warm-up to last set. I\'ve tried five other brands — PURE is the only one that delivers on the label.', avatar: 'S' },
  { name: 'Arjun M.', role: 'Powerlifter', text: 'Finally — a label that doesn\'t hide behind "proprietary blends." Every dose printed, every ingredient backed by research. That\'s what got me. The transparency is everything.', avatar: 'A' },
  { name: 'Priya R.', role: 'CrossFit Athlete', text: 'Switched from a major international brand and the difference is real. Same clinical doses, better price, and I can actually see what I\'m taking. No more guessing games with my stack.', avatar: 'P' },
];

const NUMBERS = [
  { value: '1.5g', label: 'Beta-Alanine', sub: 'Clinical dose' },
  { value: '750mg', label: 'Arginine HCl', sub: 'Full pump support' },
  { value: '500mg', label: 'L-Citrulline', sub: 'Endurance boost' },
  { value: '80', label: 'Servings', sub: 'Per 280g tub' },
  { value: '₹1,299', label: 'Starting at', sub: 'Best value per serving' },
  { value: '0', label: 'Proprietary Blends', sub: 'Full transparency' },
];

export default function WhyPureClient() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

  return (
    <>
      <Suspense fallback={null}>
        <BackToTop />
      </Suspense>
      <header className={`nav ${scrolled ? 'scrolled' : ''}`}>
        <div className="wrap nav-inner">
          <a href="/" className="brand"><span className="brand-text">PURE</span></a>
          <nav className="nav-links">
            <a href="/">Home</a>
            <a href="/wholesale">Wholesale &amp; Retails</a>
            <a href="/contact">Contact Us</a>
            <a href="/athletes">Our Athletes</a>
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
            <a href="/" onClick={() => setMobileMenuOpen(false)}>Home</a>
            <a href="/wholesale" onClick={() => setMobileMenuOpen(false)}>Wholesale &amp; Retails</a>
            <a href="/contact" onClick={() => setMobileMenuOpen(false)}>Contact Us</a>
            <a href="/athletes" onClick={() => setMobileMenuOpen(false)}>Our Athletes</a>
            <a href={PARTNER_URL} target="_blank" rel="noopener noreferrer" className="btn-pure" style={{ marginTop: 16 }}>Shop PRIME X</a>
          </motion.div>
        )}
      </AnimatePresence>

    <div style={{ background: '#000', minHeight: '100vh', color: '#fff' }}>
      {/* ═══ HERO ═══ */}
      <section style={{ position: 'relative', minHeight: '70vh', display: 'flex', alignItems: 'center', overflow: 'hidden' }}>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: 'url(/products/hero-slide.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.6) 100%)' }} />
        <div style={{ position: 'relative', maxWidth: 1200, margin: '0 auto', padding: '80px 32px', width: '100%' }}>
          <div style={{ maxWidth: 700 }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                background: 'rgba(255,209,0,0.1)',
                border: '1px solid rgba(255,209,0,0.2)',
                borderRadius: 999,
                padding: '6px 18px',
                marginBottom: 20,
              }}
            >
              <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
                Why PURE
              </span>
            </div>
            <h1 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(40px, 7vw, 72px)', textTransform: 'uppercase', lineHeight: 1, letterSpacing: '-0.02em', marginBottom: 20 }}>
              Not just another<br /><span style={{ color: 'var(--yellow)' }}>pre-workout</span>.
            </h1>
            <p style={{ fontFamily: 'var(--body)', fontSize: 18, color: 'rgba(255,255,255,0.6)', lineHeight: 1.7, maxWidth: 560, marginBottom: 32 }}>
              Most brands hide behind proprietary blends, pixie-dust clinical ingredients, and sell you half a formula at full price. PURE was built to be the opposite — full transparency, real doses, zero compromise.
            </p>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <a href="#comparison" style={{ display: 'inline-block', padding: '16px 32px', background: 'var(--yellow)', color: '#000', fontFamily: 'var(--display)', fontSize: 14, letterSpacing: '0.06em', textTransform: 'uppercase', textDecoration: 'none', borderRadius: 6, fontWeight: 700, transition: 'all 0.25s ease' }}>
                See the Comparison
              </a>
              <a href="#pillars" style={{ display: 'inline-block', padding: '16px 32px', border: '1.5px solid rgba(255,255,255,0.25)', background: 'transparent', color: '#fff', fontFamily: 'var(--display)', fontSize: 14, letterSpacing: '0.06em', textTransform: 'uppercase', textDecoration: 'none', borderRadius: 6, transition: 'all 0.25s ease' }}>
                Our 4 Pillars
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ NUMBERS STRIP ═══ */}
      <section style={{ borderTop: '1px solid rgba(255,255,255,0.06)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)' }}>
          {NUMBERS.map((n) => (
            <div key={n.label} style={{ padding: '32px 20px', textAlign: 'center', borderRight: '1px solid rgba(255,255,255,0.06)' }}>
              <div style={{ fontFamily: 'var(--display)', fontSize: 28, color: 'var(--yellow)', marginBottom: 4 }}>{n.value}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>{n.label}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'rgba(255,255,255,0.3)', marginTop: 2 }}>{n.sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ THE PROBLEM — WHY OTHERS FALL SHORT ═══ */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 32px' }}>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--yellow)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 12 }}>The Problem</div>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 4vw, 48px)', textTransform: 'uppercase', lineHeight: 1.1 }}>
            What other brands<br /><span style={{ color: 'var(--yellow)' }}>don't want you to know</span>.
          </h2>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {PROBLEMS.map((item, i) => (
            <div
              key={i}
              style={{
                display: 'grid',
                gridTemplateColumns: '200px 1fr 1fr',
                gap: 24,
                padding: '24px 28px',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: 12,
                alignItems: 'start',
              }}
            >
              <div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.3)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6 }}>Problem</div>
                <div style={{ fontFamily: 'var(--display)', fontSize: 16, textTransform: 'uppercase', color: '#E8115A' }}>{item.problem}</div>
              </div>
              <div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.3)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6 }}>Other Brands</div>
                <div style={{ fontSize: 13, lineHeight: 1.6, color: 'rgba(255,255,255,0.45)' }}>{item.what_others_do}</div>
              </div>
              <div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--yellow)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6 }}>PURE Answer</div>
                <div style={{ fontSize: 13, lineHeight: 1.6, color: 'rgba(255,255,255,0.7)' }}>{item.what_pure_does}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ COMPARISON TABLE ═══ */}
      <section id="comparison" style={{ background: 'rgba(255,209,0,0.02)', borderTop: '1px solid rgba(255,255,255,0.06)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '80px 32px' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--yellow)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 12 }}>Head to Head</div>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 4vw, 48px)', textTransform: 'uppercase', lineHeight: 1.1 }}>
              PURE vs <span style={{ color: 'rgba(255,255,255,0.3)' }}>the rest</span>.
            </h2>
          </div>

          <div style={{ border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, overflow: 'hidden' }}>
            {/* Header */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px 120px', background: 'rgba(255,255,255,0.03)' }}>
              <div style={{ padding: '16px 24px', fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Feature</div>
              <div style={{ padding: '16px 24px', fontFamily: 'var(--display)', fontSize: 14, color: 'var(--yellow)', textAlign: 'center', textTransform: 'uppercase', letterSpacing: '0.06em' }}>PURE</div>
              <div style={{ padding: '16px 24px', fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.3)', textAlign: 'center', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Others</div>
            </div>

            {/* Rows */}
            {COMPARISON.map((row, i) => (
              <div
                key={row.feature}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 120px 120px',
                  borderTop: '1px solid rgba(255,255,255,0.06)',
                  background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.015)',
                }}
              >
                <div style={{ padding: '14px 24px', fontSize: 14, color: 'rgba(255,255,255,0.7)' }}>{row.feature}</div>
                <div style={{ padding: '14px 24px', textAlign: 'center' }}>
                  <span style={{ color: row.pure ? '#22c55e' : '#E8115A', fontSize: 18, fontWeight: 700 }}>
                    {row.pure ? '✓' : '✗'}
                  </span>
                </div>
                <div style={{ padding: '14px 24px', textAlign: 'center' }}>
                  <span style={{ color: row.others ? '#22c55e' : '#E8115A', fontSize: 18, fontWeight: 700 }}>
                    {row.others ? '✓' : '✗'}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <p style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.3)', textAlign: 'center', marginTop: 16, letterSpacing: '0.04em' }}>
            * Based on公开 label data from top-selling Indian pre-workouts as of 2026
          </p>
        </div>
      </section>

      {/* ═══ 4 PILLARS ═══ */}
      <section id="pillars" style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 32px' }}>
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--yellow)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 12 }}>Our Foundation</div>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 4vw, 48px)', textTransform: 'uppercase', lineHeight: 1.1 }}>
            The four pillars<br />that make us <span style={{ color: 'var(--yellow)' }}>different</span>.
          </h2>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 48 }}>
          {PILLARS.map((p, i) => (
            <div
              key={p.num}
              style={{
                display: 'grid',
                gridTemplateColumns: i % 2 === 0 ? '1fr 1fr' : '1fr 1fr',
                gap: 60,
                alignItems: 'center',
                direction: i % 2 === 0 ? 'ltr' : 'rtl',
              }}
            >
              {/* Content */}
              <div style={{ direction: 'ltr' }}>
                <div style={{ fontFamily: 'var(--display)', fontSize: 64, color: 'rgba(255,209,0,0.12)', lineHeight: 1, marginBottom: -10 }}>{p.num}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--yellow)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 8 }}>{p.subtitle}</div>
                <h3 style={{ fontFamily: 'var(--display)', fontSize: 32, textTransform: 'uppercase', lineHeight: 1.15, marginBottom: 16 }}>{p.title}</h3>
                <p style={{ fontSize: 15, lineHeight: 1.8, color: 'rgba(255,255,255,0.6)', marginBottom: 16 }}>{p.desc}</p>
                <p style={{ fontSize: 13, lineHeight: 1.7, color: 'rgba(255,255,255,0.4)', padding: '16px 20px', background: 'rgba(255,209,0,0.03)', border: '1px solid rgba(255,209,0,0.08)', borderRadius: 8 }}>
                  {p.detail}
                </p>
              </div>

              {/* Image */}
              <div style={{ direction: 'ltr', position: 'relative', aspectRatio: '4/5', background: 'linear-gradient(145deg, #161616, #0a0a0a)', borderRadius: 16, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.04)' }}>
                <Image src={p.image} alt={p.title} fill style={{ objectFit: 'contain', padding: 48 }} />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ TESTIMONIALS ═══ */}
      <section style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 32px' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--yellow)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 12 }}>Real Athletes. Real Feedback.</div>
            <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 4vw, 48px)', textTransform: 'uppercase', lineHeight: 1.1 }}>
              What they're <span style={{ color: 'var(--yellow)' }}>saying</span>.
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
            {TESTIMONIALS.map((t) => (
              <div
                key={t.name}
                style={{
                  padding: '28px 28px',
                  background: 'rgba(255,255,255,0.025)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  borderRadius: 12,
                }}
              >
                <div style={{ fontFamily: 'var(--mono)', fontSize: 14, color: 'var(--yellow)', marginBottom: 12 }}>★★★★★</div>
                <p style={{ fontSize: 15, lineHeight: 1.7, color: 'rgba(255,255,255,0.65)', marginBottom: 20, fontStyle: 'italic' }}>
                  "{t.text}"
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--yellow)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--display)', fontSize: 16, color: '#000', fontWeight: 700 }}>
                    {t.avatar}
                  </div>
                  <div>
                    <div style={{ fontFamily: 'var(--body)', fontSize: 14, fontWeight: 700 }}>{t.name}</div>
                    <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>{t.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ TRUST PANEL ═══ */}
      <section style={{ background: 'rgba(255,209,0,0.03)', borderTop: '1px solid rgba(255,255,255,0.06)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '60px 32px', textAlign: 'center' }}>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 28, textTransform: 'uppercase', marginBottom: 28 }}>Verified. Not Just Claimed.</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32 }}>
            {[
              { label: 'FSSAI Licence', value: '10824999000028' },
              { label: 'Banned Substance', value: 'Free (TGRCO)' },
              { label: 'Shelf Life', value: '18 Months' },
              { label: 'Serving Size', value: '3.5g / Half Scoop' },
              { label: 'Servings Per Tub', value: '80' },
              { label: 'Manufactured', value: 'Made in India' },
            ].map((item) => (
              <div key={item.label} style={{ padding: '16px 12px', background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--yellow)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>{item.label}</div>
                <div style={{ fontFamily: 'var(--body)', fontSize: 14, fontWeight: 700 }}>{item.value}</div>
              </div>
            ))}
          </div>
          <p style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.35)', letterSpacing: '0.04em' }}>
            Allergen: Milk · Soy · Nuts · Barley. Not for medicinal use.
          </p>
        </div>
      </section>

      {/* ═══ FINAL CTA ═══ */}
      <section style={{ maxWidth: 800, margin: '0 auto', padding: '100px 32px', textAlign: 'center' }}>
        <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(36px, 5vw, 56px)', textTransform: 'uppercase', lineHeight: 1.05, marginBottom: 20 }}>
          Ready to train<br /><span style={{ color: 'var(--yellow)' }}>different</span>?
        </h2>
        <p style={{ fontFamily: 'var(--body)', fontSize: 17, color: 'rgba(255,255,255,0.5)', lineHeight: 1.7, maxWidth: 500, margin: '0 auto 36px' }}>
          Every ingredient. Every dose. Zero compromise. Join the athletes who refuse to guess what&apos;s in their supplements.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <a
            href={PARTNER_URL}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-block',
              padding: '18px 40px',
              background: 'var(--yellow)',
              color: '#000',
              fontFamily: 'var(--display)',
              fontSize: 16,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              textDecoration: 'none',
              borderRadius: 6,
              fontWeight: 700,
              transition: 'all 0.25s ease',
            }}
          >
            Shop PRIME X
          </a>
          <a
            href="/shop"
            style={{
              display: 'inline-block',
              padding: '18px 40px',
              border: '1.5px solid rgba(255,255,255,0.25)',
              background: 'transparent',
              color: '#fff',
              fontFamily: 'var(--display)',
              fontSize: 16,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              textDecoration: 'none',
              borderRadius: 6,
              transition: 'all 0.25s ease',
            }}
          >
            View All Flavours
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
