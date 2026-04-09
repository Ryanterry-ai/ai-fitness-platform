"use client";

import Image from "next/image";
import Link from "next/link";
import { useCart } from "@/lib/cart-context";
import { categories } from "@/lib/data";

export default function CartPage() {
  const { items, updateQuantity, removeFromCart, total, clearCart } = useCart();

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

      {/* Cart Content */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="font-oswald text-3xl font-bold mb-8">SHOPPING CART</h1>
          
          {items.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-[#737373] text-lg mb-6">Your cart is empty</p>
              <Link href="/" className="inline-block bg-[#ffcc00] text-black px-6 py-3 font-oswald font-bold hover:bg-yellow-400">
                CONTINUE SHOPPING
              </Link>
            </div>
          ) : (
            <div className="grid lg:grid-cols-3 gap-12">
              {/* Cart Items */}
              <div className="lg:col-span-2">
                {items.map((item) => (
                  <div key={`${item.product.id}-${item.flavor}`} className="flex gap-6 py-6 border-b">
                    <div className="w-24 h-24 relative bg-[#fafafa] rounded">
                      <Image src={item.product.image} alt={item.product.name} fill className="object-contain p-2" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-oswald text-lg">{item.product.name}</h3>
                      <p className="text-sm text-[#737373]">{item.flavor}</p>
                      <p className="font-bold mt-2">€{item.product.price.toFixed(2)}</p>
                    </div>
                    <div className="flex flex-col items-end gap-4">
                      <button onClick={() => removeFromCart(item.product.id)} className="text-[#737373] hover:text-red-500">
                        <svg xmlns="http://www.w3.org/2000/svg" width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                          <path d="M18 6 6 18M6 6l12 12" />
                        </svg>
                      </button>
                      <div className="flex items-center gap-2">
                        <button onClick={() => updateQuantity(item.product.id, item.quantity - 1)} className="w-8 h-8 border flex items-center justify-center hover:border-[#1d1d1d]">-</button>
                        <span className="w-8 text-center">{item.quantity}</span>
                        <button onClick={() => updateQuantity(item.product.id, item.quantity + 1)} className="w-8 h-8 border flex items-center justify-center hover:border-[#1d1d1d]">+</button>
                      </div>
                      <p className="font-bold">€{(item.product.price * item.quantity).toFixed(2)}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Order Summary */}
              <div className="bg-[#fafafa] p-6 rounded-lg h-fit">
                <h2 className="font-oswald text-xl mb-6">ORDER SUMMARY</h2>
                <div className="flex justify-between mb-4">
                  <span className="text-[#737373]">Subtotal</span>
                  <span className="font-bold">€{total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between mb-4">
                  <span className="text-[#737373]">Shipping</span>
                  <span>Calculated at checkout</span>
                </div>
                <div className="border-t pt-4 flex justify-between mb-6">
                  <span className="font-bold text-lg">Total</span>
                  <span className="font-bold text-lg">€{total.toFixed(2)}</span>
                </div>
                <button 
                  onClick={() => alert("Checkout functionality coming soon! This is a demo clone.")}
                  className="w-full bg-[#ffcc00] text-black py-4 font-oswald font-bold hover:bg-yellow-400"
                >
                  PROCEED TO CHECKOUT
                </button>
              </div>
            </div>
          )}
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
