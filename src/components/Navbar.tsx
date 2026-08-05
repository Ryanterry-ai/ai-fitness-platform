'use client';

import React, { useState } from 'react';
import { Menu, X, ShoppingBag, Search, ChevronDown, ChevronRight } from 'lucide-react';
import Image from 'next/image';
import { useShop } from '@/lib/store';

const categoryLinks = [
  {
    label: 'PROTEINS',
    href: '/shop?category=protein',
    children: [
      { label: 'PRIME X Orange', href: '/product/primex-preworkout-orange' },
      { label: 'PRIME X Fruit Punch', href: '/product/primex-preworkout-fruit-punch' },
      { label: 'PRIME X Rocket Lollipop', href: '/product/primex-preworkout-rocket-lollipop' },
    ],
  },
  {
    label: 'PRE-TRAINING',
    href: '/shop?category=pre-workout',
    children: [
      { label: 'PRIME X Orange', href: '/product/primex-preworkout-orange' },
      { label: 'PRIME X Fruit Punch', href: '/product/primex-preworkout-fruit-punch' },
      { label: 'PRIME X Rocket Lollipop', href: '/product/primex-preworkout-rocket-lollipop' },
    ],
  },
  { label: 'BUILD MUSCLE', href: '/shop?category=build-muscle' },
  { label: 'AMINO ACIDS', href: '/shop?category=amino-acids' },
  { label: 'VITAMINS & MINERALS', href: '/shop?category=vitamins' },
  { label: 'WEIGHT LOSS', href: '/shop?category=weight-loss' },
];

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const { cart, setCartOpen } = useShop();
  const cartCount = cart.reduce((acc: number, item: any) => acc + item.quantity, 0);

  return (
    <>
      <nav className="sticky top-0 z-50 bg-[#1d1d1d] border-b border-white/10">
        <div className="max-w-[1100px] mx-auto px-4 sm:px-5">
          <div className="flex items-center justify-between h-14">
            {/* Logo */}
            <a href="/" className="flex items-center shrink-0">
              <span className="text-white text-xl font-bold uppercase tracking-wider font-heading">
                PURE
              </span>
            </a>

            {/* Center Nav - Desktop */}
            <div className="hidden lg:flex items-center gap-0">
              {categoryLinks.map((link) => (
                <div
                  key={link.href}
                  className="relative"
                  onMouseEnter={() => link.children && setOpenDropdown(link.label)}
                  onMouseLeave={() => setOpenDropdown(null)}
                >
                  <a
                    href={link.href}
                    className="flex items-center gap-1 px-3 py-4 text-[13px] font-normal uppercase tracking-wide text-white/90 hover:text-[#ffd100] transition-colors"
                  >
                    {link.label}
                    {link.children && <ChevronDown className="w-3 h-3 opacity-50" />}
                  </a>
                  {link.children && openDropdown === link.label && (
                    <div className="absolute top-full left-0 w-56 bg-[#1d1d1d] border border-white/10 shadow-xl py-2 z-50">
                      {link.children.map((child) => (
                        <a
                          key={child.href}
                          href={child.href}
                          className="block px-4 py-2.5 text-[13px] text-white/80 hover:text-[#ffd100] hover:bg-white/5 transition-colors"
                        >
                          {child.label}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Right Icons */}
            <div className="flex items-center gap-0">
              <button
                onClick={() => setIsSearchOpen(!isSearchOpen)}
                className="p-3 text-white/80 hover:text-[#ffd100] transition-colors"
              >
                <Search className="w-4 h-4" />
              </button>
              <button
                onClick={() => setCartOpen(true)}
                className="p-3 text-white/80 hover:text-[#ffd100] transition-colors relative"
              >
                <ShoppingBag className="w-4 h-4" />
                {cartCount > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 bg-[#ffd100] text-[#1d1d1d] text-[9px] font-bold rounded-full flex items-center justify-center">
                    {cartCount}
                  </span>
                )}
              </button>
              <button
                className="lg:hidden p-3 text-white/80 hover:text-[#ffd100] transition-colors"
                onClick={() => setIsOpen(!isOpen)}
              >
                {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        {isSearchOpen && (
          <div className="border-t border-white/10 bg-[#1d1d1d]">
            <div className="max-w-[1100px] mx-auto px-4 sm:px-5 py-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                <input
                  type="text"
                  placeholder="Search products..."
                  className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 text-sm text-white placeholder-white/40 focus:outline-none focus:border-[#ffd100]/50"
                  autoFocus
                />
              </div>
            </div>
          </div>
        )}

        {/* Mobile Nav */}
        {isOpen && (
          <div className="lg:hidden bg-[#1d1d1d] border-t border-white/10">
            <div className="px-4 py-4 space-y-0">
              {categoryLinks.map((link) => (
                <div key={link.href}>
                  <a
                    href={link.href}
                    className="flex items-center justify-between text-[13px] font-normal uppercase tracking-wide text-white/90 hover:text-[#ffd100] transition-colors py-3 border-b border-white/10"
                    onClick={() => !link.children && setIsOpen(false)}
                  >
                    {link.label}
                    {link.children && <ChevronRight className="w-4 h-4 opacity-50" />}
                  </a>
                  {link.children && (
                    <div className="pl-4 space-y-0">
                      {link.children.map((child) => (
                        <a
                          key={child.href}
                          href={child.href}
                          className="block text-[13px] text-white/60 hover:text-[#ffd100] transition-colors py-2.5 border-b border-white/5"
                          onClick={() => setIsOpen(false)}
                        >
                          {child.label}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <a href="/shop" className="block text-[13px] font-normal uppercase tracking-wide text-[#ffd100] hover:text-white transition-colors py-3" onClick={() => setIsOpen(false)}>
                Shop All
              </a>
            </div>
          </div>
        )}
      </nav>
    </>
  );
}
