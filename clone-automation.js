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
