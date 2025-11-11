# Campus Resource Hub - Security Guidelines

## Critical Security Requirements

### 1. Password Security
```python
# ✓ CORRECT: Hash passwords with bcrypt
import bcrypt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# ✗ WRONG: Never store plain text passwords
password = "user_password"  # NEVER DO THIS
```

### 2. SQL Injection Prevention
```python
# ✓ CORRECT: Parameterized queries
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))

# ✗ WRONG: String concatenation
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")  # VULNERABLE
```

### 3. CSRF Protection
```html
<!-- ✓ CORRECT: Include CSRF token in all forms -->
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <!-- form fields -->
</form>

<!-- ✗ WRONG: Missing CSRF token -->
<form method="POST">
    <!-- VULNERABLE TO CSRF ATTACKS -->
</form>
```

### 4. XSS Prevention
```python
# ✓ CORRECT: Use bleach to sanitize HTML
import bleach
clean_content = bleach.clean(user_input, tags=['b', 'i', 'u'], strip=True)

# ✗ WRONG: Directly rendering user input
{{ user_input|safe }}  # VULNERABLE IF NOT SANITIZED
```

### 5. Authentication & Authorization
```python
# ✓ CORRECT: Use @login_required decorator
from flask_login import login_required, current_user

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ✓ CORRECT: Check user permissions
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```

### 6. Session Security
```python
# ✓ CORRECT: Secure session configuration
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JS access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
```

### 7. Input Validation
```python
# ✓ CORRECT: Server-side validation
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return False
    return True
```

### 8. File Upload Security
```python
# ✓ CORRECT: Validate file types and sanitize names
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
```

### 9. Error Handling
```python
# ✓ CORRECT: Don't expose sensitive info in errors
try:
    result = UserDAL.get_user(user_id)
except Exception as e:
    app.logger.error(f"Database error: {str(e)}")
    flash('An error occurred. Please try again.', 'danger')  # Generic message

# ✗ WRONG: Exposing database structure
except Exception as e:
    flash(f'Database error: {str(e)}', 'danger')  # EXPOSES DB DETAILS
```

### 10. Rate Limiting
```python
# ✓ CORRECT: Implement rate limiting for sensitive endpoints
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Prevent brute force
def login():
    # Login logic
    pass
```

## Security Checklist for New Features

- [ ] All user input validated server-side
- [ ] SQL queries use parameterized statements
- [ ] Forms include CSRF tokens
- [ ] Passwords are hashed with bcrypt
- [ ] Authentication required for protected routes
- [ ] Authorization checks for role-based access
- [ ] User-generated content is sanitized
- [ ] Error messages don't expose sensitive data
- [ ] File uploads are validated and sanitized
- [ ] Sessions are configured securely
- [ ] Sensitive operations are rate-limited
- [ ] HTTPS enforced in production

## Common Vulnerabilities to Avoid

1. **SQL Injection**: Always use parameterized queries
2. **XSS**: Sanitize all user input before rendering
3. **CSRF**: Include tokens in all state-changing forms
4. **Broken Authentication**: Implement proper session management
5. **Sensitive Data Exposure**: Hash passwords, encrypt sensitive data
6. **Broken Access Control**: Check permissions before allowing actions
7. **Security Misconfiguration**: Review all config settings
8. **Insecure Deserialization**: Validate all serialized data
9. **Using Components with Known Vulnerabilities**: Keep dependencies updated
10. **Insufficient Logging**: Log security events for auditing
