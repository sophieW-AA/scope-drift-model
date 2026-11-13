const fs=require('fs'),zlib=require('zlib'),{JSDOM}=require('jsdom');
const h=fs.readFileSync('process.env.PAGE||'/home/user/page_nodata.html'','utf8');
const html=h.replace(/<script src="https:\/\/cdn[^>]*><\/script>/,'').replace(/<script>window\.__BLOB=[\s\S]*?<\/script>/,'');
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const dom=new JSDOM(html.replace(/<script>[\s\S]*?<\/script>/g,''),{runScripts:'outside-only',pretendToBeVisual:true});
const w=dom.window; w.eval(fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8'));
w.__DATA=JSON.parse(zlib.gunzipSync(fs.readFileSync(process.env.BLOB||'/home/user/sample.gz')).toString());
w.__log=(...a)=>console.log(...a);
let code=scripts.join('\n').replace(/loadData\(\)\.then\([\s\S]*$/,'');
code+=`
DATA=window.__DATA;
const step=(n,f)=>{try{f();__log('OK',n);}catch(e){__log('FAIL',n,'->',String(e.stack).split('\\n').slice(0,3).join(' | '));}};
const q=s=>document.querySelector(s), qa=s=>document.querySelectorAll(s);
step('init',()=>init());
step('open network tab',()=>show('net'));
__log('  macro view back:',q('#back').textContent,'visible',q('#back').style.display!=='none');
step('click back from macro',()=>q('#back').onclick());
__log('  views on:',[...qa('.view.on')].map(v=>v.id).join(','));
step('map click macro 2 then sub-group',()=>{[...qa('#msvg circle.mb')].find(x=>x.__data__.id===2).dispatchEvent(new window.MouseEvent('click',{bubbles:true}));[...qa('#csvg circle')][0].parentNode.dispatchEvent(new window.MouseEvent('click'));});
__log('  sub-group back:',q('#back').textContent);
step('back to macro',()=>q('#back').onclick());
__log('  macro',q('#fmacro').value,'| back:',q('#back').textContent,'| bubbles',qa('#csvg circle').length);
step('back to map',()=>q('#back').onclick());
__log('  views on:',[...qa('.view.on')].map(v=>v.id).join(','),'| map bubbles',qa('#msvg circle.mb').length);
`;
try{w.eval(code);}catch(e){console.log('TOP',e.stack.split('\n').slice(0,3).join(' | '));}
