/* Shared GA4 loader: starts automatically, without a popup. */
(() => {
  'use strict';
  const id = document.querySelector('script[data-measurement-id]')?.dataset.measurementId;
  if (!id) return;
  const page = new URL(location.origin + location.pathname);
  const current = new URL(location.href);
  for (const name of ['utm_source','utm_medium','utm_campaign','utm_id','utm_term','utm_content']) {
    if (current.searchParams.has(name)) page.searchParams.set(name, current.searchParams.get(name));
  }
  window.gtag('js', new Date());
  window.gtag('config', id, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    cookie_prefix: 'vicon',
    cookie_domain: location.hostname,
    cookie_expires: 180 * 24 * 60 * 60,
    // Preserve campaign attribution without passing form values or free-text URL parameters.
    page_location: page.href,
    page_title: document.title
  });
  const tag = document.createElement('script');
  tag.async = true;
  tag.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
  document.head.append(tag);
})();
