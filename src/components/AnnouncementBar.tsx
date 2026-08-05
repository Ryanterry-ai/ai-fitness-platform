'use client';

import React, { useState } from 'react';
import { X, ExternalLink } from 'lucide-react';

const PARTNER_URL = 'https://www.upgraded.co.in';

export default function AnnouncementBar() {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div className="bg-[#FFD100] text-black relative z-[60]">
      <div className="max-w-[1200px] mx-auto px-4">
        <div className="flex items-center justify-between h-9">
          <div className="flex-1 text-center">
            <span className="text-[11px] font-bold tracking-wide">
              FREE SHIPPING ON ALL ORDERS ABOVE ₹999
            </span>
          </div>
          <a
            href={PARTNER_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center gap-1 text-[10px] font-black uppercase tracking-wider hover:opacity-80 transition-opacity"
          >
            Shop Now <ExternalLink className="w-3 h-3" />
          </a>
          <button
            onClick={() => setIsVisible(false)}
            className="p-1 hover:bg-black/10 rounded transition-colors ml-2"
            aria-label="Close"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export { PARTNER_URL };
