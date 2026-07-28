# System Architecture

## Application Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FORBES MARSHALL SYSTEM                    │
└─────────────────────────────────────────────────────────────┘

                          ┌──────────────┐
                          │   USER       │
                          │  (Browser)   │
                          └──────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
           ┌────────▼────────┐      ┌────────▼────────┐
           │   FRONTEND      │      │   BACKEND       │
           │   (React 19)    │◄────►│   (Flask)       │
           │   Port 3000     │      │   Port 5000     │
           └─────────────────┘      └─────────┬───────┘
                    │                         │
                    │                    ┌────▼────────┐
                    │                    │  Database   │
                    │                    │  (MySQL)    │
                    │                    │employees.db │
                    │                    └─────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
    ┌───▼────┐           ┌─────▼──────┐
    │ Login  │           │ Protected  │
    │ Page   │           │  Routes    │
    └───┬────┘           └─────┬──────┘
        │                      │
    ┌───▼────────────────────┬─┴──────────┐
    │                        │            │
┌───▼─────┐          ┌──────▼──┐  ┌─────▼──────┐
│  ADMIN  │          │ EMPLOYEE│  │   TOKEN    │
│Dashboard│          │Homepage │  │(JWT Auth) │
├─────────┤          ├─────────┤  └────────────┘
│• Add    │          │• Welcome│
│  Emp    │          │  Message│
│• View   │          │• Data   │
│  Emp    │          │  Entry  │
│• Delete │          │• Logout │
│  Emp    │          │         │
└─────────┘          └─────────┘
```

---

## User Authentication Flow

```
START
  │
  ▼
┌─────────────────────┐
│   Login Page        │
│ Email + Password    │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐      ┌────────────────┐
    │ Verify       │      │  INVALID       │
    │ Credentials  ├─────►│  Show Error    │
    └──────┬───────┘      └────┬───────────┘
           │                   │
        VALID              TRY AGAIN
           │                   │
           └───────┬───────────┘
                   │
           ┌───────▼──────────┐
           │  Generate JWT    │
           │  Token           │
           └───────┬──────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Check User Role     │
        └──────┬───────┬───────┘
               │       │
          ┌────▼──┐ ┌──▼───┐
          │ADMIN  │ │EMPLOYEE
          └───┬───┘ └──┬────┘
              │       │
        ┌─────▼──┐ ┌──▼──────┐
        │  Admin │ │Employee  │
        │Dashboard│Homepage
        └────────┘ └──────────┘
```

---

## Database Schema

```
┌─────────────────────────────────────┐
│           USERS TABLE               │
├─────────────────────────────────────┤
│ id           │ INTEGER PRIMARY KEY  │
│ email        │ STRING (UNIQUE)      │
│ password     │ STRING (HASHED)      │
│ role         │ STRING ('admin' or   │
│              │  'employee')         │
│ name         │ STRING (Optional)    │
└─────────────────────────────────────┘

INDEXES:
- email (for fast lookup during login)
- role (for filtering admin vs employees)

SAMPLE DATA:
┌────┬───────┬───────────┬──────────┬──────────┐
│ id │ email │ password  │ role     │ name     │
├────┼───────┼───────────┼──────────┼──────────┤
│ 1  │admin@gmail.com│[hashed]   │ admin    │ NULL     │
│ 2  │john@  │[hashed]   │employee  │John Doe  │
│ 3  │jane@  │[hashed]   │ employee │Jane Smith│
└────┴───────┴───────────┴──────────┴──────────┘
```

---

## Request Flow Example

### Add Employee (Admin)

```
Frontend                Backend              Database
(Admin.js)              (Flask)              (SQLite)
   │                       │                    │
   │─ POST to /api/add-    │                    │
   │   employee with JWT   │                    │
   │   {name, email, pass} │                    │
   │                   ┌───▼────────────┐       │
   │                   │ Verify JWT     │       │
   │                   │ Check admin    │       │
   │                   │ role           │       │
   │                   └────┬───────────┘       │
   │                        │                   │
   │                        ├──────────┬────────►
   │                        │ Create   │ INSERT
   │                        │ User     │ New User
   │                        │ Hash     │
   │                        │ Password │
   │                        └────┬─────┼────────►
   │                             │    │
   │◄───── Response 201 ─────────┤    │
   │       {employee data}       │    │
   │                             │    │
   │─ Refresh Employees List ────┤    │
   │                             │    │
   │                        ┌────▼────┴────────►
   │                        │ SELECT * FROM    │
   │                        │ users WHERE role │
   │                        │ = 'employee'     │
   │                        └────┬────────┬────┘
   │◄───── Return all ──────────┤        │
   │       employees             │        │
   │                             │        │
