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
