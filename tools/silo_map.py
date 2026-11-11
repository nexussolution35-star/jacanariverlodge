"""The approved silo structure (seo/Jacana-Site-Structure.pdf), as data.

One source for the menu (header.py), the breadcrumbs and the
"more in this section" block (silo.py), so they can't drift apart.

PAGES: url -> (short label, parent url or None, silo key, one-line blurb)
  * parent None + silo set   = the silo hub
  * silo None                = outside the silos (home, plan-your-stay, legal, legacy)
Rule from the plan: links run hub <-> page, sideways only between siblings,
never across silos. Book Now / Contact Us are open to every page.
"""

SILOS = {
    'stay': ('Stay', '/luxury-self-catering-lodge-accommodation-in-mpumalanga/'),
    'act': ('Activities', '/activities-near-mjejane/'),
    'res': ('Mjejane Reserve', '/mjejane-game-reserve-accommodation-guide/'),
}

S, A, R = 'stay', 'act', 'res'
STAY = '/luxury-self-catering-lodge-accommodation-in-mpumalanga/'
ACT = '/activities-near-mjejane/'
RES = '/mjejane-game-reserve-accommodation-guide/'
KTP = '/kruger-tours-and-packages/'
IK = '/kruger-full-day-safari-with-irving-knight-safaris/'
PAN = '/panorama-tours-packages-and-pricing/'
DAY = '/day-trips-near-mjejane/'
WILD = '/wildlife-and-sightings/'
REV = '/guest-reviews/'

