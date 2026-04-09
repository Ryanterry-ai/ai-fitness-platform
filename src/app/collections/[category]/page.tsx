"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { categories, getProductsByCategory, products } from "@/lib/data";
import { useCart } from "@/lib/cart-context";

export function generateStaticParams() {
  return categories.map((cat) => ({
    category: cat.id,
  }));
}

export default function CollectionPage({ params }: { params: Promise<{ category: string }> }) {
  const [category, setCategory] = useState<string>("");
  const [showFilters, setShowFilters] = useState(false);
  const [inStockOnly, setInStockOnly] = useState(false);
  const [sortBy, setSortBy] = useState("featured");
  const { addToCart } = useCart();

  useEffect(() => {
    params.then((p) => setCategory(p.category));
  }, [params]);

  const categoryData = categories.find(c => c.id === category);
  let categoryProducts = category === "best-sellers" 
    ? products.slice(0, 8) 
    : getProductsByCategory(category);

  if (inStockOnly) {
    categoryProducts = categoryProducts.filter(p => p.status !== "sold-out");
  }

  switch (sortBy) {
    case "price-low":
      categoryProducts = [...categoryProducts].sort((a, b) => a.price - b.price);
      break;
    case "price-high":
      categoryProducts = [...categoryProducts].sort((a, b) => b.price - a.price);
      break;
    case "name":
      categoryProducts = [...categoryProducts].sort((a, b) => a.name.localeCompare(b.name));
      break;
  }

  if (!categoryData) return null;

  return (
    <div className="min-h-screen font-roboto">
      {/* Announcement Bar */}
      <div className="bg-[#1d1d1d] text-white text-[11px] py-2 overflow-hidden">
        <div className="max-w-[1100px] mx-auto px-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-[#ffd100]">🇪🇺</span>
            <span className="hidden sm:inline">FREE shipping on orders over €50 in Europe</span>
            <span className="sm:hidden">Free shipping over €50</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[#a0a0a0] cursor-pointer hover:text-white">English</span>
            <span className="text-[#a0a0a0]">|</span>
            <span className="text-[#a0a0a0] cursor-pointer hover:text-white">EUR €</span>
            <div className="flex gap-2 ml-3">
              <span className="cursor-pointer hover:text-[#ffd100]">f</span>
              <span className="cursor-pointer hover:text-[#ffd100]">in</span>
              <span className="cursor-pointer hover:text-[#ffd100]">X</span>
            </div>
          </div>
        </div>
      </div>

      {/* Header */}
      <header className="bg-[#1d1d1d] py-3 md:py-4 sticky top-0 z-50">
        <div className="max-w-[1100px] mx-auto px-4 flex items-center justify-between">
          <Link href="/" className="flex items-center">
            <Image
              src="/images/logo.png"
              alt="NEED® Supplements"
              width={180}
              height={60}
              className="h-auto w-[140px] md:w-[180px]"
            />
          </Link>
          
          <nav className="hidden md:flex items-center gap-5">
            {categories.filter(c => c.id !== "best-sellers").map((link) => (
              <Link
                key={link.id}
                href={link.href}
                className="text-[#fafafa] font-oswald text-[13px] tracking-[0.5px] hover:text-[#ffd100] transition-colors"
              >
                {link.name.toUpperCase()}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-4">
            <Link href="/search" className="text-white hover:text-[#ffd100]">
              <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <circle cx={11} cy={11} r={8} /><path d="m21 21-4.3-4.3" />
              </svg>
            </Link>
            <Link href="/cart" className="text-white hover:text-[#ffd100] relative">
              <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <circle cx={8} cy={21} r={1} /><circle cx={19} cy={21} r={1} />
                <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
              </svg>
            </Link>
          </div>
        </div>
      </header>

      {/* Breadcrumb */}
      <div className="bg-[#fafafa] py-3">
        <div className="max-w-[1100px] mx-auto px-4">
          <p className="text-sm text-[#737373]">
            <Link href="/" className="hover:text-[#1d1d1d]">Home</Link> / 
            <span className="text-[#1d1d1d] ml-1">{categoryData.name}</span>
          </p>
        </div>
      </div>

      {/* Hero */}
      <div className="bg-[#1d1d1d] py-10 md:py-12 text-center">
        <h1 className="font-oswald text-[28px] md:text-[36px] font-bold text-white uppercase tracking-[1px]">
          {categoryData.name.toUpperCase()}
        </h1>
      </div>

      {/* Main Content */}
      <section className="py-8 md:py-10 bg-white">
        <div className="max-w-[1100px] mx-auto px-4">
          {/* Utility Bar */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-[#e5e5e5]">
            <button 
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 text-[13px] text-[#1d1d1d] hover:text-[#ffd100]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <line x1={4} y1={6} x2={20} y2={6} /><line x1={4} y1={12} x2={20} y2={12} /><line x1={4} y1={18} x2={20} y2={18} />
              </svg>
              {showFilters ? "Hide Filters" : "Show Filters"}
            </button>
            
            <div className="flex items-center gap-4">
              <span className="text-[13px] text-[#737373]">{categoryProducts.length} products</span>
              <div className="flex items-center gap-2">
                <span className="text-[13px] text-[#737373]">Sort by:</span>
                <select 
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="text-[13px] border border-[#e5e5e5] px-2 py-1 rounded bg-white focus:outline-none focus:border-[#1d1d1d]"
                >
                  <option value="featured">Featured</option>
                  <option value="price-low">Price: Low to High</option>
                  <option value="price-high">Price: High to Low</option>
                  <option value="name">Name</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex gap-8">
            {/* Filter Sidebar */}
            {showFilters && (
              <aside className="w-56 shrink-0 hidden md:block">
                <div className="space-y-6">
                  {/* Availability */}
                  <div>
                    <h3 className="font-oswald text-sm font-medium text-[#1d1d1d] mb-3">Availability</h3>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={inStockOnly}
                        onChange={(e) => setInStockOnly(e.target.checked)}
                        className="w-4 h-4 accent-[#1d1d1d]"
                      />
                      <span className="text-[13px] text-[#1d1d1d]">In stock only</span>
                    </label>
                  </div>

                  {/* Price Range */}
                  <div>
                    <h3 className="font-oswald text-sm font-medium text-[#1d1d1d] mb-3">Price</h3>
                    <div className="space-y-2">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="price" className="accent-[#1d1d1d]" defaultChecked />
                        <span className="text-[13px] text-[#1d1d1d]">All prices</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="price" className="accent-[#1d1d1d]" />
                        <span className="text-[13px] text-[#1d1d1d]">Under €25</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="price" className="accent-[#1d1d1d]" />
                        <span className="text-[13px] text-[#1d1d1d]">€25 - €50</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="price" className="accent-[#1d1d1d]" />
                        <span className="text-[13px] text-[#1d1d1d]">Over €50</span>
                      </label>
                    </div>
                  </div>
                </div>
              </aside>
            )}

            {/* Products Grid - 3 columns on desktop */}
            <div className="flex-1">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
                {categoryProducts.map((product) => (
                  <div key={product.id} className="group">
                    <Link href={`/products/${product.id}`} className="block">
                      <div className="relative bg-[#fafafa] rounded-md overflow-hidden mb-2 md:mb-3">
                        <div className="aspect-[3/4] relative">
                          <Image
                            src={product.image}
                            alt={product.name}
                            fill
                            className="object-contain p-3 md:p-4 transition-transform duration-500 group-hover:scale-105"
                            sizes="(max-width: 768px) 50vw, 33vw"
                          />
                        </div>
                        {product.originalPrice && (
                          <span className="absolute top-2 left-2 bg-[#ffcc00] text-black text-[11px] font-bold px-2 py-0.5">
                            {Math.round((1 - product.price / product.originalPrice) * 100)}% off
                          </span>
                        )}
                        {product.status === "sold-out" && (
                          <span className="absolute inset-0 bg-black/40 flex items-center justify-center">
                            <span className="bg-white text-black text-[11px] font-bold px-3 py-1">Sold out</span>
                          </span>
                        )}
                      </div>
                      <h3 className="font-oswald text-xs md:text-sm font-medium text-[#1d1d1d] group-hover:text-[#ffd100] transition-colors line-clamp-2">{product.name}</h3>
                      <div className="mt-1">
                        {product.originalPrice ? (
                          <div className="flex items-center gap-2">
                            <span className="text-[#1d1d1d] font-bold text-sm">€{product.price.toFixed(2)}</span>
                            <span className="text-[#737373] line-through text-xs">€{product.originalPrice.toFixed(2)}</span>
                          </div>
                        ) : (
                          <span className="text-[#1d1d1d] text-sm">€{product.price.toFixed(2)}</span>
                        )}
                      </div>
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#1d1d1d] text-white py-10">
        <div className="max-w-[1100px] mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-oswald text-sm font-medium mb-4 text-[#ffd100]">SHOP</h4>
              <ul className="space-y-2 text-[13px] text-[#a0a0a0]">
                <li><Link href="/collections/proteins" className="hover:text-white">Proteins</Link></li>
                <li><Link href="/collections/pre-training" className="hover:text-white">Pre-Training</Link></li>
                <li><Link href="/collections/build-muscle" className="hover:text-white">Build Muscle</Link></li>
                <li><Link href="/collections/amino-acids" className="hover:text-white">Amino Acids</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-oswald text-sm font-medium mb-4 text-[#ffd100]">HELP</h4>
              <ul className="space-y-2 text-[13px] text-[#a0a0a0]">
                <li><Link href="/search" className="hover:text-white">Search</Link></li>
                <li><Link href="/cart" className="hover:text-white">Cart</Link></li>
              </ul>
            </div>
            <div className="col-span-2">
              <h4 className="font-oswald text-sm font-medium mb-4 text-[#ffd100]">NEWSLETTER</h4>
              <p className="text-[13px] text-[#a0a0a0] mb-3">Subscribe to receive updates, access to exclusive deals, and more.</p>
              <div className="flex">
                <input 
                  type="email" 
                  placeholder="Enter your email" 
                  className="flex-1 px-3 py-2 text-sm bg-white border border-[#333] focus:outline-none"
                />
                <button className="bg-[#ffd100] text-black px-4 py-2 font-oswald text-sm font-medium hover:bg-[#e6b800]">
                  SUBSCRIBE
                </button>
              </div>
            </div>
          </div>
          <div className="border-t border-[#333] pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-[#a0a0a0] text-sm">© 2026 NEED® Supplements.</div>
            <div className="flex gap-3 text-[#a0a0a0]">
              <span className="cursor-pointer hover:text-white">f</span>
              <span className="cursor-pointer hover:text-white">in</span>
              <span className="cursor-pointer hover:text-white">X</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}