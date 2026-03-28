
async function login(){
await fetch("/login",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
email:document.getElementById("email").value,
password:document.getElementById("password").value
})})
window.location="dashboard.html"
}

async function register(){
await fetch("/register",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
email:document.getElementById("email").value,
password:document.getElementById("password").value
})})
alert("registered")
}

async function uploadBCA(){
let f=document.getElementById("file").files[0]
let form=new FormData()
form.append("file",f)
await fetch("/upload_bca",{method:"POST",body:form})
alert("uploaded")
}

async function uploadPhysique(){
let files=document.getElementById("files").files
let form=new FormData()
for(let f of files){form.append("files",f)}
await fetch("/upload_physique",{method:"POST",body:form})
alert("uploaded")
}

async function medical(){
let r=await fetch("/medical",{method:"POST"})
let d=await r.json()
document.getElementById("result").innerHTML=JSON.stringify(d)
}

async function cycle(){
let r=await fetch("/cycle",{method:"POST"})
let d=await r.json()
document.getElementById("result").innerHTML=JSON.stringify(d)
}

async function generate(){
let r=await fetch("/diet",{method:"POST"})
let d=await r.json()
document.getElementById("result").innerHTML=JSON.stringify(d)
}

async function grocery(){
let r=await fetch("/grocery",{method:"POST"})
let d=await r.json()
document.getElementById("result").innerHTML=JSON.stringify(d)
}
