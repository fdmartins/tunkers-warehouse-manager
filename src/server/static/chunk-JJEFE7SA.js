import{a as m}from"./chunk-ANSMRTUX.js";import{Ja as p,R as s,Tb as a,X as t}from"./chunk-6VFV3J45.js";var r=class e{http=t(a);constructor(){}bufferList(){return this.http.get(`${m.REST}/buffers/list`)}static \u0275fac=function(i){return new(i||e)};static \u0275prov=s({token:e,factory:e.\u0275fac,providedIn:"root"})};var u=class e{menuService=t(r);static TODOS=["ADMIN","OPERADOR","ANONYMOUS"];static USER=["ADMIN","OPERADOR"];MENUS=[{icon:"visao_geral.png",label:"Vis\xE3o Geral",path:"/",permissions:e.TODOS},{icon:"buffers.png",label:"Buffers",path:"/buffers",permissions:e.TODOS},{icon:"botoeira.png",label:"Botoeiras",path:"/botoeiras",permissions:e.TODOS,submenus:[{label:"Chamados",path:"/calls",permissions:e.TODOS},{label:"Comunica\xE7\xE3o",path:"/communications",permissions:e.TODOS}]},{icon:"historico.png",label:"Hist\xF3rico",path:"/histories",permissions:e.TODOS},{icon:"usuarios.png",label:"Usu\xE1rios",path:"/users",permissions:e.USER}];menus=p(this.MENUS);constructor(){setTimeout(()=>this.menuService.bufferList().subscribe(this.loadBufferSubmenus.bind(this)),100)}loadBufferSubmenus(o){[...this.MENUS].map(i=>(i.label==="Buffers"&&(i.submenus=o.map(n=>({label:n.description,permissions:e.TODOS,path:`${n.description.replace(" ","-")}/${n.row_id}`}))),i))}recreate(){this.menus.set([]),setTimeout(()=>this.menus.set([...this.MENUS]),2)}static \u0275fac=function(i){return new(i||e)};static \u0275prov=s({token:e,factory:e.\u0275fac,providedIn:"root"})};export{u as a};