const menuButton = document.querySelector('.menu-button');
const menu = document.querySelector('.mobile-menu');
function closeMenu() { menu?.classList.remove('is-open'); menuButton?.setAttribute('aria-expanded','false'); }
menuButton?.addEventListener('click', () => { const open = menuButton.getAttribute('aria-expanded') !== 'true'; menuButton.setAttribute('aria-expanded',String(open)); menu.classList.toggle('is-open',open); });
document.addEventListener('keydown', e => { if(e.key === 'Escape') closeMenu(); });
document.addEventListener('click', e => { if(menu && !menu.contains(e.target) && !menuButton?.contains(e.target)) closeMenu(); });
window.matchMedia('(min-width:761px)').addEventListener('change', e => {if(e.matches) closeMenu();});
const lightbox = document.querySelector('.lightbox');
const photos = Array.from(document.querySelectorAll('[data-lightbox]'));
let activePhoto = 0;
function showPhoto(i) {
  if(!lightbox || !photos.length) return;
  activePhoto = (i + photos.length) % photos.length;
  const photo = photos[activePhoto];
  const img = lightbox.querySelector('img');
  img.src = photo.dataset.full;
  img.alt = photo.querySelector('img').alt;
  lightbox.querySelector('.lb-caption').textContent = img.alt;
  lightbox.querySelector('.lb-counter').textContent = `${activePhoto+1} / ${photos.length}`;
}
photos.forEach((photo,i) => photo.addEventListener('click', () => {showPhoto(i);lightbox.showModal();document.body.classList.add('no-scroll');}));
function closeLightbox() {if(lightbox?.open)lightbox.close();document.body.classList.remove('no-scroll');}
lightbox?.querySelector('.lb-close').addEventListener('click', closeLightbox);
lightbox?.querySelector('.lb-prev').addEventListener('click', () => showPhoto(activePhoto-1));
lightbox?.querySelector('.lb-next').addEventListener('click', () => showPhoto(activePhoto+1));
lightbox?.addEventListener('close', () => {document.body.classList.remove('no-scroll');photos[activePhoto]?.focus({preventScroll:true});});
lightbox?.addEventListener('click', e => { if(e.target === lightbox || e.target.classList.contains('lightbox-inner')) closeLightbox(); });
document.addEventListener('keydown', e => {if(!lightbox?.open)return;if(e.key==='ArrowLeft'){e.preventDefault();showPhoto(activePhoto-1);}if(e.key==='ArrowRight'){e.preventDefault();showPhoto(activePhoto+1);}});
let startX = 0;
lightbox?.addEventListener('touchstart', e => {startX=e.changedTouches[0].clientX;},{passive:true});
lightbox?.addEventListener('touchend', e => {const distance=e.changedTouches[0].clientX-startX;if(Math.abs(distance)>60)showPhoto(activePhoto+(distance<0?1:-1));},{passive:true});
document.querySelectorAll('video').forEach(video => {
  video.muted = true;
  video.addEventListener('play', () => { document.querySelectorAll('video').forEach(other => {if(other!==video)other.pause();}); });
});
