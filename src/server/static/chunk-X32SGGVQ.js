import{a as v}from"./chunk-YMG7CMKX.js";import"./chunk-JJEFE7SA.js";import{a as P,b as _,c as N,d as T,e as D,f as C,g as O,h as G,i as j,m as A}from"./chunk-SH6EOPS2.js";import"./chunk-ODSXTPVL.js";import"./chunk-4IFBPCWC.js";import{d as M,e as k}from"./chunk-JLEYIN34.js";import"./chunk-ANSMRTUX.js";import{$a as s,Ba as o,Bb as F,D as S,Db as E,Oa as u,Sa as c,Ta as g,Va as f,X as p,Z as b,Za as t,_a as n,cb as h,db as x,ib as r,kb as y,lb as w,mb as L}from"./chunk-6VFV3J45.js";import"./chunk-2VMXMS7J.js";function V(i,m){if(i&1&&(t(0,"div",3),r(1),n()),i&2){let l=x();o(),y(" ",l.authState().message," ")}}function q(i,m){i&1&&(t(0,"div",9),s(1,"div",12),t(2,"span"),r(3,"Acessando..."),n()())}function I(i,m){i&1&&(t(0,"span"),r(1,"Acessar"),n())}var R=class i{authStore=p(v);authState=this.authStore.authState;router=p(M);isLoading=F(()=>this.authState().state==="loading");loginForm=new D({username:new C("",[_.required]),password:new C("",[_.required])});constructor(){this.authStore.isLogged()&&this.router.navigateByUrl("/"),E(()=>{this.isLoading()?this.loginForm.disable():this.loginForm.enable()})}onLogin(){this.loginForm.valid&&this.authStore.login(this.loginForm.value).pipe(S(1)).subscribe()}static \u0275fac=function(l){return new(l||i)};static \u0275cmp=b({type:i,selectors:[["app-login"]],standalone:!0,features:[w([v]),L],decls:19,vars:9,consts:[[1,"login-wrapper","bg-black","text-white","gap-3",3,"formGroup"],[1,"login-container"],["height","60","width","80%","src","static/icons/logo.png",1,"align-self-center"],["role","alert",1,"alert","alert-danger","alert-dismissible","fade","show"],[1,"login-form"],[1,"d-flex","flex-column","gap-2"],["type","text","placeholder","usu\xE1rio","formControlName","username",1,"form-control"],["type","password","autocomplete","on","formControlName","password","placeholder","senha",1,"form-control",3,"keyup.enter"],["type","button",1,"btn","btn-secondary","px-5","text-center",3,"click","disabled"],[1,"d-flex","align-items-center","justify-content-center","gap-2"],["routerLink","/",1,"d-flex","justify-content-center","align-items-center","gap-2","text-white-50"],[1,"bi","bi-arrow-return-left"],["role","status",1,"spinner-border","text-light"]],template:function(l,e){if(l&1&&(t(0,"form",0)(1,"div",1),s(2,"img",2),u(3,V,2,1,"div",3),t(4,"div",4)(5,"label",5)(6,"span"),r(7,"Usu\xE1rio"),n(),s(8,"input",6),n(),t(9,"label",5)(10,"span"),r(11,"Senha"),n(),t(12,"input",7),h("keyup.enter",function(){return e.onLogin()}),n()(),t(13,"button",8),h("click",function(){return e.onLogin()}),u(14,q,4,0,"div",9)(15,I,2,0,"span"),n(),t(16,"a",10),s(17,"i",11),r(18," Tela de in\xEDcio "),n()()()()),l&2){let a,d;c("formGroup",e.loginForm),o(3),f(e.authState().message?3:-1),o(5),g("is-invalid",((a=e.loginForm.get("username"))==null?null:a.touched)&&((a=e.loginForm.get("username"))==null?null:a.invalid)),o(4),g("is-invalid",((d=e.loginForm.get("password"))==null?null:d.touched)&&((d=e.loginForm.get("password"))==null?null:d.invalid)),o(),c("disabled",e.loginForm.invalid)("disabled",e.isLoading()),o(),f(e.isLoading()?14:15)}},dependencies:[k,A,O,P,N,T,G,j],styles:["[_nghost-%COMP%]   .login-wrapper[_ngcontent-%COMP%]{display:flex;flex-direction:column;justify-content:center;align-items:center;height:100dvh;width:100dvw}[_nghost-%COMP%]   .login-container[_ngcontent-%COMP%]{display:flex;flex-direction:column;width:300px;gap:1rem}[_nghost-%COMP%]   .login-form[_ngcontent-%COMP%]{display:flex;flex-direction:column;width:100%;gap:1rem}"]})};export{R as LoginComponent};