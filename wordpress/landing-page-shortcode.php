<?php
/**
 * Landing Page Shortcode
 *
 * Usage: [landing_page name="mashpian"]
 *
 * Add this code to your theme's functions.php
 * Or create a new file in wp-content/mu-plugins/landing-page-shortcode.php
 */

add_shortcode('landing_page', function($atts) {
    $atts = shortcode_atts(['name' => ''], $atts);

    if (empty($atts['name'])) {
        return '<!-- landing_page: no name specified -->';
    }

    $name = sanitize_file_name($atts['name']);
    $file = WP_CONTENT_DIR . "/landing-pages/{$name}/index.html";

    if (file_exists($file)) {
        return file_get_contents($file);
    }

    return "<!-- landing_page: '{$name}' not found -->";
});
