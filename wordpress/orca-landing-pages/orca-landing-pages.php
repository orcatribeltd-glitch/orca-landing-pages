<?php
/**
 * Plugin Name: Orca Landing Pages (GitHub)
 * Plugin URI:  https://github.com/orcatribeltd-glitch/orca-landing-pages
 * Description: מציג דפי נחיתה ישירות מריפו GitHub. שימוש: [landing_page name="rachel-pottery"]. כל commit לריפו מתעדכן באתר תוך דקות, בלי FTP.
 * Version:     1.2.0
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
    const VERSION     = '1.2.0';
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
    }

    /* ---------- server page cache ---------- */

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

        return '<div class="olp-page" data-olp-page="' . esc_attr($name) . '" data-olp-source="' . esc_attr($source) . '">'
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
                return new WP_REST_Response(['ok' => true, 'generation' => $gen, 'ref' => self::git_ref()], 200);
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
            <p>גרסה בשימוש מגיטהאב: <code dir="ltr"><?php echo esc_html(self::git_ref()); ?></code></p>
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
