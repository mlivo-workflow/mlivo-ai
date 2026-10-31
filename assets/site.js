/* Mlivo AI – gemeinsames Script für alle Seiten (DE/EN) */
(function(){
  var lang = (document.documentElement.getAttribute('lang') || 'de').slice(0,2);

  // Alte Sprungmarken (vor dem Umbau 10/2026) auf neue Ziele umleiten
  var h = location.hash;
  var isHome = /^\/(en\/)?$/.test(location.pathname);
  if (isHome && h) {
    var archi = lang === 'en' ? '/en/architects/' : '/architekten/';
    var map = { '#cad': archi + '#mcp', '#vierd': archi + '#vierd' };
    var local = { '#start':'#ablauf', '#process':'#ablauf', '#einstieg':'#ablauf',
                  '#begleitung':'#preise', '#training':'#preise',
                  '#packages':'#agenten', '#portal':'#agenten', '#onpremise':'#agenten', '#betrieb':'#agenten', '#agents':'#agenten',
                  '#examples':'#beispiele', '#cases':'#beispiele' };
    if (map[h]) { location.replace(map[h]); return; }
    if (local[h]) { history.replaceState(null, '', local[h]); var t = document.querySelector(local[h]); if (t) setTimeout(function(){ t.scrollIntoView(); }, 0); }
  }

  var nav = document.getElementById('nav'), progress = document.getElementById('progress');
  function onScroll(){
    var y = window.scrollY || document.documentElement.scrollTop;
    nav.classList.toggle('scrolled', y > 10);
    var max = document.documentElement.scrollHeight - window.innerHeight;
    if (progress) progress.style.width = (max > 0 ? (y / max * 100) : 0) + '%';
  }
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();

  var burger = document.getElementById('burger'), navLinks = document.getElementById('navLinks');
  if (burger) {
    burger.addEventListener('click', function(){ var o = navLinks.classList.toggle('open'); burger.setAttribute('aria-expanded', o); });
    navLinks.querySelectorAll('a').forEach(function(a){ a.addEventListener('click', function(){ navLinks.classList.remove('open'); burger.setAttribute('aria-expanded', false); }); });
  }

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){ if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, {threshold:0.12, rootMargin:'0px 0px -40px 0px'});
    document.querySelectorAll('.reveal').forEach(function(el){ io.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function(el){ el.classList.add('in'); });
  }

  // Kontaktformular (Web3Forms, Fallback: E-Mail-Programm)
  var form = document.getElementById('leadForm'); if (!form) return;
  var status = document.getElementById('lfStatus');
  var g = function(n){ return form.elements[n]; };
  var en = lang === 'en';
  form.addEventListener('submit', function(e){
    e.preventDefault();
    if (g('botcheck') && g('botcheck').checked) return;
    var key = g('access_key').value;
    if (!key || key.indexOf('DEIN_') === 0) {
      var body = encodeURIComponent('Name: ' + g('name').value + '\nFirma: ' + g('firma').value + '\nE-Mail: ' + g('email').value + '\n\n' + g('nachricht').value);
      location.href = 'mailto:kontakt@mlivo-ai.at?subject=' + encodeURIComponent('Anfrage über mlivo-ai.at') + '&body=' + body;
      status.className = 'lf-status'; status.textContent = en ? 'Opening your email app…' : 'E-Mail-App wird geöffnet…';
      return;
    }
    status.className = 'lf-status'; status.textContent = en ? 'Sending…' : 'Wird gesendet…';
    fetch('https://api.web3forms.com/submit', {method:'POST', body:new FormData(form)})
      .then(function(r){ return r.json(); })
      .then(function(j){
        if (!j.success) throw new Error();
        form.reset(); status.className = 'lf-status';
        status.textContent = en ? "Thanks! I usually reply within 1–2 business days." : 'Danke! Ich melde mich in der Regel innerhalb von 1–2 Werktagen.';
      })
      .catch(function(){
        status.className = 'lf-status err';
        status.textContent = en ? 'Something went wrong — please email me directly.' : 'Etwas ist schiefgelaufen — bitte direkt per E-Mail.';
      });
  });
})();

/* YouTube erst nach Klick laden (youtube-nocookie, DSGVO) */
(function(){
  document.querySelectorAll('.yt[data-yt]').forEach(function(box){
    var btn = box.querySelector('.yt-play');
    if (!btn) return;
    btn.addEventListener('click', function(){
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + box.getAttribute('data-yt') + '?autoplay=1&rel=0&modestbranding=1&hl=' + (document.documentElement.lang || 'de');
      f.title = btn.getAttribute('aria-label') || 'Video';
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      f.allowFullscreen = true;
      f.referrerPolicy = 'strict-origin-when-cross-origin';
      box.appendChild(f);
      box.classList.add('on');
      f.focus();
    });
  });
})();
