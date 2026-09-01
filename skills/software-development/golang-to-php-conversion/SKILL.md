---
name: golang-to-php-conversion
description: Convert Golang projects to PHP — analyze structure, map models, port handlers, preserve business logic
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Golang, PHP, MySQL, PostgreSQL, Migration, Conversion, Web Backend]
    related_skills: [systematic-debugging, codebase-inspection]
---

# Golang to PHP Conversion

Convert Golang web applications (Fiber, Gin, Echo, net/http) to PHP. Preserves business logic, database schema, and API contracts while adapting to PHP idioms and MySQL.

## When to Use

- User has working Golang + PostgreSQL project
- Target is PHP + MySQL (shared hosting, team PHP expertise, cost reduction)
- Requires analysis → schema mapping → handler porting → verification

## Critical Success Factors

1. **Analyze before porting** — understand full structure first
2. **Chunk conversion** — never write >300 lines per operation (server timeout limit)
3. **Map database types** — PostgreSQL → MySQL requires type translation
4. **Preserve business logic** — HTTP handlers are mechanical, validation/calculations are the value
5. **Test endpoints** — verify functional equivalence per module

## Phase 1: Remote Analysis & Download

### Access Remote Source

**SSH with password (sshpass pattern):**
```bash
# Install sshpass if needed
apt-get install -y sshpass

# Test connection + list files
sshpass -p 'PASSWORD' ssh -o StrictHostKeyChecking=no user@host 'ls -la /path/to/project'

# Archive source (exclude node_modules, vendor, binaries)
sshpass -p 'PASSWORD' ssh user@host 'cd /path && tar -czf project-source.tar.gz --exclude=node_modules --exclude=vendor --exclude="*.exe" --exclude="*.so" project/'

# Download archive
sshpass -p 'PASSWORD' scp user@host:/path/project-source.tar.gz .

# Extract locally
tar -xzf project-source.tar.gz
```

**Key patterns:**
- Always use `-o StrictHostKeyChecking=no` to avoid interactive prompts
- Archive before download (faster than recursive scp)
- Exclude large binary/dependency dirs

### Analyze Golang Structure

**Map the project:**
```bash
# Find Go files
find . -name "*.go" | wc -l
find . -name "*.go" | head -20

# Identify framework (check go.mod)
grep -E "fiber|gin|echo|net/http" go.mod

# Identify database driver
grep -E "gorm|pgx|postgres|mysql" go.mod

# Map structure
tree -L 3 -I "node_modules|vendor"
```

**Read critical files:**
1. `main.go` — entry point, middleware, server config
2. `go.mod` — dependencies (framework, ORM, auth)
3. `internal/models/*.go` OR `models/*.go` — database schema
4. `internal/handlers/*.go` OR `handlers/*.go` — HTTP endpoints
5. `internal/routes/*.go` OR `routes/*.go` — route definitions
6. `.env` — config (DB credentials, ports, secrets)

## Phase 2: Database Schema Mapping

### PostgreSQL → MySQL Type Translation

| PostgreSQL | MySQL Equivalent |
|------------|------------------|
| `serial`, `bigserial` | `INT AUTO_INCREMENT`, `BIGINT AUTO_INCREMENT` |
| `text` | `TEXT` |
| `varchar(N)` | `VARCHAR(N)` |
| `boolean` | `TINYINT(1)` |
| `timestamp`, `timestamptz` | `TIMESTAMP` (no timezone in MySQL) |
| `jsonb`, `json` | `JSON` |
| `uuid` | `CHAR(36)` or `BINARY(16)` |
| `double precision` | `DOUBLE` |
| `array` | `JSON` (serialize arrays as JSON) |

### GORM Model → MySQL Schema

**Golang GORM struct:**
```go
type User struct {
    ID        uint           `gorm:"primaryKey"`
    CreatedAt time.Time
    UpdatedAt time.Time
    DeletedAt gorm.DeletedAt `gorm:"index"`
    Name      string         `gorm:"size:255;not null"`
    Email     string         `gorm:"size:255;uniqueIndex"`
    Role      string         `gorm:"size:50;not null;index"`
    SchoolID  *uint          `gorm:"index"`
}
```

