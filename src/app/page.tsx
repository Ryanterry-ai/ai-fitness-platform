'use client';

import React, { useEffect, useRef, useState } from 'react';
import Image from '@/components/Image';
const WelcomePopup = React.lazy(() => import('../components/WelcomePopup'));

const INGREDIENTS = [
  { value: '1.5', unit: 'g', name: 'Beta-Alanine', desc: 'Buffers lactic acid buildup in muscles, delaying fatigue so you can push harder for longer. One of the most clinically studied performance ingredients.' },
  { value: '750', unit: 'mg', name: 'Arginine HCl', desc: 'Boosts nitric oxide production for enhanced blood flow, delivering more oxygen and nutrients to working muscles during intense training.' },
  { value: '500', unit: 'mg', name: 'L-Citrulline', desc: 'Converts to L-Arginine in the kidneys, providing sustained nitric oxide support. Reduces muscle soreness and improves endurance across sessions.' },
  { value: '250', unit: 'mg', name: 'L-Carnitine', desc: 'Transports fatty acids into mitochondria for energy production. Supports endurance,加速 recovery, and helps maintain lean muscle during cutting phases.' },
  { value: '125', unit: 'mg', name: 'L-Tyrosine', desc: 'Precursor to dopamine and norepinephrine. Sharpens focus, mental clarity, and reaction time — especially under the stress of heavy training.' },
  { value: '50', unit: 'mg', name: 'Encapsulated Caffeine', desc: 'Sustained-release caffeine technology delivers clean, jitter-free energy that lasts through your entire session without the dreaded crash.' },
  { value: '45', unit: 'mg', name: 'Coffee Bean Extract', desc: 'Natural source of caffeine packed with chlorogenic antioxidants. Works synergistically with encapsulated caffeine for smooth, extended energy.' },
  { value: '37.5', unit: 'mg', name: 'Garcinia Cambogia', desc: 'Contains HCA which supports fat metabolism and may help manage appetite. Complements the energy blend for a leaner, more focused training experience.' },
];

const TESTIMONIALS = [
  { stars: '★★★★★', text: '"Half a scoop and I feel it inside fifteen minutes. No crash by the time I\'m back at my desk."', name: 'Rohit A.', role: 'Working Professional', avatar: 'R' },
  { stars: '★★★★★', text: '"Rocket Lollipop tastes exactly like it should, no chalky aftertaste. Pump lasted the whole session."', name: 'Simran K.', role: 'Strength Training', avatar: 'S' },
  { stars: '★★★★★', text: '"Finally a pre-workout that lists actual dosages instead of a \'proprietary blend.\' That\'s what sold me."', name: 'Arjun M.', role: 'Powerlifter', avatar: 'A' },
];

const PRODUCTS = [
  { flavor: 'orange', label: 'Flavour 01 — Orange', name: 'Orange', img: '/products/Orange.png', tubImg: '/products/tub-orange.png', desc: 'Bright, citrus-forward pre-workout built for the early sessions — sharp focus from the first sip.', delay: '1' },
  { flavor: 'rocket', label: 'Flavour 02 — Rocket Lollipop', name: 'Rocket Lollipop', img: '/products/Rocket Lolli pop.png', tubImg: '/products/tub-rocket.png', desc: 'Nostalgic, electric, and unapologetically fun — our most requested flavour for a reason.', delay: '2' },
  { flavor: 'fruit', label: 'Flavour 03 — Fruit Punch', name: 'Fruit Punch', img: '/products/Fruit Punch.png', tubImg: '/products/tub-fruit-punch.png', desc: 'A full mixed-fruit hit — the flagship flavour, built for max-intensity training days.', delay: '3' },
];

