'use client';

import React, { useState } from 'react';
import Image from '@/components/Image';
import { useShop } from '@/lib/store';
import { PARTNER_URL } from '@/components/AnnouncementBar';

const INGREDIENTS_INFO = [
  { name: 'Beta-Alanine', dose: '1.5g', desc: 'Buffers lactic acid buildup in muscles, delaying fatigue so you can push harder for longer. One of the most clinically studied performance ingredients.' },
  { name: 'Arginine HCl', dose: '750mg', desc: 'Boosts nitric oxide production for enhanced blood flow, delivering more oxygen and nutrients to working muscles during intense training.' },
  { name: 'L-Citrulline', dose: '500mg', desc: 'Converts to L-Arginine in the kidneys, providing sustained nitric oxide support. Reduces muscle soreness and improves endurance across sessions.' },
  { name: 'L-Carnitine', dose: '250mg', desc: 'Transports fatty acids into mitochondria for energy production. Supports endurance and helps maintain lean muscle during cutting phases.' },
  { name: 'L-Tyrosine', dose: '125mg', desc: 'Precursor to dopamine and norepinephrine. Sharpens focus, mental clarity, and reaction time — especially under the stress of heavy training.' },
  { name: 'Encapsulated Caffeine', dose: '50mg', desc: 'Sustained-release caffeine technology delivers clean, jitter-free energy that lasts through your entire session without the dreaded crash.' },
  { name: 'Coffee Bean Extract', dose: '45mg', desc: 'Natural source of caffeine packed with chlorogenic antioxidants. Works synergistically with encapsulated caffeine for smooth, extended energy.' },
  { name: 'Garcinia Cambogia', dose: '37.5mg', desc: 'Contains HCA which supports fat metabolism and may help manage appetite. Complements the energy blend for a leaner, more focused training experience.' },
];

const FAQS = [
  { q: 'How should I take PRIME X?', a: 'Mix 3.5g (half scoop) with 200-300ml of cold water. Consume 15-20 minutes before your workout. Do not exceed 1 serving per day.' },
  { q: 'Is PRIME X safe?', a: 'PRIME X is FSSAI certified and manufactured in a licensed facility. It is banned substance free and WADA compliant. Contains caffeine — avoid combining with other caffeinated products.' },
  { q: 'How many servings per tub?', a: 'Each 280g tub provides approximately 80 servings of 3.5g (half scoop) each.' },
  { q: 'Can I stack PRIME X with other supplements?', a: 'Yes. PRIME X pairs well with creatine, BCAAs, or whey protein. Avoid combining with other pre-workouts due to cumulative caffeine content.' },
  { q: 'What does it taste like?', a: 'Each flavour is carefully formulated for a smooth, non-chalky taste. Orange is citrus-forward, Fruit Punch is a full mixed-fruit hit, and Rocket Lollipop is nostalgic and sweet.' },
];

