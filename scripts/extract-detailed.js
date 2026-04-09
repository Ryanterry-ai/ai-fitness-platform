const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  
  console.log('Loading page...');
  await page.goto('https://needsupps.site/', { waitUntil: 'networkidle', timeout: 60000 });
  
  // Take screenshot
  await page.screenshot({ path: 'docs/design-references/homepage-desktop.png', fullPage: true });
  console.log('Screenshot saved');
  
  // Get all sections with detailed structure
  const sections = await page.evaluate(() => {
    const result = [];
    
    // Top bar
    const topBar = document.querySelector('#shopify-section-header');
    if (topBar) {
      result.push({
        name: 'header',
        id: 'header',
        html: topBar.outerHTML.slice(0, 5000)
      });
    }
    
    // All major sections
    document.querySelectorAll('section[id*="shopify-section"]').forEach((section, i) => {
      if (section.id) {
        result.push({
          name: section.id.replace('shopify-section-', '').slice(0, 30),
          id: section.id,
          html: section.outerHTML.slice(0, 8000)
        });
      }
    });
    
    return result;
  });
  
  fs.writeFileSync('docs/research/sections.json', JSON.stringify(sections.map(s => ({ name: s.name, id: s.id })), null, 2));
  console.log(`Found ${sections.length} sections`);
  
  // Get nav links
  const navLinks = await page.evaluate(() => {
    return [...document.querySelectorAll('nav a, .nav a, header a')].map(a => ({
      href: a.href,
      text: a.textContent?.trim().slice(0, 30)
    })).filter(a => a.href);
  });
  
  fs.writeFileSync('docs/research/nav-links.json', JSON.stringify(navLinks, null, 2));
  console.log(`Found ${navLinks.length} nav links`);
  
  // Get product cards
  const products = await page.evaluate(() => {
    return [...document.querySelectorAll('.product-card, [class*="product"] a[href*="/products/"]')].slice(0, 20).map((el, i) => {
      const link = el.closest('a') || el;
      const img = el.querySelector('img') || el.closest('[class*="card"]')?.querySelector('img');
      const title = el.querySelector('[class*="title"], h3, h4')?.textContent?.trim();
      const price = el.querySelector('[class*="price"]')?.textContent?.trim();
      
      return {
        href: link?.href,
        title: title || `Product ${i + 1}`,
        price: price,
        image: img?.src
      };
    }).filter(p => p.href);
  });
  
  fs.writeFileSync('docs/research/products.json', JSON.stringify(products, null, 2));
  console.log(`Found ${products.length} products`);
  
  // Get all text content for reference
  const allText = await page.evaluate(() => {
    const headings = [...document.querySelectorAll('h1, h2, h3')].map(h => h.textContent?.trim()).filter(Boolean);
    const paragraphs = [...document.querySelectorAll('p')].map(p => p.textContent?.trim()).filter(t => t.length > 10).slice(0, 30);
    return { headings, paragraphs };
  });
  
  fs.writeFileSync('docs/research/text-content.json', JSON.stringify(allText, null, 2));
  
  console.log('Extraction complete!');
  await browser.close();
})();
