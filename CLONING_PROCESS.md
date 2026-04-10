# HD Muscle Clone Process V3

Target Website:

https://hdmuscle.com

---
Scripts to run:

Clone Automation Script:

import { chromium } from "playwright"
import fs from "fs"
import axios from "axios"

const BASE_URL="https://hdmuscle.com"

const visited=new Set()

async function autoScroll(page){

await page.evaluate(async()=>{

await new Promise(resolve=>{

let totalHeight=0
const distance=500

const timer=setInterval(()=>{

const scrollHeight=document.body.scrollHeight

window.scrollBy(0,distance)

totalHeight+=distance

if(totalHeight>=scrollHeight){

clearInterval(timer)
resolve()

}

},200)

})

})

}

async function download(url,file){

try{

const response=await axios({
url,
method:"GET",
responseType:"stream"
})

response.data.pipe(fs.createWriteStream(file))

}catch(e){

console.log("error",url)

}

}

async function extractAssets(page){

const images=await page.$$eval("img",i=>i.map(x=>x.src))
const css=await page.$$eval("link[rel='stylesheet']",c=>c.map(x=>x.href))
const js=await page.$$eval("script[src]",s=>s.map(x=>x.src))
const videos=await page.$$eval("video source",v=>v.map(x=>x.src))

for(const img of images){

if(img.startsWith("http")){

await download(img,"assets/"+img.split("/").pop())

}

}

}

async function crawl(page,url){

if(visited.has(url)) return

visited.add(url)

await page.goto(url,{waitUntil:"networkidle"})

await autoScroll(page)

const html=await page.content()

fs.writeFileSync("pages/"+Date.now()+".html",html)

await extractAssets(page)

const links=await page.$$eval("a",a=>a.map(x=>x.href))

for(const link of links){

if(link.includes(BASE_URL)){

await crawl(page,link)

}

}

}

async function run(){

const browser=await chromium.launch()

const page=await browser.newPage()

await crawl(page,BASE_URL)

await browser.close()

}

run()

Playwright Auto Clone Script:

import { chromium } from "playwright"
import fs from "fs"

const base="https://hdmuscle.com"

async function run(){

const browser=await chromium.launch()

const page=await browser.newPage()

await page.goto(base)

await page.screenshot({
path:"homepage.png",
fullPage:true
})

const links=await page.$$eval("a",a=>a.map(x=>x.href))

for(const link of links){

if(link.includes(base)){

await page.goto(link)

await page.screenshot({
path:`screens/${Date.now()}.png`,
fullPage:true
})

}

}

await browser.close()

}

run()

Repo Generator:

import fs from "fs"

const folders=[

"clone",
"clone/pages",
"clone/components",
"clone/assets",
"clone/assets/images",
"clone/assets/fonts",
"clone/assets/videos"

]

folders.forEach(f=>{
fs.mkdirSync(f,{recursive:true})
})


7. 404 Fix:export default function NotFound(){

return(
<div>
<h1>Page Not Found</h1>
</div>
)

}

Install Required Packages
npm install playwright axios
npm install framer-motion
npm install swiper
npm install gsap
npm install remotion


Shopify Theme Extractor:

import { chromium } from "playwright"
import fs from "fs"

async function run(){

const browser=await chromium.launch()

const page=await browser.newPage()

await page.goto("https://hdmuscle.com")

const theme=await page.evaluate(()=>{

return{

css:[...document.querySelectorAll("link[rel='stylesheet']")]
.map(e=>e.href),

scripts:[...document.querySelectorAll("script[src]")]
.map(e=>e.src),

fonts:[...document.querySelectorAll("link[rel='preload']")]
.map(e=>e.href)

}

})

fs.writeFileSync("theme.json",JSON.stringify(theme,null,2))

await browser.close()

}

run()



# Phase 1

Playwright Crawl

- Visit homepage
- Crawl internal links
- Crawl collections
- Crawl products

---

# Phase 2

Lazy Load Extraction

Auto scroll entire page

Load:

Images  
Videos  
Products  

---

# Phase 3

Asset Extraction

Download:

Images  
Fonts  
Videos  
CSS  
JS  

---

# Phase 4

Animation Extraction

Detect:

Framer Motion  
GSAP  
Swiper  

---

# Phase 5

Shopify Theme Extraction

Extract:

Theme CSS  
Fonts  
Components  

---

# Phase 6

Component Mapping

Header  
Footer  
Hero  
Product Card  
Cart Drawer  

---

# Phase 7

Dynamic Pages

/products  
/collections  
/cart  
/search  

---

# Phase 8

404 Fix

Create fallback page

---

# Phase 9

Repo Generation

Generate:

Pages  
Components  
Assets  

---

# Phase 10

Deploy

Vercel  
Render  
Netlify

---

# Result

Full HD Muscle Clone
