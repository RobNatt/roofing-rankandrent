"""
Static site builder for omaharoofingexperts.com.

Run from the repo root:   python _src/build.py
It rewrites every page's index.html, sitemap.xml and robots.txt from the
page list below and the content fragments in _src/content/.

_src/ is excluded from the Vercel deploy by .vercelignore.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = pathlib.Path(__file__).resolve().parent / "content"
SITE = "https://www.omaharoofingexperts.com"
BRAND = "Omaha Roofing Experts"
PHONE_HREF = "tel:+14027726658"
PHONE_DISPLAY = "(402) 772-6658"
PHONE_SCHEMA = "+1-402-772-6658"
EMAIL = "contact@omaharoofingexperts.com"
LASTMOD = "2026-11-15"
GA_ID = "G-D5QE6Q32P3"

DISCLOSURE = (
    "Omaha Roofing Experts is a referral service; work is performed by "
    "independent roofing contractors. Nebraska requires contractors to register "
    "with the state Department of Labor, and you can check any contractor in its "
    '<a href="https://dol.nebraska.gov/conreg/Search" rel="noopener">registration search</a>.'
)

AREA = ["Omaha", "Bellevue", "Papillion", "La Vista", "Ralston", "Elkhorn", "Bennington"]

# ---------------------------------------------------------------------------
# Lead forms. The four original forms are kept byte-for-byte (action, hidden
# fields, field names, ids and button text). New pages reuse the homepage form
# with their own _subject and _next values.
# ---------------------------------------------------------------------------
FORM_HOME = """<form
              class="w-full max-w-md rounded-2xl border border-neutral-200 bg-neutral-50 p-6 text-left shadow-sm"
              data-lead-form
              action="https://formsubmit.co/robnattrass429@gmail.com"
              method="POST"
            >
              <input type="hidden" name="_subject" value="{subject}" />
              <input type="hidden" name="_next" value="{next}" />
              <input type="hidden" name="_captcha" value="false" />
              <div class="space-y-4">
                <div>
                  <label for="name" class="block text-sm font-semibold text-ink">Name</label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    autocomplete="name"
                    class="mt-1 w-full rounded-lg border border-neutral-300 bg-white px-4 py-3 text-ink shadow-sm focus:border-cta focus:outline-none focus:ring-2 focus:ring-cta/30"
                  />
                </div>
                <div>
                  <label for="phone" class="block text-sm font-semibold text-ink">Phone</label>
                  <input
                    id="phone"
                    name="phone"
                    type="tel"
                    required
                    autocomplete="tel"
                    class="mt-1 w-full rounded-lg border border-neutral-300 bg-white px-4 py-3 text-ink shadow-sm focus:border-cta focus:outline-none focus:ring-2 focus:ring-cta/30"
                  />
                </div>
                <div>
                  <label for="message" class="block text-sm font-semibold text-ink">Message</label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows="4"
                    class="mt-1 w-full rounded-lg border border-neutral-300 bg-white px-4 py-3 text-ink shadow-sm focus:border-cta focus:outline-none focus:ring-2 focus:ring-cta/30"
                  ></textarea>
                </div>
                <button
                  type="submit"
                  class="w-full min-h-[48px] rounded-lg bg-cta py-3 text-base font-semibold text-white shadow-md transition hover:bg-orange-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cta"
                >
                  Request Free Estimate
                </button>
              </div>
            </form>"""

FORM_SERVICE = """<form
              class="w-full max-w-md rounded-2xl border border-neutral-200 bg-neutral-50 p-6 text-left{shadow}"
              data-lead-form
              action="https://formsubmit.co/robnattrass429@gmail.com"
              method="POST"
            >
              <input type="hidden" name="_subject" value="{subject}" />
              <input type="hidden" name="_next" value="{next}" />
              <input type="hidden" name="_captcha" value="false" />
              <label {a1}>Name</label>
              <input id="name" name="name" type="text" required class="mt-1 w-full rounded-lg border border-neutral-300 px-4 py-3 focus:border-cta focus:outline-none focus:ring-2 focus:ring-cta/30" />
              <label {a2}>Phone</label>
              <input id="phone-field" name="phone" type="tel" required class="mt-1 w-full rounded-lg border border-neutral-300 px-4 py-3 focus:border-cta focus:outline-none focus:ring-2 focus:ring-cta/30" />
              <label {a3}>Message</label>
              <textarea id="message" name="message" rows="4" required class="mt-1 w-full rounded-lg border border-neutral-300 px-4 py-3 focus:border-cta focus:outline-none focus:ring-2 focus:ring-cta/30"></textarea>
              <button type="submit" class="mt-4 w-full min-h-[48px] rounded-lg bg-cta py-3 font-semibold text-white hover:bg-orange-600">{button}</button>
            </form>"""


def service_form(subject, nxt, button, emergency=False, shadow=""):
    if emergency:  # emergency page had for= before class=
        a1 = 'for="name" class="block text-sm font-semibold"'
        a2 = 'for="phone-field" class="mt-4 block text-sm font-semibold"'
        a3 = 'for="message" class="mt-4 block text-sm font-semibold"'
    else:
        a1 = 'class="block text-sm font-semibold" for="name"'
        a2 = 'class="mt-4 block text-sm font-semibold" for="phone-field"'
        a3 = 'class="mt-4 block text-sm font-semibold" for="message"'
    return FORM_SERVICE.format(subject=subject, next=nxt, button=button, a1=a1, a2=a2, a3=a3, shadow=shadow)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
PAGES = [
    dict(
        path="/",
        file="home.html",
        kind="home",
        title="Omaha Roofing Repair & Replacement | Omaha Roofing Experts",
        description="Roof leak, storm damage or emergency in Omaha? Call (402) 772-6658 and we'll connect you with a local roofing contractor. Free Omaha roofing guides.",
        eyebrow="Omaha, Nebraska roofing help",
        h1="Find a Local Omaha Roofer for Repairs, Leaks and Storm Damage",
        intro="Omaha Roofing Experts connects Omaha homeowners with local roofing contractors. Tell us what is going on with your roof and we will pass your request to an independent contractor who serves your area.",
        hero=("roofer-homeowner-house", 1200, "Roofer in a hard hat going over a clipboard with a homeowner outside a house with a ladder on the roof"),
        form=FORM_HOME.format(subject="Omaha Roofing — New lead (home)", next=f"{SITE}/?sent=1#contact"),
        crumbs=[],
    ),
    dict(
        path="/emergency-roof-repair-omaha/",
        file="emergency.html",
        kind="service",
        service_name="Emergency roof repair",
        title="Emergency Roof Repair Omaha | Call (402) 772-6658",
        description="Roof leaking or storm-damaged right now? Call (402) 772-6658 to reach a local Omaha roofer who can tarp it. Plus what to do in the first hour.",
        eyebrow="Emergency roof repair",
        h1="Emergency Roof Repair in Omaha, NE",
        intro="Water coming through the ceiling, shingles torn off in a storm, or a branch through the roof? Call and we will connect you with a local Omaha roofing contractor who can tarp or patch the damage.",
        hero=("roofer-safety-harness", 1200, "Roofer in a hard hat and safety harness talking with a homeowner beside a ladder"),
        form=service_form("Omaha Roofing — Emergency repair lead", f"{SITE}/emergency-roof-repair-omaha/?sent=1#contact", "Request emergency callback", emergency=True, shadow=" shadow-sm"),
        crumbs=[("Emergency Roof Repair", "/emergency-roof-repair-omaha/")],
    ),
    dict(
        path="/roof-leak-repair-omaha/",
        file="leak.html",
        kind="service",
        service_name="Roof leak repair",
        title="Roof Leak Repair Omaha | Call (402) 772-6658",
        description="Roof leaking in Omaha? Call (402) 772-6658 to reach a local roofer. Plus why the stain is rarely under the hole, 2026 repair costs and ice dams.",
        eyebrow="Roof leak repair",
        h1="Roof Leak Repair in Omaha, NE",
        intro="A brown ring on the ceiling or a drip during rain usually means water is getting past the shingles somewhere. Here is how leaks happen on Omaha roofs, how a roofer finds them, and how to get one out to your home.",
        hero=("roofer-shingle-sample", 800, "Roofer holding a shingle sample while explaining roof damage to a homeowner"),
        form=service_form("Omaha Roofing — Roof leak lead", f"{SITE}/roof-leak-repair-omaha/?sent=1#contact", "Request leak repair"),
        crumbs=[("Roof Leak Repair", "/roof-leak-repair-omaha/")],
    ),
    # Added 24 Nov 2026: "roof repair omaha" had 407 Google views since launch
    # and no page (Search Console). Costs are This Old House 2026 national
    # figures, labelled as national; no source publishes Omaha-only repair prices.
    dict(
        path="/roof-repair-omaha/",
        file="repair.html",
        kind="service",
        service_name="Roof repair",
        title="Roof Repair Omaha: 2026 Costs | Call (402) 772-6658",
        description="Most minor roof repairs cost $150 to $1,000. What changes the price, how to check an Omaha quote, and a local roofer. Call (402) 772-6658.",
        eyebrow="Roof repair",
        h1="Roof Repair in Omaha, NE: Costs and What to Expect",
        intro="Shingles blown off, a leak around the chimney, or hail damage after a storm? Here is what roof repairs typically cost, what changes the price, how to tell whether a quote is fair, and how to get a local Omaha roofer out to your home.",
        hero=("roofer-shingle-sample", 800, "Roofer holding a shingle sample while explaining roof damage to a homeowner"),
        form=service_form("Omaha Roofing — Roof repair lead", f"{SITE}/roof-repair-omaha/?sent=1#contact", "Request a repair quote"),
        crumbs=[("Roof Repair", "/roof-repair-omaha/")],
    ),
    dict(
        path="/storm-damage-roofing-omaha/",
        file="storm.html",
        kind="service",
        service_name="Storm and hail damage roofing",
        title="Storm & Hail Damage Roofing Omaha | Omaha Roofing Experts",
        description="Hail or wind hit your Omaha roof? How to spot real hail damage, what to do before you call your insurer, Nebraska rules on storm contractors, and local help.",
        eyebrow="Hail and wind damage",
        h1="Storm and Hail Damage Roofing in Omaha, NE",
        intro="Hail and high wind are the most common reasons Omaha homeowners need roof work. Here is how to tell whether a storm actually damaged your roof, what to do next, and how to get a local roofer to inspect it.",
        hero=("roofer-homeowner-house", 1200, "Roofer in a hard hat going over a clipboard with a homeowner outside a house with a ladder on the roof"),
        form=service_form("Omaha Roofing — Storm damage lead", f"{SITE}/storm-damage-roofing-omaha/?sent=1#contact", "Request inspection"),
        crumbs=[("Storm Damage Roofing", "/storm-damage-roofing-omaha/")],
    ),
    dict(
        path="/guides/",
        file="guides.html",
        kind="collection",
        title="Omaha Roofing Guides: Hail Claims, Costs, Repair vs Replace",
        description="Plain-English roofing guides for Omaha homeowners: hail damage insurance claims, roof replacement cost with sourced 2025-2026 figures, and repair vs replacement.",
        eyebrow="Guides",
        h1="Omaha Roofing Guides",
        intro="Plain-English guides for Omaha homeowners. Every cost or insurance figure links to its source and says what year it is from.",
        hero=None,
        form=FORM_HOME.format(subject="Omaha Roofing — Guides lead", next=f"{SITE}/guides/?sent=1#contact"),
        crumbs=[("Guides", "/guides/")],
    ),
    dict(
        path="/guides/hail-damage-roof-insurance-claim-omaha/",
        file="guide-hail.html",
        kind="article",
        title="Hail Damage Roof Insurance Claims in Omaha: Step by Step",
        description="Step-by-step hail damage roof insurance claims in Omaha: checking damage, deductibles, the adjuster, ACV vs replacement cost and Nebraska contractor law.",
        eyebrow="Guide",
        h1="Hail Damage Roof Insurance Claims in Omaha: Step by Step",
        intro="Hail hit your neighborhood and now you are wondering whether to file a claim. This guide walks through the whole process in order, using guidance from the Nebraska Department of Insurance and the Nebraska statutes that apply to storm repair contracts.",
        hero=None,
        form=FORM_HOME.format(subject="Omaha Roofing — Hail claim guide lead", next=f"{SITE}/guides/hail-damage-roof-insurance-claim-omaha/?sent=1#contact"),
        crumbs=[("Guides", "/guides/"), ("Hail Damage Insurance Claims", "/guides/hail-damage-roof-insurance-claim-omaha/")],
    ),
    dict(
        path="/guides/roof-replacement-cost-omaha/",
        file="guide-cost.html",
        kind="article",
        title="Roof Replacement Cost in Omaha (2025-2026 Sourced Figures)",
        description="What a roof replacement costs in Omaha, using 2025 Cost vs Value data for Omaha and 2026 Nebraska figures, why quotes vary so much, and how to compare bids.",
        eyebrow="Guide",
        h1="Roof Replacement Cost in Omaha",
        intro="Published roof prices for Omaha range from under $6,000 to over $30,000, and both ends can be right. This guide shows where the numbers come from, what drives the spread, and how to read the quotes you get.",
        hero=None,
        form=FORM_HOME.format(subject="Omaha Roofing — Cost guide lead", next=f"{SITE}/guides/roof-replacement-cost-omaha/?sent=1#contact"),
        crumbs=[("Guides", "/guides/"), ("Roof Replacement Cost", "/guides/roof-replacement-cost-omaha/")],
    ),
    dict(
        path="/guides/roof-repair-or-replacement/",
        file="guide-repair-replace.html",
        kind="article",
        title="Roof Repair or Replacement? How to Decide (Omaha Guide)",
        description="Should you repair or replace your roof? A plain-English checklist for Omaha homeowners: age, damage spread, decking, leaks, insurance, costs and timing.",
        eyebrow="Guide",
        h1="Roof Repair or Replacement? How to Decide",
        intro="Most roof problems can be repaired. Some cannot, and paying for repair after repair on a worn-out roof is money you will not get back. Use this guide to work out which side of that line your roof is on.",
        hero=None,
        form=FORM_HOME.format(subject="Omaha Roofing — Repair or replace guide lead", next=f"{SITE}/guides/roof-repair-or-replacement/?sent=1#contact"),
        crumbs=[("Guides", "/guides/"), ("Repair or Replacement", "/guides/roof-repair-or-replacement/")],
    ),
    # Added 24 Nov 2026 from the findquestions.com roofing list (hiring and
    # vetting cluster). Statute text checked on nebraskalegislature.gov that day.
    dict(
        path="/guides/how-to-hire-a-roofer-omaha/",
        file="guide-hire.html",
        kind="article",
        title="How to Hire a Roofer in Omaha Without Getting Scammed",
        description="Hiring a roofer in Omaha: check Nebraska registration and insurance, questions to ask, what the contract must say, your rights under state law, red flags.",
        eyebrow="Guide",
        h1="How to Hire a Roofer in Omaha Without Getting Scammed",
        intro="After a hailstorm, Omaha fills with roofing trucks, and most of them are honest. This guide shows how to check the one you are talking to, what to ask, what the contract should say, and the rights Nebraska law gives you when insurance is paying.",
        hero=None,
        form=FORM_HOME.format(subject="Omaha Roofing — Hiring guide lead", next=f"{SITE}/guides/how-to-hire-a-roofer-omaha/?sent=1#contact"),
        crumbs=[("Guides", "/guides/"), ("How to Hire a Roofer", "/guides/how-to-hire-a-roofer-omaha/")],
    ),
]

NAV_SERVICES = [
    ("Roof repair", "/roof-repair-omaha/"),
    ("Emergency roof repair", "/emergency-roof-repair-omaha/"),
    ("Roof leak repair", "/roof-leak-repair-omaha/"),
    ("Storm and hail damage", "/storm-damage-roofing-omaha/"),
]
NAV_GUIDES = [
    ("All guides", "/guides/"),
    ("How to hire a roofer", "/guides/how-to-hire-a-roofer-omaha/"),
    ("Hail damage insurance claims", "/guides/hail-damage-roof-insurance-claim-omaha/"),
    ("Roof replacement cost in Omaha", "/guides/roof-replacement-cost-omaha/"),
    ("Repair or replacement?", "/guides/roof-repair-or-replacement/"),
]

# ---------------------------------------------------------------------------
CSS = """
:root{--ink:#1a1a1a;--muted:#4b4b4b;--line:#e3e3e3;--soft:#f6f6f4;--cta:#c2410c;--cta-d:#9a3412;--link:#b23c08;--dark:#1a1a1a}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:#fff;line-height:1.65;font-size:17px}
img{max-width:100%;height:auto;display:block}
a{color:var(--link);text-underline-offset:2px}
h1,h2,h3{line-height:1.2;letter-spacing:-.01em}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
.narrow{max-width:760px;margin:0 auto;padding:0 16px}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:99}
header.site{position:sticky;top:0;z-index:50;background:#fff;border-bottom:1px solid var(--line);box-shadow:0 1px 3px rgba(0,0,0,.05)}
.hdr{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 16px;max-width:1100px;margin:0 auto}
.brand{font-weight:800;color:var(--ink);text-decoration:none;font-size:1.05rem;line-height:1.15}
.hdr nav{display:flex;align-items:center;gap:16px}
.navlink{color:var(--ink);text-decoration:none;font-weight:600;font-size:.95rem}
@media (max-width:560px){.navlink{display:none}}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:12px 22px;border-radius:10px;font-weight:700;text-decoration:none;border:2px solid transparent;font-size:1rem;line-height:1.2;text-align:center}
.btn-cta{background:var(--cta);color:#fff}.btn-cta:hover{background:var(--cta-d)}
.btn-ghost{border-color:var(--ink);color:var(--ink);background:#fff}.btn-ghost:hover{background:var(--soft)}
.btn-sm{min-height:44px;padding:8px 14px;font-size:.92rem;white-space:nowrap}
.hero{padding:28px 0 8px;text-align:center;border-bottom:1px solid var(--line)}
.hero.text-only{padding-bottom:28px}
.eyebrow{margin:0;color:var(--cta);font-weight:700;font-size:.85rem;text-transform:uppercase;letter-spacing:.05em}
.hero h1{font-size:clamp(1.8rem,5.5vw,3rem);margin:.4em auto .35em;max-width:20em}
.lede{font-size:1.1rem;color:var(--muted);max-width:40em;margin:0 auto}
.actions{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:22px 0 0}
.hero-img{margin:26px auto 20px;max-width:900px;border-radius:14px;overflow:hidden;border:1px solid var(--line);aspect-ratio:16/9;background:#e9e7e2}
.hero-img img{width:100%;height:100%;object-fit:cover}
.crumbs{font-size:.88rem;color:var(--muted);margin:0 0 6px}
.crumbs ol{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px;justify-content:center}
.crumbs li+li:before{content:"/";margin-right:6px;color:#999}
.crumbs a{color:var(--muted)}
.band{background:var(--soft);border-bottom:1px solid var(--line);padding:12px 16px;text-align:center;font-weight:600}
.band a{white-space:nowrap}
.prose{padding:32px 16px 8px}
.prose h2{font-size:1.5rem;margin:1.8em 0 .5em}
.prose h3{font-size:1.15rem;margin:1.5em 0 .4em}
.prose p,.prose li{color:#262626}
.prose ul,.prose ol{padding-left:1.3em}
.prose li{margin:.35em 0}
.prose table{width:100%;border-collapse:collapse;margin:1em 0;font-size:.95rem}
.prose th,.prose td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
.prose th{background:var(--soft)}
.table-scroll{overflow-x:auto}
.example{border-left:4px solid var(--cta);background:#fff7f2;padding:12px 16px;border-radius:0 10px 10px 0;margin:1.2em 0}
.example strong:first-child{display:inline-block;background:var(--cta);color:#fff;font-size:.75rem;letter-spacing:.06em;padding:2px 8px;border-radius:4px;margin-right:6px}
.note{background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:12px 16px;font-size:.95rem}
.cta-box{margin:2em 0;padding:20px;border-radius:14px;background:var(--dark);color:#fff;text-align:center}
.cta-box p{color:#e8e8e8;margin:.2em 0 .9em}
.cta-box .h{font-size:1.25rem;font-weight:800;color:#fff;margin:0}
.cta-box a.link-light{color:#fff}
.grid{display:grid;gap:18px;grid-template-columns:1fr}
@media (min-width:700px){.grid-3{grid-template-columns:repeat(3,1fr)}.grid-2{grid-template-columns:repeat(2,1fr)}}
.card{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff;display:flex;flex-direction:column}
.card img{aspect-ratio:16/9;object-fit:cover;width:100%}
.card .in{padding:16px 18px 18px}
.card h3{margin:0 0 .3em;font-size:1.15rem}
.card p{margin:0 0 .6em;color:var(--muted)}
.section{padding:36px 0}
.section h2{font-size:1.6rem;margin:0 0 .5em}
.steps{counter-reset:s;list-style:none;padding:0}
.steps li{counter-increment:s;position:relative;padding-left:46px;margin:0 0 14px}
.steps li:before{content:counter(s);position:absolute;left:0;top:0;width:32px;height:32px;border-radius:50%;background:var(--cta);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center}
.related{padding:8px 16px 24px}
.related ul{padding-left:1.2em}
.sources{font-size:.9rem;color:var(--muted)}
.sources li{color:var(--muted)}
.contact{background:var(--soft);border-top:1px solid var(--line);padding:40px 0;text-align:center}
.contact h2{font-size:1.7rem;margin:0 0 .3em}
.contact-row{display:flex;flex-direction:column;align-items:center;gap:28px;margin-top:24px}
@media (min-width:900px){.contact-row{flex-direction:row;justify-content:center;align-items:flex-start}}
.callbox{max-width:360px}
.callbox p{color:var(--muted);font-size:.95rem}
form[data-lead-form]{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px;text-align:left;width:100%;max-width:440px;box-shadow:0 1px 3px rgba(0,0,0,.05)}
form[data-lead-form] label{display:block;font-weight:600;font-size:.93rem;margin-top:12px}
form[data-lead-form] input:not([type=hidden]),form[data-lead-form] textarea{display:block;width:100%;margin-top:4px;padding:12px 14px;border:1px solid #b5b5b5;border-radius:8px;font:inherit;background:#fff;color:var(--ink)}
form[data-lead-form] input:focus,form[data-lead-form] textarea:focus{outline:3px solid rgba(194,65,12,.35);border-color:var(--cta)}
form[data-lead-form] button{margin-top:18px;width:100%;min-height:48px;border:0;border-radius:10px;background:var(--cta);color:#fff;font-weight:700;font-size:1rem;cursor:pointer;font-family:inherit}
form[data-lead-form] button:hover{background:var(--cta-d)}
footer.site{border-top:1px solid var(--line);padding:32px 0 40px;font-size:.95rem;color:var(--muted)}
.fcols{display:grid;gap:20px;grid-template-columns:1fr}
@media (min-width:700px){.fcols{grid-template-columns:2fr 1fr 1fr}}
footer.site ul{list-style:none;padding:0;margin:.3em 0}
footer.site li{margin:.3em 0}
footer.site .fh{font-weight:700;color:var(--ink);margin:0}
.disclosure{margin-top:22px;padding-top:16px;border-top:1px solid var(--line);font-size:.88rem}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""


def e(s):
    return html.escape(s, quote=True)


def abs_url(path):
    return SITE + path


def place(name):
    return {
        "@type": "City",
        "name": name,
        "containedInPlace": {"@type": "State", "name": "Nebraska"},
    }


ORG = {
    "@type": "Organization",
    "@id": SITE + "/#org",
    "name": BRAND,
    "url": SITE + "/",
    "telephone": PHONE_SCHEMA,
    "email": EMAIL,
    "description": "Referral service that connects Omaha-area homeowners with independent local roofing contractors.",
}
WEBSITE = {
    "@type": "WebSite",
    "@id": SITE + "/#website",
    "name": BRAND,
    "url": SITE + "/",
    "publisher": {"@id": SITE + "/#org"},
    "inLanguage": "en-US",
}


def breadcrumb(page):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
    for i, (name, path) in enumerate(page["crumbs"], start=2):
        items.append({"@type": "ListItem", "position": i, "name": name, "item": abs_url(path)})
    return {"@type": "BreadcrumbList", "@id": abs_url(page["path"]) + "#breadcrumb", "itemListElement": items}


def schema(page):
    graph = [ORG, WEBSITE]
    url = abs_url(page["path"])
    webpage = {
        "@type": "CollectionPage" if page["kind"] == "collection" else "WebPage",
        "@id": url + "#webpage",
        "url": url,
        "name": page["title"],
        "description": page["description"],
        "isPartOf": {"@id": SITE + "/#website"},
        "breadcrumb": {"@id": url + "#breadcrumb"},
        "dateModified": LASTMOD,
    }
    graph.append(webpage)
    graph.append(breadcrumb(page))
    if page["kind"] == "home":
        graph.append({
            "@type": "Service",
            "@id": SITE + "/#service",
            "name": "Roofing contractor referrals in Omaha",
            "serviceType": "Roofing contractor referral",
            "description": "Connects homeowners in Omaha and nearby cities with independent local roofing contractors for roof repair, leak repair, emergency repair and storm damage.",
            "provider": {"@id": SITE + "/#org"},
            "areaServed": [place(c) for c in AREA],
            "url": SITE + "/",
        })
    elif page["kind"] == "service":
        graph.append({
            "@type": "Service",
            "@id": url + "#service",
            "name": page["service_name"] + " in Omaha, NE",
            "serviceType": page["service_name"],
            "description": page["description"],
            "provider": {"@id": SITE + "/#org"},
            "areaServed": [place(c) for c in AREA],
            "url": url,
        })
    elif page["kind"] == "article":
        graph.append({
            "@type": "Article",
            "@id": url + "#article",
            "headline": page["h1"],
            "description": page["description"],
            "mainEntityOfPage": {"@id": url + "#webpage"},
            "author": {"@id": SITE + "/#org"},
            "publisher": {"@id": SITE + "/#org"},
            "datePublished": LASTMOD,
            "dateModified": LASTMOD,
            "inLanguage": "en-US",
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)


def hero_img(page):
    if not page["hero"]:
        return "", ""
    name, big, alt = page["hero"]
    small = 720
    srcset = f"/images/{name}-{small}.webp {small}w, /images/{name}-{big}.webp {big}w"
    sizes = "(max-width: 932px) calc(100vw - 32px), 900px"
    preload = (
        f'<link rel="preload" as="image" type="image/webp" fetchpriority="high" '
        f'imagesrcset="{srcset}" imagesizes="{sizes}" />'
    )
    h = round(big * 9 / 16)
    img = (
        f'<figure class="hero-img"><img src="/images/{name}-{big}.webp" srcset="{srcset}" sizes="{sizes}" '
        f'width="{big}" height="{h}" alt="{e(alt)}" fetchpriority="high" decoding="async" /></figure>'
    )
    return preload, img


def cta_box():
    return f"""<aside class="cta-box" aria-label="Call for roofing help">
  <p class="h">Need a roofer to look at it?</p>
  <p>Call and we will connect you with a local Omaha roofing contractor, or send the form and get a callback.</p>
  <a href="{PHONE_HREF}" class="btn btn-cta js-phone-tap-label">Tap to Call {PHONE_DISPLAY}</a>
  <p style="margin:.8em 0 0"><a class="link-light" href="#contact">Or request a callback online</a></p>
</aside>"""


def header():
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="hdr">
    <a href="/" class="brand">{BRAND}</a>
    <nav aria-label="Main">
      <a class="navlink" href="/guides/">Guides</a>
      <a href="{PHONE_HREF}" class="btn btn-cta btn-sm js-phone-call-label">Call {PHONE_DISPLAY}</a>
    </nav>
  </div>
</header>"""


def footer():
    svc = "\n".join(f'<li><a href="{p}">{e(n)}</a></li>' for n, p in NAV_SERVICES)
    gd = "\n".join(f'<li><a href="{p}">{e(n)}</a></li>' for n, p in NAV_GUIDES)
    return f"""<footer class="site">
  <div class="wrap">
    <div class="fcols">
      <div>
        <p class="fh">{BRAND}</p>
        <p>Connecting homeowners in Omaha, Bellevue, Papillion, La Vista, Ralston, Elkhorn and Bennington with local roofing contractors.</p>
        <p><a href="{PHONE_HREF}" class="js-phone-inline">{PHONE_DISPLAY}</a><br /><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      </div>
      <div>
        <p class="fh">Services</p>
        <ul>
{svc}
        </ul>
      </div>
      <div>
        <p class="fh">Guides</p>
        <ul>
{gd}
        </ul>
      </div>
    </div>
    <p class="disclosure">{DISCLOSURE} Calling or sending the form does not create a contract; any estimate, price and warranty come from the contractor you choose to hire.</p>
  </div>
</footer>"""


def crumbs_html(page):
    if not page["crumbs"]:
        return ""
    items = ['<li><a href="/">Home</a></li>']
    for i, (name, path) in enumerate(page["crumbs"]):
        if i == len(page["crumbs"]) - 1:
            items.append(f'<li aria-current="page">{e(name)}</li>')
        else:
            items.append(f'<li><a href="{path}">{e(name)}</a></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def contact(page):
    return f"""<section id="contact" class="contact" aria-labelledby="contact-heading">
  <div class="wrap">
    <h2 id="contact-heading">Get Help With Your Roof</h2>
    <p class="lede">Call, or tell us what happened and we will pass it to a local roofing contractor serving your part of the Omaha area.</p>
    <div class="contact-row">
      <div class="callbox">
        <a href="{PHONE_HREF}" class="btn btn-cta js-phone-tap-label">Tap to Call {PHONE_DISPLAY}</a>
        <p>Prefer to write it down? Use the form and include your neighborhood or ZIP code and what you are seeing.</p>
      </div>
      {page["form"]}
    </div>
  </div>
</section>"""


def render(page):
    body = (CONTENT / page["file"]).read_text(encoding="utf-8")
    body = body.replace("{{CTA}}", cta_box())
    body = body.replace("{{PHONE}}", f'<a href="{PHONE_HREF}" class="js-phone-inline">{PHONE_DISPLAY}</a>')
    url = abs_url(page["path"])
    preload, img = hero_img(page)
    og_image = f"{SITE}/images/roofer-homeowner-house-1200.webp"
    if page["hero"]:
        og_image = f"{SITE}/images/{page['hero'][0]}-{page['hero'][1]}.webp"
    hero_cls = "hero" if page["hero"] else "hero text-only"
    is_article = page["kind"] == "article"
    ga = f"""<script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}');
      window.addEventListener('load', function () {{
        var go = function () {{ var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id={GA_ID}'; document.head.appendChild(s); }};
        if ('requestIdleCallback' in window) requestIdleCallback(go, {{ timeout: 3000 }}); else setTimeout(go, 1500);
      }});
    </script>"""
    out = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{e(page["title"])}</title>
    <meta name="description" content="{e(page["description"])}" />
    <link rel="canonical" href="{url}" />
    <meta name="robots" content="index, follow, max-image-preview:large" />
    {preload}
    <meta property="og:type" content="{'article' if is_article else 'website'}" />
    <meta property="og:site_name" content="{BRAND}" />
    <meta property="og:title" content="{e(page["title"])}" />
    <meta property="og:description" content="{e(page["description"])}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{og_image}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="675" />
    <meta property="og:locale" content="en_US" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="theme-color" content="#1a1a1a" />
    <style>{CSS.strip()}</style>
    <script type="application/ld+json">
{schema(page)}
    </script>
    <!-- Google tag (gtag.js), loaded after the page has finished loading -->
    {ga}
  </head>
  <body>
{header()}
<main id="main">
  <section class="{hero_cls}">
    <div class="wrap">
      {crumbs_html(page)}
      <p class="eyebrow">{e(page["eyebrow"])}</p>
      <h1>{e(page["h1"])}</h1>
      <p class="lede">{e(page["intro"])}</p>
      <div class="actions">
        <a href="{PHONE_HREF}" class="btn btn-cta js-phone-call-label">Call {PHONE_DISPLAY}</a>
        <a href="#contact" class="btn btn-ghost">Request a callback</a>
      </div>
      {img}
    </div>
  </section>
{body}
{contact(page)}
</main>
{footer()}
    <script src="/contact-config.js" defer></script>
    <script src="/contact-apply.js" defer></script>
  </body>
</html>
"""
    dest = ROOT / page["path"].strip("/") / "index.html" if page["path"] != "/" else ROOT / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8", newline="\n")
    return dest


def sitemap():
    urls = "\n".join(
        f"  <url>\n    <loc>{abs_url(p['path'])}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n  </url>" for p in PAGES
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8", newline="\n",
    )
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    for p in PAGES:
        print("wrote", render(p).relative_to(ROOT))
    sitemap()
    print("wrote sitemap.xml, robots.txt")
