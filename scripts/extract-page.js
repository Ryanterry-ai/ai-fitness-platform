const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  
  console.log('Loading page...');
  await page.goto('https://needsupps.site/', { waitUntil: 'networkidle', timeout: 60000 });
  
  // 1. Get HTML content
  const html = await page.content();
  fs.writeFileSync('docs/research/original-page.html', html);
  console.log('Saved: docs/research/original-page.html');
  
  // 2. Get computed styles for key elements
  const globalStyles = await page.evaluate(() => {
    const getStyle = (selector) => {
      const el = document.querySelector(selector);
      if (!el) return null;
      const cs = getComputedStyle(el);
      return {
        fontFamily: cs.fontFamily,
        fontSize: cs.fontSize,
        fontWeight: cs.fontWeight,
        color: cs.color,
        backgroundColor: cs.backgroundColor,
        backgroundImage: cs.backgroundImage,
      };
    };
    
    return {
      body: getStyle('body'),
      h1: getStyle('h1'),
      h2: getStyle('h2'),
      h3: getStyle('h3'),
      p: getStyle('p'),
      a: getStyle('a'),
      button: getStyle('button'),
    };
  });
  
  fs.writeFileSync('docs/research/global-styles.json', JSON.stringify(globalStyles, null, 2));
  console.log('Saved: docs/research/global-styles.json');
  
  // 3. Get all images with full details
  const images = await page.evaluate(() => {
    return [...document.querySelectorAll('img')].map(img => ({
      src: img.src,
      alt: img.alt,
      width: img.naturalWidth,
      height: img.naturalHeight,
      className: img.className,
      parentTag: img.parentElement?.tagName,
      parentClass: img.parentElement?.className
    }));
  });
  
  fs.writeFileSync('docs/research/images.json', JSON.stringify(images, null, 2));
  console.log(`Found ${images.length} images`);
  
  // 4. Get all links
  const links = await page.evaluate(() => {
    return [...document.querySelectorAll('a')].map(a => ({
      href: a.href,
      text: a.textContent?.trim().slice(0, 50),
      className: a.className
    })).filter(l => l.href);
  });
  
  fs.writeFileSync('docs/research/links.json', JSON.stringify(links, null, 2));
  console.log(`Found ${links.length} links`);
  
  // 5. Get page structure
  const structure = await page.evaluate(() => {
    const sections = [];
    document.querySelectorAll('section, header, footer, nav, main').forEach(el => {
      if (el.id || el.className) {
        sections.push({
          tag: el.tagName.toLowerCase(),
          id: el.id,
          className: el.className.slice(0, 50),
          childCount: el.children.length
        });
      }
    });
    return sections;
  });
  
  fs.writeFileSync('docs/research/structure.json', JSON.stringify(structure, null, 2));
  console.log(`Found ${structure.length} sections`);
  
  // 6. Get colors from page
  const colors = await page.evaluate(() => {
    const allColors = new Set();
    const allBgColors = new Set();
    
    document.querySelectorAll('*').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.color && cs.color !== 'rgba(0, 0, 0, 0)') allColors.add(cs.color);
      if (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'rgba(255, 255, 255, 0)') allBgColors.add(cs.backgroundColor);
    });
    
    return {
      textColors: [...allColors].slice(0, 20),
      bgColors: [...allBgColors].slice(0, 20)
    };
  });
  
  fs.writeFileSync('docs/research/colors.json', JSON.stringify(colors, null, 2));
  console.log('Saved: docs/research/colors.json');
  
  console.log('\\nExtraction complete!');
  await browser.close();
})();