PAGES = {
    # ---------------- STAY ----------------
    STAY: ('The Lodge', None, S, 'Five king en-suite rooms, an infinity pool and the Crocodile River at your feet.'),
    '/rooms-and-suites/': ('Rooms & Suites', STAY, S, 'Five en-suite king rooms for up to 10 guests, one wheelchair-friendly.'),
    '/facilities/': ('Rates & Facilities', STAY, S, 'Nightly rates for the whole lodge and everything it includes.'),
    '/mjejane-accommodation-specials/': ('Specials', STAY, S, 'Stay 3 nights and get the 4th night at 50% off in the low season.'),
    '/mjejane-accommodation-prices-and-packages/': ('5-Night Packages', STAY, S, 'Five nights at the lodge with two free game drives.'),
    '/self-catering-getaway-in-mpumalanga/': ('Bush Getaway', STAY, S, 'A private bush getaway in Mpumalanga, 4 hours from Johannesburg.'),
    '/self-catering-family-retreat-in-mpumalanga/': ('Family Retreat', STAY, S, 'A family-friendly self-catering retreat with a pool over the river.'),
    '/self-catering-guide/': ('Self-Catering Guide', STAY, S, 'The kitchen, the braai areas and the boma, and what to bring.'),
    '/gallery/': ('Gallery', STAY, S, 'The lodge, the river and recent sightings in photos.'),
    REV: ('Guest Reviews', STAY, S, 'What guests say on Google, Booking.com and Facebook.'),
    '/accommodation-near-malelane/': ('Near Malelane', STAY, S, "About 38 minutes' drive from Malelane along the N4."),
    '/accommodation-near-komatipoort/': ('Near Komatipoort', STAY, S, "About 38 minutes' drive from Komatipoort along the N4."),
    # legacy testimonial pages live under Guest Reviews
    '/testimonial-item/708/': ('708', REV, S, ''),
    '/testimonial-item/an-african-winter-wonderland/': ('An African Winter Wonderland', REV, S, ''),
    '/testimonial-item/best-experience-and-atmosphere/': ('Best Experience and Atmosphere', REV, S, ''),
    '/testimonial-item/everything-was-better-than-it-looks-in-the-pictures/': ('Better Than the Pictures', REV, S, ''),
    '/testimonial-item/i-will-be-coming-back/': ('I Will Be Coming Back', REV, S, ''),
    '/testimonial-item/it-surpassed-all-our-expectations/': ('It Surpassed All Our Expectations', REV, S, ''),
    '/testimonial-item/no-camera-in-the-world-could-capture-the-beauty-of-this-place/': ('No Camera Could Capture It', REV, S, ''),
    '/testimonial-item/truly-a-five-star-authentic-african-experience/': ('A Five-Star African Experience', REV, S, ''),

    # ---------------- ACTIVITIES ----------------
    ACT: ('Activities', None, A, 'Everything to do from the lodge, in the reserve and beyond.'),
    # In the Mjejane
    '/game-drive-mjejane-game-reserve/': ('Private Game Drives', ACT, A, 'Three-hour drives in the Mjejane in the lodge\'s 10-seater game viewer.'),
    '/guided-bush-walks-kruger-national-park/': ('Guided Bush Walks', ACT, A, 'Walking safaris in the Mjejane every Tuesday, Thursday and Saturday.'),
    '/mjejane-game-reserve-birding-guide/': ('Birding Guide', ACT, A, 'More than 330 bird species recorded in the Mjejane.'),
    '/mjejane-mobile-bush-spa/': ('Bush Spa', ACT, A, 'Mobile spa therapists who come to you at the lodge.'),
    '/kingsland-recreational-area/': ('Kingsland', ACT, A, 'Walking trails, a mountain-bike route and a bush braai in the reserve.'),
    # Kruger & Panorama
    KTP: ('Kruger Tours & Packages', ACT, A, 'Every Kruger and Panorama tour from the lodge, with packages compared.'),
    '/full-and-half-day-game-drive-in-the-kruger-park/': ('Kruger Day Drives', KTP, A, 'Full- and half-day game drives in the Kruger National Park.'),
    '/kruger-private-drives-special-khoza/': ('Drives with Special Khoza', KTP, A, 'Private Kruger drives with ranger Special Khoza.'),
    IK: ('Irving Knight Safaris', KTP, A, 'Four nights at the lodge with a full-day Kruger safari by Irving Knight.'),
    PAN: ('Panorama Tours', KTP, A, "God's Window, Bourke's Luck Potholes and the Blyde River Canyon."),
    '/kruger-full-day-safari-with-irving-knight-safaris-at-jacana-river-lodge-1-week/': ('Irving Knight: 1 Week', IK, A, 'Four nights, Monday to Thursday, with a full-day Kruger safari.'),
    '/kruger-full-day-safari-with-irving-knight-safaris-at-jacana-river-lodge-weekend/': ('Irving Knight: Weekend', IK, A, 'Four nights, Thursday to Sunday, with a full-day Kruger safari.'),
    '/kruger-full-day-safari-with-lihlosi-safaris-at-jacana-river-lodge-1-week/': ('Lihlosi: 1 Week', KTP, A, 'Four nights, Monday to Thursday, with a Lihlosi Kruger safari.'),
    '/kruger-full-day-safari-with-lihlosi-safaris-at-jacana-river-lodge-weekend/': ('Lihlosi: Weekend', KTP, A, 'Four nights, Thursday to Sunday, with a Lihlosi Kruger safari.'),
    '/kruger-and-panorama-route-tour-week/': ('Kruger & Panorama: 1 Week', PAN, A, 'Four nights, Monday to Thursday, with a full-day Panorama Route tour.'),
    '/kruger-and-panorama-route-tour-weekend/': ('Kruger & Panorama: Weekend', PAN, A, 'Four nights, Thursday to Sunday, with a full-day Panorama Route tour.'),
    # Nearby & day trips
    DAY: ('Day Trips', ACT, A, 'Graskop Gorge Lift, Chimp Eden, Jabulani and the Panorama Route.'),
    '/golf-near-kruger/': ('Golf near the Kruger', DAY, A, 'Kambaku, Malelane and Leopard Creek.'),

    # ---------------- MJEJANE RESERVE ----------------
    RES: ('Mjejane Reserve', None, R, 'The private reserve on the Kruger\'s southern boundary.'),
    WILD: ('Wildlife & Sightings', RES, R, 'What lives in the Mjejane and what guests have seen.'),
    '/big-5-safari-mjejane/': ('The Big 5', RES, R, 'Lion, leopard, elephant, rhino and buffalo in the Mjejane.'),
    '/best-time-to-visit-kruger/': ('Best Time to Visit', RES, R, 'The seasons in the southern Kruger, month by month.'),
    '/mjejane-bridge-entrance-to-knp/': ('Bridge to the Kruger', RES, R, 'How the Mjejane bridge entrance to the Kruger works.'),
    '/rules-and-safety/': ('Rules & Safety', RES, R, 'The lodge and reserve rules every guest signs.'),
    '/wildlife-and-sightings/sightings/': ('Sightings', WILD, R, 'Wildlife experiences of our guests and rangers.'),
    '/wildlife-and-sightings/wildlife-in-mjejane/': ('Wildlife in the Mjejane', WILD, R, 'The animals that live in the reserve.'),
    '/portfolio-item/mjejane-dam/': ('The Mjejane Dam', WILD, R, 'A sundowner spot with hippo, crocodile and elephant.'),
    '/portfolio-item/our-lion-pride/': ('Our Lion Pride', WILD, R, 'A photo story of the resident lions.'),
    '/portfolio-item/verreaux-eagle-owls/': ("Verreaux's Eagle-Owls", WILD, R, 'A photo story of the eagle-owls.'),

    # ---------------- outside the silos ----------------
    '/': ('Home', None, None, ''),
    '/book-now/': ('Book Now', None, None, 'Send your dates and we confirm availability.'),
    '/contact-us/': ('Contact Us', None, None, 'Phone, WhatsApp and email for the lodge.'),
    '/directions/': ('Directions', None, None, 'How to reach the lodge by road or air.'),
    '/faq/': ('FAQ', None, None, 'Answers about the lodge, rates, activities and the reserve.'),
    '/news/': ('News', None, None, ''),
    '/backlinks/': ('Useful Links', None, None, ''),
    '/cookies-and-privacy-policy/': ('Cookies & Privacy Policy', None, None, ''),
    '/thank-you/': ('Thank You', None, None, ''),
    '/thank-you-for-your-booking-enquiry/': ('Thank You', None, None, ''),
    '/activities/': ('Activities', None, A, ''),  # live duplicate of the hub; copied by seo.py
}

