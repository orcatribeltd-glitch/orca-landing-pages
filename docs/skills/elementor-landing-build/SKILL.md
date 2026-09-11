---
name: elementor-landing-build
description: "מוסיף את כל כשלי הביצוע שהתגלו בפועל: מחלקה על קונטיינר בלבד, ספציפיות מול עיצוב הטופס של אלמנטור, מירכוז ב-RTL, והרצת בדיקה מול אב עוין"
---

# Elementor Landing Build

Execution only. The design and copy already exist; this skill gets them onto a live page intact.

## The two rules everything else serves

**1. Never retype content.** Every string reaches the page by copy-paste from a file. An agent that retypes long Hebrew copy will corrupt it — in practice this produced "הזן הזן את פרטי האשראי" and "גישה לכל האפליקציה השידור שלי". Content comes from a file. Design values come from the source. The agent assembles; it does not author.

**2. Fix one name per element, then never deviate.** The user is looking at a screen full of nearly identical grey boxes. "The text widget", "the container", "the second one" — each can mean three things, and every ambiguous reference costs a round trip. Publish a naming table before the first instruction, then use those exact words and no synonyms.

## Step 0 — Establish the shared names

Hand the user a table of every element with its fixed name and the file it holds, and ask them to rename the elements in Elementor's Navigator to match, so the word appears on their screen.

| Name | What it is | File |
|---|---|---|
| פונטים | HTML widget | `1-fonts.txt` |
| עיצוב | HTML widget | `2-styles.txt` |
| גוף הדף | HTML widget — all continuous content | `3-page.txt` |
| קופסת הטופס | the **container** carrying the card CSS class | — |
| ראש הטופס | HTML widget inside it | `4-form-texts.txt` |
| הטופס | the native Form widget | — |

If the structure changes, republish the whole table rather than patching it verbally.

## Step 1 — Get the real source, cheaply

A Claude Design "Project HTML" export is a self-extracting bundle, often 3–4 MB, because fonts and images are base64-embedded. Never hand that file to another agent — it blows the context window and the session dies with "Prompt is too long".

Strip it first: parse the `__bundler/template` script (JSON string) for the markup and `__bundler/manifest` for the assets. Replace embedded fonts with a Google Fonts `@import` or extracted base64 `@font-face` blocks; replace embedded images with a placeholder. Result: ~15 KB instead of ~3.8 MB.

## Step 2 — Extract exact values, never estimate

Read colors, sizes, spacings, radii, gradients and shadows from the source code, never from a screenshot. Produce a build spec listing them per section, plus a separate copy deck with every string verbatim, labeled by location.

## Step 3 — Decide the split from one constraint

The only thing that forces a split is **a real Elementor widget that must nest inside the design** — a form, video, slider, countdown. Everywhere else the HTML runs continuously; two adjacent sections with nothing between them belong in one widget so backgrounds and textures flow without a seam.

**A CSS class that draws a frame goes on a CONTAINER, never on a widget.** A widget cannot contain another widget, so a frame drawn on an HTML widget can never have the form placed inside it. Getting this wrong is unrecoverable without restructuring, and it looks correct until the moment something must go inside.

Fonts and CSS belong in an HTML widget only when Elementor Pro is unavailable. With Pro, prefer site-level Custom Fonts and the page's Custom CSS field. Google Fonts via one `@import` beats embedding whenever the client has no policy against external requests.

## Step 4 — Deliver as numbered .txt files

One file per paste target, numbered in paste order and matching the naming table. Not one file with section markers inside. `.txt`, not `.html`, so double-clicking opens an editor. Ship an ASCII-safe twin (non-Latin characters as numeric HTML entities) if encoding breaks anywhere in the chain.

## Step 5 — Beat Elementor's CSS, deliberately

Elementor's own rules are more specific than naive selectors and will win. Three places this bites:

- **Containers**: `.e-con` sets `width` and `max-width` from its own variable, and overrides `align-items`. Width, centering and alignment need `!important`.
- **Form fields**: `input[type="text"]` loses to `.elementor-widget-form .elementor-field-group .elementor-field-textual`. Target Elementor's own classes — `.elementor-field-textual`, `.elementor-button[type="submit"]`, `.elementor-field-group`, `.elementor-field-type-acceptance` — with `!important`.
- **Field spacing**: set `margin-bottom` on `.elementor-field-group`, not `gap` on the wrapper. The wrapper is not reliably a flex container.

**Never rely on the parent to center a child.** `align-items` on the container is overridden, and in RTL "start" is the right edge, so a `max-width` block without auto margins hugs the right while everything around it looks centered. Give every constrained child `margin-left:auto; margin-right:auto` explicitly.

Never send the user hunting through Elementor panels for alignment or width. Fix it in the CSS and prove it.

## Step 6 — Verify against a hostile parent, then measure

Before shipping any CSS, build a local harness that reproduces what Elementor actually does: a flex container with `align-items: normal`, widgets forced to `width: 100%`, and Elementor's default field and button rules present. Render it with Playwright and measure. Every Elementor-specific breakage in this skill was found this way and would have shipped otherwise.

What to measure:

- **Fonts loaded**: render the same word in the target font and in a deliberately fake font name, and compare widths. Equal widths mean everything fell back — invisible in a screenshot.
- **Per-element symmetry**: for each text block and the form, measure left gap and right gap against the card. "Looks centered" is not evidence; an editor selection outline once made a correctly centered layout look shifted.
- **Horizontal overflow**: `scrollWidth` vs `innerWidth` at 1440, 768 and 375.
- **Paste integrity on the live page**: character count of each HTML widget's `innerHTML` against the source file size.
- **Images**: `naturalWidth > 0` and rendered width matches intent.
- **Leftover placeholders**: search the live DOM for `REPLACE`.