export default function ProductPageClient({ slug }: { slug: string }) {
  const { products, addToCart } = useShop();
  const product = products.find((p) => p.slug === slug);

  const [selectedVariant, setSelectedVariant] = useState(product?.variants[0] || null);
  const [selectedImage, setSelectedImage] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [added, setAdded] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [openAccordion, setOpenAccordion] = useState<'suggested' | 'ingredients' | 'faq' | null>('ingredients');

  if (!product || !selectedVariant) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000', color: '#fff' }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontFamily: 'var(--display)', fontSize: 42, textTransform: 'uppercase', marginBottom: 16 }}>Product Not Found</h1>
          <a href="/shop" style={{ color: 'var(--yellow)', fontWeight: 700, textDecoration: 'underline' }}>Back to Shop</a>
        </div>
      </div>
    );
  }

  const handleAddToCart = () => {
    addToCart(product, selectedVariant, quantity);
    setAdded(true);
    setTimeout(() => setAdded(false), 1800);
  };

  const otherFlavours = products.filter((p) => p.id !== product.id);

  return (
    <div style={{ background: '#000', minHeight: '100vh', color: '#fff' }}>
      {/* Breadcrumb */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 32px 0' }}>
        <nav style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', fontFamily: 'var(--mono)', letterSpacing: '0.05em' }}>
          <a href="/" style={{ color: 'rgba(255,255,255,0.4)', textDecoration: 'none' }}>HOME</a>
          <span style={{ margin: '0 8px' }}>/</span>
          <a href="/shop" style={{ color: 'rgba(255,255,255,0.4)', textDecoration: 'none' }}>SHOP</a>
          <span style={{ margin: '0 8px' }}>/</span>
          <span style={{ color: '#fff' }}>{product.name}</span>
        </nav>
      </div>

      {/* Main Product Section */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 32px 80px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 60, alignItems: 'start' }}>
        {/* Left — Image Gallery */}
        <div>
          {/* Main Image */}
          <div style={{ position: 'relative', aspectRatio: '4/5', background: 'linear-gradient(145deg, #1a1a1a, #0a0a0a)', borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.06)' }}>
            <Image
              src={product.galleryImages[selectedImage]}
              alt={product.name}
              fill
              style={{ objectFit: 'contain', padding: 32 }}
              priority
            />
            {product.isBestseller && (
              <div style={{ position: 'absolute', top: 16, left: 16, background: 'var(--yellow)', color: '#000', fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, padding: '6px 12px', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                BESTSELLER
              </div>
            )}
          </div>
          {/* Thumbnails */}
          <div style={{ display: 'flex', gap: 10, marginTop: 12 }}>
            {product.galleryImages.map((img, i) => (
              <button
                key={i}
                onClick={() => setSelectedImage(i)}
                style={{
                  width: 72, height: 72, position: 'relative', borderRadius: 8, overflow: 'hidden',
                  border: i === selectedImage ? '2px solid var(--yellow)' : '1px solid rgba(255,255,255,0.1)',
                  background: '#111', cursor: 'pointer', opacity: i === selectedImage ? 1 : 0.5,
                  transition: 'all 0.2s ease',
                }}
              >
                <Image src={img} alt="" fill style={{ objectFit: 'contain', padding: 6 }} sizes="72px" />
              </button>
            ))}
          </div>
        </div>

        {/* Right — Product Details */}
        <div>
          <h1 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(32px, 4vw, 48px)', textTransform: 'uppercase', lineHeight: 1.05, marginBottom: 8 }}>
            {product.name}
          </h1>
          <p style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'rgba(255,255,255,0.45)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 24 }}>
            {product.category} · {product.flavour}
          </p>

          {/* Price */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 14, marginBottom: 28 }}>
            <span style={{ fontFamily: 'var(--display)', fontSize: 38, color: 'var(--yellow)' }}>₹{selectedVariant.price.toLocaleString('en-IN')}</span>
            {selectedVariant.originalPrice > selectedVariant.price && (
              <span style={{ fontFamily: 'var(--mono)', fontSize: 16, color: 'rgba(255,255,255,0.35)', textDecoration: 'line-through' }}>₹{selectedVariant.originalPrice.toLocaleString('en-IN')}</span>
            )}
          </div>

          {/* Flavour Selector */}
          <div style={{ marginBottom: 24 }}>
            <label style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.14em', textTransform: 'uppercase', display: 'block', marginBottom: 10 }}>
              FLAVOUR
            </label>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {product.variants.map((v) => (
                <button
                  key={v.id}
                  onClick={() => setSelectedVariant(v)}
                  style={{
                    padding: '10px 18px',
                    background: selectedVariant.id === v.id ? 'var(--yellow)' : 'transparent',
                    color: selectedVariant.id === v.id ? '#000' : 'rgba(255,255,255,0.6)',
                    border: selectedVariant.id === v.id ? '1px solid var(--yellow)' : '1px solid rgba(255,255,255,0.15)',
                    fontFamily: 'var(--body)',
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    textTransform: 'uppercase',
                    letterSpacing: '0.03em',
                  }}
                >
                  {v.name}
                </button>
              ))}
            </div>
          </div>

          {/* Size / Format */}
          <div style={{ marginBottom: 24 }}>
            <label style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.14em', textTransform: 'uppercase', display: 'block', marginBottom: 10 }}>
              FORMAT · 80 SERVINGS
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              {['280g', '560g', '840g'].map((w, i) => {
                const v = product.variants[i];
                if (!v) return null;
                return (
                  <button
                    key={w}
                    onClick={() => setSelectedVariant(v)}
                    style={{
                      flex: 1, padding: '14px 12px', textAlign: 'center',
                      background: selectedVariant.weight === w ? 'rgba(255,209,0,0.1)' : 'rgba(255,255,255,0.03)',
                      border: selectedVariant.weight === w ? '1px solid var(--yellow)' : '1px solid rgba(255,255,255,0.08)',
                      color: selectedVariant.weight === w ? 'var(--yellow)' : 'rgba(255,255,255,0.5)',
                      fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, cursor: 'pointer',
                      transition: 'all 0.2s ease', letterSpacing: '0.05em',
                    }}
                  >
                    {w}
                    <div style={{ fontSize: 10, marginTop: 4, opacity: 0.6 }}>₹{v.price.toLocaleString('en-IN')}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Quantity + Add to Cart */}
          <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <div style={{ display: 'flex', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 4 }}>
              <button onClick={() => setQuantity(Math.max(1, quantity - 1))} style={{ width: 44, background: 'transparent', border: 'none', color: '#fff', fontSize: 18, cursor: 'pointer' }}>−</button>
              <span style={{ width: 48, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--mono)', fontSize: 14, fontWeight: 700 }}>{quantity}</span>
              <button onClick={() => setQuantity(quantity + 1)} style={{ width: 44, background: 'transparent', border: 'none', color: '#fff', fontSize: 18, cursor: 'pointer' }}>+</button>
            </div>
            <button
              onClick={handleAddToCart}
              style={{
                flex: 1, padding: '16px 24px',
                background: added ? '#22c55e' : 'var(--yellow)',
                color: added ? '#fff' : '#000',
                fontFamily: 'var(--display)', fontSize: 16, letterSpacing: '0.06em',
                textTransform: 'uppercase', border: 'none', cursor: 'pointer',
                clipPath: 'polygon(0 0, 100% 0, 100% 70%, 92% 100%, 0 100%)',
                transition: 'all 0.25s ease',
              }}
            >
              {added ? '✓ ADDED' : 'ADD TO CART'}
            </button>
          </div>

          {/* Buy Now */}
          <a
            href={PARTNER_URL}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'block', width: '100%', padding: '16px 24px', textAlign: 'center',
              border: '1.5px solid rgba(255,255,255,0.25)', background: 'transparent',
              color: '#fff', fontFamily: 'var(--display)', fontSize: 14, letterSpacing: '0.06em',
              textTransform: 'uppercase', textDecoration: 'none', marginBottom: 28,
              transition: 'all 0.25s ease',
            }}
          >
            BUY NOW ON PURE SUPPS
          </a>

          {/* Trust Badges */}
          <div style={{ display: 'flex', gap: 24, paddingTop: 24, borderTop: '1px solid rgba(255,255,255,0.08)', marginBottom: 28 }}>
            {[
              { icon: '🛡️', label: 'FSSAI Certified' },
              { icon: '✓', label: 'Banned Substance Free' },
              { icon: '🇮🇳', label: 'Made in India' },
            ].map((b) => (
              <div key={b.label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 16 }}>{b.icon}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.45)', letterSpacing: '0.05em' }}>{b.label}</span>
              </div>
            ))}
          </div>

          {/* Key Benefits */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            {[
              { label: '80 SERVINGS', sub: 'Per 280g Tub' },
              { label: 'HALF SCOOP', sub: '3.5g Serving Size' },
              { label: 'ZERO CRASH', sub: 'Sustained Energy Release' },
              { label: 'CLINICAL DOSES', sub: 'Transparent Labeling' },
            ].map((b) => (
              <div key={b.label} style={{ padding: '14px 16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: 'var(--yellow)', letterSpacing: '0.08em' }}>{b.label}</div>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.45)', marginTop: 4 }}>{b.sub}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ═══ ACCORDION SECTIONS ═══ */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px 80px' }}>
        {/* Suggested Use */}
        <div style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <button
            onClick={() => setOpenAccordion(openAccordion === 'suggested' ? null : 'suggested')}
            style={{
              width: '100%', padding: '24px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer',
              fontFamily: 'var(--display)', fontSize: 20, textTransform: 'uppercase', letterSpacing: '0.04em',
            }}
          >
            SUGGESTED USE
            <span style={{ fontSize: 24, color: 'var(--yellow)', transition: 'transform 0.3s', transform: openAccordion === 'suggested' ? 'rotate(45deg)' : 'rotate(0)' }}>+</span>
          </button>
          {openAccordion === 'suggested' && (
            <div style={{ paddingBottom: 28, fontSize: 14, lineHeight: 1.8, color: 'rgba(255,255,255,0.65)', maxWidth: 700 }}>
              <p style={{ marginBottom: 12 }}>Mix 3.5g (half scoop) of PRIME X with 200-300ml of cold water. Shake or stir well.</p>
              <p style={{ marginBottom: 12 }}>Consume 15-20 minutes before your workout for optimal results.</p>
              <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12 }}>WARNING: This product is only intended for healthy adults, 18 years of age or older. Do not use if pregnant or nursing. Consult a licensed healthcare professional before use. Contains caffeine. Do not combine with other caffeinated products.</p>
            </div>
          )}
        </div>

        {/* Supplement Facts / Ingredients */}
        <div style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <button
            onClick={() => setOpenAccordion(openAccordion === 'ingredients' ? null : 'ingredients')}
            style={{
              width: '100%', padding: '24px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer',
              fontFamily: 'var(--display)', fontSize: 20, textTransform: 'uppercase', letterSpacing: '0.04em',
            }}
          >
            SUPPLEMENT FACTS
            <span style={{ fontSize: 24, color: 'var(--yellow)', transition: 'transform 0.3s', transform: openAccordion === 'ingredients' ? 'rotate(45deg)' : 'rotate(0)' }}>+</span>
          </button>
          {openAccordion === 'ingredients' && (
            <div style={{ paddingBottom: 28 }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
                {INGREDIENTS_INFO.map((ing) => (
                  <div key={ing.name} style={{ padding: '20px 18px', background: 'linear-gradient(145deg, #1a1a1a, #111)', border: '1px solid rgba(255,209,0,0.1)', borderRadius: 10 }}>
                    <div style={{ fontFamily: 'var(--mono)', fontSize: 24, fontWeight: 700, color: '#fff' }}>
                      {ing.dose.replace(/[^0-9.]/g, '')}
                      <span style={{ fontSize: 12, color: 'var(--yellow)', marginLeft: 3 }}>{ing.dose.replace(/[0-9.]/g, '')}</span>
                    </div>
                    <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: 6 }}>
                      {ing.name}
                    </div>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 20, padding: '16px 20px', background: 'rgba(255,209,0,0.05)', border: '1px solid rgba(255,209,0,0.1)', fontSize: 13, color: 'rgba(255,255,255,0.55)', lineHeight: 1.7 }}>
                <strong style={{ color: 'var(--yellow)' }}>Power Performance Nutrients Blend</strong> — Every ingredient, every dose, printed on the tub. No proprietary blends hiding under-dosed formulas. Third-party tested, FSSAI compliant, banned-substance free.
              </div>
            </div>
          )}
        </div>

        {/* FAQ */}
        <div>
          <button
            onClick={() => setOpenAccordion(openAccordion === 'faq' ? null : 'faq')}
            style={{
              width: '100%', padding: '24px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer',
              fontFamily: 'var(--display)', fontSize: 20, textTransform: 'uppercase', letterSpacing: '0.04em',
            }}
          >
            FAQ
            <span style={{ fontSize: 24, color: 'var(--yellow)', transition: 'transform 0.3s', transform: openAccordion === 'faq' ? 'rotate(45deg)' : 'rotate(0)' }}>+</span>
          </button>
          {openAccordion === 'faq' && (
            <div style={{ paddingBottom: 28 }}>
              {FAQS.map((faq, i) => (
                <div key={i} style={{ borderBottom: i < FAQS.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
                  <button
                    onClick={() => setOpenFaq(openFaq === i ? null : i)}
                    style={{
                      width: '100%', padding: '18px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.8)', cursor: 'pointer',
                      fontFamily: 'var(--body)', fontSize: 14, fontWeight: 600, textAlign: 'left',
                    }}
                  >
                    {faq.q}
                    <span style={{ fontSize: 18, color: 'var(--yellow)', flexShrink: 0, marginLeft: 16, transition: 'transform 0.3s', transform: openFaq === i ? 'rotate(45deg)' : 'rotate(0)' }}>+</span>
                  </button>
                  {openFaq === i && (
                    <p style={{ paddingBottom: 18, fontSize: 13, lineHeight: 1.7, color: 'rgba(255,255,255,0.5)' }}>{faq.a}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ═══ STACKS WELL WITH ═══ */}
      {otherFlavours.length > 0 && (
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px 100px' }}>
          <h2 style={{ fontFamily: 'var(--display)', fontSize: 'clamp(28px, 3.5vw, 40px)', textTransform: 'uppercase', marginBottom: 32 }}>
            TRY ANOTHER <span style={{ color: 'var(--yellow)' }}>FLAVOUR</span>
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
            {otherFlavours.map((p) => (
              <a
                key={p.id}
                href={`/product/${p.slug}`}
                style={{
                  display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'center',
                  padding: 24, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                  textDecoration: 'none', color: '#fff', transition: 'all 0.3s ease',
                }}
              >
                <div style={{ position: 'relative', aspectRatio: '1/1' }}>
                  <Image src={p.image} alt={p.name} fill style={{ objectFit: 'contain', padding: 16 }} />
                </div>
                <div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 18, textTransform: 'uppercase', marginBottom: 6 }}>{p.name.split('—')[1]?.trim() || p.name}</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'rgba(255,255,255,0.45)' }}>80 SERVINGS · 280G</div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 22, color: 'var(--yellow)', marginTop: 8 }}>₹{p.price.toLocaleString('en-IN')}</div>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Responsive override */}
      <style>{`
        @media(max-width:900px) {
          div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }
          div[style*="grid-template-columns: repeat(4"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }
      `}</style>
    </div>
  );
}
