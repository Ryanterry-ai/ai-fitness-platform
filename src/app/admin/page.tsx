"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { products, Product } from "@/lib/data";

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState("products");
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  const stats = {
    totalProducts: products.length,
    totalSales: "€12,450",
    orders: 156,
    customers: 89,
  };

  return (
    <div className="min-h-screen font-roboto bg-gray-50">
      {/* Admin Header */}
      <header className="bg-[#1d1d1d] text-white py-4">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Image src="/images/logo.png" alt="NEED® Admin" width={150} height={50} className="h-auto" />
            <span className="font-oswald text-xl">ADMIN PANEL</span>
          </div>
          <Link href="/" className="text-sm hover:text-[#ffcc00]">
            View Store →
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <p className="text-[#737373] text-sm">Total Products</p>
            <p className="text-3xl font-bold">{stats.totalProducts}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <p className="text-[#737373] text-sm">Total Sales</p>
            <p className="text-3xl font-bold">{stats.totalSales}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <p className="text-[#737373] text-sm">Orders</p>
            <p className="text-3xl font-bold">{stats.orders}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <p className="text-[#737373] text-sm">Customers</p>
            <p className="text-3xl font-bold">{stats.customers}</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="flex border-b">
            {["products", "orders", "customers", "settings"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 font-oswald text-sm ${
                  activeTab === tab
                    ? "border-b-2 border-[#ffcc00] text-[#1d1d1d]"
                    : "text-[#737373] hover:text-[#1d1d1d]"
                }`}
              >
                {tab.toUpperCase()}
              </button>
            ))}
          </div>

          {/* Products Tab */}
          {activeTab === "products" && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="font-oswald text-xl">Manage Products</h2>
                <button className="bg-[#ffcc00] text-black px-4 py-2 font-bold text-sm hover:bg-yellow-400">
                  + Add Product
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="pb-3 text-sm font-oswald">IMAGE</th>
                      <th className="pb-3 text-sm font-oswald">NAME</th>
                      <th className="pb-3 text-sm font-oswald">PRICE</th>
                      <th className="pb-3 text-sm font-oswald">CATEGORY</th>
                      <th className="pb-3 text-sm font-oswald">STATUS</th>
                      <th className="pb-3 text-sm font-oswald">ACTIONS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((product) => (
                      <tr key={product.id} className="border-b">
                        <td className="py-4">
                          <div className="w-16 h-16 relative bg-gray-100 rounded">
                            <Image src={product.image} alt={product.name} fill className="object-contain p-2" />
                          </div>
                        </td>
                        <td className="py-4 font-medium">{product.name}</td>
                        <td className="py-4">€{product.price.toFixed(2)}</td>
                        <td className="py-4 capitalize">{product.category}</td>
                        <td className="py-4">
                          <span className={`px-2 py-1 text-xs rounded ${
                            product.status === "sale" ? "bg-green-100 text-green-800" :
                            product.status === "sold-out" ? "bg-red-100 text-red-800" :
                            "bg-gray-100 text-gray-800"
                          }`}>
                            {product.status || "active"}
                          </span>
                        </td>
                        <td className="py-4">
                          <button className="text-blue-600 hover:text-blue-800 text-sm mr-3">Edit</button>
                          <button className="text-red-600 hover:text-red-800 text-sm">Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Orders Tab */}
          {activeTab === "orders" && (
            <div className="p-6">
              <h2 className="font-oswald text-xl mb-6">Recent Orders</h2>
              <div className="space-y-4">
                {[
                  { id: "#ORD-001", customer: "John Doe", total: "€89.90", status: "Completed" },
                  { id: "#ORD-002", customer: "Jane Smith", total: "€124.50", status: "Processing" },
                  { id: "#ORD-003", customer: "Mike Johnson", total: "€45.00", status: "Pending" },
                ].map((order) => (
                  <div key={order.id} className="flex justify-between items-center p-4 bg-gray-50 rounded">
                    <div>
                      <p className="font-bold">{order.id}</p>
                      <p className="text-sm text-[#737373]">{order.customer}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">{order.total}</p>
                      <p className="text-sm">{order.status}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Customers Tab */}
          {activeTab === "customers" && (
            <div className="p-6">
              <h2 className="font-oswald text-xl mb-6">Customers</h2>
              <div className="space-y-4">
                {[
                  { name: "John Doe", email: "john@example.com", orders: 5 },
                  { name: "Jane Smith", email: "jane@example.com", orders: 3 },
                  { name: "Mike Johnson", email: "mike@example.com", orders: 8 },
                ].map((customer) => (
                  <div key={customer.email} className="flex justify-between items-center p-4 bg-gray-50 rounded">
                    <div>
                      <p className="font-bold">{customer.name}</p>
                      <p className="text-sm text-[#737373]">{customer.email}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">{customer.orders} orders</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === "settings" && (
            <div className="p-6">
              <h2 className="font-oswald text-xl mb-6">Store Settings</h2>
              <div className="space-y-6 max-w-md">
                <div>
                  <label className="block font-bold text-sm mb-2">Store Name</label>
                  <input type="text" defaultValue="NEED® Supplements" className="w-full border px-4 py-2 rounded" />
                </div>
                <div>
                  <label className="block font-bold text-sm mb-2">Currency</label>
                  <select className="w-full border px-4 py-2 rounded">
                    <option>EUR (€)</option>
                    <option>USD ($)</option>
                    <option>GBP (£)</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-sm mb-2">Shipping Cost</label>
                  <input type="text" defaultValue="€5.99" className="w-full border px-4 py-2 rounded" />
                </div>
                <button className="bg-[#1d1d1d] text-white px-6 py-2 font-bold hover:bg-gray-800">
                  Save Settings
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
