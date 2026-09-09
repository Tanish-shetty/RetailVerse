export type Row = Record<string, string | number | null>;
export type Filters = Record<string,string>;
export type Envelope<T> = {data:T;rows:number;source:string[];total:number|null};
export async function request<T>(path:string, filters:Filters={}, signal?:AbortSignal):Promise<T> {
  const response=await fetch('/api/'+path+'?'+new URLSearchParams(Object.entries(filters).filter(([,v])=>v)),{signal});
  if(!response.ok){const error=await response.json().catch(()=>({}));throw new Error(error.detail||'The analytics service could not complete this request.');}
  return response.json();
}
export const money=(value:number)=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0,notation:Math.abs(value)>=1000000?'compact':'standard'}).format(value);
export const number=(value:number)=>new Intl.NumberFormat('en-IN',{maximumFractionDigits:1}).format(value);
