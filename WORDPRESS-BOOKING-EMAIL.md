# Automatic confirmation email (WordPress)

The booking form cannot send real email by itself: browsers only support `mailto:` (manual send). **Automatic** delivery to your team **and** to the person who filled the form requires server-side mail, for example WordPress `wp_mail()`.

## What we added

1. **Plugin** `wordpress/airport-passes-booking/airport-passes-booking.php`  
   - AJAX action `ap_mega_booking_email` (also for logged-out visitors).  
   - Sends **two** plain-text messages: one to the business inbox, one **confirmation to the submitter’s email**.  
   - Optional honeypot field `website` (spam bots).  
   - Simple rate limiting by IP (filters can adjust limits).  
   - Injects `window.AP_MEGA_BOOKING_AJAX` once per page in **`wp_head` (priority 99)** and **`wp_footer` (priority 20)** so Elementor popups and themes that behave oddly still define the object on normal front-end pages.

2. **Form script** (`airport-passes-booking-form.html` or `airport-passes-booking-form-elementor.html`)  
   - If `window.AP_MEGA_BOOKING_AJAX` exists, **Send via Email** uses `fetch()` to WordPress.  
   - If the plugin is **not** active, it falls back to dual-`mailto:` compose windows (not automatic).

3. **Honeypot** in the form: hidden `#ap_website_hp` — leave it in place.

## Elementor popup: which file to paste?

| File | Use when |
|------|-----------|
| **`airport-passes-booking-form-elementor.html`** | **Recommended** for the Elementor **HTML** widget. It is only `<style>` + `#apMegaWrap` + `<script>` — **no** `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>`. Nested full documents inside a widget can break scripts or layout. |
| `airport-passes-booking-form.html` | Standalone test page, or if your host/Elementor version handles a full document inside a widget. |

## Install on WordPress

1. Copy the folder `wordpress/airport-passes-booking/` into `wp-content/plugins/`.
2. In **Plugins**, activate **Airport Passes Mega Booking Email**.
3. Install **WP Mail SMTP** (or similar), connect real SMTP, and send that plugin’s **test email** until it succeeds.
4. In your **Elementor popup** → **HTML** widget, paste **`airport-passes-booking-form-elementor.html`** (full file). **Update** the popup.
5. Optional: change the business address with a filter in **Code Snippets** or `functions.php`:

```php
add_filter('ap_mega_booking_business_email', function () {
  return 'bookings@yourdomain.com';
});
```

## Troubleshooting (email not sent on desktop or mobile)

Do these checks **on the real website** (open your homepage in a **new incognito/private window**). Do **not** rely only on the grey Elementor canvas: you need a normal loaded page on your domain.

### 1. Confirm the AJAX object exists

On a **published** page (same domain as WordPress):

1. Open DevTools → **Console**.  
2. Type: `AP_MEGA_BOOKING_AJAX` and press Enter.

**Expected:** an object with `url`, `action`, and `nonce`.

- If you see **`undefined`**: the plugin is not active, or you are not on a real front-end page (e.g. wrong domain, maintenance plugin blocking footer, or viewing only inside Elementor without loading the public site). Fix plugin activation and test again on the live homepage.

### 2. Confirm the server request when you click Send

1. Open DevTools → **Network**.  
2. Complete the form through step 4 and click **Send via Email**.  
3. Find the request to **`admin-ajax.php`**.  
4. Open the **Response** tab.

**Expected:** JSON containing `"success":true` and `sent_business` / `sent_customer`.

- If you see **`success:false`** or a **400/403/500** status: read the `message` in the JSON (invalid email, nonce failed, rate limit, or `wp_mail` failure).  
- If **no** `admin-ajax.php` request appears: the form script is not running (often from pasting a **full HTML document** into the widget — switch to **`airport-passes-booking-form-elementor.html`**), or a script blocker is active.

### 3. Confirm WordPress can send mail at all

If `admin-ajax.php` returns success but **no messages arrive**, the problem is almost always **delivery** (SMTP, spam folder, wrong “From” domain).

1. Send a test from **WP Mail SMTP** until it is received.  
2. Retry the booking form.  
3. Check **Spam** on both the business inbox and the submitter’s inbox.

### 4. Popup display conditions

The page the visitor loads must be a normal WordPress front-end page that runs `wp_head` / `wp_footer`. Set the popup to **Entire Site** (or every template where “Book now” appears) so the footer/head hooks run before the popup opens.

## Filters (optional)

- `ap_mega_booking_business_email` — recipient for the main enquiry.  
- `ap_mega_booking_max_per_window` — default `8` sends per IP per window.  
- `ap_mega_booking_rate_window` — default `600` seconds.
