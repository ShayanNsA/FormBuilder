const API_BASE="";
const API={
 async request(path,opt){
  opt=opt||{};const h=Object.assign({},opt.headers||{}),t=localStorage.getItem("fb_token");if(t)h.Authorization="Token "+t;if(opt.body&&!(opt.body instanceof FormData))h["Content-Type"]="application/json";
  const r=await fetch(API_BASE+path,Object.assign({},opt,{headers:h}));let d=null;try{d=await r.json()}catch(e){}
  if(!r.ok){const m=d&&(d.error||d.detail||Object.values(d).flat().join(" "));throw new Error(m||"درخواست با خطا مواجه شد")}return d;
 },get(p){return this.request(p)},post(p,b){return this.request(p,{method:"POST",body:JSON.stringify(b)})},patch(p,b){return this.request(p,{method:"PATCH",body:JSON.stringify(b)})},delete(p){return this.request(p,{method:"DELETE"})}
};