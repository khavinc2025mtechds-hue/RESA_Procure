(function(root){
'use strict';
const clamp=(v,a=0,b=100)=>Math.max(a,Math.min(b,v));
const age=(date,asOf)=>Math.floor((new Date(asOf+'T00:00:00Z')-new Date(date+'T00:00:00Z'))/86400000);
function evaluate(data,req){
 const quotes=data.quotes.filter(q=>q.part===req.part);
 const pmax=Math.max(...quotes.map(q=>q.unit_price));const pmin=Math.min(...quotes.map(q=>q.unit_price));
 return data.suppliers.map(s=>{
  const q=quotes.find(q=>q.supplier_id===s.id);
  const history=data.scorecards.filter(c=>c.supplier_id===s.id).sort((a,b)=>a.date.localeCompare(b.date));
  const sc=history.at(-1);const fresh=sc&&age(sc.date,data.asOf)<=120;const valid=q&&q.issued<=data.asOf&&q.valid_until>=data.asOf;
  const check=(key,label,value,pass,doc)=>({key,label,value,state:value===null?'unknown':pass?'satisfied':'violated',doc});
  const checks=[
   check('part','Component',valid?q.part:null,valid&&q.part===req.part,q?.id),
   check('delivery',`Delivery ≤ ${req.days} days`,valid&&q.lead_days!=null?q.lead_days:null,valid&&q.lead_days!=null&&q.lead_days<=req.days,q?.id),
   check('quality',`Defect rate < ${req.defect}%`,fresh?sc.defect_rate:null,fresh&&sc.defect_rate<req.defect,sc?.id),
   check('capacity',`Capacity ≥ ${req.quantity}`,valid?q.capacity:null,valid&&q.capacity>=req.quantity,q?.id)
  ];
  const unknown=checks.filter(c=>c.state==='unknown').length;const violated=checks.some(c=>c.state==='violated');
  const status=violated?'Excluded':unknown?'Needs review':'Eligible';
  const coverage=(4-unknown)/4*100;
  // Risk uses available recent monthly history with recency weights (1,2,3).
  const recent=history.filter(c=>age(c.date,data.asOf)<=120);
  const denom=recent.reduce((a,c,i)=>a+i+1,0);
  const risk=denom?recent.reduce((a,c,i)=>a+(i+1)*(clamp(100-c.on_time_delivery)*.65+clamp(c.defect_rate*10)*.35),0)/denom:null;
  const quality=fresh?clamp(100-sc.defect_rate*10):0;
  const price=q?(pmax===pmin?100:100*(pmax-q.unit_price)/(pmax-pmin)):0;
  const delivery=valid&&q.lead_days!=null?clamp(100*(20-q.lead_days)/20):0;
  const reliability=fresh?sc.on_time_delivery:0;
  const parts={quality:quality*.25,price:price*.20,delivery:delivery*.20,reliability:reliability*.20,evidence:coverage*.15,riskPenalty:(risk??100)*.15};
  const score=status==='Eligible'?Math.round(clamp(parts.quality+parts.price+parts.delivery+parts.reliability+parts.evidence-parts.riskPenalty)*10)/10:null;
  return {...s,q,sc,history,fresh,checks,status,coverage,risk,score,parts};
 }).sort((a,b)=>({Eligible:0,'Needs review':1,Excluded:2}[a.status]-{Eligible:0,'Needs review':1,Excluded:2}[b.status])||((b.score??-1)-(a.score??-1))||a.id.localeCompare(b.id));
}
function kpiSummary(rows){
 const num=v=>v!==''&&v!=null&&Number.isFinite(Number(v))?Number(v):null;
 const delivered=rows.filter(r=>r.Order_Status==='Delivered');
 const durations=delivered.map(r=>r.Delivery_Date&&r.Order_Date?age(r.Order_Date,r.Delivery_Date):null).filter(x=>x!==null&&Number.isFinite(x)&&x>=0);
 const defectRows=delivered.filter(r=>num(r.Defective_Units)!==null&&num(r.Quantity)>0&&num(r.Defective_Units)>=0&&num(r.Defective_Units)<=num(r.Quantity));
 const defectQty=defectRows.reduce((n,r)=>n+Number(r.Quantity),0);
 const yes=rows.filter(r=>r.Compliance==='Yes').length;const assessed=rows.filter(r=>['Yes','No'].includes(r.Compliance)).length;
 return {rows:rows.length,delivered:delivered.length,duration:durations.length?durations.reduce((a,b)=>a+b,0)/durations.length:null,durationN:durations.length,defect:defectQty?100*defectRows.reduce((n,r)=>n+Number(r.Defective_Units),0)/defectQty:null,defectN:defectRows.length,compliance:assessed?yes/assessed*100:null,missingDates:rows.filter(r=>!r.Delivery_Date).length};
}
root.RESA={evaluate,kpiSummary,age};
})(typeof window!=='undefined'?window:globalThis);
