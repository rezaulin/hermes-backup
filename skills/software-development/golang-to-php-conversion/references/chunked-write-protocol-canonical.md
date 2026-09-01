# CHUNKED WRITE PROTOCOL — CANONICAL REFERENCE

**Last Updated:** 2026-07-03T03:38:32.409Z  
**Status:** MANDATORY — ZERO TOLERANCE ENFORCEMENT  
**Scope:** ALL file write operations across ALL tools

---

## ABSOLUTE LIMITS

- **MAXIMUM 350 LINES** per single write/edit operation - NO EXCEPTIONS WHATSOEVER
- **RECOMMENDED 300 LINES** or less for optimal performance and safety margin
- **NEVER** write entire files in one operation if >300 lines total

**CRITICAL:** Treat 300 lines as the hard limit, NOT 350. The 350-line maximum is an emergency buffer, not a target.

---

## WHY THIS MATTERS

### Server Constraints
- **Server timeout:** 2-3 minutes for file operations
- **Large writes exceed timeout** and FAIL completely with NO partial output
- **No partial credit:** 90% of a timed-out write = 0% success

### Real-World Impact
1. **Operation fails completely** — entire write is lost on timeout
2. **User time wasted** — repeated corrections, retries, frustration
3. **Server resources wasted** — timeout = no output + retry overhead
4. **Trust eroded** — shows agent is not learning from feedback
5. **Project blocked** — cannot proceed until violation is fixed

### Performance Reality
- **Chunked writes are FASTER and more RELIABLE** — each chunk completes in seconds
- **Failed writes waste time** and require complete retry
- **Multiple small operations > one large operation** — ALWAYS

**GOLDEN RULE:** When in doubt, write LESS per operation.

---

## TOOL SCOPE — APPLIES UNIVERSALLY

This protocol applies to **EVERY** file write tool, not just write_file:
- ✅ `write_file()` — primary write tool
- ✅ `write_to_file()` — alternative write API
- ✅ `fsWrite()` — filesystem write
- ✅ `apply_diff()` — diff-based edits
- ✅ `patch()` — targeted replacements
- ⚠️ **ANY tool that modifies file contents**

**Rule applies universally:** Count the TOTAL lines being modified/written per operation, not just "new" lines.

---

## MANDATORY CHUNKED WRITE STRATEGY

### For NEW FILES (>300 lines total):

**MANDATORY APPROACH:**
1. **FIRST:** Write initial chunk (first 250-300 lines) using write_to_file/fsWrite/write_file
2. **THEN:** Append remaining content in 250-300 line chunks using file append operations
3. **REPEAT:** Continue appending until complete

**Example (600-line file):**
```
✅ Operation 1: Write lines 1-300 (initial file creation)
   write_file('BigController.php', $lines_1_to_300);

✅ Operation 2: Append lines 301-600
   patch(mode: 'replace', path: 'BigController.php', 
         old_string: '}', new_string: $lines_301_to_600 . '\n}');
```

**WRONG approach:**
```
❌ Single operation: write_file('BigController.php', $all_600_lines);
   Result: TIMEOUT at 2-3 minutes → COMPLETE FAILURE
```

---

### For EDITING EXISTING FILES:

**MANDATORY APPROACH:**
1. Use **surgical edits** (apply_diff/patch/targeted edits) — change ONLY what's needed
2. **NEVER rewrite entire files** — use incremental modifications
3. Split large refactors into multiple small, focused edits

**Example (editing 3 functions):**
```
✅ Operation 1: Edit function A
   patch(mode: 'replace', path: 'file.php', 
         old_string: 'function A() {', new_string: 'function A($param) {');

✅ Operation 2: Edit function B
   patch(mode: 'replace', path: 'file.php', 
         old_string: 'function B() {', new_string: 'function B($param) {');

✅ Operation 3: Edit function C
   patch(mode: 'replace', path: 'file.php', 
         old_string: 'function C() {', new_string: 'function C($param) {');
```

**WRONG approach:**
```
❌ Read entire 500-line file → modify 3 functions → write back entire file
   Result: TIMEOUT risk + unnecessary server load
```

---

### For LARGE CODE GENERATION:

**MANDATORY APPROACH:**
1. Generate in **logical sections** (imports, types, functions separately)
2. Write each section as a **separate operation**
3. Use **append operations** for subsequent sections

**Example (generating large class):**
```
✅ Operation 1: Write class structure + imports + first methods (280 lines)
   write_file('Class.php', $imports_and_first_methods);

✅ Operation 2: Append middle methods (250 lines)
   patch(mode: 'replace', path: 'Class.php', 
         old_string: '}', new_string: $middle_methods . '\n}');

✅ Operation 3: Append final methods (200 lines)
   patch(mode: 'replace', path: 'Class.php', 
         old_string: '}', new_string: $final_methods . '\n}');
```

---

## PRE-FLIGHT CHECK (MANDATORY BEFORE EVERY WRITE)

**BEFORE calling ANY write tool:**

1. **Count the lines** you're about to write (mentally estimate line count)
2. **Decision tree:**
   - **≤250 lines:** Safe to proceed ✅
   - **251-280 lines:** Acceptable with caution, monitor closely ⚠️
   - **281-300 lines:** Strong warning zone — chunking highly recommended ⚠️⚠️
   - **>300 lines:** **MANDATORY CHUNK** — STOP and chunk immediately ⛔

