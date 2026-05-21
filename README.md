# API-KEY

## Airport Passes booking form

| Artifact | Purpose |
|----------|---------|
| `airport-passes-booking-form.html` | Full standalone HTML document (test page or special embeds). |
| `airport-passes-booking-form-elementor.html` | **Recommended for Elementor HTML widgets** (style + markup + script only — no nested `<html>` / `<body>`). |
| `wordpress/airport-passes-booking/` | WordPress plugin: **automatic** team + customer emails via `wp_mail` (required for auto-confirmation). |
| `WORDPRESS-BOOKING-EMAIL.md` | Install steps, Elementor notes, and email troubleshooting. |

Paste **`airport-passes-booking-form-elementor.html`** into the popup’s HTML widget, install and activate the plugin on the same site, and configure SMTP so `wp_mail` delivers reliably.
