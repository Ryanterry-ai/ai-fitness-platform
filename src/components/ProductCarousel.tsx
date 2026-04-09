"use client";

import { useRef, useState, useEffect } from "react";
import { Product } from "@/lib/data";
import ProductCard from "./ProductCard";

interface ProductCarouselProps {
  products: Product[];
  title?: string;
  showViewAll?: boolean;
  viewAllLink?: string;
}

export default function ProductCarousel({ 
  products, 
  title, 
  showViewAll = false, 
  viewAllLink = "/collections/all" 
}: ProductCarouselProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  const checkScroll = () => {
    if (scrollRef.current) {
      const { scrollLeft: s, scrollWidth, clientWidth } = scrollRef.current;
      setShowLeftArrow(s > 5);
      setShowRightArrow(s < scrollWidth - clientWidth - 5);
    }
  };

  useEffect(() => {
    checkScroll();
    const container = scrollRef.current;
    if (container) {
      container.addEventListener('scroll', checkScroll);
      window.addEventListener('resize', checkScroll);
      return () => {
        container.removeEventListener('scroll', checkScroll);
        window.removeEventListener('resize', checkScroll);
      };
    }
  }, [products]);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = scrollRef.current.clientWidth * 0.8;
      scrollRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="relative">
      {/* Header - Centered Title with View All on right */}
      {(title || showViewAll) && (
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4 gap-2">
          {title && (
            <div className="text-center md:text-left">
              <h2 className="font-oswald text-2xl md:text-3xl font-bold text-[#1d1d1d] uppercase tracking-wide">
                {title}
              </h2>
            </div>
          )}
          {showViewAll && (
            <div className="text-center md:text-right">
              <a 
                href={viewAllLink}
                className="font-roboto text-sm text-[#737373] hover:text-[#1d1d1d] transition-colors duration-300 inline-flex items-center gap-1"
              >
                View all
                <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                  <path d="m9 18 6-6-6-6"/>
                </svg>
              </a>
            </div>
          )}
        </div>
      )}

      {/* Carousel Container */}
      <div className="relative group">
        {/* Left Arrow */}
        <button
          onClick={() => scroll('left')}
          className={`absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white shadow-lg rounded-full w-10 h-10 flex items-center justify-center hover:bg-gray-100 transition-all duration-300 hidden md:flex ${showLeftArrow ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
          aria-label="Scroll left"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>

        {/* Products Scroll Container */}
        <div
          ref={scrollRef}
          className="flex gap-3 md:gap-4 overflow-x-auto overflow-y-hidden scroll-smooth scrollbar-hide px-2 md:px-0 pb-2"
          style={{ 
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
            WebkitOverflowScrolling: 'touch'
          }}
        >
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>

        {/* Right Arrow */}
        <button
          onClick={() => scroll('right')}
          className={`absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white shadow-lg rounded-full w-10 h-10 flex items-center justify-center hover:bg-gray-100 transition-all duration-300 hidden md:flex ${showRightArrow ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
          aria-label="Scroll right"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </button>
      </div>

      {/* Mobile View All Button */}
      {showViewAll && (
        <div className="md:hidden mt-4">
          <a 
            href={viewAllLink}
            className="block text-center font-roboto text-sm text-[#1d1d1d] border border-[#1d1d1d] py-2 hover:bg-[#1d1d1d] hover:text-white transition-colors duration-300"
          >
            View all
          </a>
        </div>
      )}
    </div>
  );
}