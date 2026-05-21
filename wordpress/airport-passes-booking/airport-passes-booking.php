<?php
/**
 * Plugin Name: Airport Passes Mega Booking Email
 * Description: Sends booking enquiries to your team and automatically emails a confirmation to the submitter (wp_mail). Use with the Airport Passes booking HTML form.
 * Version: 1.1.0
 * Author: Airport Passes
 * License: GPL-2.0-or-later
 */

if (!defined('ABSPATH')) {
    exit;
}

define('AP_MEGA_BOOKING_VERSION', '1.1.0');

/**
 * Business inbox for booking enquiries.
 * Override with: add_filter('ap_mega_booking_business_email', fn() => 'you@example.com');
 */
function ap_mega_booking_business_email(): string
{
    $default = 'wasif@airportpasses.net';
    return (string) apply_filters('ap_mega_booking_business_email', $default);
}

function ap_mega_booking_client_ip(): string
{
    if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
        return sanitize_text_field(wp_unslash((string) $_SERVER['HTTP_CLIENT_IP']));
    }
    if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $parts = explode(',', (string) wp_unslash($_SERVER['HTTP_X_FORWARDED_FOR']));
        return sanitize_text_field(trim($parts[0]));
    }
    return sanitize_text_field(wp_unslash((string) ($_SERVER['REMOTE_ADDR'] ?? '')));
}

function ap_mega_booking_rate_limited(): bool
{
    $ip = ap_mega_booking_client_ip();
    if ($ip === '') {
        return false;
    }
    $key = 'ap_mega_rl_' . md5($ip);
    $count = (int) get_transient($key);
    $max = (int) apply_filters('ap_mega_booking_max_per_window', 8);
    $window = (int) apply_filters('ap_mega_booking_rate_window', 600);
    if ($count >= $max) {
        return true;
    }
    set_transient($key, $count + 1, $window);
    return false;
}

function ap_mega_booking_sanitize_body(string $raw, int $max = 60000): string
{
    $raw = wp_unslash($raw);
    if (strlen($raw) > $max) {
        return '';
    }
    return wp_strip_all_tags($raw, true);
}

function ap_mega_handle_booking_email(): void
{
    check_ajax_referer('ap_mega_booking', 'nonce');

    if (!empty($_POST['website'])) {
        wp_send_json_success(['ok' => true, 'sent_business' => false, 'sent_customer' => false]);
    }

    if (ap_mega_booking_rate_limited()) {
        wp_send_json_error(['message' => 'Too many requests. Please wait a few minutes and try again.'], 429);
    }

    $customer_email = sanitize_email(wp_unslash((string) ($_POST['customer_email'] ?? '')));
    if (!$customer_email || !is_email($customer_email)) {
        wp_send_json_error(['message' => 'Invalid email address.'], 400);
    }

    $subject_business = sanitize_text_field(wp_unslash((string) ($_POST['email_subject'] ?? 'Booking Request')));
    $body_business = ap_mega_booking_sanitize_body((string) ($_POST['email_body_business'] ?? ''));
    if ($body_business === '') {
        wp_send_json_error(['message' => 'Missing message body.'], 400);
    }

    $subject_confirm = sanitize_text_field(wp_unslash((string) ($_POST['email_subject_confirm'] ?? 'Your Booking Enquiry')));
    $body_confirm = ap_mega_booking_sanitize_body((string) ($_POST['email_body_confirm'] ?? ''));
    if ($body_confirm === '') {
        wp_send_json_error(['message' => 'Missing confirmation body.'], 400);
    }

    $headers = ['Content-Type: text/plain; charset=UTF-8'];

    $to_business = ap_mega_booking_business_email();
    if (!is_email($to_business)) {
        wp_send_json_error(['message' => 'Server email is not configured.'], 500);
    }

    $sent_business = wp_mail($to_business, $subject_business, $body_business, $headers);
    $sent_customer = wp_mail($customer_email, $subject_confirm, $body_confirm, $headers);

    if (!$sent_business && !$sent_customer) {
        wp_send_json_error(['message' => 'Email could not be sent. Check your site mail configuration or use WhatsApp.'], 500);
    }

    wp_send_json_success([
        'ok' => true,
        'sent_business' => (bool) $sent_business,
        'sent_customer' => (bool) $sent_customer,
    ]);
}

add_action('wp_ajax_nopriv_ap_mega_booking_email', 'ap_mega_handle_booking_email');
add_action('wp_ajax_ap_mega_booking_email', 'ap_mega_handle_booking_email');

/**
 * Exposes AJAX URL + nonce for the booking form (Elementor HTML widget, etc.).
 * Printed in the footer so it is defined before the user taps Send.
 */
/**
 * Print once so Elementor popups and themes that omit wp_footer still get the object early.
 */
function ap_mega_print_booking_ajax_bootstrap(): void
{
    static $printed = false;
    if ($printed) {
        return;
    }
    // Skip normal wp-admin screens; Elementor live preview loads the front-end with query args.
    if (is_admin() && empty($_GET['elementor-preview'])) {
        return;
    }
    $printed = true;
    $payload = [
        'url' => admin_url('admin-ajax.php'),
        'action' => 'ap_mega_booking_email',
        'nonce' => wp_create_nonce('ap_mega_booking'),
    ];
    echo '<script>window.AP_MEGA_BOOKING_AJAX=' . wp_json_encode($payload) . ";</script>\n";
}

add_action('wp_head', 'ap_mega_print_booking_ajax_bootstrap', 99);
add_action('wp_footer', 'ap_mega_print_booking_ajax_bootstrap', 20);
