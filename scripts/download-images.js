const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const images = [
  { url: 'https://needsupps.site/cdn/shop/files/logo_NEED_white_20180621_0c910b62-0758-4dd1-92b1-47cd54b83933.png?v=1613685133&width=300', filename: 'logo.png' },
  { url: 'https://needsupps.site/cdn/shop/files/slider_web_NEED_bcaasglutamine_1920x550_20210112.jpg?v=1613717349&width=1920', filename: 'hero-slider.jpg' },
  { url: 'https://needsupps.site/cdn/shop/files/menu_NEED_masonry_PROTEIN_20210112_7a980109-3dc9-493c-a775-b3eed35c4106.jpg?v=1613717361&width=800', filename: 'category-proteins.jpg' },
  { url: 'https://needsupps.site/cdn/shop/files/categoria_pretraining_sustituto.jpg?v=1657178996&width=800', filename: 'category-pretraining.jpg' },
  { url: 'https://needsupps.site/cdn/shop/files/collection_aminoacids_1080x1920_dd35fc46-04cc-44b7-813f-3a3e4fe8923e.jpg?v=1613684961&width=800', filename: 'category-aminoacids.jpg' },
  { url: 'https://needsupps.site/cdn/shop/files/collection_vitaminsminerals_1080x1920_c0be9132-82ba-4815-8220-1a372b5adc5d.jpg?v=1613684961&width=800', filename: 'category-vitamins.jpg' },
  { url: 'https://needsupps.site/cdn/shop/files/collection_weightloss_20200731_1080x1920_6e4e9755-4fc4-4779-a5d8-e44238cd4b15.jpg?v=1613691177&width=800', filename: 'category-weightloss.jpg' },
  { url: 'https://needsupps.site/cdn/shop/files/menu_NEED_masonry_BUILDMUSCLE_20210112.jpg?v=1613717336&width=800', filename: 'category-buildmuscle.jpg' },
  { url: 'https://needsupps.site/cdn/shop/files/flyer_cierre_home_sustituto_20220704.jpg?v=1657179134&width=1920', filename: 'packs-banner.jpg' },
];

const downloadDir = path.join(__dirname, '../public/images');
if (!fs.existsSync(downloadDir)) {
  fs.mkdirSync(downloadDir, { recursive: true });
}

function downloadImage(imageUrl, filename) {
  return new Promise((resolve, reject) => {
    const filePath = path.join(downloadDir, filename);
    const protocol = imageUrl.startsWith('https') ? https : http;
    
    const cleanUrl = imageUrl.split('?')[0];
    
    protocol.get(cleanUrl, (response) => {
      if (response.statusCode === 301 || response.statusCode === 302) {
        return downloadImage(response.headers.location, filename).then(resolve).catch(reject);
      }
      
      if (response.statusCode !== 200) {
        return reject(new Error(`Failed to download ${filename}: ${response.statusCode}`));
      }
      
      const fileStream = fs.createWriteStream(filePath);
      response.pipe(fileStream);
      
      fileStream.on('finish', () => {
        fileStream.close();
        console.log(`Downloaded: ${filename}`);
        resolve();
      });
      
      fileStream.on('error', (err) => {
        fs.unlink(filePath, () => {});
        reject(err);
      });
    }).on('error', reject);
  });
}

async function downloadAll() {
  console.log('Downloading images...');
  
  for (const image of images) {
    try {
      await downloadImage(image.url, image.filename);
    } catch (err) {
      console.error(`Error downloading ${image.filename}:`, err.message);
    }
  }
  
  console.log('Done!');
}

downloadAll();
