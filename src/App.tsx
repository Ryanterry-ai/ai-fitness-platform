import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const HomePage = lazy(() => import('./app/page'));
const ShopPage = lazy(() => import('./app/shop/page'));
const ProductPage = lazy(() => import('./app/product/[slug]/page'));
const CartPage = lazy(() => import('./app/cart/page'));
const CheckoutPage = lazy(() => import('./app/checkout/page'));
const AboutPage = lazy(() => import('./app/about/page'));
const BlogPage = lazy(() => import('./app/blog/page'));
const ContactPage = lazy(() => import('./app/contact/page'));
const AdminPage = lazy(() => import('./app/admin/page'));
const Pack3DPage = lazy(() => import('./app/3d-pack/page'));
const WhyPurePage = lazy(() => import('./app/why-pure/page'));
const StackSavePage = lazy(() => import('./app/stack-save/page'));

const WholesalePage = lazy(() => import('./app/wholesale/page'));
const AthletesPage = lazy(() => import('./app/athletes/page'));

function LoadingFallback() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000', color: '#fff' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontFamily: 'var(--display)', fontSize: 24, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Loading...</div>
      </div>
    </div>
  );
}

function NotFound() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000', color: '#fff', padding: 32 }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontFamily: 'var(--display)', fontSize: 72, color: 'var(--yellow)', lineHeight: 1, marginBottom: 16 }}>404</div>
        <h1 style={{ fontFamily: 'var(--display)', fontSize: 28, textTransform: 'uppercase', marginBottom: 12 }}>Page Not Found</h1>
        <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 15, marginBottom: 32 }}>The page you are looking for does not exist or has been moved.</p>
        <a href="/" style={{ display: 'inline-block', padding: '14px 32px', background: 'var(--yellow)', color: '#000', fontFamily: 'var(--display)', fontSize: 13, letterSpacing: '0.06em', textTransform: 'uppercase', textDecoration: 'none', borderRadius: 10, fontWeight: 700 }}>
          Back to Home
        </a>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <main id="main-content" role="main">
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/shop" element={<ShopPage />} />
            <Route path="/product/:slug" element={<ProductPage />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/checkout" element={<CheckoutPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/blog" element={<BlogPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/3d-pack" element={<Pack3DPage />} />
            <Route path="/why-pure" element={<WhyPurePage />} />
            <Route path="/stack-save" element={<StackSavePage />} />
            <Route path="/wholesale" element={<WholesalePage />} />
            <Route path="/athletes" element={<AthletesPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </main>
    </BrowserRouter>
  );
}
