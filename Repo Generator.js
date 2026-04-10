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