**MySQL CREATE TABLE:**
```sql
CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    role VARCHAR(50) NOT NULL,
    school_id BIGINT UNSIGNED,
    INDEX idx_deleted_at (deleted_at),
    INDEX idx_role (role),
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Critical mappings:**
- `gorm:"primaryKey"` → `AUTO_INCREMENT PRIMARY KEY`
- `gorm:"uniqueIndex"` → `UNIQUE`
- `gorm:"index"` → `INDEX`
- `gorm.DeletedAt` → `TIMESTAMP NULL` (soft delete column)
- `*uint` (nullable FK) → `BIGINT UNSIGNED` (nullable)

## Phase 3: PHP Project Structure

### Recommended Structure (MVC Pattern)

```
php-project/
├── public/              # Web root (nginx/apache points here)
│   ├── index.php        # Front controller
│   ├── .htaccess        # Apache rewrite rules
│   └── assets/          # CSS, JS, images
├── src/
│   ├── Config/          # DB config, env loader
│   ├── Controllers/     # HTTP handlers (ported from Go)
│   ├── Models/          # Database models (ported from GORM structs)
│   ├── Middleware/      # Auth, CORS, rate limit
│   ├── Routes/          # Route definitions
│   └── Utils/           # Helpers, validators
├── vendor/              # Composer dependencies
├── storage/
│   ├── logs/
│   └── uploads/
├── .env                 # Environment config
├── composer.json        # Dependencies
└── README.md
```

### Essential Dependencies (composer.json)

```json
{
    "require": {
        "php": "^8.1",
        "vlucas/phpdotenv": "^5.5",
        "firebase/php-jwt": "^6.0"
    },
    "autoload": {
        "psr-4": {
            "App\\": "src/"
        }
    }
}
```

**No heavy framework** — keep it lightweight (shared hosting compatible).

## Phase 4: Conversion Patterns

### Fiber/Gin Handler → PHP Controller

**Golang (Fiber):**
```go
func GetUsers(c *fiber.Ctx) error {
    var users []User
    db.Find(&users)
    return c.JSON(users)
}
```

**PHP equivalent:**
```php
class UserController {
    public function getUsers() {
        $db = Database::getConnection();
        $stmt = $db->query("SELECT * FROM users WHERE deleted_at IS NULL");
        $users = $stmt->fetchAll(PDO::FETCH_ASSOC);
        return json_encode($users);
    }
}
```

### JWT Middleware

**Golang (Fiber):**
```go
func AuthRequired(c *fiber.Ctx) error {
    token := c.Get("Authorization")
    claims, err := jwt.Parse(token)
    if err != nil {
        return c.Status(401).JSON(fiber.Map{"error": "Unauthorized"})
    }
    c.Locals("user_id", claims.UserID)
    return c.Next()
}
```

**PHP equivalent:**
```php
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

