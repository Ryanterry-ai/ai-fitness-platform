"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { products } from "@/lib/data";
import { useCart } from "@/lib/cart-context";
import { categories } from "@/lib/data";
import { useParams } from "next/navigation";

export default function ProductPage() {
  const params = useParams();
  const id = params.id as string;
  const productId = parseInt(id);
  const product = products.find(p => p.id === productId);
  const [selectedFlavor, setSelectedFlavor] = useState(product?.flavors[0] || "");
  const [quantity, setQuantity] = useState(1);
  const { addToCart } = useCart();

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="font-oswald text-2xl mb-4">Product not found</h1>
          <Link href="/" className="text-[#ffcc00] hover:underline">Go back home</Link>
        </div>
      </div>
    );
  }

  const handleAddToCart = () => {
    addToCart(product, quantity, selectedFlavor);
    alert(`${product.name} added to cart!`);
  };

  return (
    <div className="min-h-screen font-roboto">
      {/* Header */}
      <header className="bg-[#1d1d1d] py-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
          <Link href="/" className="flex items-center">
            <Image src="/images/logo.png" alt="NEED® Supplements" width={180} height={60} className="h-auto" />
          </Link>
          <nav className="hidden md:flex items-center gap-6">
            {categories.map((link) => (
              <Link key={link.id} href={link.href} className="text-white font-oswald text-sm hover:text-[#ffcc00]">
                {link.name.toUpperCase()}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/search" className="text-white hover:text-[#ffcc00]">
              <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <circle cx={11} cy={11} r={8} /><path d="m21 21-4.3-4.3" />
              </svg>
            </Link>
            <Link href="/cart" className="text-white hover:text-[#ffcc00]">
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
        <div className="max-w-7xl mx-auto px-4">
          <p className="text-sm text-[#737373]">
            <Link href="/" className="hover:text-[#1d1d1d]">Home</Link> / 
            <Link href={`/collections/${product.category}`} className="hover:text-[#1d1d1d] ml-1">{product.category}</Link> / 
            <span className="text-[#1d1d1d] ml-1">{product.name}</span>
          </p>
        </div>
      </div>

      {/* Product Details */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12">
            {/* Image */}
            <div className="relative bg-[#fafafa] rounded-lg overflow-hidden">
              <div className="aspect-square relative">
                <Image src={product.image} alt={product.name} fill className="object-contain p-8" sizes="(max-width: 768px) 100vw, 50vw" />
              </div>
              {product.originalPrice && (
                <span className="absolute top-4 left-4 bg-[#ffcc00] text-black text-sm font-bold px-3 py-1">
                  {Math.round((1 - product.price / product.originalPrice) * 100)}% OFF
                </span>
              )}
              {product.status === "sold-out" && (
                <span className="absolute top-4 right-4 bg-red-500 text-white text-sm font-bold px-3 py-1">SOLD OUT</span>
              )}
            </div>

            {/* Info */}
            <div>
              <h1 className="font-oswald text-3xl md:text-4xl font-bold text-[#1d1d1d] mb-4">{product.name}</h1>
              
              <div className="mb-6">
                {product.originalPrice ? (
                  <div className="flex items-center gap-3">
                    <span className="text-3xl font-bold text-[#1d1d1d]">€{product.price.toFixed(2)}</span>
                    <span className="text-xl text-[#737373] line-through">€{product.originalPrice.toFixed(2)}</span>
                  </div>
                ) : (
                  <span className="text-3xl font-bold text-[#1d1d1d]">€{product.price.toFixed(2)}</span>
                )}
              </div>

              <p className="text-[#737373] mb-6">{product.description}</p>

              {/* Flavor Selection */}
              {product.flavors.length > 0 && (
                <div className="mb-6">
                  <label className="block font-oswald text-sm mb-2">FLAVOR</label>
                  <div className="flex flex-wrap gap-2">
                    {product.flavors.map((flavor) => (
                      <button
                        key={flavor}
                        onClick={() => setSelectedFlavor(flavor)}
                        className={`px-4 py-2 border text-sm ${
                          selectedFlavor === flavor
                            ? "border-[#1d1d1d] bg-[#1d1d1d] text-white"
                            : "border-[#e5e5e5] text-[#1d1d1d] hover:border-[#1d1d1d]"
                        }`}
                      >
                        {flavor}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Quantity */}
              <div className="mb-6">
                <label className="block font-oswald text-sm mb-2">QUANTITY</label>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="w-10 h-10 border border-[#e5e5e5] flex items-center justify-center text-xl hover:border-[#1d1d1d]"
                  >
                    -
                  </button>
                  <span className="w-12 text-center font-bold">{quantity}</span>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="w-10 h-10 border border-[#e5e5e5] flex items-center justify-center text-xl hover:border-[#1d1d1d]"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Add to Cart */}
              <button
                onClick={handleAddToCart}
                disabled={product.status === "sold-out"}
                className={`w-full py-4 font-oswald text-lg font-bold ${
                  product.status === "sold-out"
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-[#ffcc00] text-black hover:bg-yellow-400"
                }`}
              >
                {product.status === "sold-out" ? "SOLD OUT" : "ADD TO CART"}
              </button>

              {/* Product Info */}
              <div className="mt-8 border-t pt-6">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-[#737373] block">Weight</span>
                    <span className="font-bold">{product.weight}</span>
                  </div>
                  <div>
                    <span className="text-[#737373] block">Protein/Serving</span>
                    <span className="font-bold">{product.proteinPerServing}</span>
                  </div>
                  <div>
                    <span className="text-[#737373] block">Servings</span>
                    <span className="font-bold">{product.servings}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#1d1d1d] text-white py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-[#737373] text-sm">
          © 2026 <Link href="/" className="hover:text-white">NEED® Supplements</Link>.
        </div>
      </footer>
    </div>
  );
}
