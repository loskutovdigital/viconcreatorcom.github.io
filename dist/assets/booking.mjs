import {endpoint} from './booking-config.mjs';
import {localDate, validateBooking, buildPayload} from './booking-core.mjs';

const dialog=document.querySelector('#booking-dialog');
const form=document.querySelector('#booking-form');
const lang=document.documentElement.lang==='nl'?'nl':'en';
const text={
 en:{sending:'Submitting your enquiry…',send:'Send enquiry',uncertain:'Delivery could not be confirmed. Your details are still here. You can try again or contact @vicon.creator on Instagram.',name:'Please enter your name (2–100 characters).',session:'Please choose a session.',idea:'Please describe your idea (5–1,800 characters).',date:'Please choose today or a future date.',method:'Please choose how I should contact you.',contact:'Please enter your contact details.',email:'Please enter a valid email address.',phone:'Please enter a phone number with country code.',handle:'Please enter your username or profile link.'},
 nl:{sending:'Je aanvraag wordt verstuurd…',send:'Verstuur aanvraag',uncertain:'De bezorging kon niet worden bevestigd. Je gegevens staan er nog. Probeer het opnieuw of neem contact op via @vicon.creator op Instagram.',name:'Vul je naam in (2–100 tekens).',session:'Kies een fotoshoot.',idea:'Beschrijf je idee (5–1.800 tekens).',date:'Kies vandaag of een toekomstige datum.',method:'Kies hoe ik contact mag opnemen.',contact:'Vul je contactgegevens in.',email:'Vul een geldig e-mailadres in.',phone:'Vul een telefoonnummer met landcode in.',handle:'Vul je gebruikersnaam of profiellink in.'}
}[lang];
const channels={
 telegram:{label:'Telegram',type:'text',placeholder:'@username',hint:lang==='nl'?'Gebruikersnaam of t.me-profiellink':'Your username or t.me profile link',autocomplete:'off',inputmode:'text'},
 whatsapp:{label:'WhatsApp',type:'tel',placeholder:'+31 6 1234 5678',hint:lang==='nl'?'Je WhatsApp-nummer, inclusief landcode':'Your WhatsApp number, including country code',autocomplete:'tel',inputmode:'tel'},
 email:{label:lang==='nl'?'E-mailadres':'Email address',type:'email',placeholder:'you@example.com',hint:'',autocomplete:'email',inputmode:'email'},
 phone:{label:lang==='nl'?'Telefoonnummer':'Phone number',type:'tel',placeholder:'+31 6 1234 5678',hint:lang==='nl'?'Inclusief landcode':'Include your country code',autocomplete:'tel',inputmode:'tel'},
 instagram:{label:'Instagram',type:'text',placeholder:'@username',hint:lang==='nl'?'Gebruikersnaam of Instagram-profiellink':'Your username or Instagram profile link',autocomplete:'off',inputmode:'text'},
};
if(dialog && form) {
  const field=name=>form.elements.namedItem(name);
  const status=form.querySelector('.booking-status');
  const submit=form.querySelector('[type="submit"]');
  const confirmation=dialog.querySelector('.booking-confirmation');
  let opener=null, pending=false, submitted=false;
  field('preferred_date').min=localDate();
  const syncSession=()=>{
    const other=field('session_type').value==='other';
    document.querySelector('#booking-idea-group').hidden=!other;
    field('idea').disabled=!other;
    field('idea').required=other;
    field('idea').setCustomValidity('');
  };
  const syncContact=()=>{
    const channel=channels[field('contact_method').value];
    const input=field('contact_value');
    input.disabled=!channel;input.setCustomValidity('');
    document.querySelector('#booking-contact-label').textContent=channel?.label||(lang==='nl'?'Je contactgegevens':'Your contact details');
    input.type=channel?.type||'text';input.placeholder=channel?.placeholder||'';
    input.autocomplete=channel?.autocomplete||'off';input.inputMode=channel?.inputmode||'text';
    document.querySelector('#booking-contact-hint').textContent=channel?.hint||'';
  };
  const reset=()=>{
    form.reset();form.hidden=false;confirmation.hidden=true;status.textContent='';status.className='booking-status';submitted=false;
    submit.disabled=false;submit.textContent=text.send+' ↗';syncSession();syncContact();
  };
  const open=(trigger)=>{
    opener=trigger;
    if(submitted)reset();
    const session=trigger.dataset.session||document.body.dataset.session;
    if(session && !field('session_type').value)field('session_type').value=session;
    syncSession();syncContact();field('preferred_date').min=localDate();
    document.querySelector('.mobile-menu')?.classList.remove('is-open');
    document.querySelector('.menu-button')?.setAttribute('aria-expanded','false');
    dialog.showModal();document.body.classList.add('no-scroll');
    field('name').focus({preventScroll:true});
  };
  document.querySelectorAll('[data-booking-open]').forEach(trigger=>trigger.addEventListener('click',event=>{event.preventDefault();open(trigger);}));
  dialog.querySelectorAll('[data-booking-close]').forEach(button=>button.addEventListener('click',()=>dialog.close()));
  dialog.addEventListener('close',()=>{
    document.body.classList.remove('no-scroll');opener?.focus({preventScroll:true});
  });
  dialog.addEventListener('click',event=>{if(event.target===dialog){const box=dialog.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)dialog.close();}});
  field('session_type').addEventListener('change',syncSession);
  field('contact_method').addEventListener('change',()=>{field('contact_value').value='';syncContact();if(!field('contact_value').disabled)field('contact_value').focus();});
  form.addEventListener('input',event=>{event.target.setCustomValidity?.('');status.textContent='';});
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(pending||submitted)return;
    if(field('website').value)return;
    const data=Object.fromEntries(new FormData(form));
    const error=validateBooking(data);
    if(error){const input=field(error.field);input.setCustomValidity(text[error.code]);input.reportValidity();return;}
    if(!form.reportValidity())return;
    const payload=buildPayload(data,{pageUrl:window.location.href,language:lang});
    const body=new FormData();Object.entries(payload).forEach(([key,value])=>body.append(key,value));
    pending=true;form.querySelector('fieldset').disabled=true;form.setAttribute('aria-busy','true');submit.disabled=true;submit.textContent=text.sending;status.textContent=text.sending;status.className='booking-status';
    const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),20000);
    try {
      // The existing Apps Script receiver accepts FormData and returns an opaque response.
      // Opaque transport completion is not proof of notification delivery or a confirmed booking.
      const response=await fetch(endpoint,{method:'POST',mode:'no-cors',credentials:'omit',body,signal:controller.signal,referrerPolicy:'strict-origin-when-cross-origin'});
      if(response.type!=='opaque' && !response.ok)throw new Error('Unconfirmed delivery');
      submitted=true;form.hidden=true;confirmation.hidden=false;
      confirmation.querySelector('h3').setAttribute('tabindex','-1');confirmation.querySelector('h3').focus();
    } catch {
      status.textContent=text.uncertain;status.className='booking-status is-error';
    } finally {
      clearTimeout(timeout);pending=false;form.querySelector('fieldset').disabled=false;form.removeAttribute('aria-busy');submit.disabled=submitted;submit.textContent=text.send+' ↗';
    }
  });
}
