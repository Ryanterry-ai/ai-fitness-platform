const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  
  console.log('Loading original site...');
  await page.goto('https://needsupps.site/', { waitUntil: 'networkidle', timeout: 60000 });
  
  // Get exact colors
  const colors = await page.evaluate(() => {
    const allColors = { text: new Set(), bg: new Set(), border: new Set() };
    
    document.querySelectorAll('*').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.color && cs.color !== 'rgba(0, 0, 0, 0)' && cs.color !== 'rgb(0, 0, 0)') allColors.text.add(cs.color);
      if (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'rgb(255, 255, 255)' && !cs.backgroundColor.includes('transparent')) allColors.bg.add(cs.backgroundColor);
      if (cs.borderColor && cs.borderColor !== 'rgba(0, 0, 0, 0)') allColors.border.add(cs.borderColor);
    });
    
    return {
      text: [...allColors.text].slice(0, 15),
      bg: [...allColors.bg].slice(0, 15),
      border: [...allColors.border].slice(0, 10)
    };
  });
  
  console.log('Text Colors:', JSON.stringify(colors.text));
  console.log('Bg Colors:', JSON.stringify(colors.bg));
  console.log('Border Colors:', JSON.stringify(colors.border));
  
  // Check for animations
  const animations = await page.evaluate(() => {
    const styles = [];
    
    // Check for transitions
    const elementsWithTransition = [...document.querySelectorAll('*')].filter(el => {
      const cs = getComputedStyle(el);
      return cs.transition && cs.transition !== 'none' && cs.transition !== 'all 0s ease 0s';
    }).slice(0, 10).map(el => ({
      tag: el.tagName,
      className: el.className?.slice(0, 30),
      transition: getComputedStyle(el).transition
    }));
    
    // Check for animations
    const elementsWithAnimation = [...document.querySelectorAll('*')].filter(el => {
      const cs = getComputedStyle(el);
      return cs.animation && cs.animation !== 'none';
    }).slice(0, 5).map(el => ({
      tag: el.tagName,
      animation: getComputedStyle(el).animation
    }));
    
    // Check for hover states
    const hoverable = [...document.querySelectorAll('a, button, .product-card, [class*="card"]')].slice(0, 10).map(el => ({
      tag: el.tagName,
      className: el.className?.slice(0, 40),
      cursor: getComputedStyle(el).cursor
    }));
    
    return { elementsWithTransition, elementsWithAnimation, hoverable };
  });
  
  console.log('Transitions:', JSON.stringify(animations.elementsWithTransition, null, 2));
  console.log('Animations:', JSON.stringify(animations.elementsWithAnimation, null, 2));
  console.log('Hoverable:', JSON.stringify(animations.hoverable, null, 2));
  
  await browser.close();
})();
