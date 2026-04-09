#!/usr/bin/env node

/**
 * Automated Product Image Downloader
 * 
 * Downloads product images from needsupps.site by:
 * 1. Fetching each product page
 * 2. Extracting the product image URL
 * 3. Downloading and saving to public/images/products/
 * 
 * Usage: node scripts/download-images-auto.js
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

async function fetchUrl(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
        },
      });
      if (response.ok) {
        return await response.text();
      }
    } catch (e) {
      console.log(`  Retry ${i + 1}/${retries}: ${url}`);
    }
  }
  return null;
}

function extractImageUrl(html) {
  const patterns = [
    /"image":"([^"]+\.png[^"]*)"/,
    /"featured_image":"([^"]+\.png[^"]*)"/,
    /<img[^>]+src="([^"]*cdn[^"]*products[^"]*\.png[^"]*)"/,
    /"src":"([^"]*cdn\.shopify[^"]*products[^"]*\.png[^"]*)"/,
    /url\('([^']*cdn[^']*products[^']*\.png[^']*)'\)/,
  ];

  for (const pattern of patterns) {
    const match = html.match(pattern);
    if (match) {
      let url = match[1].replace(/\\/g, '').replace(/&amp;/g, '&');
      url = url.replace(/&width=\d+/, '&width=800');
      url = url.replace(/&height=\d+/, '&height=800');
      if (url.startsWith('//')) url = 'https:' + url;
      if (!url.startsWith('http')) url = 'https://needsupps.site' + url;
      return url;
    }
  }
  return null;
}

async function downloadImage(url, outputPath) {
  if (fs.existsSync(outputPath)) {
    console.log(`  ✓ Already exists: ${path.basename(outputPath)}`);
    return true;
  }

  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
    });
    
    if (response.ok) {
      const buffer = await response.arrayBuffer();
      fs.writeFileSync(outputPath, Buffer.from(buffer));
      console.log(`  ✓ Downloaded: ${path.basename(outputPath)}`);
      return true;
    }
  } catch (e) {
    console.log(`  ✗ Failed to download`);
  }
  return false;
}

async function main() {
  console.log('🔍 Automated Product Image Downloader\n');
  console.log('Downloading from: https://needsupps.site\n');
  
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  let downloaded = 0;
  let failed = [];
  let skipped = 0;
  let alreadyExisted = 0;

  for (const product of products) {
    const outputPath = path.join(OUTPUT_DIR, product.image);
    
    // Check if we already have a good image (>50KB = likely real image, not placeholder)
    if (fs.existsSync(outputPath)) {
      const stats = fs.statSync(outputPath);
      if (stats.size > 50000) {
        console.log(`[${product.id}] ${product.name}: ✓ Already exists (${Math.round(stats.size/1000)}KB)`);
        alreadyExisted++;
        continue;
      }
    }

    console.log(`[${product.id}] ${product.name}...`);
    
    const productUrl = `https://needsupps.site/products/${product.id}`;
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      
      const response = await fetch(productUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Cache-Control': 'no-cache',
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        console.log(`  ✗ HTTP ${response.status} - using existing`);
        if (fs.existsSync(outputPath)) {
          skipped++;
        } else {
          failed.push(product.name);
        }
        continue;
      }
      
      const html = await response.text();
      const imageUrl = extractImageUrl(html);
      
      if (imageUrl) {
        console.log(`  Found: ${imageUrl.substring(0, 70)}...`);
        const success = await downloadImage(imageUrl, outputPath);
        if (success) {
          downloaded++;
        } else {
          failed.push(product.name);
        }
      } else {
        console.log(`  ✗ Could not extract image URL - using existing`);
        if (fs.existsSync(outputPath)) {
          skipped++;
        } else {
          failed.push(product.name);
        }
      }
    } catch (e) {
      console.log(`  ✗ Error: ${e.message} - using existing`);
      if (fs.existsSync(outputPath)) {
        skipped++;
      } else {
        failed.push(product.name);
      }
    }
  }

  console.log('\n📊 Summary:');
  console.log(`  ✓ Downloaded: ${downloaded}`);
  console.log(`  ✓ Already existed: ${alreadyExisted}`);
  console.log(`  ⊘ Reused: ${skipped}`);
  console.log(`  ✗ Failed: ${failed.length}`);
  
  if (failed.length > 0) {
    console.log('\nFailed products (need manual download):');
    failed.forEach(p => console.log(`  - ${p}`));
    
    console.log('\n💡 To download manually:');
    console.log('  1. Visit https://needsupps.site/products/[id]');
    console.log('  2. Right-click product image → Save As');
    console.log('  3. Save to public/images/products/[product-name].png');
  }
}

main().catch(console.error);