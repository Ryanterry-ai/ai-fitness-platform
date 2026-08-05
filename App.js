import React, { useState, useEffect } from "react";
import { 
  ShoppingBag, Zap, Shield, Flame, Activity, Sparkles, CheckCircle2, 
  Star, ChevronRight, Menu, X, ArrowRight, RotateCw, ExternalLink, 
  Truck, Award, Clock, MapPin, Check, Plus, Minus, FileText, Download, Play
} from "lucide-react";
import { mockProducts, mockIngredients, mockBadges, mockReviews } from "./mock";

export default function App() {
  const [selectedProductIndex, setSelectedProductIndex] = useState(2); // Default to Rocket Lollipop (fan favorite)
  const [cartOpen, setCartOpen] = useState(false);
  const [cart, setCart] = useState([
    { ...mockProducts[2], quantity: 1 }
  ]);
  const [activeTab, setActiveTab] = useState("overview"); // overview, ingredients, reviews
  const [pdfModalOpen, setPdfModalOpen] = useState(false);
  const [checkoutModalOpen, setCheckoutModalOpen] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [notificationOpen, setNotificationOpen] = useState(true);

  const currentProduct = mockProducts[selectedProductIndex];

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 3500);
  };

  const addToCart = (prod) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === prod.id);
      if (existing) {
        return prev.map(item => item.id === prod.id ? { ...item, quantity: item.quantity + 1 } : item);
      }
      return [...prev, { ...prod, quantity: 1 }];
    });
    showToast(`Added ${prod.flavor} to your cart!`);
    setCartOpen(true);
  };

  const updateQuantity = (id, delta) => {
    setCart(prev => prev.map(item => {
      if (item.id === id) {
        const newQty = item.quantity + delta;
        return newQty > 0 ? { ...item, quantity: newQty } : null;
      }
      return item;
    }).filter(Boolean));
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const cartItemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#EDEDED] relative selection:bg-red-600 selection:text-white font-sans">
      
      {/* Toast Notification */}
      {toastMessage && (
        <div data-testid="toast-notification" className="fixed bottom-6 right-6 z-50 bg-neutral-900 border border-neutral-700 text-white px-6 py-3 rounded-xl shadow-2xl flex items-center space-x-3 animate-bounce">
          <div className="w-3 h-3 rounded-full bg-red-500 animate-ping"></div>
          <span className="font-medium text-sm">{toastMessage}</span>
        </div>
      )}

      {/* Announcement Bar */}
      {notificationOpen && (
        <div data-testid="announcement-bar" className="bg-gradient-to-r from-red-600 via-orange-600 to-red-600 text-white text-xs md:text-sm font-semibold py-2 px-4 text-center relative flex items-center justify-center">
          <span className="flex items-center space-x-2">
            <Zap className="w-4 h-4 animate-pulse text-yellow-300" />
            <span>🔥 NEW LAUNCH SALE: Get Extra 20% OFF with Code <strong className="underline">PRIME20</strong> + Free Shaker Cup on Orders Above ₹1,499!</span>
          </span>
          <button data-testid="close-announcement" onClick={() => setNotificationOpen(false)} className="absolute right-4 hover:opacity-75">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Navigation Header */}
      <header className="sticky top-0 z-40 bg-[#0A0A0A]/90 backdrop-blur-xl border-b border-neutral-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <a data-testid="nav-logo" href="#" className="flex items-center space-x-2 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-600 to-orange-500 flex items-center justify-center font-black text-white text-xl shadow-lg shadow-red-900/40 group-hover:scale-105 transition-transform">
                P
              </div>
              <div>
                <span className="font-black text-lg tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-white via-neutral-200 to-neutral-400">PURE SUPPS</span>
                <span className="block text-[10px] text-red-500 font-bold tracking-widest uppercase">Elite Science</span>
              </div>
            </a>
          </div>

          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-neutral-300">
            <a href="#showcase" data-testid="nav-showcase" className="hover:text-white transition-colors">3D Showcase</a>
            <a href="#flavors" data-testid="nav-flavors" className="hover:text-white transition-colors">Flavors</a>
            <a href="#ingredients" data-testid="nav-ingredients" className="hover:text-white transition-colors">Formula & Science</a>
            <a href="#reviews" data-testid="nav-reviews" className="hover:text-white transition-colors">Athletes</a>
            <button data-testid="nav-pdf-btn" onClick={() => setPdfModalOpen(true)} className="flex items-center space-x-1 text-red-400 hover:text-red-300 font-semibold">
              <FileText className="w-4 h-4" />
              <span>PDF Dossiers</span>
            </button>
          </nav>

          <div className="flex items-center space-x-4">
            <button 
              data-testid="cart-trigger-btn"
              onClick={() => setCartOpen(true)}
              className="relative p-2.5 rounded-xl bg-neutral-900 border border-neutral-800 hover:border-neutral-700 text-white transition-all flex items-center space-x-2"
            >
              <ShoppingBag className="w-5 h-5 text-red-500" />
              <span className="hidden sm:inline text-xs font-bold">Cart</span>
              {cartItemCount > 0 && (
                <span data-testid="cart-badge-count" className="absolute -top-2 -right-2 bg-red-600 text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center shadow-lg">
                  {cartItemCount}
                </span>
              )}
            </button>

            <a 
              href="#showcase" 
              data-testid="nav-buy-now-btn"
              className="hidden sm:inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-gradient-to-r from-red-600 to-orange-600 text-white text-xs font-bold uppercase tracking-wider shadow-lg shadow-red-600/30 hover:shadow-red-600/50 hover:scale-[1.02] transition-all"
            >
              Order Prime X
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section with 3D Interactive Showcase */}
      <section id="showcase" className="relative min-h-[90vh] flex items-center justify-center overflow-hidden py-16 px-4 sm:px-6 lg:px-8">
        {/* Background Ambient Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-600/15 rounded-full blur-[140px] pointer-events-none animate-pulse-glow"></div>
        
        <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
          
          {/* Left Column: Product Info & Flavor Selector */}
          <div className="lg:col-span-6 space-y-6">
            <div className="inline-flex items-center space-x-2 bg-neutral-900/90 border border-neutral-800 px-3.5 py-1.5 rounded-full text-xs font-bold text-red-500 shadow-inner">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
              <span>{currentProduct.badge} • 30 Servings</span>
            </div>

            <h1 data-testid="hero-heading" className="text-4xl sm:text-6xl font-black tracking-tight leading-none uppercase">
              {currentProduct.name}
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 mt-1">
                {currentProduct.flavor}
              </span>
            </h1>

            <p data-testid="hero-description" className="text-neutral-400 text-base sm:text-lg max-w-lg leading-relaxed">
              {currentProduct.description}
            </p>

            {/* Flavor Switcher Buttons */}
            <div className="space-y-3 pt-2">
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">Select Flavor Variant:</span>
              <div className="flex flex-wrap gap-3">
                {mockProducts.map((prod, idx) => (
                  <button
                    key={prod.id}
                    data-testid={`flavor-btn-${idx}`}
                    onClick={() => setSelectedProductIndex(idx)}
                    className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                      selectedProductIndex === idx
                        ? 'bg-white text-black shadow-lg scale-105'
                        : 'bg-neutral-900 border border-neutral-800 text-neutral-400 hover:text-white hover:border-neutral-700'
                    }`}
                  >
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: prod.color }}></span>
                    <span>{prod.flavor}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Price & Add to Cart Action */}
            <div className="pt-4 flex flex-wrap items-center gap-6">
              <div>
                <div className="flex items-baseline space-x-3">
                  <span data-testid="product-price" className="text-3xl font-black text-white">₹{currentProduct.price}</span>
                  <span className="text-sm font-semibold text-neutral-500 line-through">₹{currentProduct.originalPrice}</span>
                  <span className="text-xs font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded">Save 32%</span>
                </div>
                <span className="text-[11px] text-neutral-500">Inclusive of all taxes • Free express shipping</span>
              </div>

              <button
                data-testid="add-to-cart-main-btn"
                onClick={() => addToCart(currentProduct)}
                className="flex-1 min-w-[200px] py-4 px-8 rounded-xl bg-gradient-to-r from-red-600 via-orange-600 to-red-600 text-white font-black uppercase tracking-wider shadow-xl shadow-red-600/30 hover:shadow-red-600/60 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center space-x-3"
              >
                <ShoppingBag className="w-5 h-5" />
                <span>Add To Cart</span>
              </button>
            </div>

            {/* Key stats row */}
            <div className="grid grid-cols-3 gap-4 pt-6 border-t border-neutral-800/80">
              <div className="bg-neutral-900/60 p-3 rounded-xl border border-neutral-800/60">
                <span className="block text-[11px] font-bold text-neutral-400 uppercase">Nitric Oxide</span>
                <span className="text-sm font-extrabold text-white">8,000mg Citrulline</span>
              </div>
              <div className="bg-neutral-900/60 p-3 rounded-xl border border-neutral-800/60">
                <span className="block text-[11px] font-bold text-neutral-400 uppercase">Energy Matrix</span>
                <span className="text-sm font-extrabold text-white">{currentProduct.caffeine.split(' ')[0]}</span>
              </div>
              <div className="bg-neutral-900/60 p-3 rounded-xl border border-neutral-800/60">
                <span className="block text-[11px] font-bold text-neutral-400 uppercase">Rating</span>
                <span className="text-sm font-extrabold text-white flex items-center space-x-1">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400 inline" />
                  <span>{currentProduct.rating} ({currentProduct.reviewsCount})</span>
                </span>
              </div>
            </div>

          </div>

          {/* Right Column: 3D Interactive Product View / Orbit Simulator */}
          <div className="lg:col-span-6 flex flex-col items-center justify-center relative">
            
            {/* Interactive Badge Controls */}
            <div className="absolute top-0 right-0 z-20 flex space-x-2">
              <button 
                data-testid="toggle-rotate-btn"
                onClick={() => setIsRotating(!isRotating)}
                className={`p-3 rounded-xl border transition-all flex items-center space-x-2 text-xs font-bold ${
                  isRotating ? 'bg-red-600 border-red-500 text-white shadow-lg' : 'bg-neutral-900 border-neutral-800 text-neutral-300 hover:bg-neutral-800'
                }`}
              >
                <RotateCw className={`w-4 h-4 ${isRotating ? 'animate-spin' : ''}`} />
                <span>{isRotating ? '3D Spin Active' : 'Orbit 3D'}</span>
              </button>
            </div>

            {/* 3D Container */}
            <div className="relative w-full max-w-md h-[450px] sm:h-[520px] flex items-center justify-center group">
              
              {/* Radial glow background corresponding to flavor */}
              <div 
                className="absolute inset-0 rounded-full blur-3xl opacity-30 transition-all duration-700"
                style={{ backgroundColor: currentProduct.color }}
              ></div>

              {/* Orbit rings animation */}
              <div className="absolute inset-8 rounded-full border border-neutral-800/60 animate-[spin_20s_linear_infinite] pointer-events-none"></div>
              <div className="absolute inset-16 rounded-full border border-dashed border-neutral-700/40 animate-[spin_30s_linear_infinite_reverse] pointer-events-none"></div>

              {/* Product Tub Image with floating & rotation state */}
              <img 
                data-testid="hero-product-tub"
                src={currentProduct.tubImage} 
                alt={currentProduct.flavor} 
                className={`max-h-[400px] object-contain drop-shadow-[0_25px_35px_rgba(0,0,0,0.8)] transition-all duration-500 ${isRotating ? 'animate-float scale-105' : 'hover:scale-105'}`}
              />

              {/* Interactive Hotspot 1 */}
              <div className="absolute bottom-12 left-6 bg-neutral-900/90 backdrop-blur-md border border-neutral-800 p-3 rounded-xl shadow-xl flex items-center space-x-3 animate-pulse">
                <div className="w-8 h-8 rounded-lg bg-red-600/20 text-red-500 flex items-center justify-center font-bold">
                  <Zap className="w-4 h-4" />
                </div>
                <div>
                  <span className="block text-[10px] text-neutral-400 font-bold uppercase">Active Matrix</span>
                  <span className="text-xs font-bold text-white">{currentProduct.nitricOxide}</span>
                </div>
              </div>

              {/* Interactive Hotspot 2 */}
              <div className="absolute top-16 right-4 bg-neutral-900/90 backdrop-blur-md border border-neutral-800 p-3 rounded-xl shadow-xl flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-600/20 text-emerald-400 flex items-center justify-center font-bold">
                  <Shield className="w-4 h-4" />
                </div>
                <div>
                  <span className="block text-[10px] text-neutral-400 font-bold uppercase">Safety Guarantee</span>
                  <span className="text-xs font-bold text-white">100% Banned Free</span>
                </div>
              </div>

            </div>

            {/* Quick PDF Dossier Preview button */}
            <div className="mt-4">
              <button 
                data-testid="open-pdf-modal-btn"
                onClick={() => setPdfModalOpen(true)}
                className="text-xs font-semibold text-neutral-400 hover:text-white underline underline-offset-4 flex items-center space-x-1"
              >
                <FileText className="w-3.5 h-3.5 text-red-500" />
                <span>View Official Laboratory Analysis PDF for {currentProduct.flavor}</span>
              </button>
            </div>

          </div>

        </div>
      </section>

      {/* Trust Badges Bar */}
      <section className="border-y border-neutral-800/80 bg-neutral-950 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          {mockBadges.map((badge, idx) => (
            <div key={idx} data-testid={`trust-badge-${idx}`} className="flex items-center space-x-4 p-4 rounded-xl bg-neutral-900/50 border border-neutral-800/60">
              <div className="w-12 h-12 rounded-xl bg-red-600/10 border border-red-600/20 flex items-center justify-center text-red-500 font-bold">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{badge.title}</h4>
                <p className="text-xs text-neutral-400">Rigorously tested for maximum athletic purity & potency.</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Interactive Ingredient Breakdown & Formula Section */}
      <section id="ingredients" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold uppercase tracking-widest text-red-500 bg-red-950/50 border border-red-900/50 px-3 py-1 rounded-full">
            Transparent Clinical Dosing
          </span>
          <h2 className="text-3xl sm:text-5xl font-black uppercase tracking-tight">
            What Goes Inside <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500">Prime X</span>
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base">
            No proprietary blends. Every active ingredient is fully disclosed with clinical dosages to guarantee supreme workout performance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockIngredients.map((ing, idx) => (
            <div 
              key={idx}
              data-testid={`ingredient-card-${idx}`}
              className="bg-neutral-900/60 border border-neutral-800 hover:border-red-600/50 p-6 rounded-2xl transition-all hover:scale-[1.02] group relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-red-600/5 rounded-full blur-2xl group-hover:bg-red-600/15 transition-all"></div>
              
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-neutral-800 text-red-500 flex items-center justify-center font-bold border border-neutral-700">
                  <Zap className="w-5 h-5" />
                </div>
                <span className="text-xs font-black bg-red-950/80 text-red-400 border border-red-900/60 px-3 py-1 rounded-full">
                  {ing.dosage}
                </span>
              </div>

              <h3 className="text-lg font-bold text-white mb-2">{ing.name}</h3>
              <p className="text-xs sm:text-sm text-neutral-400 leading-relaxed">{ing.benefit}</p>
            </div>
          ))}
        </div>

        {/* PDF Download Banner */}
        <div className="mt-12 bg-gradient-to-r from-neutral-900 via-neutral-900 to-neutral-950 border border-neutral-800 rounded-3xl p-8 sm:p-10 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-2xl">
          <div className="space-y-2 text-center sm:text-left">
            <span className="text-xs font-bold text-red-500 uppercase">Official Documentation</span>
            <h3 className="text-xl sm:text-2xl font-black">Download Complete Lab Dossiers & Supplement Facts</h3>
            <p className="text-xs sm:text-sm text-neutral-400 max-w-xl">
              Access the exact PDF certificates and ingredient breakdown sheets for Fruit Punch, Orange, and Rocket Lollipop.
            </p>
          </div>
          <button
            data-testid="download-dossier-btn"
            onClick={() => setPdfModalOpen(true)}
            className="px-6 py-3.5 rounded-xl bg-white text-black font-black uppercase text-xs tracking-wider hover:bg-neutral-200 transition-all flex items-center space-x-2 shadow-lg"
          >
            <Download className="w-4 h-4" />
            <span>Open PDF Viewer</span>
          </button>
        </div>
      </section>

      {/* Flavor Showcase Grid */}
      <section id="flavors" className="py-24 bg-neutral-950 border-t border-neutral-800/80 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
            <span className="text-xs font-bold uppercase tracking-widest text-orange-500 bg-orange-950/50 border border-orange-900/50 px-3 py-1 rounded-full">
              Sensory Perfection
            </span>
            <h2 className="text-3xl sm:text-5xl font-black uppercase tracking-tight">
              Choose Your Weapon
            </h2>
            <p className="text-neutral-400 text-sm sm:text-base">
              Crafted by elite flavorists to deliver refreshing taste without artificial chemical aftertaste.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {mockProducts.map((prod, idx) => (
              <div 
                key={prod.id}
                data-testid={`flavor-grid-card-${idx}`}
                className={`bg-neutral-900 border rounded-3xl p-6 flex flex-col justify-between transition-all hover:scale-[1.02] relative overflow-hidden ${
                  selectedProductIndex === idx ? 'border-red-600 ring-2 ring-red-600/30' : 'border-neutral-800'
                }`}
              >
                <div className="absolute top-0 right-0 w-40 h-40 rounded-full blur-3xl opacity-20" style={{ backgroundColor: prod.color }}></div>
                
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-bold uppercase px-3 py-1 rounded-full bg-neutral-800 text-neutral-300">
                      {prod.badge}
                    </span>
                    <span className="flex items-center space-x-1 text-xs font-bold text-yellow-400">
                      <Star className="w-3.5 h-3.5 fill-yellow-400" />
                      <span>{prod.rating}</span>
                    </span>
                  </div>

                  <div className="h-48 flex items-center justify-center my-4">
                    <img src={prod.tubImage} alt={prod.flavor} className="max-h-44 object-contain hover:scale-110 transition-transform drop-shadow-2xl" />
                  </div>

                  <h3 className="text-xl font-black uppercase mb-1">{prod.flavor}</h3>
                  <p className="text-xs text-neutral-400 mb-6">{prod.tagline}</p>
                </div>

                <div className="space-y-4 pt-4 border-t border-neutral-800">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-2xl font-black text-white">₹{prod.price}</span>
                      <span className="text-xs text-neutral-500 line-through ml-2">₹{prod.originalPrice}</span>
                    </div>
                    <span className="text-xs font-bold text-emerald-400">In Stock</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <button
                      data-testid={`select-flavor-quick-${idx}`}
                      onClick={() => {
                        setSelectedProductIndex(idx);
                        window.scrollTo({ top: 400, behavior: 'smooth' });
                      }}
                      className="py-2.5 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-white text-xs font-bold uppercase transition-all"
                    >
                      View in 3D
                    </button>
                    <button
                      data-testid={`add-flavor-cart-${idx}`}
                      onClick={() => addToCart(prod)}
                      className="py-2.5 rounded-xl bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white text-xs font-bold uppercase transition-all shadow-lg shadow-red-600/30 flex items-center justify-center space-x-1"
                    >
                      <ShoppingBag className="w-3.5 h-3.5" />
                      <span>Buy</span>
                    </button>
                  </div>
                </div>

              </div>
            ))}
          </div>

        </div>
      </section>

      {/* Athlete Reviews Section */}
      <section id="reviews" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold uppercase tracking-widest text-emerald-500 bg-emerald-950/50 border border-emerald-900/50 px-3 py-1 rounded-full">
            Verified Feedback
          </span>
          <h2 className="text-3xl sm:text-5xl font-black uppercase tracking-tight">
            Trusted By Elite Athletes
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base">
            See why professional bodybuilders and CrossFit champions swear by Pure Supps Prime X.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {mockReviews.map((rev) => (
            <div key={rev.id} data-testid={`review-card-${rev.id}`} className="bg-neutral-900/60 border border-neutral-800 p-8 rounded-3xl space-y-4 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center space-x-1">
                  {[...Array(rev.rating)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm text-neutral-300 italic leading-relaxed">"{rev.comment}"</p>
              </div>
              <div className="pt-4 border-t border-neutral-800/80 flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white">{rev.name}</h4>
                  <span className="text-xs text-neutral-500">{rev.role}</span>
                </div>
                <span className="text-[10px] text-neutral-600 font-bold">{rev.date}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-neutral-950 border-t border-neutral-800/80 py-16 px-4 sm:px-6 lg:px-8 text-neutral-400 text-xs">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-10">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-red-600 to-orange-500 flex items-center justify-center font-black text-white text-lg">
                P
              </div>
              <span className="font-black text-base text-white tracking-wider">PURE SUPPS</span>
            </div>
            <p className="text-neutral-400 leading-relaxed">
              Formulated with pure science and zero banned substances. Built for athletes who refuse to compromise on performance.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Quick Links</h4>
            <ul className="space-y-2.5">
              <li><a href="#showcase" className="hover:text-white transition-colors">3D Interactive Product</a></li>
              <li><a href="#flavors" className="hover:text-white transition-colors">Flavor Variants</a></li>
              <li><a href="#ingredients" className="hover:text-white transition-colors">Clinical Formula</a></li>
              <li><button onClick={() => setPdfModalOpen(true)} className="hover:text-white transition-colors">Lab PDF Dossiers</button></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Certifications</h4>
            <ul className="space-y-2.5">
              <li className="flex items-center space-x-2"><Check className="w-3.5 h-3.5 text-emerald-400" /><span>100% Banned Substance Free</span></li>
              <li className="flex items-center space-x-2"><Check className="w-3.5 h-3.5 text-emerald-400" /><span>FSSAI Certified Laboratory</span></li>
              <li className="flex items-center space-x-2"><Check className="w-3.5 h-3.5 text-emerald-400" /><span>GMP Quality Assured</span></li>
            </ul>
          </div>

          <div className="space-y-4">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Join The Elite</h4>
            <p className="text-neutral-400">Subscribe for secret drop access & VIP discount codes.</p>
            <div className="flex space-x-2">
              <input type="email" placeholder="Enter your email" className="bg-neutral-900 border border-neutral-800 px-4 py-2.5 rounded-xl text-white text-xs w-full focus:outline-none focus:border-red-500" />
              <button onClick={() => showToast("Subscribed successfully! Use code PRIME20")} className="bg-red-600 hover:bg-red-500 text-white font-bold px-4 py-2.5 rounded-xl transition-all">Join</button>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto mt-12 pt-8 border-t border-neutral-900 flex flex-col sm:flex-row items-center justify-between text-neutral-400">
          <p>© 2026 PURE SUPPS. All Rights Reserved. Inspired by elite nutritional standards.</p>
          <div className="flex space-x-6 mt-4 sm:mt-0">
            <a href="#" className="hover:text-white">Privacy Policy</a>
            <a href="#" className="hover:text-white">Terms of Service</a>
            <a href="#" className="hover:text-white">Contact Support</a>
          </div>
        </div>
      </footer>

      {/* Slide-over Cart Drawer */}
      {cartOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={() => setCartOpen(false)}></div>
          
          <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
            <div data-testid="cart-drawer" className="w-screen max-w-md bg-neutral-900 border-l border-neutral-800 p-6 flex flex-col justify-between shadow-2xl">
              
              <div>
                <div className="flex items-center justify-between pb-6 border-b border-neutral-800">
                  <div className="flex items-center space-x-2">
                    <ShoppingBag className="w-5 h-5 text-red-500" />
                    <h3 className="text-lg font-black uppercase text-white">Your Shopping Cart ({cartItemCount})</h3>
                  </div>
                  <button data-testid="close-cart-btn" onClick={() => setCartOpen(false)} className="p-2 hover:bg-neutral-800 rounded-xl text-neutral-400 hover:text-white">
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {cart.length === 0 ? (
                  <div className="py-20 text-center space-y-4">
                    <div className="w-16 h-16 rounded-full bg-neutral-800 flex items-center justify-center mx-auto text-neutral-500">
                      <ShoppingBag className="w-8 h-8" />
                    </div>
                    <p className="text-neutral-400 text-sm">Your cart is currently empty.</p>
                    <button onClick={() => setCartOpen(false)} className="px-6 py-2.5 rounded-xl bg-red-600 text-white font-bold text-xs uppercase">
                      Start Shopping
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4 py-6 max-h-[55vh] overflow-y-auto">
                    {cart.map((item) => (
                      <div key={item.id} data-testid={`cart-item-${item.id}`} className="flex items-center justify-between bg-neutral-950 p-4 rounded-2xl border border-neutral-800/80">
                        <div className="flex items-center space-x-4">
                          <img src={item.tubImage} alt={item.flavor} className="w-12 h-16 object-contain" />
                          <div>
                            <h4 className="text-sm font-bold text-white">{item.flavor}</h4>
                            <span className="text-xs text-red-500 font-bold">₹{item.price}</span>
                          </div>
                        </div>

                        <div className="flex items-center space-x-3 bg-neutral-900 px-3 py-1.5 rounded-xl border border-neutral-800">
                          <button data-testid={`cart-dec-${item.id}`} onClick={() => updateQuantity(item.id, -1)} className="text-neutral-400 hover:text-white">
                            <Minus className="w-3.5 h-3.5" />
                          </button>
                          <span className="text-xs font-bold text-white w-4 text-center">{item.quantity}</span>
                          <button data-testid={`cart-inc-${item.id}`} onClick={() => updateQuantity(item.id, 1)} className="text-neutral-400 hover:text-white">
                            <Plus className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {cart.length > 0 && (
                <div className="space-y-4 pt-6 border-t border-neutral-800">
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between text-neutral-400">
                      <span>Subtotal</span>
                      <span className="text-white font-bold">₹{cartTotal}</span>
                    </div>
                    <div className="flex justify-between text-neutral-400">
                      <span>Express Shipping</span>
                      <span className="text-emerald-400 font-bold">FREE</span>
                    </div>
                    <div className="flex justify-between text-neutral-400">
                      <span>Launch Promo (PRIME20)</span>
                      <span className="text-red-500 font-bold">-20% Applied</span>
                    </div>
                    <div className="flex justify-between text-sm pt-2 border-t border-neutral-800 text-white font-black">
                      <span>Total</span>
                      <span className="text-lg text-red-500">₹{Math.round(cartTotal * 0.8)}</span>
                    </div>
                  </div>

                  <button
                    data-testid="proceed-checkout-btn"
                    onClick={() => {
                      setCartOpen(false);
                      setCheckoutModalOpen(true);
                    }}
                    className="w-full py-4 rounded-xl bg-gradient-to-r from-red-600 to-orange-600 text-white font-black uppercase tracking-wider text-xs shadow-xl shadow-red-600/30 hover:scale-[1.02] transition-all flex items-center justify-center space-x-2"
                  >
                    <span>Proceed To Secure Checkout</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              )}

            </div>
          </div>
        </div>
      )}

      {/* PDF Dossier & Supplement Facts Modal */}
      {pdfModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/80 backdrop-blur-md" onClick={() => setPdfModalOpen(false)}></div>
          
          <div data-testid="pdf-modal" className="relative bg-neutral-900 border border-neutral-800 rounded-3xl max-w-3xl w-full p-8 z-10 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-4">
              <div className="flex items-center space-x-3">
                <FileText className="w-6 h-6 text-red-500" />
                <div>
                  <h3 className="text-lg font-black uppercase text-white">Official Laboratory Analysis & PDF Dossiers</h3>
                  <span className="text-xs text-neutral-400">Verified clinical breakdown for Pure Supps Prime X</span>
                </div>
              </div>
              <button data-testid="close-pdf-modal" onClick={() => setPdfModalOpen(false)} className="p-2 hover:bg-neutral-800 rounded-xl text-neutral-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <p className="text-xs text-neutral-300 leading-relaxed">
                Click any of the official lab reports below to inspect the complete ingredient profile, heavy metal screening, and micro-biological purity certificates.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {mockProducts.map((prod, idx) => (
                  <div key={idx} className="bg-neutral-950 p-4 rounded-2xl border border-neutral-800 space-y-3 flex flex-col justify-between">
                    <div>
                      <span className="text-[10px] font-bold text-red-500 uppercase">{prod.flavor}</span>
                      <h4 className="text-sm font-bold text-white mt-1">Prime X Lab Dossier</h4>
                      <span className="text-xs text-neutral-500 block mt-1">PDF Document • 2.4 MB</span>
                    </div>

                    <a 
                      data-testid={`download-pdf-link-${idx}`}
                      href={prod.pdfUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="w-full py-2.5 rounded-xl bg-neutral-900 hover:bg-neutral-800 border border-neutral-700 text-white text-xs font-bold uppercase flex items-center justify-center space-x-2 transition-all"
                    >
                      <Download className="w-3.5 h-3.5 text-red-500" />
                      <span>View / Download PDF</span>
                    </a>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-neutral-800 flex justify-end">
              <button 
                onClick={() => setPdfModalOpen(false)}
                className="px-6 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs uppercase"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Secure Checkout Simulation Modal */}
      {checkoutModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/80 backdrop-blur-md" onClick={() => setCheckoutModalOpen(false)}></div>
          
          <div data-testid="checkout-modal" className="relative bg-neutral-900 border border-neutral-800 rounded-3xl max-w-lg w-full p-8 z-10 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-4">
              <h3 className="text-lg font-black uppercase text-white">Express Secure Checkout</h3>
              <button data-testid="close-checkout-modal" onClick={() => setCheckoutModalOpen(false)} className="p-2 hover:bg-neutral-800 rounded-xl text-neutral-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={(e) => {
              e.preventDefault();
              showToast("🎉 Order Placed Successfully! Order #PS-94821 Confirmed.");
              setCheckoutModalOpen(false);
              setCart([]);
            }} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase text-neutral-400 mb-1">Full Name</label>
                <input required type="text" placeholder="Vikram Malhotra" className="w-full bg-neutral-950 border border-neutral-800 rounded-xl px-4 py-3 text-white text-xs focus:outline-none focus:border-red-500" />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-neutral-400 mb-1">Shipping Address</label>
                <textarea required rows="2" placeholder="Flat 402, Elite Towers, Bandra West, Mumbai" className="w-full bg-neutral-950 border border-neutral-800 rounded-xl px-4 py-3 text-white text-xs focus:outline-none focus:border-red-500"></textarea>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-neutral-400 mb-1">Phone Number</label>
                  <input required type="tel" placeholder="+91 98765 43210" className="w-full bg-neutral-950 border border-neutral-800 rounded-xl px-4 py-3 text-white text-xs focus:outline-none focus:border-red-500" />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-neutral-400 mb-1">Payment Method</label>
                  <select className="w-full bg-neutral-950 border border-neutral-800 rounded-xl px-4 py-3 text-white text-xs focus:outline-none focus:border-red-500">
                    <option>UPI / Google Pay / PhonePe</option>
                    <option>Credit / Debit Card</option>
                    <option>Cash on Delivery (COD)</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 border-t border-neutral-800 flex items-center justify-between">
                <div>
                  <span className="text-xs text-neutral-400 block">Total Amount</span>
                  <span className="text-xl font-black text-white">₹{Math.round(cartTotal * 0.8)}</span>
                </div>
                <button
                  data-testid="submit-order-btn"
                  type="submit"
                  className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white font-black uppercase text-xs shadow-lg shadow-red-600/30 transition-all"
                >
                  Place Order Now
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
