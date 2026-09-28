"""Prepare source-preserving first-review data. Run after raw files are downloaded."""
import csv,json,hashlib,io,zipfile,shutil
from pathlib import Path
from datetime import datetime
P=Path('dist/data');R=P/'raw';P.mkdir(exist_ok=True)
def readcsv(n):return list(csv.DictReader((R/n).open(encoding='utf-8-sig')))
if (R/'Procurement KPI Analysis Dataset.csv').exists():
 shutil.copyfile(R/'Procurement KPI Analysis Dataset.csv',R/'procurement_kpi.csv')
kpi=readcsv('procurement_kpi.csv')
graph={k:readcsv(n) for k,n in [('suppliers','nodes_supplier.csv'),('parts','nodes_part.csv'),('relations','is_supplied_by.csv'),('vehicles','nodes_car_model.csv')]}
bench=json.loads((R/'benchmark_dev.json').read_text())
if isinstance(bench,dict):
 for k in ['queries','data','items','benchmark']:
  if isinstance(bench.get(k),list):bench=bench[k];break
assert isinstance(bench,list)
names=[('DEMO-S01','Chennai Precision Works','Chennai'),('DEMO-S02','Kovai Motion Components','Coimbatore'),('DEMO-S03','Pune Auto Systems','Pune'),('DEMO-S04','Hosur Component Works','Hosur'),('DEMO-S05','Deccan Brake Technologies','Hyderabad'),('DEMO-S06','Madras Mobility Parts','Chennai')]
lead=[8,14,None,7,9,9];prices=[420,365,398,382,355,390];defects=[1.1,0.8,1.0,0.9,3.2,1.5];otd=[97,86,93,96,83,94]
suppliers=[];quotes=[];scorecards=[];evidence=[]
for i,(sid,name,city) in enumerate(names):
 suppliers.append(dict(id=sid,name=name,location=city,provenance='Synthetic review scenario',fictional=True))
 for part,mult in [('Brake pad',1),('Air filter',.55)]:
  qid=f'DEMO-Q{i+1:02d}-'+('BP' if part=='Brake pad' else 'AF')
  q=dict(id=qid,supplier_id=sid,part=part,unit_price=round(prices[i]*mult),currency='INR',lead_days=lead[i],capacity=2000 if i!=5 else 1000,issued='2026-09-01',valid_until='2026-09-30')
  quotes.append(q)
  excerpt=f"{name} offers {part.lower()} at INR {q['unit_price']} per unit. Capacity: {q['capacity']} units. "+(f"Committed lead time: {q['lead_days']} calendar days." if q['lead_days'] is not None else 'Delivery commitment is not specified.')+' Offer valid until 30 September 2026.'
  evidence.append(dict(id=qid,supplier_id=sid,type='Quotation',title=f'{part} quotation',date=q['issued'],excerpt=excerpt,provenance='Synthetic review scenario',fields=q))
 for j,date in enumerate(['2026-06-30','2026-07-31','2026-08-31'] if i!=3 else ['2025-10-31','2025-11-30','2025-12-31']):
  scid=f'DEMO-SC{i+1:02d}-{j+1}'
  sc=dict(id=scid,supplier_id=sid,date=date,defect_rate=round(defects[i]+[.3,.15,0][j],2),on_time_delivery=otd[i]+[-2,-1,0][j])
  scorecards.append(sc)
  evidence.append(dict(id=scid,supplier_id=sid,type='Scorecard',title='Monthly supplier scorecard',date=date,excerpt=f"{name}: observed defect rate {sc['defect_rate']}%. On-time delivery against agreed due dates: {sc['on_time_delivery']}%. Reporting period ended {date}. These are historical measurements, not a future delivery guarantee.",provenance='Synthetic review scenario',fields=sc))
