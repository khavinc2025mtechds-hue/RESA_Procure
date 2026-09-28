const fs=require('fs'),vm=require('vm'),assert=require('assert');
require('./dist/engine.js');
const data=JSON.parse(fs.readFileSync('dist/data/dashboard.json'));
for(const test of data.checks){const got=RESA.evaluate(data,test.scenario).filter(s=>s.status==='Eligible').map(s=>s.id).sort();assert.deepEqual(got,test.eligible.sort());console.log(test.id,'pass');}
let result=RESA.evaluate(data,data.scenarios[0]);console.log(result.map(s=>({id:s.id,status:s.status,score:s.score,coverage:s.coverage})));
assert(result.find(s=>s.id==='DEMO-S03').checks.find(c=>c.key==='delivery').state==='unknown');
assert(result.find(s=>s.id==='DEMO-S04').checks.find(c=>c.key==='quality').state==='unknown');
assert(result.find(s=>s.id==='DEMO-S05').status==='Excluded');
assert(RESA.evaluate(data,{...data.scenarios[0],defect:1.1}).find(s=>s.id==='DEMO-S01').status==='Excluded');
const k=RESA.kpiSummary(data.kpi);assert.equal(k.rows,777);console.log('Public KPI:',k);
assert.equal(data.benchmark.length,149);
const evidenceIds=new Set(data.evidence.map(d=>d.id));
for(const s of result)for(const c of s.checks)if(c.doc)assert(evidenceIds.has(c.doc));
// Exercise every component tree and action callback without a browser.
const src=fs.readFileSync('dist/app.js','utf8').replace(/fetch\('data\/dashboard.json'\)[\s\S]*$/,'');
for(const tab of ['overview','analytics','evidence','datasets','research']){
 let hook=0;
 const FakeReact={Fragment:'fragment',createElement:(type,props,...children)=>({type,props:{...props,children:children.length===1?children[0]:children}}),useState:v=>[hook++===0?tab:v,()=>{}],useEffect:()=>{},useRef:()=>({current:null})};
 const ctx={React:FakeReact,RESA,data,console,Blob,URL,setTimeout,Date,document:{},ReactDOM:{}};vm.createContext(ctx);vm.runInContext(src,ctx);
 const tree=vm.runInContext('App({data})',ctx);let nodes=0;
 function walk(n){if(n==null||n===false||typeof n!=='object')return;if(Array.isArray(n)){n.forEach(walk);return;}nodes++;if(typeof n.type==='function')walk(n.type(n.props));else walk(n.props?.children);}
 walk(tree);assert(nodes>50);console.log('Component tree',tab,nodes,'nodes OK');
}
console.log('Validation passed.');
