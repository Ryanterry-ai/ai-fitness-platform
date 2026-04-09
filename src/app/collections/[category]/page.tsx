import Image from "next/image";
import Link from "next/link";
import { categories, products } from "@/lib/data";

export async function generateStaticParams() {
  return categories.map((cat) => ({
    category: cat.id,
  }));
}

export default async function CollectionPage({ params }: { params: Promise<{ category: string }> }) {
  const { category } = await params;
  const categoryData = categories.find(c => c.id === category);
  const categoryProducts = products.filter(p => p.category === category);

  return (
    <div className="min-h-screen font-roboto">
      {/* Header */}
      <header className="bg-[#1d1d1d] py-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
          <Link href="/" className="flex items-center">
            <Image
              src="/images/logo.png"
              alt="NEED® Supplements"
              width={180}
              height={60}
              className="h-auto"
            />
          </Link>
          
          <nav className="hidden md:flex items-center gap-6">
            {categories.map((link) => (
              <Link
                key={link.id}
                href={link.href}
                className="text-white font-oswald text-sm tracking-wide hover:text-[#ffcc00] transition-colors"
              >
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
            <Link href="/cart" className="text-white hover:text-[#ffcc00] relative">
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
            <span className="text-[#1d1d1d] ml-1">{categoryData?.name}</span>
          </p>
        </div>
      </div>

      {/* Hero */}
      <div className="bg-[#1d1d1d] py-12 text-center">
        <h1 className="font-oswald text-4xl md:text-5xl font-bold text-white">
          {categoryData?.name?.toUpperCase()}
        </h1>
      </div>

      {/* Products Grid */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <p className="text-[#737373] mb-8">{categoryProducts.length} products</p>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {categoryProducts.map((product) => (
              <Link
                key={product.id}
                href={`/products/${product.id}`}
                className="group block"
              >
                <div className="relative bg-[#fafafa] rounded-lg overflow-hidden mb-3">
                  <div className="aspect-[3/4] relative">
                    <Image
                      src={product.image}
                      alt={product.name}
                      fill
                      className="object-contain p-4"
                      sizes="(max-width: 768px) 50vw, 25vw"
                    />
                  </div>
                  {product.originalPrice && (
                    <span className="absolute top-2 left-2 bg-[#ffcc00] text-black text-xs font-bold px-2 py-1">
                      {Math.round((1 - product.price / product.originalPrice) * 100)}% off
                    </span>
                  )}
                  {product.status === "sold-out" && (
                    <span className="absolute inset-0 bg-black/50 flex items-center justify-center">
                      <span className="bg-white text-black text-xs font-bold px-3 py-1">Sold out</span>
                    </span>
                  )}
                </div>
                <h3 className="font-oswald text-sm font-medium text-[#1d1d1d]">{product.name}</h3>
                <div className="mt-1">
                  {product.originalPrice ? (
                    <div className="flex items-center gap-2">
                      <span className="text-[#1d1d1d] font-bold">€{product.price.toFixed(2)}</span>
                      <span className="text-[#737373] line-through text-sm">€{product.originalPrice.toFixed(2)}</span>
                    </div>
                  ) : (
                    <span className="text-[#1d1d1d]">€{product.price.toFixed(2)}</span>
                  )}
                </div>
              </Link>
            ))}
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
