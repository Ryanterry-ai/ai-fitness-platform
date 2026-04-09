"use client";

import Image from "next/image";
import { useState } from "react";
import BestSellers from "@/components/BestSellers";
import ProductCarousel from "@/components/ProductCarousel";

const topBarLinks = [
  { href: "https://www.facebook.com/needsupplements/", label: "Facebook" },
  { href: "https://www.youtube.com/channel/UCn5elEu8ZPYqfE388aZp_Og", label: "YouTube" },
  { href: "https://www.instagram.com/need_supps/", label: "Instagram" },
];

const navLinks = [
  { href: "/collections/proteins", label: "PROTEINS" },
  { href: "/collections/pre-training", label: "PRE-TRAINING" },
  { href: "/collections/muscle-builder", label: "BUILD MUSCLE" },
  { href: "/collections/amino-acids", label: "AMINO ACIDS" },
  { href: "/collections/vitality-and-health", label: "VITAMINS & MINERALS" },
  { href: "/collections/weight-loss", label: "WEIGHT LOSS" },
];

const bestSellers = [
  {
    id: 1,
    name: "NEED PURE WHEY",
    price: "From €1,95",
    image: "/images/products/pure-whey.png",
    status: "sold-out",
    reviews: 34,
  },
  {
    id: 2,
    name: "NEED DIURE·6",
    price: "€19,50",
    originalPrice: "€25,90",
    image: "/images/products/diure6.png",
    discount: "25% off",
    status: "sold-out",
    reviews: 5,
  },
  {
    id: 3,
    name: "NEED PURE ISO",
    price: "€69,90",
    originalPrice: "€104,90",
    image: "/images/products/pure-iso.png",
    discount: "33% off",
    status: "sale",
    reviews: 4,
  },
  {
    id: 4,
    name: "NEED 0·CARBS",
    price: "€24,90",
    originalPrice: "€29,90",
    image: "/images/products/0carbs.png",
    discount: "17% off",
    status: "sale",
    reviews: 4,
  },
];

const categories = [
  { name: "Proteins", image: "/images/category-proteins.jpg", href: "/collections/proteins" },
  { name: "Pre-training", image: "/images/category-pretraining.jpg", href: "/collections/pre-training" },
  { name: "Amino acids", image: "/images/category-aminoacids.jpg", href: "/collections/amino-acids" },
  { name: "Vitamins & Minerals", image: "/images/category-vitamins.jpg", href: "/collections/vitality-and-health" },
  { name: "Weight loss", image: "/images/category-weightloss.jpg", href: "/collections/weight-loss" },
  { name: "Build Muscle", image: "/images/category-buildmuscle.jpg", href: "/collections/muscle-builder" },
];

const muscleProducts = [
  { name: "NEED PURE WHEY", price: "From €1,95", image: "/images/products/pure-whey.png", status: "sold-out", reviews: 34 },
  { name: "NEED POWER CREATINE", price: "From €1,95", image: "/images/products/power-creatine.png", status: "", reviews: 10 },
  { name: "NEED BCAAS & GLUTAMINE", price: "From €1,95", image: "/images/products/bcaas-glutamine.png", status: "sold-out", reviews: 14 },
  { name: "NEED PURE MASS GAINER", price: "€39,90", originalPrice: "€76,90", image: "/images/products/mass-gainer.png", discount: "48% off", status: "sale", reviews: 10 },
  { name: "NEED PURE ISO", price: "€69,90", originalPrice: "€104,90", image: "/images/products/pure-iso.png", discount: "33% off", status: "sale", reviews: 4 },
  { name: "NEED TE5TO S7", price: "€24,90", originalPrice: "€42,90", image: "/images/products/testo-s7.png", discount: "42% off", status: "sale", reviews: 1 },
  { name: "NEED PROTEIN MAX", price: "€57,65", image: "/images/products/protein-max.png", status: "sold-out", reviews: 0 },
];

