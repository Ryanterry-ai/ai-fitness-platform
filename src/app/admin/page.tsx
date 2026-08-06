'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Package, ShoppingBag, Users, BarChart3, Settings, Plus, Edit3, Trash2, Eye, Search, ChevronDown, Check, X, Truck, Clock, CheckCircle, XCircle, Tag, ArrowLeft } from 'lucide-react';
import { useShop, Product, Order, Coupon } from '@/lib/store';
import ScrollReveal from '@/components/ScrollReveal';

const EASE = [0.23, 1, 0.32, 1] as const;

type Tab = 'dashboard' | 'products' | 'orders' | 'coupons' | 'customers';

export default function AdminPage() {
  const { products, orders, coupons, updateOrderStatus } = useShop();
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [searchQuery, setSearchQuery] = useState('');

  const totalRevenue = orders.reduce((sum: number, o: Order) => sum + o.total, 0);
  const paidOrders = orders.filter((o: Order) => o.paymentStatus === 'PAID').length;
  const pendingOrders = orders.filter((o: Order) => o.orderStatus === 'Processing').length;

  const tabs: { id: Tab; label: string; icon: any; count?: number }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'products', label: 'Products', icon: Package, count: products.length },
    { id: 'orders', label: 'Orders', icon: ShoppingBag, count: orders.length },
    { id: 'coupons', label: 'Coupons', icon: Tag, count: coupons.length },
    { id: 'customers', label: 'Customers', icon: Users },
  ];

  return (
    <div className="bg-pure-black min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <a href="/" className="text-xs text-gray-500 hover:text-pure-yellow transition-colors flex items-center gap-1 mb-2">
              <ArrowLeft className="w-3 h-3" /> Back to Store
            </a>
            <h1 className="text-3xl font-black text-white uppercase tracking-tight">Admin Panel</h1>
            <p className="text-sm text-gray-500 mt-1">Manage your store</p>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <div className="lg:w-56 shrink-0">
            <div className="glass rounded-2xl p-3 border border-white/5 space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                    activeTab === tab.id
                      ? 'bg-pure-yellow text-pure-black'
                      : 'text-gray-500 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span className="flex-1 text-left">{tab.label}</span>
                  {tab.count !== undefined && (
                    <span className={`text-[10px] px-2 py-0.5 rounded-full ${activeTab === tab.id ? 'bg-pure-black/20' : 'bg-white/10'}`}>
                      {tab.count}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <AnimatePresence mode="wait">
              {activeTab === 'dashboard' && (
                <motion.div key="dashboard" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="space-y-6">
                  {/* Stats */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                      { label: 'Total Revenue', value: `₹${totalRevenue.toLocaleString('en-IN')}`, icon: BarChart3, color: 'text-pure-yellow' },
                      { label: 'Total Orders', value: orders.length, icon: ShoppingBag, color: 'text-blue-400' },
                      { label: 'Paid Orders', value: paidOrders, icon: CheckCircle, color: 'text-green-400' },
                      { label: 'Pending', value: pendingOrders, icon: Clock, color: 'text-orange-400' },
                    ].map((stat, i) => (
                      <div key={i} className="glass rounded-2xl p-5 border border-white/5">
                        <stat.icon className={`w-5 h-5 ${stat.color} mb-3`} />
                        <p className="text-2xl font-black text-white">{stat.value}</p>
                        <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
                      </div>
                    ))}
                  </div>

                  {/* Recent Orders */}
                  <div className="glass rounded-2xl border border-white/5 overflow-hidden">
                    <div className="p-5 border-b border-white/5">
                      <h3 className="text-sm font-bold text-white">Recent Orders</h3>
                    </div>
                    <div className="divide-y divide-white/5">
                      {orders.slice(0, 5).map((order: Order) => (
                        <div key={order.id} className="px-5 py-3 flex items-center justify-between">
                          <div>
                            <p className="text-sm font-bold text-white">{order.orderNumber}</p>
                            <p className="text-xs text-gray-500">{order.shippingAddress.name} • {new Date(order.date).toLocaleDateString()}</p>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${
                              order.orderStatus === 'Delivered' ? 'bg-green-500/20 text-green-400' :
                              order.orderStatus === 'Dispatched' ? 'bg-blue-500/20 text-blue-400' :
                              'bg-orange-500/20 text-orange-400'
                            }`}>
                              {order.orderStatus}
                            </span>
                            <span className="text-sm font-bold text-pure-yellow">₹{order.total.toLocaleString('en-IN')}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}

              {activeTab === 'products' && (
                <motion.div key="products" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-bold text-white">Products ({products.length})</h2>
                  </div>
                  <div className="space-y-3">
                    {products.map((product: Product) => (
                      <div key={product.id} className="glass rounded-2xl p-4 border border-white/5 flex items-center gap-4">
                        <img src={product.image} alt="" className="w-16 h-16 rounded-xl object-cover bg-pure-dark" />
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-bold text-white truncate">{product.name}</h3>
                          <p className="text-xs text-gray-500">{product.category} • {product.flavour || 'N/A'} • {product.variants.length} variants</p>
                        </div>
                        <div className="text-right shrink-0">
                          <p className="text-sm font-bold text-pure-yellow">₹{product.price.toLocaleString('en-IN')}</p>
                          <p className="text-xs text-gray-500">{product.rating}★ • {product.reviewCount} reviews</p>
                        </div>
                        <div className="flex gap-1 shrink-0">
                          <button className="p-2 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-colors"><Eye className="w-4 h-4" /></button>
                          <button className="p-2 text-gray-500 hover:text-pure-yellow hover:bg-pure-yellow/10 rounded-lg transition-colors"><Edit3 className="w-4 h-4" /></button>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {activeTab === 'orders' && (
                <motion.div key="orders" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="space-y-4">
                  <h2 className="text-lg font-bold text-white">Orders ({orders.length})</h2>
                  <div className="space-y-3">
                    {orders.map((order: Order) => (
                      <div key={order.id} className="glass rounded-2xl p-5 border border-white/5">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <p className="text-sm font-bold text-white">{order.orderNumber}</p>
                            <p className="text-xs text-gray-500">{new Date(order.date).toLocaleString()}</p>
                          </div>
                          <div className="flex gap-2">
                            <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${
                              order.paymentStatus === 'PAID' ? 'bg-green-500/20 text-green-400' : 'bg-orange-500/20 text-orange-400'
                            }`}>
                              {order.paymentStatus}
                            </span>
                            <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${
                              order.orderStatus === 'Delivered' ? 'bg-green-500/20 text-green-400' :
                              order.orderStatus === 'Dispatched' ? 'bg-blue-500/20 text-blue-400' :
                              'bg-orange-500/20 text-orange-400'
                            }`}>
                              {order.orderStatus}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="text-xs text-gray-500">
                            <p>{order.shippingAddress.name} • {order.shippingAddress.city}, {order.shippingAddress.state}</p>
                            <p>{order.paymentMethod.toUpperCase()} • ₹{order.total.toLocaleString('en-IN')}</p>
                          </div>
                          <div className="flex gap-1">
                            {(['Processing', 'Dispatched', 'Delivered'] as const).map((status) => (
                              <button
                                key={status}
                                onClick={() => updateOrderStatus(order.id, status)}
                                className={`text-[10px] px-2 py-1 rounded-lg font-bold transition-all ${
                                  order.orderStatus === status
                                    ? 'bg-pure-yellow text-pure-black'
                                    : 'bg-white/5 text-gray-500 hover:bg-white/10'
                                }`}
                              >
                                {status}
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {activeTab === 'coupons' && (
                <motion.div key="coupons" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="space-y-4">
                  <h2 className="text-lg font-bold text-white">Coupons ({coupons.length})</h2>
                  <div className="space-y-3">
                    {coupons.map((coupon: Coupon) => (
                      <div key={coupon.code} className="glass rounded-2xl p-5 border border-white/5 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 bg-pure-yellow/10 rounded-xl flex items-center justify-center">
                            <Tag className="w-5 h-5 text-pure-yellow" />
                          </div>
                          <div>
                            <p className="text-sm font-bold text-pure-yellow">{coupon.code}</p>
                            <p className="text-xs text-gray-500">{coupon.description}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-black text-white">
                            {coupon.discountType === 'percentage' ? `${coupon.value}%` : `₹${coupon.value}`}
                          </p>
                          <p className="text-[10px] text-gray-500">Min order ₹{coupon.minOrder}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {activeTab === 'customers' && (
                <motion.div key="customers" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="space-y-4">
                  <h2 className="text-lg font-bold text-white">Customers</h2>
                  <div className="glass rounded-2xl p-8 border border-white/5 text-center">
                    <Users className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                    <p className="text-sm text-gray-500">Customer management coming soon.</p>
                    <p className="text-xs text-gray-600 mt-1">Integrate with your CRM or database for full customer profiles.</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
