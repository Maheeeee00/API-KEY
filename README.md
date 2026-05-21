# API-KEY

## Airport Passes booking form

| Artifact | Purpose |
|----------|---------|
| `airport-passes-booking-form.html` | Full standalone HTML document (includes optional WordPress AJAX email if `AP_MEGA_BOOKING_AJAX` exists). |
| `airport-passes-booking-form-elementor.html` | Elementor HTML widget version (no `<html>` wrapper), with optional AJAX if the plugin is active. |
| **`airport-passes-booking-form-standalone-mailto.html`** | **Full page, mailto only** — no plugin, no AJAX. |
| **`airport-passes-booking-form-elementor-standalone-mailto.html`** | **Elementor widget, mailto only** — paste this for a popup **without** the WordPress email plugin. |
| **`airport-passes-booking.zip`** | WordPress plugin ZIP (server-side automatic email). |
| `wordpress/airport-passes-booking/` | Plugin source folder. |
| `WORDPRESS-BOOKING-EMAIL.md` | Install and troubleshooting (plugin + SMTP). |

**mailto-only:** use **`airport-passes-booking-form-elementor-standalone-mailto.html`** in the popup. Email opens the visitor’s mail app twice (team + confirmation); nothing sends until they press Send.

**Automatic email:** use the plugin + **`airport-passes-booking-form-elementor.html`** and SMTP.
