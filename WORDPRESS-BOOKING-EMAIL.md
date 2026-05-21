# Automatic confirmation email (WordPress)

The booking form in `airport-passes-booking-form.html` cannot send real email by itself: browsers only support `mailto:` (manual send). **Automatic** delivery to your team **and** to the person who filled the form requires server-side mail, for example WordPress `wp_mail()`.

## What we added

1. **Plugin** `wordpress/airport-passes-booking/airport-passes-booking.php`  
   - AJAX action `ap_mega_booking_email` (also for logged-out visitors).  
   - Sends **two** plain-text messages: one to the business inbox, one **confirmation to the submitter’s email**.  
   - Optional honeypot field `website` (spam bots).  
   - Simple rate limiting by IP (filters can adjust limits).

2. **Form script** (same HTML file)  
   - If `window.AP_MEGA_BOOKING_AJAX` exists (injected by the plugin in `wp_footer`), **Send via Email** uses `fetch()` to WordPress.  
   - If the plugin is **not** active, it falls back to the previous dual-`mailto:` behaviour.

3. **Honeypot** in the form: hidden `#ap_website_hp` — leave it in place when pasting into Elementor.

## Install on WordPress

1. Copy the folder `wordpress/airport-passes-booking/` into `wp-content/plugins/`.
2. In **Plugins**, activate **Airport Passes Mega Booking Email**.
3. Ensure your host can send mail (SMTP plugin recommended if `wp_mail` is unreliable).
4. Optional: change the business address from code with a filter in `functions.php`:

```php
add_filter('ap_mega_booking_business_email', function () {
  return 'bookings@yourdomain.com';
});
```

5. Paste/update the contents of `airport-passes-booking-form.html` inside your Elementor HTML widget (or enqueue the asset however you prefer).

After activation, submitting with **Send via Email** should show a success line stating that a confirmation was sent automatically to the customer’s address when both `wp_mail` calls succeed.

## Filters (optional)

- `ap_mega_booking_business_email` — recipient for the main enquiry.  
- `ap_mega_booking_max_per_window` — default `8` sends per IP per window.  
- `ap_mega_booking_rate_window` — default `600` seconds.
