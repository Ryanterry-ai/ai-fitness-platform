"use client";

import Image from "next/image";
import Link from "next/link";
import { Product } from "@/lib/data";

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const reviews = ((product.id * 7) % 50) + 5;

  return (
    <Link 
      href={`/products/${product.id}`} 
      className="group block min-w-[140px] md:min-w-[180px] lg:min-w-[220px]"
    >
      <div className="relative bg-[#fafafa] rounded-lg overflow-hidden mb-2 transition-all duration-300 group-hover:shadow-lg">
        <div className="aspect-[3/4] relative">
          <Image
            src={product.image}
            alt={product.name}
            fill
            className="object-contain p-3 md:p-4 transition-transform duration-500 group-hover:scale-105"
            sizes="(max-width: 768px) 45vw, (max-width: 1024px) 25vw, 20vw"
          />
        </div>
        
        {/* Discount Badge - Position based on status */}
        {product.status === "sale" && (
          <span className="absolute top-2 left-2 bg-[#ffcc00] text-black text-xs font-bold px-2 py-0.5">
            {Math.round((1 - product.price / product.originalPrice!) * 100)}% off
          </span>
        )}
        
        {/* Sold out Badge */}
        {product.status === "sold-out" && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
            <span className="bg-white text-black text-xs font-bold px-3 py-1">Sold out</span>
          </div>
        )}
      </div>
      
      {/* Product Info */}
      <div className="px-1">
        <h3 className="font-oswald text-xs md:text-sm font-medium text-[#1d1d1d] group-hover:text-[#ffcc00] transition-colors duration-300 line-clamp-2">
          {product.name}
        </h3>
        
        {/* Reviews */}
        <div className="flex items-center gap-1 mt-0.5">
          {[1, 2, 3, 4, 5].map((star) => (
            <svg 
              key={star} 
              xmlns="http://www.w3.org/2000/svg" 
              width={10} 
              height={10} 
              viewBox="0 0 24 24" 
              fill={star <= 4 ? "#f6a529" : "#d1d5db"} 
              stroke={star <= 4 ? "#f6a529" : "#d1d5db"} 
              strokeWidth={2}
            >
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          ))}
          <span className="text-[10px] text-[#737373]">{reviews}</span>
        </div>
        
        {/* Price - Matching original format */}
        <div className="mt-1">
          {product.originalPrice ? (
            <div className="flex flex-col">
              <span className="text-[#1d1d1d] font-bold text-sm">{product.price.toFixed(2)} €</span>
              <span className="text-[#737373] line-through text-xs">{product.originalPrice.toFixed(2)} €</span>
            </div>
          ) : (
            <span className="text-[#1d1d1d] font-bold text-sm">From {product.price.toFixed(2)} €</span>
          )}
        </div>
        
        {/* Status label */}
        {product.status === "sale" && (
          <span className="text-xs font-bold text-[#1d1d1d]">Sale</span>
        )}
        {product.status === "sold-out" && (
          <span className="text-xs text-[#737373]">Sold out</span>
        )}
      </div>
    </Link>
  );
}