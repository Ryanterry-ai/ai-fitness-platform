'use client';

import React from 'react';

const footerLinks = {
  shop: [
    { label: 'PROTEINS', href: '/shop?category=protein' },
    { label: 'PRE-TRAINING', href: '/shop?category=pre-workout' },
    { label: 'BUILD MUSCLE', href: '/shop?category=build-muscle' },
    { label: 'AMINO ACIDS', href: '/shop?category=amino-acids' },
    { label: 'VITAMINS & MINERALS', href: '/shop?category=vitamins' },
    { label: 'WEIGHT LOSS', href: '/shop?category=weight-loss' },
  ],
  company: [
    { label: 'The Health Project', href: '/blog' },
    { label: 'About us', href: '/about' },
    { label: 'Contact us', href: '/contact' },
  ],
  legal: [
    { label: 'Privacy Policy', href: '/privacy' },
    { label: 'Legal Notice', href: '/legal' },
    { label: 'Shipping Policy', href: '/shipping' },
    { label: 'Refund Policy', href: '/refund' },
    { label: 'Terms of Service', href: '/terms' },
    { label: 'Cookies', href: '/cookies' },
  ],
};

const socials = [
  { label: 'FB', href: '#' },
  { label: 'YT', href: '#' },
  { label: 'IG', href: '#' },
];

const paymentIcons = ['Visa', 'Mastercard', 'PayPal', 'Apple Pay', 'Google Pay', 'Klarna'];

export default function GlobalFooter() {
  return (
    <footer className="bg-[#1d1d1d]">
      <div className="max-w-[1100px] mx-auto px-4 sm:px-5 py-10 sm:py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
          {/* Shop Collections */}
          <div>
            <h4 className="text-[13px] font-normal uppercase tracking-wide text-[#e1e1d9] mb-4">
              Shop Collections
            </h4>
            <ul className="space-y-2">
              {footerLinks.shop.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="text-[13px] text-white/70 hover:text-[#ffd100] transition-colors">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Pages */}
          <div>
            <h4 className="text-[13px] font-normal uppercase tracking-wide text-[#e1e1d9] mb-4">
              Company Pages
            </h4>
            <ul className="space-y-2">
              {footerLinks.company.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="text-[13px] text-white/70 hover:text-[#ffd100] transition-colors">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Policies */}
          <div>
            <h4 className="text-[13px] font-normal uppercase tracking-wide text-[#e1e1d9] mb-4">
              Legal Policies
            </h4>
            <ul className="space-y-2">
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="text-[13px] text-white/70 hover:text-[#ffd100] transition-colors">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Newsletter + Social */}
          <div>
            <h4 className="text-[13px] font-normal uppercase tracking-wide text-[#e1e1d9] mb-4">
              Newsletter
            </h4>
            <p className="text-[13px] text-white/70 mb-3">
              Signup for our newsletter:
            </p>
            <form className="flex gap-2 mb-6">
              <input
                type="email"
                placeholder="Email address"
                className="flex-1 px-3 py-2 bg-white/5 border border-white/10 text-[13px] text-white placeholder-white/40 focus:outline-none focus:border-[#ffd100]/50"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-[#ffd100] text-[#1d1d1d] text-[13px] font-bold uppercase tracking-wider hover:bg-[#fbea9d] transition-colors"
              >
                Subscribe
              </button>
            </form>
            <div className="flex items-center gap-3">
              {socials.map((s) => (
                <a
                  key={s.label}
                  href={s.href}
                  className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white/70 hover:text-[#ffd100] hover:bg-[#ffd100]/10 transition-all text-[10px] font-bold uppercase"
                >
                  {s.label}
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Payment Icons */}
        <div className="border-t border-white/10 pt-6 mb-6">
          <div className="flex flex-wrap items-center gap-3 text-white/50">
            {paymentIcons.map((icon) => (
              <span key={icon} className="text-[10px] font-normal uppercase tracking-wide bg-white/5 px-2 py-1">
                {icon}
              </span>
            ))}
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-white/10 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-[11px] text-white/50">
            &copy; {new Date().getFullYear()} PURE HEALTH SUPPS. All rights reserved.
          </p>
          <p className="text-[11px] text-white/50">
            Made in India. FSSAI Certified.
          </p>
        </div>
      </div>
    </footer>
  );
}
