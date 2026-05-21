# API-KEY

## Airport Passes booking form

| Artifact | Purpose |
|----------|---------|
| `airport-passes-booking-form.html` | Full standalone HTML document (test page or special embeds). |
| `airport-passes-booking-form-elementor.html` | **Recommended for Elementor HTML widgets** (style + markup + script only — no nested `<html>` / `<body>`). |
| **`airport-passes-booking.zip`** | **WordPress: Plugins → Add New → Upload Plugin** — install and activate this ZIP. |
| `wordpress/airport-passes-booking/` | Same plugin as plain files (FTP / manual copy if you prefer). |
| `WORDPRESS-BOOKING-EMAIL.md` | Install steps, Elementor notes, and email troubleshooting. |

Paste **`airport-passes-booking-form-elementor.html`** into the popup’s HTML widget, upload **`airport-passes-booking.zip`** under Plugins, then configure SMTP so `wp_mail` delivers reliably.