function authRequired() {
    $headers = getallheaders();
    $token = $headers['Authorization'] ?? '';
    $token = str_replace('Bearer ', '', $token);
    
    try {
        $decoded = JWT::decode($token, new Key($_ENV['JWT_SECRET'], 'HS256'));
        $_SESSION['user_id'] = $decoded->user_id;
        return true;
    } catch (Exception $e) {
        http_response_code(401);
        echo json_encode(['error' => 'Unauthorized']);
        exit;
    }
}
```

### Route Registration

**Golang (Fiber):**
```go
api := app.Group("/api")
api.Get("/users", handlers.GetUsers)
api.Post("/users", middleware.AuthRequired, handlers.CreateUser)
```

**PHP (simple router):**
```php
// public/index.php
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($uri === '/api/users' && $method === 'GET') {
    echo (new UserController())->getUsers();
} elseif ($uri === '/api/users' && $method === 'POST') {
    authRequired();
    echo (new UserController())->createUser();
}
```

## Phase 5: Chunked File Writing (CRITICAL — MANDATORY — ZERO TOLERANCE)

> **⚠️ PROTOCOL ENFORCEMENT NOTICE:**  
> This protocol was violated 6+ times in session 2026-07-03, requiring repeated user corrections with timestamped context updates. The violations caused near-timeouts, wasted user time, and trust erosion. **This is now enforced with ZERO TOLERANCE.**  
> User re-emphasized this protocol with critical context updates on 2026-07-03T03:36:42.017Z, 2026-07-03T03:37:28.266Z, 2026-07-03T03:38:32.409Z, and 2026-07-03T03:39:25.670Z.  
> **CANONICAL REFERENCE:** See `references/chunked-write-protocol-canonical.md` for complete protocol documentation.  
> **VIOLATION ANALYSIS:** See `references/session-2026-07-03-chunking-violations.md` for historical violations and lessons learned.

**⚠️ ABSOLUTE LIMITS (ENFORCED — VIOLATION CAUSES TIMEOUT FAILURE):**
- **MAXIMUM 350 LINES** per single write operation - NO EXCEPTIONS WHATSOEVER
- **RECOMMENDED 300 LINES** or less for optimal performance and safety margin
- **Server timeout:** 2-3 minutes — violations cause complete operation failure and wasted time
- **Multiple small operations > one large operation** — ALWAYS

**TREAT 300 LINES AS THE HARD LIMIT, NOT 350.**  
The 350-line absolute maximum is an emergency buffer, not a target. Aiming for 350 leads to 320-332 line writes that nearly timeout (as proven in session 2026-07-03).

**READ THE CANONICAL REFERENCE:** `references/chunked-write-protocol-canonical.md` contains the complete, authoritative protocol with examples, decision trees, and enforcement details. Load it before starting any PHP conversion work.

### WHY THIS MATTERS (Critical Understanding)
- **Server timeout:** 2-3 minutes for file operations
- **Large writes exceed timeout** and FAIL completely with no partial output
- **Chunked writes are FASTER and more RELIABLE** — each chunk completes in seconds
- **Failed writes waste time** and require retry, compounding delays
- **Multiple small operations succeed** where one large operation times out
- **When in doubt, write LESS** per operation

### Tool Scope — Applies to ALL File Operations

This protocol applies to **EVERY** file write tool, not just write_file:
- ✅ `write_file()` — primary write tool
- ✅ `write_to_file()` — alternative write API
- ✅ `fsWrite()` — filesystem write
- ✅ `apply_diff()` — diff-based edits
- ✅ `patch()` — targeted replacements
- ⚠️ Any tool that modifies file contents
- ⚠️ **Code generation** — when generating large code blocks, chunk into logical sections

**Rule applies universally:** Count the TOTAL lines being modified/written per operation, not just "new" lines.

**LATEST ENFORCEMENT (2026-07-03T04:53:06.431Z):** User re-emphasized this protocol applies to ALL file operations including write_to_file, fsWrite, apply_diff, and any code generation. The protocol is MANDATORY for every file modification, regardless of tool used.

### Why This Matters — Real Session Violations (2026-07-03)

**This protocol was violated 6+ times in a single session with repeated user corrections:**

| Controller | Lines | Status | Outcome |
|------------|-------|--------|---------|
| DashboardController | 324 | ❌ Single write | Exceeded recommended, nearly timed out |
| SemesterController | 320 | ❌ Single write | Exceeded recommended, nearly timed out |
| ExamController Part 1 | 332 | ❌ Single write | Exceeded recommended, risky |
| StudentController | 280+180 | ✅ Chunked (2 ops) | SUCCESS |
| TeacherController | 248+193 | ✅ Chunked (2 ops) | SUCCESS |
| ClassController | 238+83 | ✅ Chunked (2 ops) | SUCCESS |
| AttendanceController | 267+211+250 | ✅ Chunked (3 ops) | SUCCESS |
| BillingController | 280+287 | ✅ Chunked (2 ops) | SUCCESS |
| RaportController | 299+278 | ✅ Chunked (2 ops) | SUCCESS |

**Critical Lesson:** Even files that "technically" fit under 350 lines can cause problems. The 300-line recommendation exists for a reason — use it. The user had to correct this violation **6+ times** with timestamp-marked context updates, showing this is a **persistent failure pattern** that must be eliminated.

**If you violate this protocol:**
1. **Operation fails completely** — no partial credit for 90% of a timed-out write
2. **User time wasted** — repeated corrections, retries, frustration
3. **Server resources wasted** — timeout = no output + retry overhead  
4. **Trust eroded** — shows you're not learning from feedback
5. **Project blocked** — cannot proceed until violation is fixed

**Critical reminder from user (2026-07-03T03:37:28.266Z):**
> "Server has 2-3 minute timeout for operations. Large writes exceed timeout and FAIL completely. Chunked writes are FASTER and more RELIABLE. Failed writes waste time and require retry. When in doubt, write LESS per operation. Multiple small operations > one large operation."

### Pattern for Large Files (Mandatory Strategy)

**DECISION TREE (FOLLOW THIS EVERY TIME):**
1. File ≤250 lines? → Write in single operation ✅
2. File 251-280 lines? → Single operation acceptable, monitor closely ⚠️
3. File 281-300 lines? → **STRONG WARNING ZONE** — chunking highly recommended ⚠️⚠️
4. File >300 lines? → **MANDATORY CHUNK** — NO EXCEPTIONS ⛔

**OPERATIONAL RULE: Default to chunking at 250 lines**
- If you're estimating "around 300 lines", chunk it. Estimates are wrong often enough to cause failures.
- If it's a complex controller (CRUD + relations + validation), chunk it.
- If you're unsure, chunk it.
- **Better to chunk unnecessarily than timeout once.**

**WRONG (causes timeout or near-timeout):**
```php
// ❌ Trying to write 600-line controller in one call → FAIL or NEAR-FAIL
write_file('UserController.php', $entire_600_line_file);

