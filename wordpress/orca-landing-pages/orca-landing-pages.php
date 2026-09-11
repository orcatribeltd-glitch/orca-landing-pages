<?php
/**
 * Plugin Name: Orca Landing Pages (GitHub)
 * Plugin URI:  https://github.com/orcatribeltd-glitch/orca-landing-pages
 * Description: מציג דפי נחיתה ישירות מריפו GitHub ([landing_page name="…"]), ויוצר עמודים חדשים כטיוטה לפי pages.json בריפו. כל push מתעדכן באתר, בלי FTP.
 * Version:     1.7.3
 * Author:      Orca Tribe
 * Text Domain: orca-landing-pages
 */

if (!defined('ABSPATH')) {
    exit;
}

final class Orca_Landing_Pages
{
    const OPTION      = 'olp_settings';
    const CACHE_PFX   = 'olp_page_';
    const STALE_PFX   = 'olp_stale_';
    const VERSION     = '1.7.3';
    const PAGE_CACHE_SECONDS = 60;
    const GEN_OPTION  = 'olp_cache_generation';
    const REF_OPTION  = 'olp_git_ref';   // commit SHA from the last push webhook, else the branch

    public static function defaults(): array
    {
        return [
            'repo'           => 'orcatribeltd-glitch/orca-landing-pages',
            'branch'         => 'main',
            'token'          => '',
            'ttl'            => 300,
            'webhook_secret' => '',
            'cpanel_host'    => '',
            'cpanel_user'    => '',
            'cpanel_token'   => '',
        ];
    }

    public static function settings(): array
    {
        $saved = get_option(self::OPTION, []);
        if (!is_array($saved)) {
            $saved = [];
        }
        $s = array_merge(self::defaults(), $saved);
        if (defined('OLP_GITHUB_TOKEN') && OLP_GITHUB_TOKEN) {
            $s['token'] = OLP_GITHUB_TOKEN;
        }
        $s['ttl'] = max(30, (int) $s['ttl']);
        return $s;
    }

    public static function boot(): void
    {
        add_shortcode('landing_page', [__CLASS__, 'shortcode']);
        add_action('admin_menu', [__CLASS__, 'admin_menu']);
        add_action('admin_init', [__CLASS__, 'register_settings']);
        add_action('admin_post_olp_purge', [__CLASS__, 'handle_purge']);
        add_action('rest_api_init', [__CLASS__, 'rest_routes']);
        add_action('send_headers', [__CLASS__, 'short_page_cache']);
        add_filter('pre_set_site_transient_update_plugins', [__CLASS__, 'inject_update']);
        add_filter('plugins_api', [__CLASS__, 'plugin_info'], 10, 3);
    }

    /* ---------- self-update from the repo ---------- */

    const UPDATE_CACHE = 'olp_remote_version';

    /** wordpress/version.json in the repo: {"version":"1.7.2","package":"https://…/orca-landing-pages-1.7.2.zip"} */
    public static function remote_version(bool $force = false): array
    {
        $cached = get_transient(self::UPDATE_CACHE);
        if (!$force && is_array($cached)) {
            return $cached;
        }
        $s   = self::settings();
        $url = sprintf('https://raw.githubusercontent.com/%s/%s/wordpress/version.json', trim($s['repo'], '/'), rawurlencode($s['branch']));
        $res = wp_remote_get($url, ['timeout' => 10, 'headers' => ['Cache-Control' => 'no-cache', 'User-Agent' => 'orca-landing-pages/' . self::VERSION]]);
        $info = [];
        if (!is_wp_error($res) && (int) wp_remote_retrieve_response_code($res) === 200) {
            $data = json_decode((string) wp_remote_retrieve_body($res), true);
            if (is_array($data) && !empty($data['version']) && !empty($data['package'])) {
                $info = ['version' => (string) $data['version'], 'package' => (string) $data['package']];
            }
        }
        set_transient(self::UPDATE_CACHE, $info, 6 * HOUR_IN_SECONDS);
        return $info;
    }

    public static function inject_update($transient)
    {
        if (!is_object($transient)) {
            return $transient;
        }
        $info = self::remote_version();
        if (!$info || version_compare($info['version'], self::VERSION, '<=')) {
            return $transient;
        }
        $basename = plugin_basename(__FILE__);
        $transient->response[$basename] = (object) [
            'slug'        => 'orca-landing-pages',
            'plugin'      => $basename,
            'new_version' => $info['version'],
            'package'     => $info['package'],
            'url'         => 'https://github.com/' . trim(self::settings()['repo'], '/'),
            'tested'      => get_bloginfo('version'),
        ];
        return $transient;
    }

    public static function plugin_info($result, $action, $args)
    {
        if ($action !== 'plugin_information' || empty($args->slug) || $args->slug !== 'orca-landing-pages') {
            return $result;
        }
        $info = self::remote_version();
        return (object) [
            'name' => 'Orca Landing Pages (GitHub)', 'slug' => 'orca-landing-pages', 'version' => $info['version'] ?? self::VERSION,
            'author' => 'Orca Tribe', 'homepage' => 'https://github.com/' . trim(self::settings()['repo'], '/'),
            'download_link' => $info['package'] ?? '', 'sections' => ['description' => 'דפי נחיתה מריפו GitHub. עדכונים מגיעים מהריפו.'],
        ];
    }

