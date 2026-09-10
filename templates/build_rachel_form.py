#!/usr/bin/env python3
"""Builds templates/rachel-form.json — the Elementor template that follows the
[landing_page name="rachel-pottery"] shortcode.

Everything that ACTS is a native Elementor widget so Jonathan edits it in the panel:
the Form (leads), the WhatsApp Button (link), the footer Text Editor (privacy link).
The HTML widgets carry only CSS and a decorative divider.
Re-run after any change:  python3 templates/build_rachel_form.py

Field IDs must never collide with Elementor's own submission meta keys
(date, time, page_url, user_agent, remote_ip, powered_by, form_id, form_name):
the webhook payload is a flat merge and the meta wins. "date" for the visit date
silently became the submission date in Zapier (2026-09-10).
"""
import json, pathlib, secrets

OUT = pathlib.Path(__file__).with_name("rachel-form.json")
WA_URL = "https://wa.me/972534255780?text=היי רחל, אנחנו מתעניינים בסדנה..."

CSS = r"""<style>
.rachel-form{--rf-primary:#C4A962;--rf-primary-dark:#A68B45;--rf-wa:#25D366;--rf-text:#3D3D3D;--rf-text-light:#6B6B6B;--rf-border:#E5E5E5;--rf-bg:#FFFFFF;--rf-font:'Heebo',sans-serif;
  font-family:var(--rf-font)!important;direction:rtl;background:var(--rf-bg)!important;padding:0 20px 80px!important;width:100%!important;max-width:100%!important;box-sizing:border-box}
.rachel-form>.e-con-inner{max-width:600px!important;margin-left:auto!important;margin-right:auto!important;width:100%!important;box-sizing:border-box}
.rachel-form .elementor-widget{max-width:600px!important;margin-left:auto!important;margin-right:auto!important;width:100%!important;margin-bottom:0!important}
/* form */
.rachel-form .elementor-widget-form .elementor-form-fields-wrapper{display:flex!important;flex-wrap:wrap!important;margin:0 -10px!important}
.rachel-form .elementor-widget-form .elementor-field-group{padding:0 10px!important;margin-bottom:20px!important;box-sizing:border-box}
.rachel-form .elementor-widget-form .elementor-field-group.elementor-col-50{width:50%!important}
.rachel-form .elementor-widget-form .elementor-field-group.elementor-col-100{width:100%!important}
.rachel-form .elementor-widget-form .elementor-field-label{display:block!important;margin-bottom:8px!important;font-size:.95rem!important;color:var(--rf-text)!important;font-family:var(--rf-font)!important;font-weight:400!important}
.rachel-form .elementor-widget-form .elementor-field-textual,.rachel-form .elementor-widget-form select.elementor-field{width:100%!important;padding:14px 16px!important;border:1px solid var(--rf-border)!important;border-radius:4px!important;
  font-family:var(--rf-font)!important;font-size:16px!important;direction:rtl!important;background:var(--rf-bg)!important;color:var(--rf-text)!important;box-shadow:none!important;transition:all .3s ease}
.rachel-form .elementor-widget-form .elementor-field-textual:focus,.rachel-form .elementor-widget-form select.elementor-field:focus{outline:none!important;border-color:var(--rf-primary)!important;box-shadow:0 0 0 3px rgba(196,169,98,.1)!important}
.rachel-form .elementor-widget-form .elementor-field-textual::placeholder{color:#9a9a9a}
.rachel-form .elementor-widget-form .elementor-field-type-submit{margin-top:10px!important;margin-bottom:0!important}
.rachel-form .elementor-widget-form .elementor-button[type="submit"]{width:100%!important;display:block!important;padding:14px 36px!important;font-size:1.1rem!important;font-weight:500!important;
  border-radius:4px!important;border:none!important;background-color:var(--rf-primary)!important;color:#fff!important;font-family:var(--rf-font)!important;text-align:center!important;transition:all .3s ease;cursor:pointer}
.rachel-form .elementor-widget-form .elementor-button[type="submit"]:hover{background-color:var(--rf-primary-dark)!important;transform:translateY(-2px)}
/* divider (decorative only) */
.rachel-form .rf-divider{display:flex;align-items:center;gap:15px;color:var(--rf-text-light);font-size:.9rem;margin:15px 0;font-family:var(--rf-font)}
.rachel-form .rf-divider::before,.rachel-form .rf-divider::after{content:'';flex:1;height:1px;background:var(--rf-border)}
/* WhatsApp = native Button widget, link set in the panel */
.rachel-form .rf-wa-btn .elementor-button-wrapper{display:block!important}
.rachel-form .rf-wa-btn .elementor-button{display:flex!important;align-items:center;justify-content:center;gap:10px;width:100%!important;box-sizing:border-box;padding:14px 36px!important;font-size:1.1rem!important;font-weight:500!important;
  border-radius:4px!important;border:none!important;background-color:var(--rf-wa)!important;color:#fff!important;text-decoration:none!important;font-family:var(--rf-font)!important;transition:all .3s ease;box-shadow:none!important}
.rachel-form .rf-wa-btn .elementor-button:hover{background-color:#1da851!important;color:#fff!important}
.rachel-form .rf-wa-btn .elementor-button-content-wrapper{display:flex;align-items:center;justify-content:center;gap:10px}
.rachel-form .rf-wa-btn .elementor-button-icon{font-size:22px;line-height:1}
.rachel-form .rf-wa-btn .elementor-button-icon svg{width:24px;height:24px;fill:currentColor}
/* footer = native Text Editor widget */
.rachel-form .rf-footer{margin-top:60px!important;padding-top:30px;border-top:1px solid var(--rf-border);text-align:center!important;color:var(--rf-text-light);font-size:.9rem;line-height:1.8;font-family:var(--rf-font)}
.rachel-form .rf-footer p{margin:0;text-align:center}
.rachel-form .rf-footer a{color:var(--rf-text-light)}
@media (max-width:576px){.rachel-form .elementor-widget-form .elementor-field-group.elementor-col-50{width:100%!important}.rachel-form{padding-bottom:60px!important}}
</style>"""