```

---

## Component Hierarchy

```
App.js (Router)
  │
  ├─► Login.js
  │    └─► handleLogin()
  │        └─► localStorage.setItem('token')
  │
  ├─► Home.js (Protected)
  │    ├─► useEffect (check token)
  │    ├─► handleSubmit()
  │    ├─► handleLogout()
  │    └─► Displays: "Welcome, {user.name}!"
  │
  └─► Admin.js (Protected)
       ├─► useEffect (fetch employees)
       ├─► handleAddEmployee()
       ├─► handleDeleteEmployee()
       └─► Display:
           ├─► Add Employee Form
           └─► Employees Table
```

---

## State Management (localStorage)

```
Local Storage
├─ token: "eyJ0eXAiOiJKV1QiLC..."  (JWT Token)
└─ user: {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "role": "employee"
   }
```

---

## Security Flow

```
1. PASSWORD HASHING
   ┌─────────────────────────────────┐
   │ User enters: "mypassword123"    │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │ werkzeug.security.hash_password()│
   │ (uses PBKDF2 by default)         │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │ Store in DB:                    │
   │ "pbkdf2:sha256:600000$xxxx..."  │
   └─────────────────────────────────┘

2. JWT TOKEN GENERATION
   ┌──────────────────────────────────┐
   │ After successful login           │
   │ JWT Token created with:          │
   │ - user_id as identity            │
   │ - Expiration: 30 days            │
   │ - Secret key signed              │
   └──────────┬───────────────────────┘
              │
              ▼
   ┌────────────────────────────────────┐
   │ Token sent to frontend             │
   │ Stored in localStorage             │
   │ Sent in Authorization header:      │
   │ "Bearer eyJ0eXAi..."               │
   └────────────┬───────────────────────┘
                │
                ▼
   ┌────────────────────────────────────┐
   │ Backend verifies token on          │
   │ each protected API call            │
   │ (Check signature, expiration)      │
   └────────────────────────────────────┘

3. ROLE-BASED ACCESS
   ┌──────────────────────────────────┐
   │ Token verified                   │
   │ Check user.role                  │
   ├──────────────────────────────────┤
   │ IF role = 'admin'  ✓ Allow       │
   │ IF role = 'employee' ✗ Deny      │
   └──────────────────────────────────┘
```

---

## Error Handling Flow

```
API Request
    │
    ▼
┌────────────────────────┐
│ Network Error?         │
└──────┬─────────────────┘
       │ NO
       ▼
┌──────────────────────────┐
│ Check Status Code        │
└──────┬──────────────────┘
       │
   ┌───┴───┬──────┬──────┐
   │       │      │      │
 200     400    401    500
   │     │      │      │
 ✓OK  Bad    Auth   Server
     Req    Error   Error
   │     │      │      │
   └─────┴──────┴──────►
         │
         ▼
   Get Error Message
   from response.data.error
         │
         ▼
   Display to User
```

---

This architecture ensures:
- ✅ **Security**: Password hashing + JWT tokens
- ✅ **Performance**: Database indexed queries
- ✅ **Scalability**: Stateless backend
- ✅ **Usability**: Clear user flows
- ✅ **Maintainability**: Modular components
