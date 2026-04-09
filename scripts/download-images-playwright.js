#!/usr/bin/env node

/**
 * Automated Product Image Downloader using Playwright
 * Bypasses anti-bot protection to download product images from needsupps.site
 * 
 * Usage: node scripts/download-images-playwright.js
 */

const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(process.cwd(), 'public', 'images', 'products');

const products = [
  { id: 1, name: "PURE WHEY", image: "pure-whey.png" },
  { id: 2, name: "DIURE·6", image: "diure6.png" },
  { id: 3, name: "PURE ISO", image: "pure-iso.png" },
  { id: 4, name: "0·CARBS", image: "0carbs.png" },
  { id: 5, name: "POWER CREATINE", image: "power-creatine.png" },
  { id: 6, name: "BCAAS & GLUTAMINE", image: "bcaas-glutamine.png" },
  { id: 7, name: "PURE MASS GAINER", image: "mass-gainer.png" },
  { id: 8, name: "TE5TO S7", image: "testo-s7.png" },
  { id: 9, name: "PROTEIN MAX", image: "protein-max.png" },
  { id: 10, name: "PRE-WORKOUT EXTREME", image: "pre-workout.png" },
  { id: 11, name: "CAFFEINE BOOST", image: "caffeine.png" },
  { id: 12, name: "PUMP ENHANCER", image: "pump.png" },
  { id: 13, name: "L-CARNITINE", image: "l-carnitine.png" },
  { id: 14, name: "FAT BURNER", image: "fat-burner.png" },
  { id: 15, name: "MULTIVITAMIN", image: "multivitamin.png" },
  { id: 16, name: "OMEGA-3", image: "omega3.png" },
  { id: 17, name: "VITAMIN D3", image: "vitamin-d.png" },
];

async function downloadWithPlaywright() {
  console.log('🚀 Starting Playwright-based image download...\n');
  console.log('Bypassing anti-bot protection...\n');
  
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  let downloaded = 0;
  let alreadyExisted = 0;
  let failed = [];

  const { chromium } = require('playwright');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  // First, get all product URLs from collection pages
  console.log('Fetching collection pages to find products...\n');
  const collections = ['proteins', 'pre-training', 'muscle-builder', 'amino-acids', 'vitality-and-health', 'weight-loss'];
  const productUrls = new Map();

  for (const collection of collections) {
    try {
      console.log(`Checking collection: ${collection}...`);
      await page.goto(`https://needsupps.site/collections/${collection}`, { waitUntil: 'networkidle', timeout: 30000 });
      
      const productLinks = await page.$$eval('a[href*="/products/"]', links => 
        links.map(link => ({
          href: link.href,
          text: link.textContent?.trim() || ''
        }))
      );
      
      for (const link of productLinks) {
        const productName = link.text.toUpperCase().replace(/[^A-Z0-9]/g, '').substring(0, 20);
        if (!productUrls.has(productName)) {
          productUrls.set(productName, link.href);
        }
      }
    } catch (e) {
      console.log(`  Collection ${collection}: ${e.message}`);
    }
  }

  console.log(`\nFound ${productUrls.size} product links on site\n`);

  for (const product of products) {
    const outputPath = path.join(OUTPUT_DIR, product.image);
    
    // Check if we already have a real image (>50KB and not duplicate placeholder)
    if (fs.existsSync(outputPath)) {
      const stats = fs.statSync(outputPath);
      const isDuplicate = stats.size === 361751;
      if (stats.size > 50000 && !isDuplicate) {
        console.log(`[${product.id}] ${product.name}: ✓ Already exists (${Math.round(stats.size/1000)}KB)`);
        alreadyExisted++;
        continue;
      }
    }

    console.log(`[${product.id}] ${product.name}...`);
    
    // Build direct product URL based on slug format from the site
    const slug = product.name.toLowerCase()
      .replace(/·/g, '')
      .replace(/&/g, '')
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9-]/g, '');
    
    // Try direct product URL first
    let productUrl = `https://needsupps.site/products/${slug}`;
    
    // Also search in collected URLs for better match
    const productNameKey = product.name.toUpperCase().replace(/[^A-Z0-9]/g, '');
    let bestMatch = null;
    let bestScore = 0;
    
    for (const [key, url] of productUrls) {
      // Exact match
      if (key === productNameKey) {
        bestMatch = url;
        bestScore = 100;
        break;
      }
      // Partial match
      const score = Math.min(
        productNameKey.includes(key) ? key.length : 0,
        key.includes(productNameKey) ? productNameKey.length : 0
      );
      if (score > bestScore) {
        bestScore = score;
        bestMatch = url;
      }
    }
    
    if (bestMatch && bestScore > 5) {
      productUrl = bestMatch;
    }

    try {
      console.log(`  Fetching: ${productUrl}`);
      await page.goto(productUrl, { waitUntil: 'load', timeout: 30000 });
      
      // Multiple selectors for product image
      const imageSelectors = [
        'meta[property="og:image"]',
        '[data-product-image] img',
        '.product-main-image img', 
        '.product-featured-image img',
        '.product-image img',
        '.gallery-image img',
        '.product-gallery img',
        'img[src*="cdn"][src*="products"]',
        'main img',
        '.grid-view-item img',
        '.card-image img'
      ];

      let imageUrl = null;
      for (const selector of imageSelectors) {
        const img = await page.$(selector);
        if (img) {
          const attr = selector.startsWith('meta') ? 'content' : 'src';
          const dataAttr = selector.startsWith('meta') ? 'content' : 'data-src';
          imageUrl = await img.getAttribute(attr) || await img.getAttribute(dataAttr);
          if (imageUrl) break;
        }
      }

      if (imageUrl) {
        let fullUrl = imageUrl;
        if (imageUrl.startsWith('//')) fullUrl = 'https:' + imageUrl;
        if (!imageUrl.startsWith('http')) fullUrl = 'https://needsupps.site' + imageUrl;
        fullUrl = fullUrl.replace(/&width=\d+/, '&width=800').replace(/&height=\d+/, '&height=800');
        
        console.log(`  Downloading: ${fullUrl.substring(0, 60)}...`);
        
        try {
          const response = await page.request.get(fullUrl);
          if (response.ok()) {
            const buffer = await response.body();
            if (buffer.length > 1000) {
              fs.writeFileSync(outputPath, buffer);
              console.log(`  ✓ Saved: ${product.image} (${Math.round(buffer.length/1000)}KB)`);
              downloaded++;
            } else {
              console.log(`  ✗ Image too small`);
              failed.push(product.name);
            }
          } else {
            console.log(`  ✗ HTTP ${response.status()}`);
            failed.push(product.name);
          }
        } catch (downloadError) {
          console.log(`  ✗ Download error: ${downloadError.message}`);
          failed.push(product.name);
        }
      } else {
        console.log(`  ✗ No image found on page`);
        failed.push(product.name);
      }
    } catch (e) {
      console.log(`  ✗ Error: ${e.message}`);
      failed.push(product.name);
    }
  }

  await browser.close();

  console.log('\n📊 Summary:');
  console.log(`  ✓ Downloaded: ${downloaded}`);
  console.log(`  ✓ Already existed: ${alreadyExisted}`);
  console.log(`  ✗ Failed: ${failed.length}`);
  
  if (failed.length > 0) {
    console.log('\nFailed products:');
    failed.forEach(p => console.log(`  - ${p}`));
  }
  
  console.log('\n✅ Done!');
}

downloadWithPlaywright().catch(console.error);