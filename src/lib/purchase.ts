/**
 * Centralized Purchase Handler
 * 
 * All purchase CTAs redirect to official distribution partner:
 * Upgraded Health Supplement Store (https://www.upgraded.co.in)
 * 
 * This utility ensures:
 * - Single source of truth for purchase URLs
 * - Future flexibility to switch to native checkout
 * - Consistent redirect experience with loading state
 */

const OFFICIAL_STORE_URL = 'https://www.upgraded.co.in';

// Product-specific URLs (update when available)
const PRODUCT_URLS: Record<string, string> = {
  'prime-x-orange': OFFICIAL_STORE_URL,
  'prime-x-fruit-punch': OFFICIAL_STORE_URL,
  'prime-x-rocket-lollipop': OFFICIAL_STORE_URL,
  'shaker': OFFICIAL_STORE_URL,
  // Default fallback
  'default': OFFICIAL_STORE_URL,
};

/**
 * Redirect to official purchase destination
 * @param productSlug - Product identifier (e.g., 'prime-x-orange')
 * @param options - Configuration options
 */
export async function purchaseProduct(
  productSlug: string = 'default',
  options: {
    showLoading?: boolean;
    loadingMessage?: string;
    newTab?: boolean;
  } = {}
): Promise<void> {
  const {
    showLoading = true,
    loadingMessage = 'Redirecting to our Official PAN India Distribution Partner...',
    newTab = true,
  } = options;

  // Get product URL (fallback to main store)
  const productUrl = PRODUCT_URLS[productSlug] || PRODUCT_URLS['default'];

  // Show loading state if enabled
  if (showLoading) {
    showRedirectLoading(loadingMessage);
  }

  // Small delay for UX (200-400ms as per brief)
  await new Promise(resolve => setTimeout(resolve, 300));

  // Redirect
  if (newTab) {
    window.open(productUrl, '_blank', 'noopener,noreferrer');
  } else {
    window.location.href = productUrl;
  }

  // Hide loading after redirect
  if (showLoading) {
    setTimeout(hideRedirectLoading, 500);
  }
}

/**
 * Show redirect loading overlay
 */
function showRedirectLoading(message: string): void {
  // Remove existing overlay if any
  hideRedirectLoading();

  const overlay = document.createElement('div');
  overlay.id = 'redirect-loading-overlay';
  overlay.innerHTML = `
    <div style="
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      animation: fadeIn 0.2s ease;
    ">
      <div style="
        width: 40px;
        height: 40px;
        border: 3px solid rgba(255, 209, 0, 0.2);
        border-top-color: #FFD100;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin-bottom: 16px;
      "></div>
      <p style="
        color: #fff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 14px;
        text-align: center;
        max-width: 280px;
        line-height: 1.5;
      ">${message}</p>
    </div>
  `;

  // Add keyframes if not already present
  if (!document.getElementById('redirect-loading-styles')) {
    const style = document.createElement('style');
    style.id = 'redirect-loading-styles';
    style.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);
  }

  document.body.appendChild(overlay);
}

/**
 * Hide redirect loading overlay
 */
function hideRedirectLoading(): void {
  const overlay = document.getElementById('redirect-loading-overlay');
  if (overlay) {
    overlay.style.animation = 'fadeIn 0.2s ease reverse';
    setTimeout(() => overlay.remove(), 200);
  }
}

/**
 * Get purchase URL for a product (for analytics or pre-fetching)
 */
export function getPurchaseUrl(productSlug: string = 'default'): string {
  return PRODUCT_URLS[productSlug] || PRODUCT_URLS['default'];
}

/**
 * Check if direct checkout is enabled (future feature)
 */
export function isDirectCheckoutEnabled(): boolean {
  // Currently false - all purchases go to Upgraded Health
  // Set to true when native checkout is ready
  return false;
}

export default {
  purchaseProduct,
  getPurchaseUrl,
  isDirectCheckoutEnabled,
  OFFICIAL_STORE_URL,
};