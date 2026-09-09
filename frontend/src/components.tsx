import { useEffect, useRef, useState } from 'react';
import Plotly from 'plotly.js-basic-dist-min';
import type { Data, Layout } from 'plotly.js';
import { Row, number } from './api';

export function Chart({title,subtitle,data,layout={}}:{title:string;subtitle?:string;data:Data[];layout?:Partial<Layout>}){
 const element=useRef<HTMLDivElement>(null);
 useEffect(()=>{const node=element.current;if(!node)return;
  void Plotly.react(node,data,{autosize:true,height:300,margin:{l:65,r:25,t:20,b:55},paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{family:'Segoe UI, sans-serif',size:11,color:'#64736f'},colorway:['#277d69','#a5bd6c','#e9b55b','#809bbb','#b791ae'],xaxis:{gridcolor:'#edf0ed'},yaxis:{gridcolor:'#edf0ed',zeroline:false},legend:{orientation:'h',y:1.15},...layout},{responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d']});
  const observer=new ResizeObserver(()=>{void Plotly.Plots.resize(node)});observer.observe(node);
  return()=>{observer.disconnect();Plotly.purge(node)};
 },[data,layout]);
 return <section className="panel chart"><div className="panel-title"><h3>{title}</h3>{subtitle&&<span>{subtitle}</span>}</div><div ref={element} role="img" aria-label={title}/></section>
}

export function Table({title,rows,columns}:{title:string;rows:Row[];columns?:string[]}){
 const [page,setPage]=useState(0);
 useEffect(()=>setPage(0),[rows]);
 const keys=columns||Object.keys(rows[0]||{});const pages=Math.ceil(rows.length/10);
 return <section className="panel"><div className="panel-title"><h3>{title}</h3><span>{rows.length} records</span></div>{!rows.length?<p className="empty">No matching records.</p>:<><div className="table-scroll"><table><thead><tr>{keys.map(key=><th key={key}>{key.replaceAll('_',' ')}</th>)}</tr></thead><tbody>{rows.slice(page*10,page*10+10).map((row,i)=><tr key={i}>{keys.map(key=><td key={key}>{row[key]===null||row[key]===undefined?'—':typeof row[key]==='number'?number(row[key] as number):String(row[key])}</td>)}</tr>)}</tbody></table></div>{pages>1&&<div className="pagination"><button disabled={!page} onClick={()=>setPage(page-1)}>Previous</button><span>{page+1} / {pages}</span><button disabled={page>=pages-1} onClick={()=>setPage(page+1)}>Next</button></div>}</>}</section>
}

export function Kpis({data}:{data:Record<string,number>}){
 const entries=[['Revenue','revenue','INR'],['Gross profit','profit','INR'],['Units sold','units','units'],['Profit margin','margin_pct','%']];
 return <div className="kpis">{entries.map(([label,key,unit])=><section className="kpi" key={key}><span>{label}</span><strong>{unit==='INR'?new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',notation:'compact',maximumFractionDigits:2}).format(data[key]||0):number(data[key]||0)+(unit==='%'?'%':'')}</strong><small>{unit==='INR'?'Net of line discounts':key==='units'?'Across the selected transactions':'Gross profit / net revenue'}</small></section>)}</div>
}