def wid(): return secrets.token_hex(4)

FIELDS = [
  {"_id":"name","custom_id":"name","field_type":"text","field_label":"שם *","placeholder":"","required":"true","width":"50","width_mobile":"100"},
  {"_id":"phone","custom_id":"phone","field_type":"tel","field_label":"טלפון *","placeholder":"","required":"true","width":"50","width_mobile":"100"},
  {"_id":"guests","custom_id":"guests","field_type":"text","field_label":"כמה אתם?","placeholder":"למשל: 4 מבוגרים + 2 ילדים","required":"","width":"50","width_mobile":"100"},
  {"_id":"visit_date","custom_id":"visit_date","field_type":"text","field_label":"תאריך משוער","placeholder":"למשל: סוף השבוע הקרוב","required":"","width":"50","width_mobile":"100"},
  {"_id":"workshop","custom_id":"workshop","field_type":"select","field_label":"איזו סדנה מעניינת אתכם?","required":"","width":"100","width_mobile":"100",
   "field_options":"בחרו סדנה...|\nקדרות ופיסול (330₪ לאדם)|pottery\nציור על כלי קרמיקה (180₪ לאדם)|painting\nעדיין מתלבטים|undecided"},
]

css_widget = {"id":wid(),"elType":"widget","widgetType":"html","elements":[],"settings":{"html":CSS.strip()}}
form_widget = {"id":wid(),"elType":"widget","widgetType":"form","elements":[],"settings":{
  "form_name":"רחל - סדנאות","form_fields":FIELDS,"show_labels":"true","mark_required":"",
  "button_text":"שריינו לנו מקום ›","button_size":"md","button_width":"100","button_width_mobile":"100",
  "submit_actions":["email"],"email_subject":"ליד חדש מדף הנחיתה: [field id=\"name\"]",
  "email_content":"[all-fields]","email_to":"","email_from_name":"רחל בסוק - סדנאות",
  "success_message":"תודה! רחל תחזור אליכם בהקדם.","error_message":"משהו השתבש, נסו שוב או שלחו הודעה בוואטסאפ.","required_field_message":"שדה חובה"}}
divider_widget = {"id":wid(),"elType":"widget","widgetType":"html","elements":[],"settings":{"html":'<div class="rf-divider">או</div>'}}
wa_button = {"id":wid(),"elType":"widget","widgetType":"button","elements":[],"settings":{
  "text":"דברו עם רחל בוואטסאפ",
  "link":{"url":WA_URL,"is_external":"on","nofollow":"","custom_attributes":""},
  "align":"justify","size":"md",
  "selected_icon":{"value":"fab fa-whatsapp","library":"fa-brands"},"icon_align":"right","icon_indent":{"unit":"px","size":10,"sizes":[]},
  "_css_classes":"rf-wa-btn"}}
footer_widget = {"id":wid(),"elType":"widget","widgetType":"text-editor","elements":[],"settings":{
  "editor":'<p>רחל בסוק | סדנאות קדרות וקרמיקה | מושבה כנרת</p><p>© 2026 כל הזכויות שמורות | <a href="#">מדיניות פרטיות</a></p>',
  "align":"center","_css_classes":"rf-footer"}}

container = {"id":wid(),"elType":"container","isInner":False,
  "elements":[css_widget, form_widget, divider_widget, wa_button, footer_widget],
  "settings":{"_css_classes":"rachel-form","content_width":"boxed","flex_direction":"column","content_position":"center",
              "padding":{"unit":"px","top":"0","right":"20","bottom":"80","left":"20","isLinked":False},
              "background_background":"classic","background_color":"#FFFFFF"}}
tpl = {"version":"0.4","title":"רחל - טופס v2","type":"container","page_settings":[],"content":[container]}
OUT.write_text(json.dumps(tpl, ensure_ascii=False, indent=2))
json.loads(OUT.read_text())
print("wrote", OUT, OUT.stat().st_size, "bytes")