Report what was measured and what was not. Never say "verified" for a dimension that was not measured.

## Step 7 — Mobile is not in the design

Design canvases are desktop-only. Author the mobile pass explicitly: heading scale, multi-column blocks collapsing to one, side padding, avatar and overlap sizes, and form fields never below 16px (smaller triggers zoom on iOS Safari). Verify at 375. Resizing the user's browser window may not change the reported viewport — if it does not, say so and ask for a phone screenshot rather than claiming mobile was checked.

## Elementor template JSON

A container exported as a template makes the whole block reusable across pages. Two things to know:

- **Import only from the local library**: Templates → Saved Templates → Import. From the editor's library popup or a cloud tab it fails with `This source does not support import`.
- **Import drops `_css_classes` from the container.** After every import, verify the class is on the container; without it none of the CSS matches and the block renders raw.

Make the template self-contained: include its CSS as the first child widget, scoped so it needs no external stylesheet. A form-only stylesheet should target `.elementor-widget-form` directly so it works with no class and no configuration.

A template written by hand always fights the install's version and permissions. Once the block works on a real page, have the user export it from Elementor — that export is authoritative and is what future pages should import.

## Known breakages

- **Element stretched**: a fixed-size box inside a flex parent needs `flex: none` plus explicit width and height.
- **Missing `box-sizing: border-box`**: invisible on desktop, breaks out of its container on mobile.
- **RTL list numbers render as `.1`**: wrap the number in `<span dir="ltr">1.</span>` or append an RLM.
- **Overlapping element clipped**: a negative margin cannot cross a widget boundary. The overlapping element must live in the same widget as what it overlaps.
- **Alt text visible on an image**: the `src` is still a placeholder.
- **Form dropped outside the card**: dragging into a populated container usually misses. Use right-click Copy on the form, then right-click Paste on the widget it should follow — Elementor pastes into that widget's container.

## What stays out of the HTML

Anything that acts — form, submit button, links edited later — stays a native Elementor widget, so redirect, validation, lead storage and integrations keep working. Style it from CSS via the container class and tell the user explicitly not to style it in the panel; also tell them what the CSS does and does not take over, since `!important` on appearance can read as losing control of behavior.

## Handover

Before declaring done: the form's Actions After Submit (redirect target), the terms link, the conversion event, real images replacing placeholders, and a full run of the flow — submit, redirect, confirmation email.

## Learned on the Rachel Pottery build (2026-09-10)

**Delivery is a repo, not a paste.** The page HTML lives in `orcatribeltd-glitch/orca-landing-pages` under `pages/<name>/`; WordPress shows it through the `orca-landing-pages` plugin and `[landing_page name="<name>"]`. Steps 1–2 above still apply to the Claude Design export; the output of step 4 for the *page* is one `index.html` in the repo, and the numbered `.txt` files are only for the parts that must be pasted (nothing, when the plugin is installed). Images go into `pages/<name>/images/` with relative paths — never hot-linked from another site; five of them were deleted from orcatribe.co.il and the page shipped broken.

**Walk every element before handover and ask "will he change this from the panel?"** Link, text, redirect, target → Button / Text Editor / Form widget with a CSS class, styled from the container CSS with `!important`. The rule already stood in "What stays out of the HTML"; the WhatsApp button and the footer shipped as HTML anyway and Jonathan could not set the link. The template is built by a script (`templates/build_<name>_form.py`) so a fix is an edit and a re-run.

**Field IDs must not collide with Elementor's webhook meta.** The webhook payload flat-merges field values with `date`, `time`, `page_url`, `user_agent`, `remote_ip`, `powered_by`, `form_id`, `form_name`, and meta wins. A visit-date field named `date` reached Zapier as the submission date. Use `visit_date`, `preferred_time`.

**Import only from the classic library page.** `wp-admin/edit.php?post_type=elementor_library&tabs_group=library` → ייבוא תבניות. The new cloud-library screen fails with `This source does not support import` — confirmed live.

**Never promise a deploy latency before measuring it on that site, and measure with a visible element, never a comment.** Caches between a push and the visitor: GitHub raw CDN (branch URLs ≤5 min; the plugin fetches by commit SHA), the plugin transient (object cache — purge by generation, not SQL), and a page cache that differs per site. Read the last 300 bytes of the live HTML first: cache plugins sign there ("Cache by SpeedyCache" on influence-club.co.il — it strips HTML comments, which made a comment-based stamp read as "stale for 15 minutes" when the real number was 8 seconds). rachel-pottery.co.il has a server-side page cache instead (15–25 min lag, Jonathan chose to live with it). `?v=1` on the URL bypasses page caches for checking. Do not ask Jonathan for a credential (cPanel token) until the layer that needs it is confirmed to be the one in play.

**The `</>` grey box in the editor is the CSS HTML widget.** It is invisible on the live page; say so before Jonathan asks.

**Since plugin 1.6.0 (2026-09-11) the page creates itself.** A page template JSON (`"type":"page"`, canvas + background in `page_settings`, a Shortcode widget for the repo HTML, a native Form widget in its own container) plus a line in `pages.json` is enough: on the next push the `orca-landing-pages` plugin creates the page as a draft on the matching site. Nobody imports templates any more. Elementor still drops `_css_classes` on the created container — so the repo HTML attaches the card classes to the form's container with a small script (see `pages/mashpian-cancel/index.html`); do the same on every new page instead of asking Jonathan to check the class. What stays human: approve the preview, set Actions After Submit, publish.

