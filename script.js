// Header
const header = document.getElementById('header');
const onScroll = () => header.classList.toggle('scrolled', window.scrollY > 30);
window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

// Mobile menu
const burger = document.getElementById('burger');
const nav = document.getElementById('nav');
burger.addEventListener('click', () => { nav.classList.toggle('open'); burger.classList.toggle('open'); });

// Reveal on scroll (with small stagger for siblings)
const io = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    const sibs = [...e.target.parentElement.children].filter(c => c.classList.contains('reveal'));
    e.target.style.transitionDelay = `${Math.min(sibs.indexOf(e.target), 6) * 70}ms`;
    e.target.classList.add('visible');
    io.unobserve(e.target);
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// Counters
const cio = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    const el = e.target, end = +el.dataset.count, t0 = performance.now(), dur = 1600;
    const tick = t => {
      const p = Math.min((t - t0) / dur, 1), v = Math.round(end * (1 - Math.pow(1 - p, 3)));
      el.textContent = v.toLocaleString('az');
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    cio.unobserve(el);
  });
}, { threshold: 0.5 });
document.querySelectorAll('[data-count]').forEach(el => cio.observe(el));

// Pearl parallax
const scene = document.getElementById('pearlScene');
const pearl = document.getElementById('pearl');
if (scene && pearl && matchMedia('(pointer: fine)').matches) {
  window.addEventListener('mousemove', e => {
    const x = (e.clientX / innerWidth - .5), y = (e.clientY / innerHeight - .5);
    pearl.style.transform = `translate(${x * 24}px, ${y * 24}px)`;
    scene.querySelectorAll('.chip').forEach((c, i) => c.style.translate = `${x * -14 * (i + 1)}px ${y * -14 * (i + 1)}px`);
  });
}

// Contact form -> WhatsApp
document.getElementById('form')?.addEventListener('submit', e => {
  e.preventDefault();
  const f = new FormData(e.target);
  const text = `Salam! Saytdan müraciət:\n👤 ${f.get('name')}\n📞 ${f.get('phone')}\n📌 ${f.get('topic')}\n💬 ${f.get('message') || '-'}`;
  window.open(`https://wa.me/994512294980?text=${encodeURIComponent(text)}`, '_blank');
});

document.getElementById('year').textContent = new Date().getFullYear();