PLAN = ['/book-now/', '/contact-us/', '/directions/', '/faq/']

# Menu: (label, hub url, [(group heading or None, [urls])])
MENU = [
    ('Stay', STAY, [(None, [STAY, '/rooms-and-suites/', '/facilities/', '/mjejane-accommodation-specials/',
                           '/mjejane-accommodation-prices-and-packages/', '/self-catering-getaway-in-mpumalanga/',
                           '/self-catering-family-retreat-in-mpumalanga/', '/self-catering-guide/', '/gallery/', REV])]),
    ('Activities', ACT, [
        ('In the Mjejane', ['/game-drive-mjejane-game-reserve/', '/guided-bush-walks-kruger-national-park/',
                            '/mjejane-game-reserve-birding-guide/', '/mjejane-mobile-bush-spa/', '/kingsland-recreational-area/']),
        ('Kruger &amp; Panorama', [KTP, '/full-and-half-day-game-drive-in-the-kruger-park/',
                                   '/kruger-private-drives-special-khoza/', IK, PAN]),
        ('Nearby', [DAY, '/golf-near-kruger/']),
    ]),
    ('Mjejane Reserve', RES, [(None, [RES, WILD, '/big-5-safari-mjejane/', '/best-time-to-visit-kruger/',
                                     '/mjejane-bridge-entrance-to-knp/', '/rules-and-safety/'])]),
]
MENU_LINKS = [('News', '/news/'), ('Contact Us', '/contact-us/')]


def silo_of(url):
    return PAGES.get(url, (None, None, None, None))[2]


def chain(url):
    """[url, parent, grandparent, ...] up to the silo hub."""
    out = [url]
    while url in PAGES and PAGES[url][1]:
        url = PAGES[url][1]
        out.append(url)
    return out


def children(url):
    return [u for u, v in PAGES.items() if v[1] == url]
