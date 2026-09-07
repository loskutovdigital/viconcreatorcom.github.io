"""Shared GA4 markup. Analytics starts automatically on every page."""
MEASUREMENT_ID = 'G-89KY41JK4Y'

def analytics_head():
 return '''<!-- Google tag (gtag.js) -->
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});</script>
<script defer src="/assets/analytics.js" data-measurement-id="G-89KY41JK4Y"></script>'''
