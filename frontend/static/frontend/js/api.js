const API_BASE = window.location.origin;
const API = {
  token:()=>localStorage.getItem("fb_token"),
  headers(extra={}){const h={"Content-Type":"application/json",...extra};const t=this.token();if(t)h.Authorization="Token "+t;return h},
  async request(path,options={}){const res=await fetch(API_BASE+path,{...options,headers:this.headers(options.headers||{})});let data=null;try{data=await res.json()}catch{}if(!res.ok){const e=new Error(data?.error||data?.detail||"درخواست با خطا مواجه شد");e.status=res.status;e.data=data;throw e}return data},
  get(path){return this.request(path)},
  post(path,body){return this.request(path,{method:"POST",body:JSON.stringify(body)})},
  put(path,body){return this.request(path,{method:"PUT",body:JSON.stringify(body)})},
  patch(path,body){return this.request(path,{method:"PATCH",body:JSON.stringify(body)})},
  del(path){return this.request(path,{method:"DELETE"})}
};