# Wellness Coins program (demo)

Static landing page for a **Wellness Coins** loyalty program, modeled after the structure and messaging of [Nutrifactor loyalty & discounts](https://www.nutrifactor.com.pk/pages/nutrifactor-loyalty-discount): earn coins, redeem vouchers, rewards, FAQs, and a clear first-screen story.

## Files

- `index.html` — main page with sections and the sign-in / sign-up modal
- `styles.css` — layout and theme
- `app.js` — opens/closes the modal and handles demo form submissions (no backend)

## Run locally

Open `index.html` in a browser, or from this folder:

```bash
python3 -m http.server 8080
```

Then visit `http://localhost:8080`.

All auth actions are **front-end only**; nothing is sent to a server.
