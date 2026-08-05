'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Phone, MapPin, Send, MessageSquare, Truck, Building, Headphones, Clock, ArrowRight } from 'lucide-react';

const EASE = [0.23, 1, 0.32, 1] as const;

const contactMethods = [
  { icon: Phone, label: 'Phone', value: '+91-9557513017', href: 'tel:+919557513017' },
  { icon: Mail, label: 'Email', value: 'puresupps.site@gmail.com', href: 'mailto:puresupps.site@gmail.com' },
  { icon: MapPin, label: 'Location', value: 'India', href: '#' },
  { icon: Clock, label: 'Response Time', value: 'Within 24 hours', href: '#' },
];

const departments = [
  { icon: Headphones, title: 'Customer Support', desc: 'Order issues, product questions, returns', email: 'puresupps.site@gmail.com' },
  { icon: Building, title: 'Dealer Enquiry', desc: 'Wholesale and distribution partnerships', email: 'dealers@puresupps.site' },
  { icon: Truck, title: 'Wholesale', desc: 'Bulk orders and gym partnerships', email: 'wholesale@puresupps.site' },
  { icon: MessageSquare, title: 'General', desc: 'Brand collaborations, media, other', email: 'hello@puresupps.site' },
];

export default function ContactPage() {
  const [formData, setFormData] = useState({ name: '', email: '', subject: 'support', message: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <div className="bg-pure-black min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: EASE }}
        >
          <h1 className="text-5xl sm:text-6xl font-black uppercase tracking-tighter">
            GET IN <span className="text-pure-yellow">TOUCH</span>
          </h1>
          <p className="text-pure-gray mt-4 max-w-xl">
            Questions about PRIME X? Need wholesale pricing? We are here to help.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-12">
          {/* Left: Contact Methods + Departments */}
          <motion.div
            className="space-y-8"
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.1, ease: EASE }}
          >
            {/* Contact Methods */}
            <div className="space-y-4">
              {contactMethods.map((m, i) => (
                <a
                  key={i}
                  href={m.href}
                  className="flex items-center gap-4 glass rounded-xl p-4 hover:bg-pure-yellow/5 transition-colors group"
                >
                  <div className="w-10 h-10 rounded-lg bg-pure-yellow/10 flex items-center justify-center group-hover:bg-pure-yellow/20 transition-colors">
                    <m.icon className="w-5 h-5 text-pure-yellow" />
                  </div>
                  <div>
                    <div className="text-xs text-pure-gray uppercase tracking-wider">{m.label}</div>
                    <div className="text-sm font-bold text-white">{m.value}</div>
                  </div>
                </a>
              ))}
            </div>

            {/* Departments */}
            <div>
              <h3 className="text-lg font-black uppercase tracking-tight mb-4">Departments</h3>
              <div className="space-y-3">
                {departments.map((d, i) => (
                  <div key={i} className="glass rounded-xl p-4">
                    <div className="flex items-center gap-3 mb-2">
                      <d.icon className="w-4 h-4 text-pure-yellow" />
                      <span className="text-sm font-bold text-white">{d.title}</span>
                    </div>
                    <p className="text-xs text-pure-gray mb-2">{d.desc}</p>
                    <a href={`mailto:${d.email}`} className="text-xs text-pure-yellow hover:underline">{d.email}</a>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Right: Contact Form */}
          <motion.div
            className="lg:col-span-2"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.2, ease: EASE }}
          >
            <div className="glass rounded-3xl p-8 md:p-12">
              <h3 className="text-2xl font-black uppercase tracking-tight mb-8">Send a Message</h3>

              {submitted ? (
                <motion.div
                  className="text-center py-16"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <div className="w-16 h-16 rounded-full bg-pure-yellow/10 flex items-center justify-center mx-auto mb-4">
                    <Send className="w-8 h-8 text-pure-yellow" />
                  </div>
                  <h4 className="text-xl font-black uppercase">Message Sent!</h4>
                  <p className="text-pure-gray mt-2">We will get back to you within 24 hours.</p>
                </motion.div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid sm:grid-cols-2 gap-6">
                    <div>
                      <label className="text-xs font-bold uppercase tracking-wider text-pure-gray mb-2 block">Name</label>
                      <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-4 py-3 rounded-xl bg-pure-dark border border-white/10 text-white text-sm placeholder:text-pure-gray focus:outline-none focus:border-pure-yellow/50 transition-colors"
                        placeholder="Your name"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-bold uppercase tracking-wider text-pure-gray mb-2 block">Email</label>
                      <input
                        type="email"
                        required
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="w-full px-4 py-3 rounded-xl bg-pure-dark border border-white/10 text-white text-sm placeholder:text-pure-gray focus:outline-none focus:border-pure-yellow/50 transition-colors"
                        placeholder="your@email.com"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-pure-gray mb-2 block">Department</label>
                    <select
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                      className="w-full px-4 py-3 rounded-xl bg-pure-dark border border-white/10 text-white text-sm focus:outline-none focus:border-pure-yellow/50 transition-colors"
                    >
                      <option value="support">Customer Support</option>
                      <option value="dealer">Dealer Enquiry</option>
                      <option value="wholesale">Wholesale</option>
                      <option value="general">General</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-pure-gray mb-2 block">Message</label>
                    <textarea
                      required
                      rows={6}
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      className="w-full px-4 py-3 rounded-xl bg-pure-dark border border-white/10 text-white text-sm placeholder:text-pure-gray focus:outline-none focus:border-pure-yellow/50 transition-colors resize-none"
                      placeholder="How can we help?"
                    />
                  </div>

                  <button type="submit" className="btn-pure w-full sm:w-auto">
                    <Send className="w-4 h-4" /> Send Message
                  </button>
                </form>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