    /**
     * Called from the webhook: if the repo says a newer plugin exists, install it
     * right now, so a push of a new version updates every site by itself.
     */
    public static function self_update(): string
    {
        delete_transient(self::UPDATE_CACHE);
        $info = self::remote_version(true);
        if (!$info || version_compare($info['version'], self::VERSION, '<=')) {
            return 'up to date (' . self::VERSION . ')';
        }
        if (!function_exists('get_filesystem_method')) {
            require_once ABSPATH . 'wp-admin/includes/file.php';
        }
        if (get_filesystem_method() !== 'direct') {
            return 'newer ' . $info['version'] . ' available, filesystem not direct — update from the plugins screen';
        }
        require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
        delete_site_transient('update_plugins');
        wp_update_plugins();
        $skin     = new WP_Ajax_Upgrader_Skin();
        $upgrader = new Plugin_Upgrader($skin);
        $basename = plugin_basename(__FILE__);
        $was_active = is_plugin_active($basename);
        $ok = $upgrader->upgrade($basename);
        if ($was_active && !is_plugin_active($basename)) {
            activate_plugin($basename);
        }
        $msg = ($ok === true ? 'updated to ' . $info['version'] : 'update failed: ' . implode(' | ', array_map('strval', (array) $skin->get_errors()->get_error_messages())));
        update_option('olp_last_self_update', gmdate('c') . ' ' . $msg, false);
        return $msg;
    }


    /* ---------- pages declared in the repo ---------- */

    /** The site's host without www, used to match `site` in pages.json. */
    public static function site_host(): string
    {
        $host = (string) wp_parse_url(home_url('/'), PHP_URL_HOST);
        return strtolower(preg_replace('/^www\./', '', $host));
    }

    /** Fetch a repo file at the pinned ref (any path, not only pages/). */
    public static function fetch_repo_file(string $path): string
    {
        $s    = self::settings();
        $url  = sprintf('https://raw.githubusercontent.com/%s/%s/%s', trim($s['repo'], '/'), rawurlencode(self::git_ref()), ltrim($path, '/'));
        $args = ['timeout' => 12, 'headers' => ['Cache-Control' => 'no-cache', 'User-Agent' => 'orca-landing-pages/' . self::VERSION]];
        if (!empty($s['token'])) {
            $args['headers']['Authorization'] = 'token ' . $s['token'];
        }
        $res = wp_remote_get($url, $args);
        if (is_wp_error($res) || (int) wp_remote_retrieve_response_code($res) !== 200) {
            return '';
        }
        return (string) wp_remote_retrieve_body($res);
    }

    /**
     * pages.json at the repo root lists pages that should exist on a site:
     *   [{"site":"influence-club.co.il","name":"mashpian-cancel","slug":"cancel",
     *     "title":"משפיען בדיגיטל – ביטול מנוי","template":"templates/mashpian-cancel.json"}]
     * A page whose slug does not exist yet is created as a DRAFT from the
     * Elementor template (content + page settings). Existing pages are never
     * touched: what Jonathan edits in the editor (form recipient, publish)
     * stays his. Returns a list of what happened, also stored in an option.
     */
    public static function sync_pages(): array
    {
        $raw = self::fetch_repo_file('pages.json');
        $log = [];
        $list = $raw !== '' ? json_decode($raw, true) : null;
        if (!is_array($list)) {
            $log[] = 'pages.json: none';
            update_option('olp_last_sync', gmdate('c') . ' ' . implode('; ', $log), false);
            return $log;
        }
        $host = self::site_host();
        foreach ($list as $entry) {
            if (!is_array($entry) || empty($entry['site']) || empty($entry['slug']) || empty($entry['template'])) {
                continue;
            }
            if (strtolower(preg_replace('/^www\./', '', (string) $entry['site'])) !== $host) {
                continue;
            }
            $slug = sanitize_title((string) $entry['slug']);
            $existing = get_page_by_path($slug, OBJECT, 'page');
            if ($existing) {
                $log[] = $slug . ': exists (#' . $existing->ID . ')';
                continue;
            }
            $tpl = json_decode(self::fetch_repo_file((string) $entry['template']), true);
            if (!is_array($tpl) || empty($tpl['content']) || !is_array($tpl['content'])) {
                $log[] = $slug . ': template unreadable';
                continue;
            }
            $page_settings = isset($tpl['page_settings']) && is_array($tpl['page_settings']) ? $tpl['page_settings'] : [];
            $wp_template   = !empty($page_settings['template']) ? (string) $page_settings['template'] : 'elementor_canvas';
            unset($page_settings['template']);

            $post_id = wp_insert_post([
                'post_type'    => 'page',
                'post_status'  => 'draft',
                'post_title'   => (string) ($entry['title'] ?? $tpl['title'] ?? $slug),
                'post_name'    => $slug,
                'post_content' => '',
            ], true);
            if (is_wp_error($post_id) || !$post_id) {
                $log[] = $slug . ': insert failed';
                continue;
            }
            update_post_meta($post_id, '_elementor_edit_mode', 'builder');
            update_post_meta($post_id, '_elementor_template_type', 'wp-page');
            update_post_meta($post_id, '_elementor_data', wp_slash(wp_json_encode($tpl['content'], JSON_UNESCAPED_UNICODE)));
            update_post_meta($post_id, '_elementor_page_settings', $page_settings);
            update_post_meta($post_id, '_wp_page_template', $wp_template);
            if (defined('ELEMENTOR_VERSION')) {
                update_post_meta($post_id, '_elementor_version', ELEMENTOR_VERSION);
            }
            update_post_meta($post_id, '_olp_created_from', (string) $entry['template'] . '@' . self::git_ref());
            $log[] = $slug . ': created draft #' . $post_id;
        }
        update_option('olp_last_sync', gmdate('c') . ' ' . implode('; ', $log), false);
        return $log;
    }


