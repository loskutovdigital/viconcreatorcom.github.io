export const sessions = Object.freeze({weddings:'Weddings',couples:'Love story / couples',portraits:'Portraits',maternity:'Maternity',family:'Children / family',events:'Events',other:'Other / personal idea'});
export const methods = Object.freeze({telegram:'Telegram',whatsapp:'WhatsApp',email:'Email',phone:'Phone',instagram:'Instagram'});
export function localDate(date = new Date()) {
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
}
export function validateBooking(data, today = localDate()) {
  if(!data.name || data.name.trim().length<2 || data.name.trim().length>100) return {field:'name',code:'name'};
  if(!Object.hasOwn(sessions,data.session_type)) return {field:'session_type',code:'session'};
  if(data.session_type==='other' && (!data.idea || data.idea.trim().length<5 || data.idea.trim().length>1800)) return {field:'idea',code:'idea'};
  if(data.preferred_date) {
    const date = data.preferred_date;
    const parsed = new Date(date+'T12:00:00Z');
    if(!/^\d{4}-\d{2}-\d{2}$/.test(date) || Number.isNaN(parsed.valueOf()) || parsed.toISOString().slice(0,10)!==date || date<today) return {field:'preferred_date',code:'date'};
  }
  if(!Object.hasOwn(methods,data.contact_method)) return {field:'contact_method',code:'method'};
  const contact=(data.contact_value||'').trim();
  if(!contact || contact.length>150) return {field:'contact_value',code:'contact'};
  if(data.contact_method==='email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact)) return {field:'contact_value',code:'email'};
  if(['phone','whatsapp'].includes(data.contact_method)) {
    const digits=contact.replace(/\D/g,'');
    if(!/^\+?[0-9\s().-]+$/.test(contact) || digits.length<8 || digits.length>15) return {field:'contact_value',code:'phone'};
  }
  if(['telegram','instagram'].includes(data.contact_method)) {
    const handle=contact.replace(/^https?:\/\//i,'').replace(/^(www\.)?(t\.me|telegram\.me|instagram\.com)\//i,'').replace(/^@/,'').replace(/\/$/,'');
    if(!/^[A-Za-z0-9_.]+$/.test(handle) || handle.length<2) return {field:'contact_value',code:'handle'};
  }
  return null;
}
export function buildPayload(data, {pageUrl, language='en', now=new Date()}={}) {
  const method=methods[data.contact_method];
  const contact=data.contact_value.trim();
  const idea=data.session_type==='other'?data.idea.trim():'';
  return {
    name:data.name.trim(),
    reply_to:data.contact_method==='email'?contact:`${method}: ${contact}`,
    service:`Vicon Creator booking · ${sessions[data.session_type]} · ${method}`,
    message:[`Photography: ${sessions[data.session_type]}`,`Preferred date: ${data.preferred_date||'Not decided'}`,`Contact method: ${method}`,`Contact details: ${contact}`,idea?`Personal idea: ${idea}`:'',`Website language: ${language}`].filter(Boolean).join('\n'),
    page_url:pageUrl,
    submitted_at:now.toISOString(),
    website:(data.website||'').trim(),
  };
}