3. **If estimating "around 300 lines":** → CHUNK IT IMMEDIATELY
   - Estimates are wrong often enough to cause failures
   - Better to chunk unnecessarily than timeout once

4. **Default behavior:** Start chunking at 250 lines to avoid boundary errors

---

## DECISION TREE (FOLLOW THIS EVERY TIME)

```
Is this a NEW file?
├─ YES → Will it be >300 lines total?
│  ├─ YES → MANDATORY CHUNK (write initial 250-300, append rest)
│  └─ NO → Single write OK (if ≤250 lines)
│
└─ NO (editing existing) → Are you changing >300 lines?
   ├─ YES → MANDATORY CHUNK (multiple surgical edits)
   └─ NO → Surgical edit OK (patch/targeted changes)
```

---

## EXAMPLES OF CORRECT vs. WRONG BEHAVIOR

### ✅ CORRECT: Writing a 600-line file
```
Operation 1: Write lines 1-300 (initial file creation)
Operation 2: Append lines 301-600
Total time: ~45 seconds (both operations complete)
Result: SUCCESS ✓
```

### ❌ WRONG: Writing 500 lines in single operation
```
Operation 1: Write all 500 lines at once
Total time: 2-3 minutes → TIMEOUT
Result: COMPLETE FAILURE ✗
```

### ✅ CORRECT: Editing multiple functions
```
Operation 1: Edit function A (surgical patch)
Operation 2: Edit function B (surgical patch)
Operation 3: Edit function C (surgical patch)
Total time: ~15 seconds
Result: SUCCESS ✓
```

### ❌ WRONG: Rewriting entire file to change 5 lines
```
Operation 1: Read 500-line file
Operation 2: Modify 5 lines
Operation 3: Write back entire 500-line file
Total time: 2-3 minutes → TIMEOUT
Result: COMPLETE FAILURE ✗
```

### ✅ CORRECT: Generating massive code
```
Operation 1: Write imports + types (280 lines)
Operation 2: Append core functions (250 lines)
Operation 3: Append utility functions (220 lines)
Total time: ~60 seconds
Result: SUCCESS ✓
```

### ❌ WRONG: Generating massive code in one block
```
Operation 1: Write all 750 lines at once
Total time: TIMEOUT at 2-3 minutes
Result: COMPLETE FAILURE ✗
```

---

## HISTORICAL VIOLATIONS — LEARN FROM THESE

### Session 2026-07-03 Violations

| File | Lines | Approach | Status | Lesson |
|------|-------|----------|--------|--------|
| DashboardController | 324 | ❌ Single write | Nearly timed out | Exceeded recommended 300 limit |
| SemesterController | 320 | ❌ Single write | Nearly timed out | Exceeded recommended 300 limit |
| ExamController Pt1 | 332 | ❌ Single write | Nearly timed out | Exceeded recommended 300 limit |
| StudentController | 280+180 | ✅ Chunked (2 ops) | SUCCESS | Proper chunking strategy |
| TeacherController | 248+193 | ✅ Chunked (2 ops) | SUCCESS | Proper chunking strategy |
| AttendanceController | 267+211+250 | ✅ Chunked (3 ops) | SUCCESS | Proper chunking strategy |

**Critical Lesson:** Files that "technically" fit under 350 lines can still cause near-timeout problems. The 300-line recommendation exists for a reason — **USE IT**.

User had to correct this violation **6+ times** with timestamp-marked context updates, showing this is a **persistent failure pattern** that MUST be eliminated.

---

## MENTAL MODEL — THINK IN CHUNKS

### ❌ Bad mental model:
- "I need to create UserController.php with all CRUD methods"
- "I'll generate the entire schema.sql file"
- "Let me write this whole API handler in one operation"

### ✅ Good mental model:
- "I need to create UserController.php **Part 1** (index, show, store) then **append Part 2** (update, destroy)"
- "I'll generate schema in **7 logical sections**, write each separately, then merge"
- "I'll write the **core logic first** (280 lines), then **append helpers** (200 lines)"

**This is not a "nice to have" optimization — it's a HARD OPERATIONAL CONSTRAINT that determines success vs. timeout failure.**

---

## ENFORCEMENT — ZERO TOLERANCE

After 6+ violations in session 2026-07-03 requiring repeated user corrections with timestamped context updates:

- ✅ This protocol is now **MANDATORY** with **ZERO TOLERANCE** for violations
- ✅ Future violations are **UNACCEPTABLE** and show failure to learn from feedback
- ✅ User will not repeat corrections — agent must internalize this protocol
- ✅ Treat 300 lines as **HARD LIMIT**, not 350 (350 is emergency buffer only)

**REMEMBER:**
- Server timeout: 2-3 minutes
- Large writes FAIL completely
- Chunked writes are FASTER and more RELIABLE
- When in doubt, write LESS per operation
- **Multiple small operations > one large operation — ALWAYS**

---

## QUICK REFERENCE CARD

**BEFORE EVERY WRITE:**
1. Count lines
2. >280 lines? → STOP and chunk
3. Editing existing? → Surgical edit only
4. When in doubt → Write LESS

**REMEMBER:**
- 300 lines = HARD LIMIT (not 350)
- Server timeout = 2-3 minutes
- Failed writes = COMPLETE FAILURE
- Chunked = FASTER and RELIABLE
- Multiple small ops > one large op