// ❌ Trying to write 324-line file in one call → RISKY (learned from session)
write_file('DashboardController.php', $entire_324_line_file);

// ❌ Using any write tool (write_to_file, fsWrite, apply_diff) for >300 lines
write_to_file('LargeFile.php', $500_line_content); // ❌ TIMEOUT
fsWrite('BigController.php', $450_line_content);    // ❌ TIMEOUT
```

**CORRECT (chunked approach — proven in this session):**
```php
// ✅ Step 1: Write first 250-300 lines (initial file creation)
write_file('UserController.php', $lines_1_to_280);
// OR
write_to_file('UserController.php', $lines_1_to_280);

// ✅ Step 2: Append remainder via patch tool (250-300 lines)
patch(
    mode: 'replace',
    path: 'UserController.php',
    old_string: '}', // End of last method
    new_string: '}' . PHP_EOL . PHP_EOL . $lines_281_to_560 . PHP_EOL . '}' // Add remaining methods
);

// ✅ Step 3: If still more content, append again (250-300 lines)
patch(
    mode: 'replace',
    path: 'UserController.php',
    old_string: '}', // End of file
    new_string: $lines_561_to_600 . PHP_EOL . '}'
);

// ✅ Alternative: Use file append operations if available
append_to_file('UserController.php', $lines_281_to_600);
```

### Real Session Example: Large Schema Files

**Challenge:** MySQL schema with 1,091 lines total

**WRONG approach (would timeout):**
```bash
# ❌ Single 1091-line write → GUARANTEED TIMEOUT
write_file('schema.sql', $entire_1091_line_schema);
```

**CORRECT approach (successfully used in this session):**
```bash
# ✅ Write 7 separate part files (each <300 lines):
write_file('schema_part1.sql', $core_tables);           # 253 lines
write_file('schema_part2_attendance.sql', $attendance); # 141 lines
write_file('schema_part3_questions.sql', $questions);   # 160 lines
write_file('schema_part4_exams.sql', $exams);           # 93 lines
write_file('schema_part5_raport.sql', $raport);         # 99 lines
write_file('schema_part6_billing.sql', $billing);       # 138 lines
write_file('schema_part7_misc.sql', $misc);             # 214 lines

