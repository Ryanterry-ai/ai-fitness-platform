"use client";

import { products } from "@/lib/data";
import ProductCarousel from "./ProductCarousel";

export default function BestSellers() {
  // First 4 products as best sellers (matching original)
  const bestSellersProducts = products.slice(0, 4);
  
  return (
    <section className="py-4 md:py-6 bg-white border-b border-[#e5e5e5]">
      <div className="max-w-7xl mx-auto px-4">
        <ProductCarousel
          products={bestSellersProducts}
          title="NEED® BEST SELLERS"
          showViewAll={true}
          viewAllLink="/collections/all"
        />
      </div>
    </section>
  );
}