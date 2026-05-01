# Omaha Roofing Experts — Owner notes

Quick reference when you hand off the site or swap contact routing.

## 1. Primary: `contact-config.js`

Edit this file and redeploy. `contact-apply.js` reads it on every page load and applies:

| Field | What it drives |
|--------|----------------|
| **`formSubmitEmail`** | Lead forms (FormSubmit) — submissions email this inbox |
| **`contactMailbox`** | All `mailto:` links on the site (public email line) |
| **`phone.href`** | Every click-to-call `tel:` link |
| **`phone.display`** | Labels like “Call …”, “Tap to Call …”, and plain-number links marked with helper classes |

## 2. Keep HTML fallbacks in sync (optional but good)

Forms also have a static `action="https://formsubmit.co/…"` URL. Copy the same Gmail (or tenant inbox) here so submits still work before JS loads:

- Search the repo for `formsubmit.co/` and replace the email segment if needed.

## 3. Homepage schema (`index.html`)

After changing phone or public email, update the JSON‑LD block (search for `application/ld+json`):

- `telephone` — align with **`phone`** in config (formatted like `+1-281-622-5095`)
- `email` — usually same idea as **`contactMailbox`**

## 4. FormSubmit

- First time a recipient inbox is used, FormSubmit sends a **confirmation** to that inbox; click it before expecting leads.
- [FormSubmit docs](https://formsubmit.co)

## 5. `contact@` at your domain

The site shows **`contact@omaharoofingexperts.com`** in mailto links. Incoming mail depends on **DNS** (forwarding alias or mailbox), e.g. Cloudflare Email Routing → your Gmail. The HTML does not configure that—it’s set at the domain/host.

---

**Deploy:** Push to your host (same branch you use for production) so `/contact-config.js` updates go live.
