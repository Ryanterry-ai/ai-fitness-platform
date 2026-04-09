const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  
  await page.goto('https://needsupps.site/', { waitUntil: 'networkidle' });
  
  // Get page content
  const html = await page.content();
  console.log('HTML length:', html.length);
  
  // Get all images
  const images = await page.evaluate(() => {
    const imgs = [...document.querySelectorAll('img')].map(img => ({
      src: img.src || img.currentSrc,
      alt: img.alt,
      width: img.naturalWidth,
      height: img.naturalHeight
    }));
    return imgs;
  });
  
  console.log('Images found:', images.length);
  console.log(JSON.stringify(images.slice(0, 10), null, 2));
  
  await browser.close();
})();
