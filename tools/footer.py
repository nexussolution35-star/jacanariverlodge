#!/usr/bin/env python3
"""Write the shared site footer into every page (run from the repo root).
Links are root-relative and match the live jacanariverlodge.com URLs."""
import os, re

def footer(r):
    ic = {
     'facebook': '<path d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.6-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/>',
     'instagram': '<path d="M12 2.2c3.2 0 3.6 0 4.8.1 3.3.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 3.9 3.9 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zM12 0C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 1 0 0 12.4 6.2 6.2 0 0 0 0-12.4zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.8a1.4 1.4 0 1 0 0 2.9 1.4 1.4 0 0 0 0-2.9z"/>',
     'youtube': '<path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8zM9.6 15.6V8.4l6.2 3.6-6.2 3.6z"/>',
     'whatsapp': '<path d="M.06 24l1.7-6.16a11.86 11.86 0 1 1 4.4 4.42L.06 24zM6.4 20.1l.37.22a9.86 9.86 0 1 0-3.4-3.4l.24.38-1 3.6 3.79-.8zM17.5 14.3c-.15-.25-.55-.4-1.15-.7s-1.38-.68-1.6-.76-.37-.12-.53.12-.6.76-.74.92-.27.18-.5.06a8.1 8.1 0 0 1-2.38-1.47 8.94 8.94 0 0 1-1.65-2.05c-.17-.3 0-.46.13-.6s.25-.3.37-.45.17-.25.25-.42a.46.46 0 0 0 0-.43c-.07-.12-.53-1.28-.73-1.76s-.39-.4-.53-.4h-.46a.88.88 0 0 0-.64.3 2.68 2.68 0 0 0-.83 2 4.64 4.64 0 0 0 .98 2.48 10.66 10.66 0 0 0 4.1 3.63 13.8 13.8 0 0 0 1.37.5 3.3 3.3 0 0 0 1.5.1 2.46 2.46 0 0 0 1.62-1.15 2 2 0 0 0 .14-1.13z"/>',
     'tripadvisor': '<path d="M12 6.2c-2.3 0-4.5.6-6.3 1.8H1.5l1.6 1.8a5.2 5.2 0 1 0 7 7.5l1.9 2.1 1.9-2.1a5.2 5.2 0 1 0 7-7.5L22.5 8h-4.2A11.5 11.5 0 0 0 12 6.2zM6.6 10.2a3.6 3.6 0 1 1 0 7.2 3.6 3.6 0 0 1 0-7.2zm10.8 0a3.6 3.6 0 1 1 0 7.2 3.6 3.6 0 0 1 0-7.2zm-10.8 1.9a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4zm10.8 0a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4zM12 8c1.4 0 2.8.3 4 .8a5.2 5.2 0 0 0-4 4.8 5.2 5.2 0 0 0-4-4.8A10 10 0 0 1 12 8z"/>',
    }
    socials = [('facebook', 'Facebook', 'https://www.facebook.com/jacanariverlodge/'),
               ('instagram', 'Instagram', 'https://www.instagram.com/jacana_river_lodge/'),
               ('youtube', 'YouTube', 'https://www.youtube.com/@jacanariverlodge9550'),
               ('whatsapp', 'WhatsApp', 'https://wa.me/27662937100'),
               ('tripadvisor', 'Tripadvisor', 'https://www.tripadvisor.co.za/VacationRentalReview-g657276-d19114871-Jacana_River_Lodge-Hectorspruit_Mpumalanga.html')]
    soc = "\n".join(f'          <li><a href="{u}" target="_blank" rel="noopener" aria-label="Jacana River Lodge on {n}"><svg viewBox="0 0 24 24" aria-hidden="true">{ic[k]}</svg></a></li>' for k, n, u in socials)
    home = '/'
    return f'''<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="footer__logo" href="{home}" aria-label="Jacana River Lodge home">
          <img class="brand-foot" src="/assets/images/logo-footer.png" alt="Jacana River Lodge" width="560" height="332" loading="lazy">
          <img class="footer__stars" src="/assets/images/tgcsa-5-star.png" alt="5-star graded by the TGCSA" width="198" height="50" loading="lazy">
        </a>
        <ul class="footer__social">
{soc}
        </ul>
      </div>
      <nav class="footer__col" aria-label="Useful links">
        <h4>Useful links</h4>
        <ul>
          <li><a href="/luxury-self-catering-lodge-accommodation-in-mpumalanga/">About the Lodge</a></li>
          <li><a href="/activities-near-mjejane/">Activities</a></li>
          <li><a href="/mjejane-game-reserve-accommodation-guide/">Mjejane Reserve</a></li>
          <li><a href="/gallery/">Gallery</a></li>
          <li><a href="/news/">News &amp; Stories</a></li>
          <li><a href="/mjejane-accommodation-specials/">Specials</a></li>
          <li><a href="/mjejane-accommodation-prices-and-packages/">Packages</a></li>
        </ul>
      </nav>
      <nav class="footer__col" aria-label="Information">
        <h4>Information</h4>
        <ul>
          <li><a href="/facilities/">Rates &amp; Facilities</a></li>
          <li><a href="/book-now/">Book Your Stay</a></li>
          <li><a href="/contact-us/">Contact Us</a></li>
          <li><a href="/directions/">Directions</a></li>
          <li><a href="{home}#faq">FAQs</a></li>
          <li><a href="tel:+27662937100">+27 (0)66 293 7100</a></li>
          <li><a href="mailto:info@jacanariverlodge.com">info@jacanariverlodge.com</a></li>
        </ul>
      </nav>
      <div class="footer__col footer__awards">
        <h4>Awarded &amp; graded</h4>
        <ul class="badges">
          <li class="badge badge--tgcsa"><img src="/assets/images/tgcsa-5-star.png" alt="" width="198" height="50" loading="lazy"><b>5-Star</b><span>TGCSA graded</span></li>
          <li><a class="badge badge--booking" href="{home}#reviews" aria-label="Booking.com Traveller Review Awards 2026: 9.6 out of 10"><span class="badge__logo">Booking.com</span><b>9.6</b><span>Traveller Review<br>Award 2026</span></a></li>
          <li><a class="badge badge--google" href="https://g.page/jacana-river-lodge?share" target="_blank" rel="noopener" aria-label="Rated 4.5 out of 5 on Google"><span class="badge__logo"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"/><path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38z"/></svg></span><b>4.5</b><span>Google<br>guest rating</span></a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <p>&copy; <span id="year"></span> Jacana River Lodge, Mjejane Private Game Reserve,<br>Hectorspruit, Mpumalanga, South Africa</p>
      <ul class="footer__legal">
        <li><a href="/cookies-and-privacy-policy/">Cookie &amp; privacy policy</a></li>
        <li><a href="/rules-and-safety/">Rules &amp; safety</a></li>
        <li><a href="/directions/">Find us</a></li>
        <li><a href="/contact-us/">Contact us</a></li>
      </ul>
    </div>
  </div>
</footer>'''

n = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git', 'seo', 'tools', 'assets', 'css', 'js', 'node_modules')]
    for f in files:
        if not f.endswith('.html'): continue
        p = os.path.join(root, f); t = open(p).read()
        if '<footer class="footer">' not in t: continue
        r = '/'
        a = t.index('<footer class="footer">'); b = t.index('</footer>', a) + len('</footer>')
        t2 = t[:a] + footer(r) + t[b:]
        if t2 != t: open(p, 'w').write(t2); n += 1
print('footers written:', n)
