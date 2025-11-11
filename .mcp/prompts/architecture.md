# Campus Resource Hub - Architecture Guide

## MVC Structure

### Controllers (`src/controllers/`)
- **Purpose**: Handle HTTP requests and responses
- **Pattern**: Flask Blueprints
- **Responsibilities**:
  - Route definitions
  - Request validation
  - Call DAL methods
  - Return templates or JSON
  - Flash messages to users

**Example**:
```python
from flask import Blueprint, render_template, request, flash
from src.data_access.user_dal import UserDAL

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user_data = UserDAL.verify_password(email, password)
        if user_data:
            # Login successful
            return redirect(url_for('main.index'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('auth/login.html')
```

### Models (`src/models/`)
- **Purpose**: Define data structures
- **Pattern**: Plain Python classes (NOT ORM)
- **Responsibilities**:
  - Data representation
  - Data validation
  - Conversion methods (to_dict, from_dict)
  - NO database operations

**Example**:
```python
class User:
    def __init__(self, user_data):
        self.id = user_data.get('user_id')
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.role = user_data.get('role', 'student')

    def to_dict(self):
        return {
            'user_id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role
        }
```

### Data Access Layer (`src/data_access/`)
- **Purpose**: Database operations ONLY
- **Pattern**: Static methods, parameterized queries
- **Responsibilities**:
  - CRUD operations
  - Complex queries
  - Transaction management
  - SQL injection prevention
  - Error handling

**Example**:
```python
class UserDAL(BaseDal):
    @staticmethod
    def create_user(name, email, password, role='student'):
        conn = UserDAL.get_connection()
        cursor = conn.cursor()

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed_password, role))

        conn.commit()
        return cursor.lastrowid
```

### Views (`src/templates/`)
- **Purpose**: HTML presentation
- **Pattern**: Jinja2 templates with inheritance
- **Responsibilities**:
  - Display data
  - Form rendering
  - Template inheritance
  - User interface

## Security Principles

1. **CSRF Protection**: All forms must include `{{ csrf_token() }}`
2. **Password Hashing**: Never store plain text passwords
3. **Input Validation**: Validate all user input server-side
4. **SQL Injection Prevention**: Always use parameterized queries
5. **XSS Protection**: Sanitize user-generated content
6. **Session Security**: Use Flask-Login for authentication

## Code Organization Rules

1. **No business logic in templates**
2. **No database queries in controllers** (use DAL)
3. **No database operations in models**
4. **Controllers call DAL, DAL returns dictionaries**
5. **Models are for data structure only**

## Database Conventions

- Use parameterized queries: `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))`
- Always close connections: Use `with` statements or explicit `conn.close()`
- Handle exceptions: Wrap database operations in try/except
- Log errors: Use `logging` module for database errors

## Testing Strategy

- **Unit Tests**: Test DAL methods independently
- **Integration Tests**: Test controller + DAL interactions
- **UI Tests**: Test authentication flows end-to-end
- **Security Tests**: Test for SQL injection, XSS, CSRF
