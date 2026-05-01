/**
 * Applies SITE_CONTACT from contact-config.js:
 * - Lead forms (data-lead-form) → FormSubmit → formSubmitEmail
 * - All mailto: → contactMailbox
 * - All tel: hrefs → phone.href
 * - Elements with classes below → phone.display text helpers
 */
(function () {
  function apply() {
    var C = window.SITE_CONTACT;
    if (!C) return;

    if (C.formSubmitEmail) {
      var encoded = encodeURIComponent(C.formSubmitEmail);
      document.querySelectorAll("form[data-lead-form]").forEach(function (form) {
        form.setAttribute("action", "https://formsubmit.co/" + encoded);
      });
    }

    if (C.contactMailbox) {
      document.querySelectorAll('a[href^="mailto:"]').forEach(function (a) {
        a.setAttribute("href", "mailto:" + C.contactMailbox);
        a.textContent = C.contactMailbox;
      });
    }

    if (C.phone && C.phone.href) {
      document.querySelectorAll('a[href^="tel:"]').forEach(function (a) {
        a.setAttribute("href", C.phone.href);
      });
    }

    if (C.phone && C.phone.display) {
      var d = C.phone.display;
      document.querySelectorAll(".js-phone-display").forEach(function (el) {
        el.textContent = d;
      });
      document.querySelectorAll(".js-phone-call-label").forEach(function (el) {
        el.textContent = "Call " + d;
      });
      document.querySelectorAll(".js-phone-tap-label").forEach(function (el) {
        el.textContent = "Tap to Call " + d;
      });
      document.querySelectorAll(".js-phone-inline").forEach(function (el) {
        el.textContent = d;
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", apply);
  } else {
    apply();
  }
})();