policy=dict(id='DEMO-POL-01',supplier_id=None,type='Policy',title='Review scenario decision rules',date='2026-09-01',excerpt='Mandatory requirements: matching component, sufficient capacity, lead time at or below the requested limit, and recent observed defect rate strictly below the requested limit. Quotation must be valid on the assessment date. Scorecards older than 120 days are insufficient evidence. A violated requirement excludes a supplier. Missing evidence requires review. Human approval is required.',provenance='Synthetic review scenario')
evidence.append(policy)
scenarios=[dict(id='CASE-01',label='Standard brake-pad purchase',part='Brake pad',days=10,defect=2,quantity=500),dict(id='CASE-02',label='Urgent delivery',part='Brake pad',days=7,defect=2,quantity=500),dict(id='CASE-03',label='Larger order',part='Brake pad',days=10,defect=2,quantity=1500),dict(id='CASE-04',label='Air-filter purchase',part='Air filter',days=10,defect=2,quantity=500)]
# Only internal scenario checks, not an independent research benchmark.
checks=[dict(id='T01',name='Standard order: two eligible suppliers',scenario=scenarios[0],eligible=['DEMO-S01','DEMO-S06']),dict(id='T02',name='Urgent order: no fully evidenced supplier',scenario=scenarios[1],eligible=[]),dict(id='T03',name='Capacity excludes S06 for 1,500 units',scenario=scenarios[2],eligible=['DEMO-S01']),dict(id='T04',name='Air-filter order uses matching quotations',scenario=scenarios[3],eligible=['DEMO-S01','DEMO-S06'])]
def csvout(path,rows):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for n,rows in [('demo_suppliers.csv',suppliers),('demo_quotes.csv',quotes),('demo_scorecards.csv',scorecards)]:csvout(P/n,rows)
(P/'demo_evidence.json').write_text(json.dumps(evidence,indent=2))
(P/'demo_scenarios.json').write_text(json.dumps(scenarios,indent=2))
sources=[
 dict(id='kpi',title='Procurement KPI Analysis',author='Shahriar Kabir',kind='Public download · publisher-described real data',count=len(kpi),unit='purchase orders',license='CC0 (publisher metadata)',url='https://www.kaggle.com/datasets/shahriarkabir/procurement-kpi-analysis-dataset',use='Supplier analytics and raw-data inspection',note='Generic procurement, not verified automotive transactions. Publisher describes 700 rows; the downloaded CSV contains 777. Origin is publisher-reported, not independently audited. Currency and promised delivery dates are absent.',files=['raw/procurement_kpi.csv'],loaded=True),
 dict(id='graph',title='Automotive Supply Chain',author='Graph Dataset Hub / Wey Gu',kind='Public sample data',count=sum(len(x) for x in graph.values()),unit='rows across 4 files',license='Source repository terms; sample data',url='https://graph-hub.siwei.io/en/stable/datasets/supply_chain/',use='Automotive parts and supplier relationships',note=f"{len(graph['suppliers'])} sample suppliers, {len(graph['parts'])} parts, {len(graph['vehicles'])} vehicle models and {len(graph['relations'])} relationship rows. Repeated relationship rows remain in raw data. No joins to KPI suppliers or demo vendors.",files=['raw/nodes_supplier.csv','raw/nodes_part.csv','raw/is_supplied_by.csv','raw/nodes_car_model.csv'],loaded=True),
 dict(id='benchmark',title='Auto-Parts Search Benchmark',author='ManmohanBuildsProducts',kind='Public authored retrieval benchmark',count=len(bench),unit='development queries',license='CC BY 4.0',url='https://huggingface.co/datasets/ManmohanBuildsProducts/auto-parts-search-benchmark',use='Inspect retrieval questions and expected parts',note='Development split only. Query annotations are not supplier-ranking ground truth. The sealed test split is not loaded. No RAG results have been measured in this dashboard.',files=['raw/benchmark_dev.json','raw/hf_README.md'],loaded=True),
 dict(id='demo',title='RESA Review Scenario',author='Khavin C · first-review prototype',kind='Synthetic demonstration data',count=len(suppliers)+len(quotes)+len(scorecards)+1,unit='linked records',license='Generated for this demonstration',url=None,use='Interactive eligibility, ranking and evidence traceability',note='Six fictional suppliers, twelve quotations, eighteen scorecards and one policy. These records demonstrate the methodology only. They are separate from all public sources.',files=['demo_suppliers.csv','demo_quotes.csv','demo_scorecards.csv','demo_evidence.json','demo_scenarios.json'],loaded=True)]
manifest=dict(retrieved_at='2026-09-11',sources=sources,files=[])
for source in sources:
 for file in source['files']:
  b=(P/file).read_bytes();manifest['files'].append(dict(path=file,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),source_id=source['id']))
(P/'manifest.json').write_text(json.dumps(manifest,indent=2))
data=dict(asOf='2026-09-11',kpi=kpi,graph=graph,benchmark=bench,suppliers=suppliers,quotes=quotes,scorecards=scorecards,evidence=evidence,scenarios=scenarios,checks=checks,sources=sources)
(P/'dashboard.json').write_text(json.dumps(data,ensure_ascii=False))
(P/'README.txt').write_text('RESA FIRST REVIEW DATA PACKAGE\n\nDownloaded public source files are preserved. KPI CSV: 777 rows, generic procurement. Automotive graph: public sample. Auto-parts benchmark: development queries, CC BY 4.0. Synthetic scenario: six fictional suppliers for RESA demonstration.\n\nDo not join supplier identities across these sources. Do not describe computed demo scores as research results. The source KPI CSV has no promised delivery date or currency; average duration is not on-time delivery. Source links, hashes and limitations: manifest.json.\n\nThe dashboard runs deterministic checks and template explanations. Hybrid RAG, Ollama/Llama 3.1, Qdrant, FastAPI, database storage and statistical research evaluation remain planned integrations.\n')
with zipfile.ZipFile(P/'RESA_First_Review_Datasets.zip','w',zipfile.ZIP_DEFLATED) as z:
 for source in sources:
  for file in source['files']:z.write(P/file,file)
 for f in ['manifest.json','README.txt']:z.write(P/f,f)
# Remove transient downloads and duplicated filenames, preserve metadata for provenance.
for f in ['graph_supplier.csv','hf_tree.json','kpi.zip','Procurement KPI Analysis Dataset.csv']:
 if (R/f).exists():(R/f).unlink()
print('Prepared:',{s['id']:s['count'] for s in sources},'evidence',len(evidence))
