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
const FormulaPage = lazy(() => import('./app/formula/page'));
const JournalPage = lazy(() => import('./app/journal/page'));

function LoadingFallback() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000', color: '#fff' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontFamily: 'var(--display)', fontSize: 24, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Loading...</div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
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
          <Route path="/formula" element={<FormulaPage />} />
          <Route path="/journal" element={<JournalPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
