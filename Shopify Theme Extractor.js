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
