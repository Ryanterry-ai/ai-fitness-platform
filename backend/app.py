<!DOCTYPE html>
<html>

<head>

<title>AI Fitness Platform</title>

<script src="https://cdn.tailwindcss.com"></script>

</head>

<body class="bg-slate-900 text-white">

<div class="max-w-6xl mx-auto mt-10">

<h1 class="text-3xl font-bold mb-6">
AI Fitness Platform
</h1>

<!-- User -->

<div id="user" class="mb-6"></div>

<!-- Search -->

<div class="bg-slate-800 p-4 rounded">

<input
id="searchInput"
class="w-full p-3 text-black rounded"
placeholder="Search supplements, fitness, diet..."
>

<button
onclick="search()"
class="bg-blue-600 px-4 py-2 mt-3 rounded"
>
Search
</button>

</div>

<!-- Premium -->

<div id="premium" class="mt-4"></div>

<!-- Recommendations -->

<div id="recommendations" class="mt-6"></div>

<!-- Saved -->

<div id="saved" class="mt-6"></div>

<!-- Results -->

<div id="results" class="mt-6"></div>

</div>


<script>

async function search(){

const query=document.getElementById("searchInput").value;

document.getElementById("results").innerHTML="Searching...";

const res=await fetch("/search",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
query
})

});

const data=await res.json();

renderResults(data.results);

renderRecommendations(data.recommendations);

}


function renderResults(results){

document.getElementById("results").innerHTML=

results.map(r=>`

<div class="bg-slate-800 p-4 rounded mb-3">

<h3 class="font-bold">${r.title}</h3>

<p>${r.summary}</p>

<a href="${r.link}" target="_blank"
class="text-blue-400">

Source

</a>

<button
onclick="save('${r.title}')"
class="ml-3 bg-green-600 px-2 py-1 rounded"
>

Save

</button>

</div>

`).join("")

}


function renderRecommendations(recs){

document.getElementById("recommendations").innerHTML=

`<h2 class="font-bold mb-2">Recommended</h2>

${recs.map(r=>`

<div
onclick="recommend('${r.title}')"
class="cursor-pointer text-green-400"
>

${r.title}

</div>

`).join("")}

`;

}


function recommend(q){

document.getElementById("searchInput").value=q;

search();

}


async function save(name){

await fetch("/save",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
name,
type:"search"
})

});

alert("Saved");

}


async function loadSaved(){

const res=await fetch("/saved");

const data=await res.json();

document.getElementById("saved").innerHTML=

`<h2 class="font-bold">Saved</h2>

${data.map(i=>`

<div>${i.item_name}</div>

`).join("")}

`;

}


async function checkPremium(){

const res=await fetch("/tier");

const data=await res.json();

if(data.tier=="free"){

document.getElementById("premium").innerHTML=

`<div class="bg-yellow-600 p-3 rounded">

Upgrade to Premium

<button
onclick="upgrade()"
class="ml-3 bg-black px-3 py-1 rounded"
>

Upgrade

</button>

</div>`

}

}


async function upgrade(){

await fetch("/upgrade",{method:"POST"});

location.reload();

}


loadSaved();
checkPremium();

</script>

</body>

</html>
