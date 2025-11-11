# Security Enhancement: Role Assignment Model

## Date: 2025-11-08

---

## 🔒 Security Issue Fixed

### Problem:
Original registration form allowed users to self-select their role (student/staff), which is a **security vulnerability**. Users could self-assign privileged roles.

### Solution:
Implemented secure role assignment model where:
- All new registrations default to **'student'** role
- Only **admins** can promote users to 'staff' or 'admin'
- Role field **removed** from public registration form

---

## 📝 Changes Made

### 1. Registration Form (src/forms/auth_forms.py)
**Before:**
```python
role = SelectField(
    'Role',
    choices=[
        ('student', 'Student'),
        ('staff', 'Staff/Faculty')
    ],
    default='student',
    validators=[DataRequired()]
)
```

**After:**
```python
# Role field REMOVED from form
# All registrations default to 'student'
```

---

### 2. User DAL (src/data_access/user_dal.py)

**Already Secure:**
```python
def create_user(cls, name: str, email: str, password: str, role: str = 'student', ...):
    # ✅ Already defaults to 'student'
```

**Added Admin-Only Methods:**
```python
@classmethod
def update_user_role(cls, user_id: int, new_role: str) -> int:
    """
    Update user's role (admin-only operation).

    Security Note:
        This method should only be called by admin users.
        Always verify admin permissions before calling.
    """
    if new_role not in ('student', 'staff', 'admin'):
        raise ValueError(f"Invalid role: {new_role}")

    query = "UPDATE users SET role = ?, updated_at = datetime('now') WHERE user_id = ?"
    return cls.execute_update(query, (new_role, user_id))

@classmethod
def get_all_users(cls, limit: int = 100, offset: int = 0) -> List[Dict]:
    """
    Get all users with pagination (admin-only).
    """
    # Returns users with department info for admin panel
```

---

### 3. Registration Template (src/templates/auth/register.html)

**Before:**
```html
<div class="mb-3">
    <label for="role" class="form-label">Role</label>
    <select class="form-select" id="role" name="role" required>
        <option value="student">Student</option>
        <option value="staff">Staff</option>
    </select>
</div>
```

**After:**
```html
<div class="alert alert-info">
    <small>
        ℹ️ <strong>Note:</strong> All new accounts are created as <strong>Student</strong> accounts.
        If you need staff or admin privileges, please contact an administrator.
    </small>
</div>
```

---

## 🎯 Role Assignment Flow

### User Registration:
```
1. User visits /auth/register
2. Fills out: Name, Email, Password
3. Submits form
4. System creates account with role='student' (hardcoded)
5. User receives verification email
6. User logs in as 'student'
```

### Admin Promotes User:
```
1. Admin logs into admin panel
2. Navigates to User Management
3. Searches for user
4. Clicks "Edit Role"
5. Selects new role: 'staff' or 'admin'
6. Confirms change
7. System calls: UserDAL.update_user_role(user_id, 'staff')
8. User gains new permissions on next login
```

---

## 🛡️ Security Benefits

### ✅ Prevents Privilege Escalation
- Users cannot self-assign 'staff' or 'admin' roles
- All privileged role assignments require admin approval

### ✅ Clear Audit Trail
- `updated_at` timestamp tracks when roles change
- Can add to admin_logs table for full audit trail

### ✅ Defense in Depth
- Even if registration form is bypassed, `create_user()` defaults to 'student'
- `update_user_role()` includes validation

---

## 🔧 Admin Panel Implementation (TODO)

When creating the admin panel, use this pattern:

```python
# src/controllers/admin_controller.py

@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
def update_user_role(user_id):
    """Update user role (admin only)."""

    # Security check
    if not current_user.is_admin:
        abort(403)  # Forbidden

    # Get new role from form
    new_role = request.form.get('role')

    # Validation
    if new_role not in ('student', 'staff', 'admin'):
        flash('Invalid role', 'danger')
        return redirect(url_for('admin.users'))

    # Prevent self-demotion (optional safety check)
    if user_id == current_user.user_id and new_role != 'admin':
        flash('Cannot demote yourself', 'warning')
        return redirect(url_for('admin.users'))

    # Update role
    try:
        UserDAL.update_user_role(user_id, new_role)

        # Log action (optional but recommended)
        AdminLogDAL.log_action(
            admin_id=current_user.user_id,
            action='update_user_role',
            target_table='users',
            target_id=user_id,
            details=f'Role changed to {new_role}'
        )

        flash(f'User role updated to {new_role}', 'success')
    except Exception as e:
        flash(f'Error updating role: {str(e)}', 'danger')

    return redirect(url_for('admin.users'))
```

---

## 📊 Database Schema (No Changes Needed)

The `users` table already supports this model:

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student','staff','admin')),  -- ✅ Constraint enforces valid roles
    -- ... other fields
);
```

**Key Points:**
- ✅ CHECK constraint prevents invalid roles
- ✅ DEFAULT is handled in application layer (UserDAL)
- ✅ No database migration needed

---

## 🧪 Testing Checklist

### Registration Flow:
- [ ] User can register without selecting role
- [ ] Registration creates account with role='student'
- [ ] User cannot bypass form to set role='staff' or 'admin'
- [ ] Verification email is sent
- [ ] User can login after registration

### Admin Role Management:
- [ ] Admin can view all users
- [ ] Admin can change user role to 'staff'
- [ ] Admin can change user role to 'admin'
- [ ] Non-admin users cannot access role management
- [ ] Role changes are logged (if logging implemented)
- [ ] User sees new role on next login

### Security Tests:
- [ ] Direct API call to /auth/register with role='admin' is rejected
- [ ] SQLite CHECK constraint prevents invalid roles
- [ ] UserDAL.update_user_role() validates role values
- [ ] Admin-only routes check current_user.is_admin

---

## 🚀 Deployment Checklist

Before deploying to production:

1. **Verify default admin exists:**
   ```sql
   SELECT * FROM users WHERE role = 'admin';
   ```

2. **Test role assignment:**
   - Create test account
   - Verify role='student'
   - Login as admin
   - Promote test account to 'staff'
   - Verify promotion worked

3. **Review permissions:**
   - Ensure all admin routes check `@login_required` and `current_user.is_admin`
   - Test unauthorized access attempts

4. **Enable audit logging:**
   - Log all role changes to admin_logs table
   - Include timestamp, admin_id, user_id, old_role, new_role

---

## 📚 Related Files

- ✅ `src/forms/auth_forms.py` - RegisterForm (role field removed)
- ✅ `src/data_access/user_dal.py` - update_user_role(), get_all_users()
- ✅ `src/templates/auth/register.html` - Role field removed, info note added
- 📋 `src/controllers/admin_controller.py` - TODO: Implement admin panel
- 📋 `src/templates/admin/users.html` - TODO: Create user management UI

---

## ✅ Summary

**What Changed:**
- Removed role selector from registration form
- All new accounts default to 'student'
- Added admin-only method to change user roles

**Security Improvement:**
- Prevents privilege escalation attacks
- Follows principle of least privilege
- Centralized role management for admins

**Status:** ✅ **Implemented and Ready for Testing**

---

**Last Updated:** 2025-11-08
**Implemented By:** Claude Code (AI Assistant)
**Reviewed By:** Team 13