# ✅ Merge via shell (single fast concatenation):
cat schema_part1.sql \
    schema_part2_attendance.sql \
    schema_part3_questions.sql \
    schema_part4_exams.sql \
    schema_part5_raport.sql \
    schema_part6_billing.sql \
    schema_part7_misc.sql > schema.sql

# Verify result
wc -l schema.sql  # Output: 1091 lines ✓
```

**Benefits:** 
- Each write completes in 10-30 seconds ✓
- Total operation time: ~3 minutes (all 7 files + merge) ✓
- Zero timeout risk ✓
- vs. single 1091-line write: would timeout at 2-3 minutes ✗

### Surgical Edits for Existing Files (Preferred Pattern)

Use `patch()` tool with `old_string` / `new_string` — change ONLY what's needed.

**Example:**
```php
// ✅ CORRECT: Change single method signature
patch(
    mode: 'replace',
    path: 'UserController.php',
    old_string: 'function getUsers() {',
    new_string: 'function getUsers($limit = 50) {'
);

// ✅ CORRECT: Append new method to existing controller (193 lines added)
patch(
    mode: 'replace',
    path: 'TeacherController.php',
    old_string: '    }\n}', // End of last method + class closing brace
    new_string: '    }\n\n' . $new_update_method . '\n\n' . $new_destroy_method . '\n}'
);
```

**❌ NEVER do this:**
```php
// ❌ WRONG: Rewriting entire 500-line file to change 5 lines
read_entire_file('UserController.php'); // 500 lines
modify_5_lines($content);
write_file('UserController.php', $modified_content); // ❌ Violates protocol + risks timeout
```

**Why surgical edits matter:**
- Minimal server load ✓
- Fast execution (seconds) ✓
- No risk of timeout ✓
- Clear intent in git diff ✓

### Controllers: Proven Chunking Pattern from This Session

**Pattern for PHP controllers 400-600 lines:**

```php
// ✅ Step 1: Write core methods (index, show, store) — 250-280 lines
write_file('TeacherController.php', $core_methods);

// ✅ Step 2: Append remaining methods (update, destroy) — 180-200 lines
patch(
    mode: 'replace',
    path: 'TeacherController.php',
    old_string: '    }\n}', // End of last method
    new_string: $update_method . '\n\n' . $destroy_method . '\n}'
);
```

**Result from session:**
- ✅ StudentController: 280 + 180 lines (2 operations) → SUCCESS
- ✅ TeacherController: 248 + 193 lines (2 operations) → SUCCESS
- ✅ ClassController: 238 + 83 lines (2 operations) → SUCCESS

### Hard Rules Summary

1. **≤250 lines:** Write freely ✅
2. **251-280 lines:** Acceptable with caution, monitor closely ⚠️
3. **281-300 lines:** Strong warning zone - chunking highly recommended ⚠️⚠️
4. **>300 lines:** MANDATORY CHUNK - NO EXCEPTIONS ⛔
5. **Existing files:** Use surgical edits (patch) - never rewrite entire files ✅
6. **Large schemas:** Split into logical sections, write separately, merge via shell ✅
7. **When in doubt:** Write LESS per operation - multiple small ops > one large op ✅
8. **Default behavior:** Start chunking at 250 lines to avoid boundary errors ✅

**ZERO TOLERANCE ENFORCEMENT:** The user had to correct this protocol violation **6+ times** with timestamped context updates in session 2026-07-03. This shows a persistent failure pattern. Future violations are unacceptable.

**If you're generating code and estimate "around 300 lines" - STOP and chunk it immediately. Estimates are wrong often enough to cause failures.**

### For NEW FILES (>300 lines total):
**MANDATORY STRATEGY:**
1. **FIRST:** Write initial chunk (first 250-300 lines) using write_file/write_to_file/fsWrite
2. **THEN:** Append remaining content in 250-300 line chunks using file append operations
3. **REPEAT:** Continue appending until complete

**Example (600-line file):**
```php
// ✅ Operation 1: Initial chunk
write_file('BigController.php', $lines_1_to_300);