export default function HomePage() {
  const heroRef = useRef<HTMLDivElement>(null);
  const heroRevealRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [heroProduct, setHeroProduct] = useState(0);

  // Auto-rotate hero product
  useEffect(() => {
    const interval = setInterval(() => {
      setHeroProduct(p => (p + 1) % 3);
    }, 3200);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let heroRevealed = false;

    // Nav scroll effect
    const nav = document.getElementById('siteNav');
    const handleNavScroll = () => {
      nav?.classList.toggle('scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', handleNavScroll, { passive: true });

    // Hero parallax grid
    const handleScroll = () => {
      const grid = document.querySelector('.hero-grid') as HTMLElement | null;
      if (grid) grid.style.transform = `translateY(${window.scrollY * 0.15}px)`;

      // Hero reveal — overlay fades from 1 to 0, stays revealed once done
      const revealOverlay = heroRevealRef.current;
      if (revealOverlay && !heroRevealed) {
        const scrollY = window.scrollY;
        const heroH = window.innerHeight * 0.65;
        const opacity = Math.max(0, 1 - scrollY / heroH);
        revealOverlay.style.opacity = String(opacity);
        if (opacity <= 0) heroRevealed = true;
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });

    // Hero mouse tracking for radial gradient
    const hero = heroRef.current;
    const handleMouseMove = (e: MouseEvent) => {
      if (!hero) return;
      const r = hero.getBoundingClientRect();
      hero.style.setProperty('--mx', (((e.clientX - r.left) / r.width) * 100) + '%');
      hero.style.setProperty('--my', (((e.clientY - r.top) / r.height) * 100) + '%');
    };
    hero?.addEventListener('mousemove', handleMouseMove);

    // Canvas particles
    const canvas = canvasRef.current;
    const heroEl = heroRef.current;
    let animId: number;
    let resizeFn: (() => void) | null = null;
    if (canvas && heroEl) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        const setSize = () => {
          canvas.width = heroEl.clientWidth;
          canvas.height = heroEl.clientHeight;
        };
        setSize();
        const count = Math.round((canvas.width * canvas.height) / 24000);
        const particles = Array.from({ length: Math.max(count, 20) }, () => ({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          r: Math.random() * 1.8 + 0.5,
          vy: -(Math.random() * 0.4 + 0.1),
          vx: (Math.random() - 0.5) * 0.15,
          a: Math.random() * 0.45 + 0.12,
        }));
        const tick = () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          particles.forEach(p => {
            p.y += p.vy;
            p.x += p.vx;
            if (p.y < -10) { p.y = canvas.height + 10; p.x = Math.random() * canvas.width; }
            ctx.globalAlpha = p.a;
            ctx.fillStyle = '#FFD100';
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fill();
          });
          ctx.globalAlpha = 1;
          animId = requestAnimationFrame(tick);
        };
        tick();
        resizeFn = () => setSize();
        window.addEventListener('resize', resizeFn);
      }
    }

    // Scroll reveal system
    const revealEls = document.querySelectorAll('[reveal-on-scroll]');
    const ro = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('is-revealed');
          ro.unobserve(e.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    revealEls.forEach(el => ro.observe(el));

    const revealItems = document.querySelectorAll('[data-reveal-items]');
    const ri = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('is-revealed');
          ri.unobserve(e.target);
        }
      });
    }, { threshold: 0.05, rootMargin: '0px 0px -60px 0px' });
    revealItems.forEach(el => ri.observe(el));

    // Parallax for break sections on scroll
    const parallaxBgs = document.querySelectorAll<HTMLElement>('.parallax-bg-js');
    const handleParallaxScroll = () => {
      parallaxBgs.forEach(bg => {
        const rect = bg.closest('.parallax-break')?.getBoundingClientRect();
        if (!rect) return;
        const progress = (window.innerHeight - rect.top) / (window.innerHeight + rect.height);
        const offset = (progress - 0.5) * 80;
        bg.style.transform = `translateY(${offset}px) scale(1.15)`;
      });
    };
    window.addEventListener('scroll', handleParallaxScroll, { passive: true });

    // Tilt effect
    const tiltEls = document.querySelectorAll<HTMLElement>('.tilt');
    const handleTilt = (el: HTMLElement) => {
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const cx = r.left + r.width / 2;
        const cy = r.top + r.height / 2;
        const dx = (e.clientX - cx) / (r.width / 2);
        const dy = (e.clientY - cy) / (r.height / 2);
        el.style.transform = `perspective(900px) rotateY(${dx * 8}deg) rotateX(${-dy * 8}deg) translateZ(6px)`;
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = '';
      });
    };
    tiltEls.forEach(handleTilt);

    // Custom cursor
    const dot = document.getElementById('cursorDot');
    const ring = document.getElementById('cursorRing');
    let cursorCleanup: (() => void) | null = null;
    if (dot && ring && !matchMedia('(hover:none)').matches) {
      let mx = innerWidth / 2, my = innerHeight / 2, rx = mx, ry = my;
      const moveCursor = (e: MouseEvent) => {
        mx = e.clientX; my = e.clientY;
        dot.style.left = mx + 'px';
        dot.style.top = my + 'px';
      };
      window.addEventListener('mousemove', moveCursor);
      let loopId: number;
      const loop = () => {
        rx += (mx - rx) * 0.16;
        ry += (my - ry) * 0.16;
        ring.style.left = rx + 'px';
        ring.style.top = ry + 'px';
        loopId = requestAnimationFrame(loop);
      };
      loop();
      cursorCleanup = () => {
        window.removeEventListener('mousemove', moveCursor);
        cancelAnimationFrame(loopId);
      };
    }

    return () => {
      window.removeEventListener('scroll', handleNavScroll);
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('scroll', handleParallaxScroll);
      hero?.removeEventListener('mousemove', handleMouseMove);
      if (resizeFn) window.removeEventListener('resize', resizeFn);
      cancelAnimationFrame(animId);
      if (cursorCleanup) cursorCleanup();
    };
  }, []);

  return (
    <>
      <div className="cursor-dot" id="cursorDot" />
      <div className="cursor-ring" id="cursorRing" />
      <WelcomePopup />

      {/* ═══ NAV ═══ */}
      <header className="nav" id="siteNav">
        <div className="wrap nav-inner">
          <nav className="nav-links nav-left">
            <a href="/shop">Products</a>
            <a href="#bundle">Stack &amp; Save</a>
            <a href="#science">Formula</a>
            <a href="#why">Why PURE</a>
            <a href="#journal">Journal</a>
          </nav>
          <a href="#top" className="brand nav-center">
            <span className="brand-text">PURE</span>
          </a>
          <div className="nav-right">
            <a href="#contact" className="hide-mobile">Contact</a>
            <a href="/shop" className="btn btn-yellow nav-cta">Shop PRIME X</a>
          </div>
        </div>
      </header>

      {/* ═══ HERO ═══ */}
      <section className="hero" id="top" ref={heroRef} style={{ backgroundImage: 'url(/products/hero-slide.png)', backgroundSize: 'cover', backgroundPosition: 'center' }}>
        <div className="hero-reveal-overlay" ref={heroRevealRef} />
      </section>

      {/* ═══ MARQUEE ═══ */}
      <div className="marquee">
        <div className="marquee-track">
          {['FOCUS','PUMP','ENERGY','FOCUS','PUMP','ENERGY','FOCUS','PUMP','ENERGY','FOCUS','PUMP','ENERGY'].map((w, i) => (
            <span key={i}>{w}</span>
          ))}
        </div>
      </div>

      {/* ═══ PARALLAX BREAK 1 — EXPLOSIVE ENERGY ═══ */}
      <div className="parallax-break full-bleed" reveal-on-scroll="fade">
        <div
          className="parallax-bg-js"
          style={{ backgroundImage: 'url(/products/hero-slide.png)', backgroundSize: 'cover', backgroundPosition: 'center' }}
        />
        <div className="parallax-overlay" />
        <div className="parallax-content">
          <h2>Explosive <span className="accent">Energy</span></h2>
          <p>Greater concentration. Muscle strength. Focus that locks in from the first sip to the last rep.</p>
        </div>
      </div>

      {/* ═══ PRODUCTS ═══ */}
      <section className="products" id="products">
        <div className="wrap">
          <div className="section-head">
            <div className="eyebrow" reveal-on-scroll="fade">The Range</div>
            <h2 reveal-on-scroll="up">Only three flavours.<br />Zero filler formulas.</h2>
            <p reveal-on-scroll="up" data-delay="1">
              We didn&apos;t launch with twenty half-finished SKUs. We launched with three we&apos;d stand behind completely — each carrying the same Power Performance Nutrients Blend.
            </p>
          </div>

          <div className="product-grid">
            {PRODUCTS.map((p, i) => (
              <a href={`/product/primex-preworkout-${p.flavor === 'fruit' ? 'fruit-punch' : p.flavor === 'rocket' ? 'rocket-lollipop' : 'orange'}`} key={p.flavor} className={`p-card tilt tub-3d-card`} data-flavor={p.flavor} reveal-on-scroll="up" style={{ textDecoration: 'none', color: 'inherit' }}>
                <div className="p-flavor-tag">{p.label}</div>
                <div className="p-canvas-wrap">
                  <Image
                    src={p.tubImg}
                    alt={`Prime X - ${p.name}`}
                    width={280}
                    height={300}
                    className="tub-3d-card-img"
                    style={{ objectFit: 'contain', maxHeight: '280px', width: 'auto' }}
                  />
                </div>
                <h3>Prime X - {p.name}</h3>
                <p className="p-desc">{p.desc}</p>
                <div className="p-meta">
                  <span className="servings">80 SERVINGS · 280G</span>
                  <span className="btn btn-ghost" style={{ padding: '9px 18px', fontSize: '11px', cursor: 'pointer' }}>
                    View Details
                  </span>
                </div>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ BESTSELLER STRIP ═══ */}
      <div className="strip">
        <div className="wrap strip-inner">
          <span className="strip-label">Best Sellers</span>
          <div className="strip-scroll">
            <div className="strip-chip"><b>01</b> PRIME X Fruit Punch — Flagship</div>
            <div className="strip-chip"><b>02</b> PRIME X Rocket Lollipop — Most Requested</div>
            <div className="strip-chip"><b>03</b> PRIME X Orange — Early Session Pick</div>
            <div className="strip-chip"><b>★</b> 80 Servings Per Tub, Every Flavour</div>
          </div>
        </div>
      </div>

      {/* ═══ CATEGORY CARDS ═══ */}
      <section className="wrap" style={{ paddingTop: 0, paddingBottom: 80 }}>
        <div className="category-cards" data-reveal-items>
          <a href="/product/primex-preworkout-fruit-punch" className="category-card" data-delay="1">
            <div className="category-card-img-wrap">
              <Image src="/products/Fruit Punch.png" alt="PRIME X Fruit Punch" fill style={{ objectFit: 'cover' }} sizes="33vw" />
            </div>
            <div className="card-overlay" />
            <div className="card-content">
              <div className="card-eyebrow">Flagship</div>
              <div className="card-title">Fruit<br />Punch</div>
              <div className="card-desc">A full mixed-fruit hit for max-intensity training days.</div>
            </div>
            <div className="card-arrow">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </div>
          </a>
          <a href="/product/primex-preworkout-rocket-lollipop" className="category-card" data-delay="2">
            <div className="category-card-img-wrap">
              <Image src="/products/Rocket Lolli pop.png" alt="PRIME X Rocket Lollipop" fill style={{ objectFit: 'cover' }} sizes="33vw" />
            </div>
            <div className="card-overlay" />
            <div className="card-content">
              <div className="card-eyebrow">Most Requested</div>
              <div className="card-title">Rocket<br />Lollipop</div>
              <div className="card-desc">Nostalgic, electric, and unapologetically fun.</div>
            </div>
            <div className="card-arrow">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </div>
          </a>
          <a href="/product/primex-preworkout-orange" className="category-card" data-delay="3">
            <div className="category-card-img-wrap">
              <Image src="/products/Orange.png" alt="PRIME X Orange" fill style={{ objectFit: 'cover' }} sizes="33vw" />
            </div>
            <div className="card-overlay" />
            <div className="card-content">
              <div className="card-eyebrow">Early Session</div>
              <div className="card-title">Orange</div>
              <div className="card-desc">Bright, citrus-forward built for sharp focus.</div>
            </div>
            <div className="card-arrow">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </div>
          </a>
        </div>
      </section>

      {/* ═══ IMAGE + TEXT SPLIT — FORMULA ═══ */}
      <section className="img-text-split" reveal-on-scroll="fade">
        <div className="split-image split-image-product">
          <Image src="/products/tub-orange.png" alt="PRIME X Formula — Orange" fill style={{ objectFit: 'contain', padding: '40px' }} sizes="50vw" />
        </div>
        <div className="split-content">
          <div className="eyebrow">The Formula</div>
          <h2>Every milligram,<br />on the <span className="accent">label</span>.</h2>
          <p>No proprietary blends hiding the dose. What&apos;s on the tub is what&apos;s in the scoop — third-party tested, FSSAI compliant, banned-substance free.</p>
          <a href="#science" className="btn btn-yellow">See the Science</a>
        </div>
      </section>

      {/* ═══ SCIENCE ═══ */}
      <section className="science" id="science">
        <div className="wrap">
          <div className="section-head">
            <div className="eyebrow" style={{ color: 'var(--yellow)' }} reveal-on-scroll="fade">Power Performance Nutrients Blend</div>
            <h2 reveal-on-scroll="up">Every milligram,<br />on the label.</h2>
            <p reveal-on-scroll="up" data-delay="1" style={{ color: 'rgba(255,255,255,.65)' }}>
              No proprietary blends hiding the dose. What&apos;s on the tub is what&apos;s in the scoop — third-party tested, FSSAI compliant, banned-substance free.
            </p>
          </div>
          <div className="sci-grid" data-reveal-items>
            {INGREDIENTS.map((ing, i) => (
              <div key={ing.name} className="sci-cell" data-delay={String(i + 1)}>
                <div className="sci-cell-front">
                  <b>{ing.value}<span className="unit">{ing.unit}</span></b>
                  <span>{ing.name}</span>
                </div>
                <div className="sci-cell-hover">
                  <div className="sci-hover-name">{ing.name}</div>
                  <div className="sci-hover-dose">{ing.value}{ing.unit}</div>
                  <p>{ing.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ PARALLAX BREAK 2 — BUILT DIFFERENT ═══ */}
      <div className="parallax-break full-bleed" reveal-on-scroll="fade">
        <div
          className="parallax-bg-js"
          style={{ backgroundImage: 'url(/products/hero-slide.png)', backgroundSize: 'cover', backgroundPosition: 'center' }}
        />
        <div className="parallax-overlay" style={{ background: 'rgba(0,0,0,0.75)' }} />
        <div className="parallax-content">
          <div className="parallax-product-float">
            <Image src="/products/Fruit Punch.png" alt="PRIME X Fruit Punch" width={200} height={220} style={{ objectFit: 'contain', filter: 'drop-shadow(0 30px 60px rgba(0,0,0,0.7))' }} />
          </div>
          <h2>Built <span className="accent">Different</span></h2>
          <p>FSSAI licensed. Banned-substance free. Zero compromise. What&apos;s on the label is what&apos;s in the scoop.</p>
        </div>
      </div>

      {/* ═══ WHY PURE ═══ */}
      <section className="why" id="why">
        <div className="wrap">
          <div className="why-header" reveal-on-scroll="up">
            <div className="eyebrow" reveal-on-scroll="fade">Why PURE</div>
            <h2>Built different,<br />by design.</h2>
          </div>

          <div className="why-row" reveal-on-scroll="left">
            <div className="why-content">
              <div className="why-num">01</div>
              <h3>Full Transparency</h3>
              <p>Every ingredient, every dose, printed on the tub. No proprietary blends hiding under-dosed formulas. You know exactly what you&apos;re putting in your body — because you deserve to.</p>
            </div>
            <div className="why-image">
              <Image src="/products/tub-orange.png" alt="Full Transparency Label" width={400} height={400} style={{ objectFit: 'contain' }} />
            </div>
          </div>

          <div className="why-row why-row-reverse" reveal-on-scroll="right">
            <div className="why-content">
              <div className="why-num">02</div>
              <h3>Science-Backed Dosing</h3>
              <p>1.5g Beta-Alanine, 750mg Arginine HCl, 500mg L-Citrulline — clinical doses that actually work. We don&apos;t cut corners on the ingredients that matter.</p>
            </div>
            <div className="why-image">
              <Image src="/products/tub-fruit-punch.png" alt="Science-Backed Formula" width={400} height={400} style={{ objectFit: 'contain' }} />
            </div>
          </div>

          <div className="why-row" reveal-on-scroll="left">
            <div className="why-content">
              <div className="why-num">03</div>
              <h3>Clean Formula</h3>
              <p>Banned-substance free. FSSAI licensed and third-party tested. What&apos;s on the label is what&apos;s in the scoop — nothing more, nothing less.</p>
            </div>
            <div className="why-image">
              <Image src="/products/tub-rocket.png" alt="Clean Formula" width={400} height={400} style={{ objectFit: 'contain' }} />
            </div>
          </div>

          <div className="trust-panel tilt" reveal-on-scroll="scale">
            <h3>Trust, Verified.</h3>
            <div className="trust-row"><span>FSSAI Licence</span><span>10824999000028</span></div>
            <div className="trust-row"><span>Banned Substance</span><span>Free (TGRCO)</span></div>
            <div className="trust-row"><span>Contains Sucralose</span><span>Non-Caloric</span></div>
            <div className="trust-row"><span>Shelf Life</span><span>18 Months</span></div>
            <div className="trust-row"><span>Serving Size</span><span>3.5g / Half Scoop</span></div>
            <div className="trust-row"><span>Manufactured</span><span>Made in India 🇮🇳</span></div>
            <div className="trust-row"><span>Allergen Facility</span><span>Milk · Soy · Nuts · Barley</span></div>
          </div>
        </div>
      </section>

      {/* ═══ IMAGE + TEXT SPLIT — TRUST ═══ */}
      <section className="img-text-split reverse" reveal-on-scroll="fade">
        <div className="split-image split-image-product">
          <Image src="/products/tub-rocket.png" alt="PRIME X Rocket Lollipop" fill style={{ objectFit: 'contain', padding: '40px' }} sizes="50vw" />
        </div>
        <div className="split-content">
          <div className="eyebrow">Trust, Verified</div>
          <h2>FSSAI Licensed.<br />Banned Substance <span className="accent">Free</span>.</h2>
          <p>Manufactured under Licence No. 10824999000028. Every batch screened. What you take before training is exactly what&apos;s on the tub.</p>
          <a href="#why" className="btn btn-yellow">Why PURE</a>
        </div>
      </section>

      {/* ═══ BUNDLE ═══ */}
      <section className="bundle" id="bundle">
        <div className="wrap">
          <div className="bundle-grid">
            <div className="bundle-visual" reveal-on-scroll="left">
              <Image src="/products/Orange.png" alt="PRIME X Orange" width={220} height={240} style={{ objectFit: 'contain', height: 'auto' }} />
              <Image src="/products/Fruit Punch.png" alt="PRIME X Fruit Punch" width={240} height={260} style={{ objectFit: 'contain', height: 'auto' }} />
              <Image src="/products/Rocket Lolli pop.png" alt="PRIME X Rocket Lollipop" width={220} height={240} style={{ objectFit: 'contain', height: 'auto' }} />
            </div>
            <div className="bundle-copy" reveal-on-scroll="right">
              <div className="eyebrow">Stack &amp; Save</div>
              <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(30px,4vw,44px)', textTransform: 'uppercase', marginTop: 16 }}>
                All three flavours.<br />One tray.
              </h2>
              <p style={{ marginTop: 16, color: 'rgba(255,255,255,.62)', maxWidth: 420, lineHeight: 1.6 }}>
                Never run out mid-cycle. The Trainer&apos;s Tray bundles Orange, Rocket Lollipop and Fruit Punch — 240 servings, one order.
              </p>
              <div className="price-row">
                <span className="now">₹3,299</span>
                <span className="was">₹3,897</span>
              </div>
              <a href="https://www.puresupps.site" target="_blank" rel="noopener noreferrer" className="btn btn-yellow" style={{ marginTop: 24, display: 'inline-block' }}>
                Order Bundle
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ PARALLAX BREAK 3 — NEVER FINISHED ═══ */}
      <div className="parallax-break full-bleed" reveal-on-scroll="fade">
        <div
          className="parallax-bg-js"
          style={{ backgroundImage: 'url(/products/hero-slide.png)', backgroundSize: 'cover', backgroundPosition: 'center top' }}
        />
        <div className="parallax-overlay" style={{ background: 'rgba(0,0,0,0.75)' }} />
        <div className="parallax-content">
          <div className="parallax-product-float">
            <Image src="/products/Rocket Lolli pop.png" alt="PRIME X Rocket Lollipop" width={180} height={200} style={{ objectFit: 'contain', filter: 'drop-shadow(0 30px 60px rgba(0,0,0,0.8))' }} />
          </div>
          <h2>Never <span className="accent">Finished</span></h2>
          <p>One half-scoop. Full focus. Zero crash. Show up and do the work.</p>
        </div>
      </div>

      {/* ═══ ATHLETE BANNER ═══ */}
      <section className="banner" id="athlete">
        <div className="wrap banner-inner">
          <div className="eyebrow" reveal-on-scroll="fade">For the working athlete</div>
          <h2 reveal-on-scroll="up">
            You clock in at the office.<br />You <span>clock in</span> at the gym too.
          </h2>
          <p reveal-on-scroll="up" data-delay="1">
            PRIME X was built for people stacking a full workday against a real training schedule — not full-time athletes with unlimited recovery time. One half-scoop, and you show up.
          </p>
          <div className="hero-cta" reveal-on-scroll="up" data-delay="2">
            <a href="#products" className="btn btn-yellow">Get PRIME X</a>
          </div>
        </div>
      </section>

      {/* ═══ JOURNAL ═══ */}
      <section className="journal" id="journal">
        <div className="wrap">
          <div className="journal-grid">
            <div className="journal-copy" reveal-on-scroll="left">
              <div className="eyebrow on-light">The PURE Performance Journal</div>
              <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(30px,4vw,44px)', textTransform: 'uppercase', margin: '16px 0 24px' }}>
                Why we only<br />ship three SKUs.
              </h2>
              <p>PURE HEALTH SUPPS was built on one rule: every formula ships with its full dosage on the label, nothing hidden behind a &quot;proprietary blend.&quot;</p>
              <p>Every batch is manufactured in an FSSAI-licensed facility in India and screened against the banned substance list — what you take before training is exactly what&apos;s on the tub.</p>
              <a href="/blog" className="btn btn-ghost dark" style={{ marginTop: 10 }}>Read the Full Story</a>
            </div>
            <div className="journal-cards" reveal-on-scroll="right">
              <div className="j-card tilt">
                <b>Transparent Dosing</b>
                <span>No proprietary blends — every gram and milligram is disclosed on every tub.</span>
              </div>
              <div className="j-card tilt">
                <b>FSSAI Licensed</b>
                <span>Manufactured under Licence No. 10824999000028, made in India.</span>
              </div>
              <div className="j-card tilt">
                <b>Banned Substance Free</b>
                <span>Screened and certified so you can train and compete with confidence.</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ TESTIMONIALS ═══ */}
      <section className="testi" id="reviews">
        <div className="wrap">
          <div className="section-head">
            <div className="eyebrow" style={{ color: 'var(--yellow)' }} reveal-on-scroll="fade">Real Training, Real Feedback</div>
            <h2 reveal-on-scroll="up">What the floor<br />is saying.</h2>
            <p style={{ color: 'rgba(255,255,255,.6)' }} reveal-on-scroll="up" data-delay="1">Early feedback from our first PRIME X training cycles.</p>
          </div>
          <div className="testi-grid" data-reveal-items>
            {TESTIMONIALS.map((t, i) => (
              <div key={t.name} className="t-card" data-delay={String(i + 1)}>
                <div className="stars">{t.stars}</div>
                <p>{t.text}</p>
                <div className="t-who">
                  <div className="t-avatar">{t.avatar}</div>
                  <div><b>{t.name}</b><span>{t.role}</span></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ INSTAGRAM ═══ */}
      <section className="insta">
        <div className="wrap">
          <div className="insta-head">
            <div>
              <div className="eyebrow" reveal-on-scroll="fade">@puresupps.site</div>
              <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(30px,4vw,44px)', textTransform: 'uppercase', marginTop: 14 }} reveal-on-scroll="up">
                Follow the training.
              </h2>
            </div>
            <a href="https://instagram.com/puresupps.site" target="_blank" rel="noopener noreferrer" className="btn btn-ghost">Follow on Instagram</a>
          </div>
          <div className="insta-grid" data-reveal-items>
            {[
              { src: '/products/tub-orange.png', alt: 'PRIME X Orange', bg: '#1a0f00' },
              { src: '/products/tub-fruit-punch.png', alt: 'PRIME X Fruit Punch', bg: '#1a0010' },
              { src: '/products/tub-rocket.png', alt: 'PRIME X Rocket Lollipop', bg: '#001a18' },
              { src: '/products/Orange.png', alt: 'PRIME X Orange Product', bg: '#0f0a00' },
              { src: '/products/Fruit Punch.png', alt: 'PRIME X Fruit Punch Product', bg: '#0f0009' },
            ].map((item, i) => (
              <div key={i} className="insta-cell" data-delay={String(i + 1)} style={{ background: item.bg }}>
                <Image src={item.src} alt={item.alt} fill style={{ objectFit: 'contain', padding: '12px' }} sizes="20vw" />
                <div className="insta-hover-overlay">
                  <span className="insta-hover-icon">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ NEWSLETTER ═══ */}
      <section className="news">
        <div className="wrap news-inner">
          <h2>Get early access to new flavours &amp; drops.</h2>
          <form onSubmit={(e) => { e.preventDefault(); alert('Thanks — you\'re on the list!'); }}>
            <input type="email" placeholder="you@email.com" required />
            <button className="btn btn-yellow" type="submit">Notify Me</button>
          </form>
        </div>
      </section>

      {/* ═══ FOOTER ═══ */}
      <footer id="contact">
        <div className="wrap">
          <div className="foot-grid">
            <div>
              <div className="foot-brand">
                <span className="brand-text" style={{ fontSize: 28 }}>PURE</span>
              </div>
              <p style={{ maxWidth: 280, color: 'rgba(255,255,255,0.55)', fontSize: 14, lineHeight: 1.7 }}>
                India&apos;s high-intensity pre-workout, built on transparent dosing and zero-compromise formulation.
              </p>
            </div>
            <div className="foot-col">
              <h5>Shop</h5>
              <a href="#products">PRIME X Orange</a>
              <a href="#products">PRIME X Rocket Lollipop</a>
              <a href="#products">PRIME X Fruit Punch</a>
              <a href="#bundle">Trainer&apos;s Tray Bundle</a>
            </div>
            <div className="foot-col">
              <h5>Company</h5>
              <a href="#why">Why PURE</a>
              <a href="#science">The Formula</a>
              <a href="#journal">Journal</a>
              <a href="#reviews">Reviews</a>
            </div>
            <div className="foot-col">
              <h5>Contact</h5>
              <a href="https://puresupps.site" target="_blank" rel="noopener noreferrer">puresupps.site</a>
              <a href="mailto:puresupps.site@gmail.com">puresupps.site@gmail.com</a>
              <a href="tel:+919557513017">+91 95575 13017</a>
              <a href="https://instagram.com/puresupps.site" target="_blank" rel="noopener noreferrer">@puresupps.site</a>
            </div>
          </div>
          <div className="foot-bottom">
            <span>© 2026 PURE HEALTH SUPPS®. FSSAI Lic. No. 10824999000028. Not for medicinal use.</span>
            <div className="foot-social">
              <a href="https://instagram.com/puresupps.site" target="_blank" rel="noopener noreferrer" aria-label="Instagram">IG</a>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