    /* ---------- shared footer declared in the repo ---------- */

    private static function new_id(): string
    {
        return substr(md5(uniqid('', true)), 0, 7);
    }

    private static function footer_element(string $name): array
    {
        return [
            'id' => self::new_id(), 'elType' => 'container', 'isInner' => false,
            'settings' => ['content_width' => 'full', 'flex_direction' => 'column', '_olp_footer' => 'yes'],
            'elements' => [[
                'id' => self::new_id(), 'elType' => 'widget', 'widgetType' => 'shortcode', 'elements' => [],
                'settings' => ['shortcode' => '[landing_page name="' . $name . '"]'],
            ]],
        ];
    }

    /**
     * sites.json in the repo:
     *   {"influence-club.co.il": {"footer": {"name": "influence-footer",
     *      "replace_containing": ["אורקה טרייב בע״מ", "orcatribeltd@gmail.com"],
     *      "append_to_pages_created_from_repo": true}}}
     * For every page of this site: a TOP-LEVEL Elementor element whose content
     * contains one of the markers (the old hand-copied footer) is replaced by a
     * container with the footer shortcode. The original element is kept in
     * post meta _olp_footer_backup. Pages created from the repo that have no
     * footer get one appended. Nothing else in the page is touched.
     */
    /** Text of an element tree, lowercased, tags/entities/quotes/whitespace removed — for marker matching. */
    private static function element_text(array $el): string
    {
        $blob = (string) wp_json_encode($el, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $blob = html_entity_decode($blob, ENT_QUOTES | ENT_HTML5, 'UTF-8');
        $blob = preg_replace('/<[^>]+>/u', ' ', $blob);
        $blob = preg_replace('/[\x{05F4}\x{05F3}"\'“”‘’`\\\\]/u', '', $blob);
        $blob = preg_replace('/\s+/u', ' ', $blob);
        return function_exists('mb_strtolower') ? mb_strtolower($blob, 'UTF-8') : strtolower($blob);
    }

    private static function normalize_marker(string $m): string
    {
        $m = preg_replace('/[\x{05F4}\x{05F3}"\'“”‘’`\\\\]/u', '', $m);
        $m = preg_replace('/\s+/u', ' ', trim($m));
        return function_exists('mb_strtolower') ? mb_strtolower($m, 'UTF-8') : strtolower($m);
    }

    private static function is_repo_footer(array $el, string $name): bool
    {
        if (($el['settings']['_olp_footer'] ?? '') === 'yes') {
            return true;
        }
        return strpos(self::element_text($el), self::normalize_marker('[landing_page name="' . $name . '"]')) !== false;
    }

    /** True when the element is, or contains, a widget of one of these types (e.g. a lead form). */
    private static function subtree_has_widget(array $el, array $types): bool
    {
        if (($el['elType'] ?? '') === 'widget' && in_array((string) ($el['widgetType'] ?? ''), $types, true)) {
            return true;
        }
        foreach ((array) ($el['elements'] ?? []) as $child) {
            if (is_array($child) && self::subtree_has_widget($child, $types)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Depth-first over an Elementor element tree. The first element (at any
     * depth) that is the repo footer or carries an old-footer marker becomes
     * THE footer; every later one is removed. Old copies go to $st['backup'].
     */
    private static function footer_walk(array $elements, string $name, array $markers, array &$st): array
    {
        $out = [];
        foreach ($elements as $el) {
            if (!is_array($el)) { $out[] = $el; continue; }
            if (self::is_repo_footer($el, $name)) {
                if ($st['seen']) { $st['deduped']++; $st['what'][] = 'dedupe'; continue; }
                $st['seen'] = true; $out[] = $el; continue;
            }
            $text = self::element_text($el); $hit = false;
            foreach ($markers as $m) {
                if ($m !== '' && strpos($text, $m) !== false) { $hit = true; break; }
            }
            if ($hit) {
                // A lead form is never a footer, even when its settings carry a marker (the
                // notification email, the acceptance text). 1.7.1 replaced buyplan's whole
                // form container this way. Leave such subtrees exactly as they are.
                if (self::subtree_has_widget($el, ['form'])) { $st['what'][] = 'form-protected'; $out[] = $el; continue; }
                // does the marker sit in this element itself, or only in a child? descend first
                $own = $el; $own['elements'] = [];
                $own_text = self::element_text($own); $own_hit = false;
                foreach ($markers as $m) { if ($m !== '' && strpos($own_text, $m) !== false) { $own_hit = true; break; } }
                if (!$own_hit && !empty($el['elements']) && is_array($el['elements'])) {
                    $el['elements'] = self::footer_walk($el['elements'], $name, $markers, $st);
                    if (empty($el['elements'])) { $st['what'][] = 'empty-wrapper-removed'; continue; } // held only the old footer
                    $out[] = $el; continue;
                }
                $st['backup'][] = $el;
                if ($st['seen']) { $st['deduped']++; $st['what'][] = 'old-dup-removed'; continue; }
                $st['seen'] = true; $st['replaced']++; $st['what'][] = 'replaced';
                $out[] = self::footer_element($name); continue;
            }
            if (!empty($el['elements']) && is_array($el['elements'])) {
                $el['elements'] = self::footer_walk($el['elements'], $name, $markers, $st);
                if (empty($el['elements'])) { $st['what'][] = 'empty-wrapper-removed'; continue; }
            }
            $out[] = $el;
        }
        return $out;
    }

    /** Elementor keeps rendered output and CSS per page; drop both so a data change is visible at once. */
    private static function clear_elementor_cache(int $pid): void
    {
        delete_post_meta($pid, '_elementor_css');
        delete_post_meta($pid, '_elementor_element_cache');
        if (class_exists('\Elementor\Plugin') && isset(\Elementor\Plugin::$instance->files_manager) && method_exists(\Elementor\Plugin::$instance->files_manager, 'clear_cache')) {
            \Elementor\Plugin::$instance->files_manager->clear_cache();
        }
    }

    public static function sync_footer(): array
    {
        $raw   = self::fetch_repo_file('sites.json');
        $sites = $raw !== '' ? json_decode($raw, true) : null;
        $log   = [];
        $cfg   = is_array($sites) ? ($sites[self::site_host()]['footer'] ?? null) : null;
        if (!is_array($cfg) || empty($cfg['name'])) {
            $log[] = 'no footer config for ' . self::site_host();
            update_option('olp_last_footer', gmdate('c') . ' ' . implode('; ', $log), false);
            return $log;
        }
        $name    = sanitize_title((string) $cfg['name']);
        $markers = array_values(array_filter(array_map([__CLASS__, 'normalize_marker'], array_map('strval', (array) ($cfg['replace_containing'] ?? [])))));
        $append  = !empty($cfg['append_to_pages_created_from_repo']);

        $pages = get_posts(['post_type' => 'page', 'post_status' => ['publish', 'draft', 'private', 'pending', 'future'], 'numberposts' => -1, 'fields' => 'ids']);
        $replaced = 0; $appended = 0; $deduped = 0; $skipped = 0; $detail = [];
        foreach ((array) $pages as $pid) {
            $pid  = (int) $pid;
            $json = get_post_meta($pid, '_elementor_data', true);
            if (!is_string($json) || $json === '') {
                $detail[] = $pid . ':no-elementor';
                continue;
            }
            $data = json_decode($json, true);
            if (!is_array($data)) {
                $detail[] = $pid . ':bad-json';
                continue;
            }
            $st = ['seen' => false, 'backup' => [], 'what' => [], 'replaced' => 0, 'deduped' => 0];
            $out = self::footer_walk($data, $name, $markers, $st);
            $changed = !empty($st['what']);
            $replaced += $st['replaced']; $deduped += $st['deduped'];
            $seen_footer = $st['seen']; $backup = $st['backup']; $what = $st['what'];
            if (!$seen_footer && $append && get_post_meta($pid, '_olp_created_from', true)) {
                $out[] = self::footer_element($name); $changed = true; $appended++; $what[] = 'appended';
            }
            if (!$changed) { $skipped++; $detail[] = $pid . ':' . ($seen_footer ? 'ok' : 'no-footer'); continue; }
            if ($backup) {
                $old = get_post_meta($pid, '_olp_footer_backup', true);
                $old = is_array($old) ? $old : [];
                update_post_meta($pid, '_olp_footer_backup', array_merge($old, [['at' => gmdate('c'), 'elements' => $backup]]));
            }
            update_post_meta($pid, '_elementor_data', wp_slash(wp_json_encode($out, JSON_UNESCAPED_UNICODE)));
            self::clear_elementor_cache($pid);
            clean_post_cache($pid);
            self::purge_page_cache_plugins($pid);
            $detail[] = $pid . ':' . implode('+', $what);
        }
        $log[] = "footer '$name': replaced $replaced, appended $appended, duplicates removed $deduped, untouched $skipped";
        $log[] = implode(' ', $detail);
        update_option('olp_last_footer', gmdate('c') . ' ' . implode('; ', $log), false);
        return $log;
    }

    /* ---------- server page cache ---------- */

    /**
     * Page-cache plugins keep a static copy of the page; ask each one that is
     * installed to drop this page. SpeedyCache (Softaculous) is what runs on
     * influence-club.co.il: it stamps "Cache by SpeedyCache" at the end of the
     * HTML and strips comments, so measure with a visible marker, not a comment.
     */
    public static function purge_page_cache_plugins(int $id): array
    {
        $done = [];
        if (class_exists('\\SpeedyCache\\Delete') && method_exists('\\SpeedyCache\\Delete', 'cache')) {
            \SpeedyCache\Delete::cache($id);
            $done[] = 'speedycache';
        }
        if (function_exists('rocket_clean_post')) {
            rocket_clean_post($id);
            $done[] = 'wp-rocket';
        }
        if (function_exists('w3tc_flush_post')) {
            w3tc_flush_post($id);
            $done[] = 'w3tc';
        }
        if (function_exists('wpsc_delete_post_cache')) {
            wpsc_delete_post_cache($id);
            $done[] = 'wp-super-cache';
        }
        if (has_action('litespeed_purge_post')) {
            do_action('litespeed_purge_post', $id);
            $done[] = 'litespeed';
        }
        if (has_action('cache_enabler_clear_page_cache_by_post')) {
            do_action('cache_enabler_clear_page_cache_by_post', $id);
            $done[] = 'cache-enabler';
        }
        if (has_action('wphb_clear_page_cache')) {
            do_action('wphb_clear_page_cache', $id);
            $done[] = 'hummingbird';
        }
        return $done;
    }

    /**
     * FastCloud (cPanel + NGINX caching) keeps the rendered page until the cache
     * is cleared; TTL and save hooks did not do it. cPanel's own API can:
     * UAPI NginxCaching::clear_cache, authenticated with a cPanel API token
     * (cPanel → Manage API Tokens). Configured in the settings page; a no-op
     * until host, user and token are all set. Returns a short status string.
     */
    public static function cpanel_clear_cache(): string
    {
        $s = self::settings();
        if ($s['cpanel_host'] === '' || $s['cpanel_user'] === '' || $s['cpanel_token'] === '') {
            return 'not configured';
        }
        $host = preg_replace('#^https?://#', '', $s['cpanel_host']);
        $host = rtrim($host, '/');
        if (strpos($host, ':') === false) {
            $host .= ':2083';
        }
        $res = wp_remote_get('https://' . $host . '/execute/NginxCaching/clear_cache', [
            'timeout'   => 15,
            'sslverify' => true,
            'headers'   => [
                'Authorization' => 'cpanel ' . $s['cpanel_user'] . ':' . $s['cpanel_token'],
                'User-Agent'    => 'orca-landing-pages/' . self::VERSION,
            ],
        ]);
        if (is_wp_error($res)) {
            $out = 'error: ' . $res->get_error_message();
        } else {
            $code = (int) wp_remote_retrieve_response_code($res);
            $data = json_decode((string) wp_remote_retrieve_body($res), true);
            $ok   = is_array($data) && !empty($data['status']);
            $out  = $ok ? 'cleared' : ('failed: HTTP ' . $code . ' ' . substr((string) wp_remote_retrieve_body($res), 0, 120));
        }
        update_option('olp_last_cpanel_purge', gmdate('c') . ' ' . $out, false);
        return $out;
    }

    /** Every published page or post that renders a landing page. */
    public static function landing_page_ids(): array
    {
        global $wpdb;
        $ids = $wpdb->get_col(
            "SELECT p.ID FROM {$wpdb->posts} p
             LEFT JOIN {$wpdb->postmeta} m ON m.post_id = p.ID AND m.meta_key = '_elementor_data'
             WHERE p.post_status = 'publish' AND p.post_type IN ('page', 'post')
               AND (p.post_content LIKE '%[landing_page%' OR m.meta_value LIKE '%landing_page%')"
        );
        return array_values(array_unique(array_map('intval', (array) $ids)));
    }

    /**
     * The host's full-page cache (nginx in front of PHP on FastCloud) kept the
     * old HTML for over 15 minutes after GitHub changed, and only let go when
     * the page was published from the editor. So a purge does what the editor
     * does: it saves each landing page again, unchanged, which fires the same
     * save_post / transition_post_status hooks the host's cache listens to.
     * Also clears WordPress' own post cache and, when present, the common
     * caching plugins' full-purge hooks.
     */
    public static function touch_landing_pages(): array
    {
        $ids = self::landing_page_ids();
        foreach ($ids as $id) {
            clean_post_cache($id);
            wp_update_post(['ID' => $id]);
            self::purge_page_cache_plugins($id);
        }
        foreach (['litespeed_purge_all', 'w3tc_flush_all', 'wp_cache_clear_cache', 'rocket_clean_domain', 'cache_enabler_clear_complete_cache', 'breeze_clear_all_cache', 'swcfpc_purge_cache'] as $hook) {
            if (has_action($hook) || has_filter($hook)) {
                do_action($hook);
            }
        }
        if (function_exists('wp_cache_flush')) {
            wp_cache_flush();
        }
        return $ids;
    }

    /** Does this post render a landing page? Elementor keeps the shortcode in
     *  post meta, the block editor keeps it in post_content; check both. */
    public static function post_uses_landing_page(int $post_id): bool
    {
        if ($post_id <= 0) {
            return false;
        }
        $post = get_post($post_id);
        if ($post && strpos((string) $post->post_content, '[landing_page') !== false) {
            return true;
        }
        $elementor = get_post_meta($post_id, '_elementor_data', true);
        return is_string($elementor) && strpos($elementor, 'landing_page') !== false;
    }

    /**
     * The host's full-page cache (nginx in front of PHP) otherwise keeps the old
     * HTML for minutes after GitHub changed. Pages that render a landing page tell
     * that cache to keep them only briefly, so a push is visible within a minute.
     */
    public static function short_page_cache(): void
    {
        if (is_admin() || !is_singular() || headers_sent()) {
            return;
        }
        if (!self::post_uses_landing_page((int) get_queried_object_id())) {
            return;
        }
        $ttl = (int) apply_filters('olp_page_cache_seconds', self::PAGE_CACHE_SECONDS);
        header('X-Accel-Expires: ' . $ttl);
        header('Cache-Control: public, max-age=0, s-maxage=' . $ttl);
        header('X-OLP-Page: landing');
    }

    /* ---------- fetching ---------- */

    /**
     * raw.githubusercontent.com sits behind a CDN that keeps a branch URL for up
     * to five minutes. A commit SHA URL is immutable, so it is never stale. The
     * push webhook hands us the new SHA; until one is known we use the branch.
     */
    public static function git_ref(): string
    {
        $s   = self::settings();
        $ref = (string) get_option(self::REF_OPTION, '');
        return preg_match('/^[0-9a-f]{7,40}$/', $ref) ? $ref : $s['branch'];
    }

    public static function raw_url(string $name, string $file = 'index.html'): string
    {
        $s = self::settings();
        return sprintf(
            'https://raw.githubusercontent.com/%s/%s/pages/%s/%s',
            trim($s['repo'], '/'),
            rawurlencode(self::git_ref()),
            rawurlencode($name),
            $file
        );
    }

    /** Ask GitHub for the branch head. Used by the manual purge button, when no
     *  webhook payload told us the SHA. Unauthenticated calls are rate-limited
     *  to 60/hour, which a button click never approaches. */
    public static function resolve_head_sha(): string
    {
        $s    = self::settings();
        $args = ['timeout' => 8, 'headers' => ['Accept' => 'application/vnd.github+json', 'User-Agent' => 'orca-landing-pages/' . self::VERSION]];
        if (!empty($s['token'])) {
            $args['headers']['Authorization'] = 'token ' . $s['token'];
        }
        $res = wp_remote_get(sprintf('https://api.github.com/repos/%s/commits/%s', trim($s['repo'], '/'), rawurlencode($s['branch'])), $args);
        if (is_wp_error($res) || (int) wp_remote_retrieve_response_code($res) !== 200) {
            return '';
        }
        $data = json_decode((string) wp_remote_retrieve_body($res), true);
        $sha  = is_array($data) ? (string) ($data['sha'] ?? '') : '';
        return preg_match('/^[0-9a-f]{7,40}$/', $sha) ? $sha : '';
    }

    public static function generation(): int
    {
        return (int) get_option(self::GEN_OPTION, 1);
    }

    private static function cache_key(string $prefix, string $name): string
    {
        $s   = self::settings();
        $gen = $prefix === self::CACHE_PFX ? self::generation() : 0;
        return $prefix . md5($s['repo'] . '|' . $s['branch'] . '|' . self::git_ref() . '|' . $name . '|' . $gen);
    }

    /**
     * Returns [html, source] where source is one of: cache | github | stale | error.
     */
    public static function get_page(string $name, bool $force = false): array
    {
        $key = self::cache_key(self::CACHE_PFX, $name);
        if (!$force) {
            $cached = get_transient($key);
            if (is_string($cached) && $cached !== '') {
                return [$cached, 'cache'];
            }
        }

        $s    = self::settings();
        $args = [
            'timeout' => 12,
            'headers' => [
                'Cache-Control' => 'no-cache',
                'User-Agent'    => 'orca-landing-pages/' . self::VERSION,
            ],
        ];
        if (!empty($s['token'])) {
            $args['headers']['Authorization'] = 'token ' . $s['token'];
        }

        $res  = wp_remote_get(self::raw_url($name), $args);
        $code = is_wp_error($res) ? 0 : (int) wp_remote_retrieve_response_code($res);
        $body = is_wp_error($res) ? '' : (string) wp_remote_retrieve_body($res);

        if ($code === 200 && $body !== '') {
            $html = self::prepare($body, $name);
            set_transient($key, $html, $s['ttl']);
            update_option(self::cache_key(self::STALE_PFX, $name), $html, false);
            return [$html, 'github'];
        }

        $stale = get_option(self::cache_key(self::STALE_PFX, $name), '');
        if (is_string($stale) && $stale !== '') {
            set_transient($key, $stale, 60);
            return [$stale, 'stale'];
        }

        $reason = is_wp_error($res) ? $res->get_error_message() : ('HTTP ' . $code);
        return ['', 'error:' . $reason];
    }

    /**
     * Turn a full HTML document into an embeddable fragment:
     * keep <style>, stylesheet <link>s, and body content; drop <html>/<head>/<meta>/<title>.
     * Rewrite relative asset paths to the GitHub raw folder of the page.
     */
    public static function prepare(string $html, string $name): string
    {
        $out = $html;

        if (preg_match('/<body[^>]*>(.*)<\/body>/is', $html, $m)) {
            $head_parts = '';
            if (preg_match('/<head[^>]*>(.*)<\/head>/is', $html, $h)) {
                if (preg_match_all('/<style\b[^>]*>.*?<\/style>/is', $h[1], $styles)) {
                    $head_parts .= implode("\n", $styles[0]) . "\n";
                }
                if (preg_match_all('/<link\b[^>]*>/i', $h[1], $links)) {
                    foreach ($links[0] as $link) {
                        if (preg_match('/rel=["\'](stylesheet|preconnect|preload)["\']/i', $link)) {
                            $head_parts .= $link . "\n";
                        }
                    }
                }
                if (preg_match_all('/<script\b[^>]*>.*?<\/script>/is', $h[1], $scripts)) {
                    $head_parts .= implode("\n", $scripts[0]) . "\n";
                }
            }
            $out = $head_parts . $m[1];
        }

        $base = dirname(self::raw_url($name)) . '/';
        $out  = preg_replace_callback(
            '/\b(src|href)=(["\'])(?!https?:|\/\/|data:|#|mailto:|tel:|javascript:|\/)([^"\']+)\2/i',
            static function ($mm) use ($base) {
                $path = preg_replace('#^\./#', '', $mm[3]);
                return $mm[1] . '=' . $mm[2] . $base . $path . $mm[2];
            },
            $out
        );

        return trim($out);
    }

    /* ---------- shortcode ---------- */

    public static function shortcode($atts): string
    {
        $atts = shortcode_atts(['name' => ''], $atts, 'landing_page');
        $name = strtolower(preg_replace('/[^a-zA-Z0-9_-]/', '', (string) $atts['name']));

        if ($name === '') {
            return '<!-- landing_page: no name specified -->';
        }

        $force = isset($_GET['olp_refresh']) && current_user_can('edit_pages');
        [$html, $source] = self::get_page($name, $force);

        if ($html === '') {
            $msg = '<!-- landing_page "' . esc_html($name) . '": ' . esc_html($source) . ' -->';
            if (current_user_can('edit_pages')) {
                $msg .= '<div dir="rtl" style="padding:24px;border:2px dashed #c00;color:#c00;font-family:sans-serif">'
                    . 'דף הנחיתה <b>' . esc_html($name) . '</b> לא נמצא בגיטהאב (' . esc_html($source) . '). '
                    . 'ההודעה הזו מוצגת רק למנהלים.</div>';
            }
            return $msg;
        }

        return '<div class="olp-page" data-olp-page="' . esc_attr($name) . '" data-olp-source="' . esc_attr($source) . '" data-olp-ref="' . esc_attr(substr(self::git_ref(), 0, 7)) . '">'
            . $html . '</div>';
    }

    /* ---------- cache purge ---------- */

    /**
     * Invalidate every cached page by moving to a new cache generation. Old
     * transients simply stop being read and expire on their own. This works
     * whether transients live in the options table or in a persistent object
     * cache (Redis / Memcached), where a SQL LIKE over wp_options finds nothing.
     * Returns the new generation number.
     */
    public static function purge_all(string $sha = ''): int
    {
        if ($sha === '') {
            $sha = self::resolve_head_sha();
        }
        if (preg_match('/^[0-9a-f]{7,40}$/', $sha)) {
            update_option(self::REF_OPTION, $sha, false);
            wp_cache_delete(self::REF_OPTION, 'options');
        }
        $next = self::generation() + 1;
        update_option(self::GEN_OPTION, $next, false);
        wp_cache_delete(self::GEN_OPTION, 'options');

        self::touch_landing_pages();
        self::cpanel_clear_cache();
        self::sync_pages();
        self::sync_footer();

        // Best effort cleanup of DB-stored transients from earlier generations.
        global $wpdb;
        $like = $wpdb->esc_like('_transient_' . self::CACHE_PFX) . '%';
        $rows = $wpdb->get_col($wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s", $like));
        foreach ($rows as $row) {
            delete_transient(substr($row, strlen('_transient_')));
        }
        return $next;
    }

    public static function handle_purge(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die('forbidden');
        }
        check_admin_referer('olp_purge');
        $gen = self::purge_all();
        wp_safe_redirect(add_query_arg(['page' => 'orca-landing-pages', 'purged' => $gen], admin_url('options-general.php')));
        exit;
    }

    public static function rest_routes(): void
    {
        register_rest_route('olp/v1', '/refresh', [
            'methods'             => ['POST', 'GET'],
            'permission_callback' => '__return_true',
            'callback'            => static function (WP_REST_Request $req) {
                $s      = self::settings();
                $secret = (string) $s['webhook_secret'];
                $given  = (string) ($req->get_header('x-olp-secret') ?: $req->get_param('secret'));
                if ($secret === '' || !hash_equals($secret, $given)) {
                    return new WP_REST_Response(['ok' => false, 'error' => 'bad secret'], 403);
                }
                $payload = $req->get_json_params();
                $sha     = is_array($payload) ? (string) ($payload['after'] ?? '') : '';
                $gen     = self::purge_all($sha);
                $update = self::self_update();
                $caches = [];
                foreach (self::landing_page_ids() as $pid) {
                    $caches = array_unique(array_merge($caches, self::purge_page_cache_plugins($pid)));
                }
                return new WP_REST_Response(['ok' => true, 'generation' => $gen, 'ref' => self::git_ref(), 'touched' => self::landing_page_ids(), 'page_cache_plugins' => array_values($caches), 'cpanel' => (string) get_option('olp_last_cpanel_purge', 'not configured'), 'pages' => (string) get_option('olp_last_sync', ''), 'footer' => (string) get_option('olp_last_footer', ''), 'plugin' => self::VERSION . ' — ' . $update], 200);
            },
        ]);
    }

    /* ---------- admin ---------- */

    public static function admin_menu(): void
    {
        add_options_page('דפי נחיתה (GitHub)', 'דפי נחיתה (GitHub)', 'manage_options', 'orca-landing-pages', [__CLASS__, 'settings_page']);
    }

    public static function register_settings(): void
    {
        register_setting('olp', self::OPTION, [
            'type'              => 'array',
            'sanitize_callback' => static function ($in) {
                $d = self::defaults();
                return [
                    'repo'           => sanitize_text_field($in['repo'] ?? $d['repo']),
                    'branch'         => sanitize_text_field($in['branch'] ?? $d['branch']),
                    'token'          => trim((string) ($in['token'] ?? '')),
                    'ttl'            => max(30, (int) ($in['ttl'] ?? $d['ttl'])),
                    'webhook_secret' => trim((string) ($in['webhook_secret'] ?? '')),
                    'cpanel_host'    => trim((string) ($in['cpanel_host'] ?? '')),
                    'cpanel_user'    => trim((string) ($in['cpanel_user'] ?? '')),
                    'cpanel_token'   => trim((string) ($in['cpanel_token'] ?? '')),
                ];
            },
        ]);
    }

    public static function settings_page(): void
    {
        $s = self::settings();
        $purged = isset($_GET['purged']) ? (int) $_GET['purged'] : null;
        ?>
        <div class="wrap" dir="rtl">
            <h1>דפי נחיתה מגיטהאב</h1>
            <?php if ($purged !== null): ?>
                <div class="notice notice-success"><p>הזיכרון נוקה (דור <?php echo $purged; ?>). הטעינה הבאה תמשוך מגיטהאב.</p></div>
            <?php endif; ?>
            <p>גרסה בשימוש מגיטהאב: <code dir="ltr"><?php echo esc_html(self::git_ref()); ?></code><br>עמודים מהריפו (pages.json): <code dir="ltr"><?php echo esc_html((string) get_option('olp_last_sync', 'עדיין לא')); ?></code><br>פוטר מהריפו (sites.json): <code dir="ltr"><?php echo esc_html((string) get_option('olp_last_footer', 'עדיין לא')); ?></code></p>
            <p>בעמוד באלמנטור מוסיפים ווידג'ט Shortcode עם הקוד <code>[landing_page name="שם-התיקייה"]</code>.
               הדף נמשך מ-<code>pages/&lt;שם&gt;/index.html</code> בריפו ונשמר בזיכרון למשך <?php echo (int) $s['ttl']; ?> שניות.
               כדי לראות שינוי מיד: להוסיף <code>?olp_refresh=1</code> לכתובת הדף (כמנהל מחובר), או ללחוץ על הכפתור למטה.</p>

            <form method="post" action="options.php">
                <?php settings_fields('olp'); ?>
                <table class="form-table">
                    <tr><th>ריפו (owner/name)</th><td><input type="text" class="regular-text" dir="ltr" name="<?php echo self::OPTION; ?>[repo]" value="<?php echo esc_attr($s['repo']); ?>"></td></tr>
                    <tr><th>ענף</th><td><input type="text" dir="ltr" name="<?php echo self::OPTION; ?>[branch]" value="<?php echo esc_attr($s['branch']); ?>"></td></tr>
                    <tr><th>טוקן GitHub (רק אם הריפו פרטי)</th><td><input type="password" class="regular-text" dir="ltr" name="<?php echo self::OPTION; ?>[token]" value="<?php echo esc_attr(defined('OLP_GITHUB_TOKEN') ? '' : $s['token']); ?>" autocomplete="new-password">
                        <?php if (defined('OLP_GITHUB_TOKEN')): ?><p class="description">מוגדר ב-wp-config.php</p><?php endif; ?></td></tr>
                    <tr><th>זמן שמירה בזיכרון (שניות)</th><td><input type="number" min="30" name="<?php echo self::OPTION; ?>[ttl]" value="<?php echo (int) $s['ttl']; ?>"></td></tr>
                    <tr><th>סוד ל-webhook (אופציונלי)</th><td><input type="text" class="regular-text" dir="ltr" name="<?php echo self::OPTION; ?>[webhook_secret]" value="<?php echo esc_attr($s['webhook_secret']); ?>">
                        <p class="description">אם מוגדר: <code dir="ltr"><?php echo esc_url(rest_url('olp/v1/refresh')); ?>?secret=…</code> מנקה את הזיכרון. אפשר לחבר כ-webhook בגיטהאב כדי שכל push יתעדכן מיד.</p></td></tr>
                    <tr><th colspan="2"><h2 style="margin:18px 0 4px">ניקוי זיכרון השרת (cPanel)</h2>
                        <p class="description" style="font-weight:normal">FastCloud שומר את העמוד המוכן עד שמנקים אותו. עם טוקן API של cPanel התוסף מנקה אותו בכל push. יצירת טוקן: cPanel → Manage API Tokens → Create. מספיק טוקן ללא הרשאות מיוחדות.</p></th></tr>
                    <tr><th>כתובת cPanel</th><td><input type="text" class="regular-text" dir="ltr" name="<?php echo self::OPTION; ?>[cpanel_host]" value="<?php echo esc_attr($s['cpanel_host']); ?>" placeholder="fast208.fcsrv.com:2083"></td></tr>
                    <tr><th>שם משתמש cPanel</th><td><input type="text" class="regular-text" dir="ltr" name="<?php echo self::OPTION; ?>[cpanel_user]" value="<?php echo esc_attr($s['cpanel_user']); ?>"></td></tr>
                    <tr><th>טוקן API של cPanel</th><td><input type="password" class="regular-text" dir="ltr" name="<?php echo self::OPTION; ?>[cpanel_token]" value="<?php echo esc_attr($s['cpanel_token']); ?>" autocomplete="new-password">
                        <p class="description">ניקוי אחרון: <code dir="ltr"><?php echo esc_html((string) get_option('olp_last_cpanel_purge', 'עדיין לא')); ?></code></p></td></tr>
                </table>
                <?php submit_button('שמירה'); ?>
            </form>

            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                <input type="hidden" name="action" value="olp_purge">
                <?php wp_nonce_field('olp_purge'); ?>
                <?php submit_button('נקה זיכרון ומשוך מחדש מגיטהאב', 'secondary'); ?>
            </form>
        </div>
        <?php
    }
}

Orca_Landing_Pages::boot();