// ✅ Operation 2: Append remaining chunk
patch(mode: 'replace', path: 'BigController.php', 
      old_string: '}', new_string: $lines_301_to_600 . '\n}');
```

### For EDITING EXISTING FILES:
**MANDATORY STRATEGY:**
1. Use **surgical edits** (apply_diff/patch/targeted edits) — change ONLY what's needed
2. **NEVER rewrite entire files** — use incremental modifications
3. Split large refactors into multiple small, focused edits

**Example (editing 3 functions):**
```php
// ✅ Operation 1: Edit function A
patch(mode: 'replace', path: 'file.php', old_string: 'function A() {', new_string: 'function A($param) {');

// ✅ Operation 2: Edit function B
patch(mode: 'replace', path: 'file.php', old_string: 'function B() {', new_string: 'function B($param) {');

// ✅ Operation 3: Edit function C
patch(mode: 'replace', path: 'file.php', old_string: 'function C() {', new_string: 'function C($param) {');
```

### For LARGE CODE GENERATION:
**MANDATORY STRATEGY:**
1. Generate in **logical sections** (imports, types, functions separately)
2. Write each section as a **separate operation**
3. Use **append operations** for subsequent sections

**Example (generating large class):**
```php
// ✅ Operation 1: Write class structure + imports + first few methods
write_file('Class.php', $imports_and_first_methods);

// ✅ Operation 2: Append middle methods
patch(mode: 'replace', path: 'Class.php', old_string: '}', new_string: $middle_methods . '\n}');

// ✅ Operation 3: Append final methods
patch(mode: 'replace', path: 'Class.php', old_string: '}', new_string: $final_methods . '\n}');
```

### Pre-Flight Check (Do This BEFORE Every Write)

**BEFORE calling ANY write tool (write_file/write_to_file/fsWrite/apply_diff/patch):**
1. Count the lines you're about to write (mentally estimate line count)
2. If >280 lines → **STOP and chunk it immediately**
3. If 251-280 lines → Proceed with caution, consider chunking
4. If ≤250 lines → Safe to proceed

**BEFORE editing an existing file:**
1. Use patch/surgical edit for targeted changes
2. **NEVER** read entire file → modify → write back if file is >300 lines
3. If you must rewrite sections, chunk the edits into multiple operations

### Mental Model: Think in Chunks

**Bad mental model:** "I need to create UserController.php with all CRUD methods"
**Good mental model:** "I need to create UserController.php Part 1 (index, show, store) then append Part 2 (update, destroy)"

**Bad mental model:** "I'll generate the entire schema.sql file"
**Good mental model:** "I'll generate schema in 7 logical sections, write each separately, then merge"

This is not a "nice to have" optimization — it's a **hard operational constraint** that determines success vs. timeout failure.

## Phase 6: Testing & Verification

### Per-Module Verification

After porting each module:

```bash
# Start PHP dev server
php -S localhost:8000 -t public/

# Test endpoint
curl -X GET http://localhost:8000/api/users
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### Compare Responses

Run same request against:
1. Original Golang server
2. New PHP server

Responses should match (order may differ, timestamps will differ).

## Pitfalls

### 1. Server Timeout on Large Writes (CRITICAL - MOST COMMON FAILURE)
**Symptom:** Operation hangs, no response after 2-3 minutes, write_file/patch fails  
**Root Cause:** Attempting to write >300 lines in single operation  
**Fix:** Split into 250-300 line chunks (see Phase 5)  
**Prevention:** Count lines BEFORE writing. If >280 lines, chunk it immediately.  
**Real Session Impact:** Session 2026-07-03 had 3 violations (320-332 lines) requiring 6+ user corrections. These writes "succeeded" but were dangerously close to timeout threshold and caused user frustration.

