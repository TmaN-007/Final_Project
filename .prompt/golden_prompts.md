# Golden Prompts - Campus Resource Hub

**Purpose:** Document the most effective AI prompts that produced high-quality results

---

## Database Design

### Prompt: Schema Review and Enhancement

**Effectiveness:** ⭐⭐⭐⭐⭐ (5/5)

**Prompt:**
```
Review this database schema for campus resource booking.
Original has 28 tables. Check if:
1. Table count is correct
2. Polymorphic FKs are documented
3. Constraints allow valid NULL cases
4. All tables are justified against project requirements

If issues found, fix them and explain why.
```

**Why It Worked:**
- Specific checklist format
- Asked for justification (not just fixes)
- Referenced project requirements
- Allowed AI to find additional issues

**Result:** Found 4 critical issues + added comprehensive justification section

---

## Application Architecture

### Prompt: Flask MVC Setup

**Effectiveness:** ⭐⭐⭐⭐⭐ (5/5)

**Prompt:**
```
Create complete Flask application structure with:
- Proper MVC layers (Model, View, Controller, DAL)
- Security utilities built-in from day 1
- AI-first folder structure (.prompt/, docs/context/)
- Testing structure
- Factory pattern for Flask app
- Production-ready configuration management

Use existing 30-table database. Don't recreate schema.
```

**Why It Worked:**
- Clear separation of concerns requested
- "Built-in from day 1" prevented adding security later
- "Use existing database" prevented duplication
- "Production-ready" set quality bar high

**Result:** Complete working Flask app with 40+ files in correct structure

---

## Code Generation

### Prompt: Data Access Layer

**Effectiveness:** ⭐⭐⭐⭐⭐ (5/5)

**Prompt:**
```
Create BaseDAL class with:
1. Context manager for connections
2. Parameterized query methods (prevent SQL injection)
3. Common CRUD operations
4. Error handling and logging
5. Type hints for all methods

Then create UserDAL extending BaseDAL with:
- User CRUD
- Email verification
- Password reset
- Authentication helpers
```

**Why It Worked:**
- Security requirement explicit ("parameterized queries")
- Inheritance pattern clear
- Specific functionality listed
- Type hints requested (better code quality)

**Result:** Production-ready DAL with full security

---

## Security Implementation

### Prompt: Security Utilities

**Effectiveness:** ⭐⭐⭐⭐ (4/5)

**Prompt:**
```
Create security.py with:
1. XSS protection (HTML sanitization with bleach)
2. File upload validation (size, extension, path traversal)
3. Email validation
4. Password strength checking
5. Safe redirect URL generation

Follow OWASP guidelines. Use industry-standard libraries.
```

**Why It Worked:**
- Referenced OWASP (set standard)
- Requested industry-standard libraries (not custom code)
- Specific threat models listed

**What Could Improve:**
- Could have requested unit tests alongside

**Result:** Comprehensive security utilities

---

## Documentation

### Prompt: AI Development Logging

**Effectiveness:** ⭐⭐⭐⭐⭐ (5/5)

**Prompt:**
```
Create dev_notes.md documenting:
1. This AI-generated setup (meta!)
2. All major files created and why
3. Design decisions with justifications
4. Code attribution (what % AI-generated)
5. Ethical AI usage notes
6. Human review status

Format for team collaboration.
```

**Why It Worked:**
- "Meta" request (AI documents itself) was clear
- Team collaboration format ensures others can continue
- Ethical AI section demonstrates responsibility

**Result:** Complete audit trail for academic integrity

---

## Anti-Patterns (Prompts That Didn't Work Well)

### ❌ Too Vague

**Bad Prompt:**
```
Create a Flask app for resource booking
```

**Why It Failed:**
- No architecture specified
- No security requirements
- No project context
- Would generate minimal code

---

### ❌ Too Prescriptive

**Bad Prompt:**
```
Create app.py with exactly these imports:
[long list of specific imports]
then create this exact function:
[full function code pasted]
```

**Why It Failed:**
- No room for AI to optimize
- Might miss better approaches
- Becomes copy/paste, not generation

---

### ❌ Missing Context

**Bad Prompt:**
```
Fix the database schema
```

**Why It Failed:**
- What's wrong with it?
- What requirements should it meet?
- No success criteria

---

## Prompt Engineering Principles (What We Learned)

1. **Be Specific About Security**
   - Always mention: "parameterized queries", "prevent SQL injection"
   - Reference standards: "OWASP guidelines"

2. **Request Justifications**
   - Not just: "Fix this"
   - Better: "Fix this and explain why"
   - AI provides better solutions when explaining

3. **Set Quality Bar**
   - "Production-ready" > "make it work"
   - "Industry standard" > "any solution"

4. **Provide Context**
   - Reference existing files: "Use existing database"
   - Reference requirements: "Project brief section 6"

5. **Request Documentation**
   - "With comments explaining" adds value
   - "Document design decisions" captures reasoning

6. **Use Checklists**
   - Numbered lists guide AI systematically
   - Prevents missing requirements

7. **Allow Optimization**
   - "Best practice" lets AI suggest improvements
   - Don't over-constrain

---

## Template for Future Prompts

```
Create [COMPONENT] with:
1. [Specific requirement 1]
2. [Security requirement]
3. [Performance requirement]

Follow [STANDARD] guidelines.
Use [EXISTING CONTEXT].
Explain design decisions.

Expected result: [SUCCESS CRITERIA]
```

---

## Context Grounding Examples

**Good Context Reference:**
```
According to DATABASE_TABLES.txt line 105, the owner_id is polymorphic.
Implement the User and Group ownership in ResourceDAL.
```

**Why It Worked:**
- Specific file and line reference
- AI can verify against actual project context

---

**Last Updated:** 2025-11-08
**Next:** Document prompts for resource booking conflict detection