const footerLinks = {
  shop: [
    { href: "/collections/proteins", label: "PROTEINS" },
    { href: "/collections/pre-training", label: "PRE-TRAINING" },
    { href: "/collections/muscle-builder", label: "BUILD MUSCLE" },
    { href: "/collections/amino-acids", label: "AMINO ACIDS" },
    { href: "/collections/vitality-and-health", label: "VITAMINS & MINERALS" },
    { href: "/collections/weight-loss", label: "WEIGHT LOSS" },
  ],
  company: [
    { href: "/blogs/the-health-project", label: "The Health Project" },
    { href: "/pages/about-us", label: "About us" },
    { href: "/pages/contact-us", label: "Contact us" },
  ],
  legal: [
    { href: "/policies/privacy-policy", label: "Privacy Policy" },
    { href: "/policies/legal-notice", label: "Legal Notice" },
    { href: "/policies/shipping-policy", label: "Shipping Policy" },
    { href: "/policies/refund-policy", label: "Refund Policy" },
    { href: "/policies/terms-of-service", label: "Terms of Service" },
    { href: "/pages/cookie-policy-page", label: "Cookies" },
  ],
};

export default function Home() {
  const [carouselIndex, setCarouselIndex] = useState(0);
  const productsPerView = 4;
  const maxIndex = Math.max(0, muscleProducts.length - productsPerView);

  const scrollCarousel = (direction: 'left' | 'right') => {
    setCarouselIndex(prev => {
      if (direction === 'left') return Math.max(0, prev - 1);
      return Math.min(maxIndex, prev + 1);
    });
  };

  return (
    <div className="min-h-screen font-roboto">
      {/* Yellow Announcement Bar */}
      <div className="bg-[#ffcc00] text-black text-xs py-2 px-4">
        <div className="max-w-[1100px] mx-auto flex items-center justify-between">
          {/* Social Icons */}
          <div className="flex items-center gap-3">
            <a href="https://www.facebook.com/needsupplements/" target="_blank" rel="noopener noreferrer" className="hover:opacity-70 transition-opacity">
              <svg xmlns="http://www.w3.org/2000/svg" width={18} height={18} viewBox="0 0 24 24" fill="currentColor">
                <path d="M18.77,7.46H14.5v-1.9c0-.9.6-1.1,1-1.1h3V.5h-4.33C10.24.5,9.5,3.44,9.5,5.32v2.15h-3v4h3v12h5v-12h3.85l.42-4Z"/>
              </svg>
            </a>
            <a href="https://www.youtube.com/channel/UCn5elEu8ZPYqfE388aZp_Og" target="_blank" rel="noopener noreferrer" className="hover:opacity-70 transition-opacity">
              <svg xmlns="http://www.w3.org/2000/svg" width={18} height={18} viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.5,6.19a3.02,3.02,0,0,0-2.12-2.14C19.54,3.5,12,3.5,12,3.5s-7.54,0-9.38.55A3.02,3.02,0,0,0,.5,6.19,30.56,30.56,0,0,0,0,12a30.56,30.56,0,0,0,.5,5.81,3.02,3.02,0,0,0,2.12,2.14c1.84.55,9.38.55,9.38.55s7.54,0,9.38-.55a3.02,3.02,0,0,0,2.12-2.14A30.56,30.56,0,0,0,24,12,30.56,30.56,0,0,0,23.5,6.19ZM9.55,15.57V8.43L15.82,12Z"/>
              </svg>
            </a>
            <a href="https://www.instagram.com/need_supps/" target="_blank" rel="noopener noreferrer" className="hover:opacity-70 transition-opacity">
              <svg xmlns="http://www.w3.org/2000/svg" width={18} height={18} viewBox="0 0 24 24" fill="currentColor">
                <path d="M12,2.16c3.2,0,3.58,0,4.85.07,1.17.07,2,.26,2.71.55s1.56.89,2.23,1.55,1.22,1.38,1.55,2.23.48,1.54.55,2.71c.06,1.27.07,1.65.07,4.85s0,3.58-.07,4.85c-.07,1.17-.26,2-.55,2.71s-.89,1.56-1.55,2.23-1.38,1.22-2.23,1.55-1.54.48-2.71.55c-1.27.06-1.65.07-4.85.07s-3.58,0-4.85-.07c-1.17-.07-2-.26-2.71-.55s-1.56-.89-2.23-1.55-1.22-1.38-1.55-2.23-.48-1.54-.55-2.71C2.16,15.58,2.16,12,2.16,12s0-3.58.07-4.85c.07-1.17.26-2,.55-2.71s.89-1.56,1.55-2.23,1.38-1.22,2.23-1.55,1.54-.48,2.71-.55C8.42,2.16,11.8,2.16,12,2.16ZM12,0C8.74,0,8.33,0,7.05.07c-1.27.06-2.14.26-2.87.56S2.69,1.77,2,2.49,1.22,3.63.91,4.88.12,6.79.06,8.05,0,8.33,0,12s0,3.58.06,4.85c.06,1.27.26,2.14.56,2.87s.73,1.69,1.46,2.44.93.93,1.44,1.38,1.32.71,2.11.9c.79.19,1.61.35,2.87.42,1.27.06,1.65.07,4.85.07s3.58,0,4.85-.07c1.27-.06,2.14-.26,2.87-.56s1.69-.73,2.44-1.46.93-.93,1.38-1.44.71-1.32.9-2.11c.19-.79.35-1.61.42-2.87.06-1.27.07-1.65.07-4.85s0-3.58-.07-4.85c-.06-1.27-.26-2.14-.56-2.87s-.73-1.69-1.46-2.44-.93-.93-1.44-1.38-1.32-.71-2.11-.9c-.79-.19-1.61-.35-2.87-.42C15.58,0,12,0,12,0Zm0,5.84A6.16,6.16,0,1,0,18.16,12,6.16,6.16,0,0,0,12,5.84ZM12,16a4,4,0,1,1,4-4A4,4,0,0,1,12,16ZM18.41,4.15a1.44,1.44,0,1,0,1.44,1.44A1.44,1.44,0,0,0,18.41,4.15Z"/>
              </svg>
            </a>
          </div>
          
          {/* Scrolling Announcement */}
          <div className="flex-1 mx-4 overflow-hidden whitespace-nowrap">
            <div className="animate-marquee font-medium text-[13px]">
              PURE WHEY. Simply PROTEIN of the best quality &nbsp;&nbsp;|&nbsp;&nbsp; STRENGTHEN YOUR DEFENSES WITH IMMUNE COMPLEX
            </div>
          </div>
          
          {/* Country & Language */}
          <div className="flex items-center gap-2 text-[13px] font-medium">
            <button className="hover:opacity-70">Spain (EUR €)</button>
            <span className="text-gray-600">|</span>
            <button className="hover:opacity-70">English</button>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <header className="bg-[#1d1d1d] py-3 md:py-4">
        <div className="max-w-[1100px] mx-auto px-4 flex items-center justify-between">
          {/* Mobile Menu Button */}
          <button className="md:hidden text-white hover:text-[#ffd100] p-1">
            <svg xmlns="http://www.w3.org/2000/svg" width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <line x1={3} y1={6} x2={21} y2={6} />
              <line x1={3} y1={12} x2={21} y2={12} />
              <line x1={3} y1={18} x2={21} y2={18} />
            </svg>
          </button>
          
          <a href="/" className="flex items-center transition-opacity hover:opacity-80">
            <Image
              src="/images/logo.png"
              alt="NEED® Supplements"
              width={180}
              height={72}
              className="h-auto w-[140px] md:w-[180px]"
              priority
            />
          </a>
          
          <nav className="hidden md:flex items-center gap-5 lg:gap-6">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-[#fafafa] font-oswald text-[13px] tracking-[0.5px] hover:text-[#ffd100] transition-colors duration-300"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-4 md:gap-5">
            <a href="/search" className="text-white hover:text-[#ffd100] transition-colors duration-300">
              <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                <circle cx={11} cy={11} r={8} />
                <path d="m21 21-4.3-4.3" />
              </svg>
            </a>
            <a href="/account/login" className="text-white hover:text-[#ffd100] transition-colors duration-300 hidden sm:block">
              <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                <circle cx={12} cy={7} r={4} />
              </svg>
            </a>
            <a href="/cart" className="text-white hover:text-[#ffd100] relative transition-colors duration-300">
              <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                <circle cx={8} cy={21} r={1} />
                <circle cx={19} cy={21} r={1} />
                <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
              </svg>
            </a>
          </div>
        </div>
      </header>

      {/* Mobile Nav - Horizontal scroll */}
      <div className="md:hidden bg-[#1d1d1d] py-2 px-4 overflow-x-auto">
        <div className="flex gap-4 min-w-max">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-white text-[11px] font-oswald whitespace-nowrap hover:text-[#ffd100] transition-colors"
            >
              {link.label}
            </a>
          ))}
        </div>
      </div>

      {/* Hero Slider - Full Width */}
      <section className="relative bg-[#1d1d1d] w-full">
        <div className="w-full">
          <Image
            src="/images/hero-slider.jpg"
            alt="PURE WHEY - Simply PROTEIN"
            width={1920}
            height={550}
            className="w-full h-auto max-h-[550px] object-cover"
            priority
          />
        </div>
      </section>

      {/* Best Sellers Carousel */}
      <BestSellers />

      {/* Categories - 6 columns on desktop */}
      <section className="py-10 md:py-12 bg-[#fafafa]">
        <div className="max-w-[1100px] mx-auto px-4">
          <h2 className="font-oswald text-[22px] md:text-[26px] font-bold text-[#1d1d1d] mb-6 md:mb-8 text-center uppercase tracking-[1px]">SPORT SUPPLEMENTATION</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
            {categories.map((cat) => (
              <a
                key={cat.name}
                href={cat.href}
                className="group block relative overflow-hidden rounded-md aspect-square"
              >
                <Image
                  src={cat.image}
                  alt={cat.name}
                  fill
                  className="object-cover transition-transform duration-500 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center transition-all duration-300 group-hover:bg-black/50">
                  <span className="text-white font-oswald text-xs md:text-sm text-center uppercase tracking-[0.5px]">{cat.name}</span>
                </div>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* Muscle Builder Products */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between mb-8">
            <h2 className="font-oswald text-3xl font-bold text-[#1d1d1d]">NEED® BUILD MUSCLE</h2>
            <a href="/collections/muscle-builder" className="text-[#737373] hover:text-[#1d1d1d] text-sm">
              View all →
            </a>
          </div>
          
          <div className="relative">
            <button 
              onClick={() => scrollCarousel('left')}
              className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 bg-white shadow-lg rounded-full w-10 h-10 flex items-center justify-center hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
              disabled={carouselIndex === 0}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path d="m15 18-6-6 6-6"/>
              </svg>
            </button>
            
            <div className="overflow-hidden mx-8">
              <div 
                className="grid grid-cols-4 md:grid-cols-4 lg:grid-cols-7 gap-4 transition-transform duration-300 ease-in-out"
                style={{ transform: `translateX(-${carouselIndex * (100 / 4)}%)` }}
              >
                {muscleProducts.map((product, i) => (
                  <a key={i} href={`/products/${i + 1}`} className="group block">
                    <div className="relative bg-[#fafafa] rounded-lg overflow-hidden mb-3">
                      <div className="aspect-[3/4] relative">
                        <Image
                          src={product.image}
                          alt={product.name}
                          fill
                          className="object-contain p-2"
                        />
                      </div>
                      {product.discount && (
                        <span className="absolute top-2 left-2 bg-[#ffcc00] text-black text-xs font-bold px-2 py-1">
                          {product.discount}
                        </span>
                      )}
                      {product.status === "sold-out" && (
                        <span className="absolute inset-0 bg-black/50 flex items-center justify-center">
                          <span className="bg-white text-black text-xs font-bold px-3 py-1">Sold out</span>
                        </span>
                      )}
                    </div>
                    <h3 className="font-oswald text-xs font-medium text-[#1d1d1d]">{product.name}</h3>
                    <div className="flex items-center gap-1 mt-1">
                      {[1,2,3,4,5].map((star) => (
                        <svg key={star} xmlns="http://www.w3.org/2000/svg" width={10} height={10} viewBox="0 0 24 24" fill={star <= Math.round(product.reviews/7) ? "#f6a529" : "#d1d5db"} stroke={star <= Math.round(product.reviews/7) ? "#f6a529" : "#d1d5db"} strokeWidth={2}>
                          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                        </svg>
                      ))}
                      <span className="text-[10px] text-[#737373]">({product.reviews})</span>
                    </div>
                    <div className="mt-1">
                      {product.originalPrice ? (
                        <div className="flex items-center gap-1">
                          <span className="text-[#1d1d1d] text-sm font-bold">{product.price}</span>
                          <span className="text-[#737373] line-through text-xs">{product.originalPrice}</span>
                        </div>
                      ) : (
                        <span className="text-[#1d1d1d] text-sm">{product.price}</span>
                      )}
                    </div>
                  </a>
                ))}
              </div>
            </div>

            <button 
              onClick={() => scrollCarousel('right')}
              className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 bg-white shadow-lg rounded-full w-10 h-10 flex items-center justify-center hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
              disabled={carouselIndex >= maxIndex}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path d="m9 18 6-6-6-6"/>
              </svg>
            </button>
          </div>
        </div>
      </section>

      {/* Packs Banner */}
      <section className="py-8">
        <div className="max-w-7xl mx-auto px-4">
          <a href="/collections/need%C2%AE-packs" className="block">
            <Image
              src="/images/packs-banner.jpg"
              alt="NEED® PACKS"
              width={1920}
              height={400}
              className="w-full h-auto rounded-lg"
            />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#1d1d1d] text-white py-10 md:py-14">
        <div className="max-w-[1100px] mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
            {/* Shop */}
            <div>
              <h3 className="font-oswald text-[15px] mb-4 tracking-[0.5px]">SHOP</h3>
              <ul className="space-y-2">
                {footerLinks.shop.map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className="text-[#a0a0a0] hover:text-white text-[13px] transition-colors">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Company */}
            <div>
              <h3 className="font-oswald text-[15px] mb-4 tracking-[0.5px]">COMPANY</h3>
              <ul className="space-y-2">
                {footerLinks.company.map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className="text-[#a0a0a0] hover:text-white text-[13px] transition-colors">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Legal */}
            <div>
              <h3 className="font-oswald text-[15px] mb-4 tracking-[0.5px]">LEGAL</h3>
              <ul className="space-y-2">
                {footerLinks.legal.map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className="text-[#a0a0a0] hover:text-white text-[13px] transition-colors">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Newsletter */}
            <div>
              <h3 className="font-oswald text-[15px] mb-4 tracking-[0.5px]">NEWSLETTER</h3>
              <p className="text-[#a0a0a0] text-[13px] mb-3">Signup for our newsletter:</p>
              <form className="flex">
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="flex-1 bg-white text-black px-3 py-2 text-[13px] rounded-l outline-none"
                />
                <button type="submit" className="bg-[#ffcc00] text-black px-4 py-2 text-[13px] font-bold rounded-r hover:bg-[#ffd100] transition-colors">
                  Subscribe
                </button>
              </form>
            </div>
          </div>
          
          {/* Bottom Footer */}
          <div className="mt-10 pt-8 border-t border-[#333]">
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              {/* Social Icons */}
              <div className="flex gap-4 order-2 md:order-1">
                <a href="https://www.facebook.com/needsupplements/" className="text-[#a0a0a0] hover:text-white transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.77,7.46H14.5v-1.9c0-.9.6-1.1,1-1.1h3V.5h-4.33C10.24.5,9.5,3.44,9.5,5.32v2.15h-3v4h3v12h5v-12h3.85l.42-4Z"/>
                  </svg>
                </a>
                <a href="https://www.youtube.com/channel/UCn5elEu8ZPYqfE388aZp_Og" className="text-[#a0a0a0] hover:text-white transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.5,6.19a3.02,3.02,0,0,0-2.12-2.14C19.54,3.5,12,3.5,12,3.5s-7.54,0-9.38.55A3.02,3.02,0,0,0,.5,6.19,30.56,30.56,0,0,0,0,12a30.56,30.56,0,0,0,.5,5.81,3.02,3.02,0,0,0,2.12,2.14c1.84.55,9.38.55,9.38.55s7.54,0,9.38-.55a3.02,3.02,0,0,0,2.12-2.14A30.56,30.56,0,0,0,24,12,30.56,30.56,0,0,0,23.5,6.19ZM9.55,15.57V8.43L15.82,12Z"/>
                  </svg>
                </a>
                <a href="https://www.instagram.com/need_supps/" className="text-[#a0a0a0] hover:text-white transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,2.16c3.2,0,3.58,0,4.85.07,1.17.07,2,.26,2.71.55s1.56.89,2.23,1.55,1.22,1.38,1.55,2.23.48,1.54.55,2.71c.06,1.27.07,1.65.07,4.85s0,3.58-.07,4.85c-.07,1.17-.26,2-.55,2.71s-.89,1.56-1.55,2.23-1.38,1.22-2.23,1.55-1.54.48-2.71.55c-1.27.06-1.65.07-4.85.07s-3.58,0-4.85-.07c-1.17-.07-2-.26-2.71-.55s-1.56-.89-2.23-1.55-1.22-1.38-1.55-2.23-.48-1.54-.55-2.71C2.16,15.58,2.16,12,2.16,12s0-3.58.07-4.85c.07-1.17.26-2,.55-2.71s.89-1.56,1.55-2.23,1.38-1.22,2.23-1.55,1.54-.48,2.71-.55C8.42,2.16,11.8,2.16,12,2.16ZM12,0C8.74,0,8.33,0,7.05.07c-1.27.06-2.14.26-2.87.56S2.69,1.77,2,2.49,1.22,3.63.91,4.88.12,6.79.06,8.05,0,8.33,0,12s0,3.58.06,4.85c.06,1.27.26,2.14.56,2.87s.73,1.69,1.46,2.44.93.93,1.44,1.38,1.32.71,2.11.9c.79.19,1.61.35,2.87.42,1.27.06,1.65.07,4.85.07s3.58,0,4.85-.07c1.27-.06,2.14-.26,2.87-.56s1.69-.73,2.44-1.46.93-.93,1.38-1.44.71-1.32.9-2.11c.19-.79.35-1.61.42-2.87.06-1.27.07-1.65.07-4.85s0-3.58-.07-4.85c-.06-1.27-.26-2.14-.56-2.87s-.73-1.69-1.46-2.44-.93-.93-1.44-1.38-1.32-.71-2.11-.9c-.79-.19-1.61-.35-2.87-.42C15.58,0,12,0,12,0Zm0,5.84A6.16,6.16,0,1,0,18.16,12,6.16,6.16,0,0,0,12,5.84ZM12,16a4,4,0,1,1,4-4A4,4,0,0,1,12,16ZM18.41,4.15a1.44,1.44,0,1,0,1.44,1.44A1.44,1.44,0,0,0,18.41,4.15Z"/>
                  </svg>
                </a>
              </div>
              
              {/* Payment Icons */}
              <div className="flex flex-wrap justify-center gap-2 order-1 md:order-2">
                {/* American Express */}
                <svg width={32} height={20} viewBox="0 0 32 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="20" rx="2" fill="#016FD0"/>
                  <path d="M6 14.5L8 6.5H10L8 14.5H6ZM12.5 14.5L10.5 6.5H13L15 14.5H12.5ZM18 14.5L16 6.5H18.5L21.5 14.5H18ZM23 14.5L21 6.5H26L24 14.5H23Z" fill="white"/>
                </svg>
                {/* Apple Pay */}
                <svg width={32} height={20} viewBox="0 0 32 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="20" rx="2" fill="black"/>
                  <path d="M13.8 6.4C13.4 5.9 12.6 5.7 12 5.7C10.6 5.7 9.6 6.7 9.6 8.2C9.6 9.5 10.2 10.5 11.2 10.5C11.6 10.5 12 10.4 12.3 10.2L12.5 10L12.8 11.2C12.5 11.5 12 11.8 11.4 11.8C10.2 11.8 9.2 10.9 9.2 8.8C9.2 6.8 10.1 5.5 11.4 5.5C12.2 5.5 12.8 5.9 13.2 6.4L13.8 6.4ZM20.2 5.5C20.6 5.5 21.1 5.6 21.5 5.8L21.3 6.4C21 6.3 20.5 6.2 20 6.2C18.9 6.2 18.2 7 18.2 8.1C18.2 9.1 18.8 9.8 19.8 9.8C20.4 9.8 20.9 9.6 21.2 9.3L21.4 9.8C20.9 10.2 20.3 10.5 19.7 10.5C18.4 10.5 17.5 9.5 17.5 8C17.5 6.5 18.5 5.5 20.2 5.5ZM23.2 8C23.2 7.7 23.2 7.3 23 7L22.2 7C22.3 7.5 22.5 8 22.8 8.3L23.2 8ZM17.2 8.3L17.6 8C17.9 7.6 18.1 7.1 18.2 6.6L18.9 6.7C18.7 7.2 18.4 7.7 18 8L17.2 8.3Z" fill="white"/>
                </svg>
                {/* Google Pay */}
                <svg width={32} height={20} viewBox="0 0 32 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="20" rx="2" fill="#4285F4"/>
                  <path d="M9.6 10.6L11.6 8.1L12.5 10.6H9.6ZM16.2 8.6C15.8 8.1 15.1 7.9 14.5 7.9C13.1 7.9 12.1 8.9 12.1 10.4C12.1 11.7 12.7 12.7 13.7 12.7C14.1 12.7 14.5 12.6 14.8 12.4L15 12.2L15.3 13.4C15 13.7 14.5 14 13.9 14C12.7 14 11.7 13.1 11.7 11C11.7 9 12.6 7.7 13.9 7.7C14.7 7.7 15.3 8.1 15.7 8.6L16.2 8.6Z" fill="white"/>
                </svg>
                {/* Maestro */}
                <svg width={32} height={20} viewBox="0 0 32 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="20" rx="2" fill="#1A1F71"/>
                  <path fillRule="evenodd" clipRule="evenodd" d="M12.5 5H19.5V15H12.5V5ZM14 7V8H17V7H14ZM14 9V10H17V9H14ZM14 11V12H17V11H14Z" fill="#EB001B"/>
                  <circle cx="10" cy="10" r="4" fill="#F79E1B"/>
                </svg>
                {/* Mastercard */}
                <svg width={32} height={20} viewBox="0 0 32 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="20" rx="2" fill="#000"/>
                  <circle cx="11" cy="10" r="5" fill="#EB001B"/>
                  <circle cx="21" cy="10" r="5" fill="#F79E1B"/>
                </svg>
                {/* PayPal */}
                <svg width={32} height={20} viewBox="0 0 32 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="20" rx="2" fill="#003087"/>
                  <path d="M10.5 8.5L11 8C11.5 7.5 12 7 12.5 7H15C15.5 7 16 7.2 16.2 7.5L17 9L16.5 9.5C16 9 15.5 8.8 15 8.8H13L12.5 9L11.5 8H10.5ZM14.5 13L15 12.5C15.5 12 16 11.8 16.5 11.8H19C20 11.8 21 12.5 21.2 13.5L20.5 14C20.2 13.8 19.8 13.5 19.2 13.5H18L17.2 14.5L16.5 14C16 13.5 15.5 13.2 15 13.2H14.2L13.8 13.8L14.5 13ZM19.5 8L20 7.5C20.5 7 21.2 6.8 22 6.8L21.5 8.2C21 8 20.5 8 20 8H19.5Z" fill="white"/>
                </svg>
                {/* Visa */}
                <svg width={32} height={20} viewBox="0 0 32 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="20" rx="2" fill="#1A1F71"/>
                  <path d="M13 14L11 6H9L7 14H9L9.5 12H12.5L13 14ZM22 14V6H20.5L18.5 12H18L16.5 6H15L17 14H18L18.2 11.5H18.3L19.8 14H20.5L22 14ZM25 14L23.5 11L23 12L22.2 14H25Z" fill="white"/>
                </svg>
              </div>
              
              {/* Country & Language */}
              <div className="flex items-center justify-center gap-4 text-[12px] order-3">
                <div className="flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                    <circle cx={12} cy={12} r={10}/>
                    <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                  </svg>
                  <select className="bg-transparent text-[#a0a0a0] hover:text-white cursor-pointer border-none outline-none">
                    <option value="es">Spain (EUR €)</option>
                    <option value="en">United Kingdom (GBP £)</option>
                    <option value="de">Germany (EUR €)</option>
                    <option value="fr">France (EUR €)</option>
                  </select>
                </div>
                <span className="text-[#444]">|</span>
                <div className="flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                    <path d="M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0014.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.94 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/>
                  </svg>
                  <select className="bg-transparent text-[#a0a0a0] hover:text-white cursor-pointer border-none outline-none">
                    <option value="en">English</option>
                    <option value="es">Español</option>
                  </select>
                </div>
              </div>
            </div>
            
            {/* Copyright */}
            <div className="text-center text-[#a0a0a0] text-[13px] mt-6">
              © 2026 <a href="/" className="hover:text-white transition-colors">NEED® Supplements</a>.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