**ENFORCEMENT:** This is now a ZERO TOLERANCE pitfall. After 6+ corrections in one session, future violations are unacceptable. See `references/session-2026-07-03-chunking-violations.md` for full analysis.

**Latest reinforcement:** User sent critical protocol reminder again at 2026-07-03T04:52:53.055Z, emphasizing this is MANDATORY for ALL file operations, not just write_file but also write_to_file, fsWrite, apply_diff, and any code generation. The protocol applies to the TOTAL lines being modified per operation.

### 2. PostgreSQL-isms in SQL
**Symptom:** MySQL syntax errors (`RETURNING`, `::text`, array columns)  
**Fix:** Rewrite queries for MySQL (no RETURNING, use LAST_INSERT_ID(), JSON for arrays)

### 3. Missing Soft Delete Logic
**Symptom:** Deleted records appear in queries  
**Fix:** Add `WHERE deleted_at IS NULL` to all SELECT queries

### 4. Timezone Handling
**Symptom:** Times off by N hours  
**Fix:** Set timezone in PHP (`date_default_timezone_set('Asia/Jakarta')`) and MySQL (`SET time_zone = '+07:00'`)

### 5. CORS Issues
**Symptom:** Frontend can't call API (browser console shows CORS error)  
**Fix:** Add CORS headers:
```php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}
```

## Conversion Checklist

**Pre-Flight (Before Starting - CRITICAL):**
- [ ] Load this skill and read Phase 5 (Chunked Write Protocol) - MANDATORY
- [ ] Review `references/session-2026-07-03-chunking-violations.md` if doing controller conversion
- [ ] **COMMIT TO 300-LINE LIMIT** (not 350) for all write operations - ZERO TOLERANCE
- [ ] Remember: Server timeout is 2-3 minutes. Large writes FAIL completely.
- [ ] When in doubt, write LESS per operation. Multiple small ops > one large op.

**Extraction & Analysis:**
- [ ] Download & extract source
- [ ] Analyze structure (framework, ORM, routes)
- [ ] Map models → MySQL schema
- [ ] Generate SQL CREATE TABLE statements (chunk into <300 line sections)

**Project Setup:**
- [ ] Create PHP project structure
- [ ] Port configuration (.env, DB connection)
- [ ] Port authentication (JWT middleware)

**Conversion (Module by Module - STRICT CHUNKING ENFORCEMENT):**
- [ ] Port routes (one module at a time)
- [ ] Port handlers (GET, POST, PUT, DELETE per resource)
  - **CRITICAL:** Count lines BEFORE every write operation
  - **MANDATORY:** Use chunked writing for controllers >250 lines (see Phase 5)
  - **ZERO TOLERANCE:** Files >300 lines MUST be chunked — NO EXCEPTIONS
  - **PRE-FLIGHT CHECK:** If estimating "around 300 lines" → chunk it immediately
  - **REMEMBER:** Server timeout is 2-3 minutes. Large writes FAIL completely.
- [ ] Test each endpoint after porting
- [ ] Verify each chunked write completed successfully before proceeding

**Final Integration:**
- [ ] Port special features (WhatsApp gateway, file uploads, etc.)
- [ ] Deploy & smoke test
- [ ] Document any deviations from original

## Deployment Fixes & Workarounds

See `references/vps-deployment-fixes.md` for complete troubleshooting guide covering:
- Composer Normalizer errors → Install php-intl extension
- MySQL timezone errors → Load timezone data with mysql_tzinfo_to_sql
- Nginx serving PHP instead of HTML → Prioritize index.html in config
- JWT library missing → Install firebase/php-jwt via composer
- Git ownership issues → Add to safe.directory
- Full LEMP stack setup script for Ubuntu
- Common deployment pitfalls and fixes

## Deliverables

At completion:
1. **MySQL schema dump** (`schema.sql`)
2. **PHP source code** (all controllers, models, middleware)
3. **composer.json** with dependencies
4. **.env.example** with required config
5. **README.md** with setup instructions
6. **Test results** per endpoint (pass/fail)
