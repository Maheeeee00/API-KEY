# API-KEY

## Airport Passes booking form

| Artifact | Purpose |
|----------|---------|
| `airport-passes-booking-form.html` | Full Elementor-ready HTML/CSS/JS multi-step form. |
| `wordpress/airport-passes-booking/` | WordPress plugin: **automatic** team + customer emails via `wp_mail` (required for auto-confirmation). |
| `WORDPRESS-BOOKING-EMAIL.md` | How to install the plugin and why `mailto` alone cannot auto-email. |

Paste the HTML into an Elementor HTML widget, install and activate the plugin on the same site, and configure SMTP if needed so `wp_mail` delivers reliably.
