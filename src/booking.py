from html import escape
from content import SERVICES, ROUTES, INSTAGRAM

COPY = {
 'en': {
  'title':'Let’s begin your story.', 'intro':'Tell me a little about your session and how you’d like me to get back to you.',
  'name':'Your name', 'nameHint':'How should I call you?', 'session':'Type of session', 'choose':'Choose a session', 'other':'Other — my own idea',
  'idea':'Your idea', 'ideaHint':'What would you love to create?', 'date':'Preferred date', 'optional':'optional',
  'dateHint':'Choose a day, or leave it open if you’re still planning.', 'method':'How should I contact you?', 'methodChoose':'Choose a contact method',
  'contact':'Your contact details', 'contactHint':'Choose a contact method above', 'send':'Send enquiry', 'close':'Close booking form',
  'privacy':'Your details will be used to reply to this enquiry.', 'privacyLink':'Privacy details',
  'note':'This is an enquiry. Your date is only reserved after a personal confirmation.',
  'submitted':'Thank you for reaching out.', 'submittedNote':'Your request has been submitted for delivery. Please wait for a personal confirmation before making plans around the date.',
  'alternative':'You can also reach me on Instagram', 'done':'Close',
 },
 'nl': {
  'title':'Hier begint jouw verhaal.', 'intro':'Vertel iets over je fotoshoot en hoe je graag een reactie ontvangt.',
  'name':'Je naam', 'nameHint':'Hoe mag ik je noemen?', 'session':'Soort fotoshoot', 'choose':'Kies een fotoshoot', 'other':'Anders — mijn eigen idee',
  'idea':'Jouw idee', 'ideaHint':'Wat zou je graag willen maken?', 'date':'Gewenste datum', 'optional':'optioneel',
  'dateHint':'Kies een dag, of laat dit open als je nog aan het plannen bent.', 'method':'Hoe mag ik contact opnemen?', 'methodChoose':'Kies een contactmethode',
  'contact':'Je contactgegevens', 'contactHint':'Kies hierboven een contactmethode', 'send':'Verstuur aanvraag', 'close':'Sluit het aanvraagformulier',
  'privacy':'Je gegevens worden gebruikt om op deze aanvraag te reageren.', 'privacyLink':'Privacygegevens',
  'note':'Dit is een aanvraag. Je datum is pas gereserveerd na een persoonlijke bevestiging.',
  'submitted':'Bedankt voor je bericht.', 'submittedNote':'Je aanvraag is ingediend voor verzending. Wacht op een persoonlijke bevestiging voordat je plannen rond de datum vastlegt.',
  'alternative':'Je kunt me ook bereiken op Instagram', 'done':'Sluiten',
 }
}

def booking_dialog(lang):
 t=COPY[lang];i=0 if lang=='en' else 1;e=escape
 options=''.join(f'<option value="{k}">{e(v["label"][i])}</option>' for k,v in SERVICES.items())
 methods=[('telegram','Telegram'),('whatsapp','WhatsApp'),('email','Email' if lang=='en' else 'E-mail'),('phone','Phone call' if lang=='en' else 'Telefoon'),('instagram','Instagram')]
 choices=''.join(f'<option value="{k}">{label}</option>' for k,label in methods)
 return f'''<dialog id="booking-dialog" class="booking-dialog" aria-labelledby="booking-title" aria-describedby="booking-intro">
 <div class="booking-shell"><div class="booking-top"><span class="eyebrow">Vicon Creator · Booking</span><button class="booking-close" type="button" data-booking-close aria-label="{t['close']}">×</button></div>
 <div class="booking-heading"><h2 id="booking-title">{t['title']}</h2><p id="booking-intro">{t['intro']}</p></div>
 <form id="booking-form" novalidate><fieldset class="booking-grid">
 <div class="booking-field booking-full"><label for="booking-name">{t['name']}</label><input id="booking-name" name="name" type="text" autocomplete="name" placeholder="{t['nameHint']}" minlength="2" maxlength="100" required></div>
 <div class="booking-field"><label for="booking-session">{t['session']}</label><select id="booking-session" name="session_type" required><option value="">{t['choose']}</option>{options}<option value="other">{t['other']}</option></select></div>
 <div class="booking-field"><label for="booking-date">{t['date']} <span class="field-optional">({t['optional']})</span></label><input id="booking-date" name="preferred_date" type="date" aria-describedby="booking-date-hint"><small id="booking-date-hint">{t['dateHint']}</small></div>
 <div class="booking-field booking-full" id="booking-idea-group" hidden><label for="booking-idea">{t['idea']}</label><textarea id="booking-idea" name="idea" placeholder="{t['ideaHint']}" rows="3" minlength="5" maxlength="1800" disabled></textarea></div>
 <div class="booking-field"><label for="booking-method">{t['method']}</label><select id="booking-method" name="contact_method" required><option value="">{t['methodChoose']}</option>{choices}</select></div>
 <div class="booking-field"><label id="booking-contact-label" for="booking-contact">{t['contact']}</label><input id="booking-contact" name="contact_value" type="text" autocomplete="off" placeholder="{t['contactHint']}" maxlength="150" required disabled><small id="booking-contact-hint"></small></div>
 <div class="booking-trap" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off" type="text"></label></div>
 </fieldset><div class="booking-bottom"><p class="booking-privacy">{t['privacy']} <a href="{ROUTES['privacy'][i]}">{t['privacyLink']}</a></p><button class="button booking-submit" type="submit">{t['send']} <span aria-hidden="true">↗</span></button><p class="booking-note">{t['note']}</p><p class="booking-status" role="status" aria-live="polite"></p></div></form>
 <div class="booking-confirmation" hidden><h3>{t['submitted']}</h3><p class="confirmation-copy">{t['submittedNote']}</p><button class="button" data-booking-close type="button">{t['done']}</button></div>
 <p class="booking-alternative">{t['alternative']}: <a href="{INSTAGRAM}" target="_blank" rel="noopener noreferrer">@vicon.creator ↗</a></p></div></dialog>'''
