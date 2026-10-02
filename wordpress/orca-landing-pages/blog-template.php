<?php
/**
 * A blog post or the blog index, dressed in a repo page (see Orca_Landing_Pages::blog_body()).
 * The theme's own header and footer are not used: the repo page carries the site's header, footer and form.
 */
if (!defined('ABSPATH')) {
    exit;
}
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class('olp-blog-body'); ?>>
<?php
if (function_exists('wp_body_open')) {
    wp_body_open();
}
echo Orca_Landing_Pages::blog_body(); // phpcs:ignore WordPress.Security.EscapeOutput -- built and escaped in blog_body()
wp_footer();
?>
</body>
</html>
