import{j as o}from"./index-C6QJM7ci.js";import{r as e}from"./vendor-BAY2eazm.js";import{A as n}from"./store-CPOsEtma.js";import{h as a,j as c}from"./createLucideIcon-DbznKt96.js";import"./store-DJqLCMKv.js";/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const l=a("ChevronUp",[["path",{d:"m18 15-6-6-6 6",key:"153udz"}]]);function h(){const[r,i]=e.useState(!1);e.useEffect(()=>{const t=()=>{i(window.scrollY>400)};return window.addEventListener("scroll",t,{passive:!0}),()=>window.removeEventListener("scroll",t)},[]);const s=()=>{window.scrollTo({top:0,behavior:"smooth"})};return o.jsx(n,{children:r&&o.jsx(c.button,{className:"back-to-top",onClick:s,initial:{opacity:0,y:20},animate:{opacity:1,y:0},exit:{opacity:0,y:20},transition:{duration:.3},"aria-label":"Back to top",children:o.jsx(l,{})})})}export{h as default};
