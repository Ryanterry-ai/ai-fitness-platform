/**
 * Asset Generation Pipeline
 * 
 * This module provides prompts and templates for generating website assets.
 * In production, these prompts would be sent to DALL-E/Midjourney/Stable Diffusion.
 * For now, it generates CSS-based visuals and manages existing assets.
 */

export interface AssetPrompt {
  id: string;
  type: 'hero' | 'product' | 'lifestyle' | 'icon' | 'pattern';
  prompt: string;
  style: string;
  dimensions: { width: number; height: number };
  fallback: 'css-gradient' | 'svg' | 'placeholder';
}

export const ASSET_PROMPTS: AssetPrompt[] = [
  {
    id: 'hero-bg',
    type: 'hero',
    prompt: 'Dark gym interior with dramatic yellow spotlight, steel weights, moody atmosphere, sports nutrition aesthetic, cinematic lighting, 8k',
    style: 'photorealistic',
    dimensions: { width: 1920, height: 1080 },
    fallback: 'css-gradient'
  },
  {
    id: 'product-shot',
    type: 'product',
    prompt: 'PURE HEALTH SUPPS PRIME X pre-workout supplement jar, black container with yellow label, dramatic studio lighting, dark background, product photography, 8k',
    style: 'photorealistic',
    dimensions: { width: 800, height: 800 },
    fallback: 'css-gradient'
  },
  {
    id: 'lifestyle-gym',
    type: 'lifestyle',
    prompt: 'Athletic person in gym with yellow supplement shaker, intense workout, dramatic lighting, sports nutrition brand aesthetic, cinematic',
    style: 'photorealistic',
    dimensions: { width: 1200, height: 800 },
    fallback: 'css-gradient'
  },
  {
    id: 'ingredient-bg',
    type: 'pattern',
    prompt: 'Abstract molecular structure pattern, yellow on dark background, scientific, supplement ingredients visualization',
    style: 'abstract',
    dimensions: { width: 1920, height: 1080 },
    fallback: 'css-gradient'
  }
];

// CSS-based fallback visuals
export const CSS_VISUALS = {
  heroGradient: `
    radial-gradient(ellipse at 30% 20%, rgba(255, 215, 0, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 80%, rgba(255, 215, 0, 0.08) 0%, transparent 50%),
    linear-gradient(180deg, #0A0A0B 0%, #1A1A1C 50%, #0A0A0B 100%)
  `,
  productGlow: `
    radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, transparent 70%)
  `,
  cardGradient: `
    linear-gradient(180deg, rgba(26, 26, 28, 0.8) 0%, rgba(10, 10, 11, 0.95) 100%)
  `
};

/**
 * Generate CSS-based visual as fallback when real images aren't available
 */
export function generateCSSVisual(type: 'hero' | 'product' | 'card' | 'glow'): React.CSSProperties {
  switch (type) {
    case 'hero':
      return {
        background: CSS_VISUALS.heroGradient,
      };
    case 'product':
      return {
        background: `#1A1A1C`,
        boxShadow: `0 0 60px rgba(255, 215, 0, 0.2), inset 0 0 60px rgba(255, 215, 0, 0.05)`,
      };
    case 'card':
      return {
        background: CSS_VISUALS.cardGradient,
      };
    case 'glow':
      return {
        background: CSS_VISUALS.productGlow,
      };
    default:
      return {};
  }
}
