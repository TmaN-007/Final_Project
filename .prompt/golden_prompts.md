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

## OOP Refactoring

### Prompt: Property-Based Encapsulation

**Effectiveness:** ⭐⭐⭐⭐⭐ (5/5)

**Prompt:**
```
"I see you are using @property a lot of the places but we need to use it
with getters and setters thats the requirement"

Follow-up: "It should be everywhere without breaking the code anywhere"
```

**Why It Worked:**
- Clear requirement: "everywhere" set scope
- Constraint: "without breaking the code" emphasized backward compatibility
- Implied testing: AI knew to verify existing code continued working
- Academic context: Understood this was a course requirement

**Result:** 80+ properties added across 5 model files with comprehensive validation

**Implementation Strategy AI Used:**
1. Used Task tool to systematically update each model file
2. Converted all attributes to private (underscore prefix)
3. Added @property getters with type hints and docstrings
4. Added setters with domain-specific validation
5. Maintained backward compatibility with property access pattern

**Code Pattern Generated:**
```python
# Private attribute in __init__
self._rating = data['rating']

# Property getter
@property
def rating(self) -> int:
    """Get rating."""
    return self._rating

# Property setter with validation
@rating.setter
def rating(self, value: int):
    """Set rating with validation."""
    if not isinstance(value, int) or not 1 <= value <= 5:
        raise ValueError("Rating must be between 1 and 5")
    self._rating = value
```

**What Made This Excellent:**
- AI added validation logic appropriate to each field
- Type hints added automatically
- Docstrings provided for documentation
- Validation rules matched business domain (e.g., rating 1-5, end > start)
- No breaking changes to existing DAL code

---

## Frontend Development

### Prompt: Theme-Aware Icon Integration

**Effectiveness:** ⭐⭐⭐⭐ (4/5)

**Initial Prompt:**
```
"I added 2 icons for light mode and dark mode for study rooms"
Context: User uploaded Study_Room_Icon_Light.png and Study_Room_Icon_Dark.png
```

**Follow-up Clarification:**
```
"the light and dark are other way arounf"
```

**Why It Worked:**
- User provided actual files (concrete assets)
- Naming convention was clear (_Light, _Dark suffixes)
- User feedback helped correct initial misunderstanding
- Iterative debugging identified CSS positioning issue

**Result:** Theme-aware icon system applied to all 5 resource categories

**Debugging Process:**
1. Initial issue: Icons not visible
   - AI investigated CSS positioning conflicts
   - Fixed by changing from absolute to flexbox layout
2. Second issue: Wrong theme mapping
   - User feedback: "light and dark are other way around"
   - AI swapped class assignments to match convention

**Code Pattern Generated:**
```html
<!-- HTML: Dual image structure -->
<div class="category-icon">
    <img src="Study_Room_Icon_Light.png" class="icon-light">
    <img src="Study_Room_Icon_Dark.png" class="icon-dark">
</div>
```

```css
/* CSS: Theme-aware display */
.category-icon .icon-dark { display: block; }
.category-icon .icon-light { display: none; }

[data-theme="light"] .category-icon .icon-dark { display: none; }
[data-theme="light"] .category-icon .icon-light { display: block; }
```

**What Could Have Been Better:**
- Initial prompt could have specified: "light icons for dark mode" explicitly
- Could have asked for preview/screenshot to verify correct mapping

**Lessons Learned:**
- Visual elements benefit from iterative feedback
- Naming conventions (Light/Dark) can be ambiguous without context
- User testing in both themes essential

---

## Feature Verification

### Prompt: Functionality Confirmation

**Effectiveness:** ⭐⭐⭐⭐⭐ (5/5)

**Prompt:**
```
"does the remember me button work does it actually remember?"
```

**Why It Worked:**
- Direct question about feature behavior
- AI traced full implementation chain
- Provided code references with line numbers
- Explained how the feature works under the hood

**Result:** Complete verification of Remember Me functionality with code path documentation

**AI Response Strategy:**
1. Found frontend checkbox element
2. Traced form data processing (validators.py)
3. Located Flask-Login integration (auth_controller.py)
4. Verified configuration settings (config.py)
5. Explained cookie mechanism and security flags

**What Made This Excellent:**
- AI provided code evidence, not just "yes it works"
- Explained the implementation chain
- Referenced specific line numbers for traceability
- Covered security aspects (httponly, secure flags)
- Gave timeline context (365-day expiration)

**Pattern for Future Verification Prompts:**
```
"Does [feature] work? Show me the code path."
```

This prompts AI to:
- Verify implementation exists
- Trace full execution path
- Provide code references
- Explain how it works

---

## Updated Prompt Engineering Principles

### 8. **Leverage User Feedback in Iterations**
- Initial implementation may need refinement
- User feedback like "other way around" guides corrections
- Visual/UX elements especially benefit from this
- AI learns context through conversation

### 9. **Request Code Path Tracing**
- Not just "does it work?" but "show me how"
- AI should reference specific files and line numbers
- Full implementation chain demonstrates thoroughness
- Helps verify security and configuration

### 10. **Academic Requirements Need Explicit Statement**
- "that's the requirement" signals non-negotiable
- "everywhere" sets clear scope
- "without breaking" defines constraints
- AI understands academic context vs. production context

---

## New Template: Refactoring Prompt

```
Refactor [COMPONENT] to use [PATTERN] with:
1. [Specific pattern requirement]
2. Must maintain backward compatibility
3. Add [validation/security/documentation]

Apply this pattern everywhere in [scope].
Verify no breaking changes to existing code.

Expected result: [SUCCESS CRITERIA]
```

**Example:**
```
Refactor all model classes to use @property getters/setters with:
1. Private attributes (underscore prefix)
2. Must maintain backward compatibility with existing DAL code
3. Add validation appropriate to each field type

Apply this pattern everywhere in src/models/.
Verify no breaking changes to existing code.

Expected result: All model attributes accessed via properties with validation
```

---

## New Template: Visual Integration Prompt

```
Integrate [ASSETS] into [LOCATION] with:
1. [Specific display requirement]
2. Theme-aware: [light/dark mode behavior]
3. Apply to all instances: [list locations]

Assets provided: [list files]

Expected result: [Visual outcome description]
Test in both themes before completing.
```

**Example:**
```
Integrate custom PNG icons into home page categories with:
1. Display 56x56 size, centered in category box
2. Theme-aware: light icons in dark mode, dark icons in light mode
3. Apply to all instances: category carousel + featured resources

Assets provided:
- Study_Room_Icon_Light.png / Study_Room_Icon_Dark.png
- (repeat for all categories)

Expected result: Icons visible in both themes with proper contrast
Test in both themes before completing.
```

---

**Last Updated:** 2025-11-11
**Next Prompts to Document:**
- Resource controller completion prompts
- Booking calendar implementation prompts
- Test generation prompts
