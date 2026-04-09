const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const productImages = [
  { url: 'https://needsupps.site/cdn/shop/products/0011_NEED-PROTEINAS-03_0005_PROTEINA-NEED-PB_J.png?v=1611753267&width=635', filename: 'pure-whey.png' },
  { url: 'https://needsupps.site/cdn/shop/products/master-botes-AGOSTO_0000_NEED-DIURE6.png?v=1611753180&width=635', filename: 'diure6.png' },
  { url: 'https://needsupps.site/cdn/shop/products/web_product_NEED_pureISO_5lbs_brownie_540x680_7d9117e0-70c9-46a7-9110-eba0576de0d5.png?v=1617120345&width=540', filename: 'pure-iso.png' },
  { url: 'https://needsupps.site/cdn/shop/products/master-botes-AGOSTO_0001_NEED-0CARB.png?v=1611753122&width=635', filename: '0carbs.png' },
  { url: 'https://needsupps.site/cdn/shop/products/web_product_NEED_PowerCreatine_coollemonlime_540x680_c699404d-fd1a-4511-a6a6-2a03bfbe8899.png?v=1615824039&width=540', filename: 'power-creatine.png' },
  { url: 'https://needsupps.site/cdn/shop/products/master-botes-AGOSTO_0006_NEED-BCAA-NEED-AGOSTO-MASTER-WATERMELON.png?v=1611753164&width=635', filename: 'bcaas-glutamine.png' },
  { url: 'https://needsupps.site/cdn/shop/products/web_product_NEED_PureMassGainer_1front_540x680_2014454d-c6cf-4e2b-b4cc-8cb37d0f4389.png?v=1611753244&width=540', filename: 'mass-gainer.png' },
  { url: 'https://needsupps.site/cdn/shop/products/web_product_NEED_TestoS7_540x680_64590b35-3d21-4abe-a478-0d6174ea91ba.png?v=1611753295&width=540', filename: 'testo-s7.png' },
  { url: 'https://needsupps.site/cdn/shop/products/web_product_NEED_proteinM4X_5lbs_brownie_540x680_039f69b5-eabd-41ab-9f5d-3646ca085d1d.png?v=1617104729&width=540', filename: 'protein-max.png' },
];

const downloadDir = path.join(__dirname, '../public/images/products');
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
  console.log('Downloading product images...');
  
  for (const image of productImages) {
    try {
      await downloadImage(image.url, image.filename);
    } catch (err) {
      console.error(`Error downloading ${image.filename}:`, err.message);
    }
  }
  
  console.log('Done!');
}

downloadAll();
