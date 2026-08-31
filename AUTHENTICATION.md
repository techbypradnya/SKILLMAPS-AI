# SkillGraph AI Authentication System

Complete authentication system for SkillGraph AI with login, signup, and protected routes.

## Overview

This authentication system provides:
- User registration with email and password
- Secure login with HttpOnly cookie-based sessions
- Protected routes that require authentication
- Logout functionality
- Forgot password flow (email delivery not configured)
- Password strength validation
- User profile display in navigation

## Getting Started

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and update SECRET_KEY for production
   # For development, the defaults are fine
   ```

3. **Run the backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   
   The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Set environment variables:**
   ```bash
   # Create .env.local
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

3. **Run the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   
   The app will be available at `http://localhost:3000`

## Authentication Flow

### Sign Up Flow
1. User navigates to `/signup`
2. Enters full name, email, password, and confirms password
3. Frontend validates password strength requirements:
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one number
4. Frontend shows password requirements in real-time
5. Backend validates all inputs and hashes password
6. User account is created
7. User is automatically logged in
8. Redirects to `/dashboard`

### Login Flow
1. User navigates to `/login`
2. Enters email and password
3. Backend validates credentials
4. Sets secure HttpOnly cookie with JWT token
5. User object is returned and stored in auth context
6. Redirects to `/dashboard`

### Protected Routes
- Dashboard and other authenticated pages automatically redirect to `/login` if user is not authenticated
- Loading state is shown while checking authentication status
- On refresh, authentication is checked via `/api/auth/me` endpoint

### Logout
- User clicks logout button in navigation
- Cookie is cleared on backend and frontend
- User is redirected to `/login`

## API Endpoints

### Authentication Routes

#### POST `/api/auth/signup`
Create a new user account.

**Request:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (201 Created):**
```json
{
  "id": "user-id",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-08-31T10:00:00"
}
```

**Errors:**
- `400 Bad Request` - Invalid email format or weak password
- `409 Conflict` - Email already registered

#### POST `/api/auth/login`
Authenticate a user.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "id": "user-id",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-08-31T10:00:00"
}
```

Sets `auth_token` cookie (HttpOnly, 7 days expiration).

**Errors:**
- `401 Unauthorized` - Invalid credentials

#### GET `/api/auth/me`
Get current authenticated user.

**Response:**
```json
{
  "id": "user-id",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-08-31T10:00:00"
}
```

**Errors:**
- `401 Unauthorized` - Not authenticated

#### POST `/api/auth/logout`
Clear authentication session.

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

#### POST `/api/auth/forgot-password`
Initiate password reset (placeholder implementation).

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "message": "If an account exists with this email, a password reset link has been sent."
}
```

## Password Requirements

Passwords must meet these requirements:
- ✓ Minimum 8 characters
- ✓ At least one uppercase letter (A-Z)
- ✓ At least one number (0-9)

Requirements are validated on both frontend (real-time feedback) and backend (enforced).

## Security Features

1. **Password Hashing**: Passwords are hashed using bcrypt with 12 rounds
2. **JWT Tokens**: Secure token-based authentication
3. **HttpOnly Cookies**: Auth tokens stored in HttpOnly cookies (not accessible via JavaScript)
4. **CORS**: Configured for localhost development
5. **Session Duration**: Tokens valid for 7 days
6. **Email Validation**: Basic email format validation

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id VARCHAR(36) PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  display_name VARCHAR(255),
  is_demo BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Frontend Components

### AuthProvider (`lib/auth.tsx`)
Global authentication state provider. Manages:
- User state
- Authentication status
- Loading state
- Login/logout functions
- Auth check on app load

Usage:
```tsx
import { useAuth } from "@/lib/auth";

export default function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();
  // ... use auth state
}
```

### ProtectedRoute (`components/ProtectedRoute.tsx`)
Wrapper component that redirects unauthenticated users to login.

Usage:
```tsx
import { ProtectedRoute } from "@/components/ProtectedRoute";

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>Protected content here</div>
    </ProtectedRoute>
  );
}
```

## Backend Components

### Security Module (`app/services/security.py`)
Utilities for:
- Password hashing and verification
- Password strength validation
- JWT token creation and validation
- Email validation

### Auth Routes (`app/api/routes/auth_routes.py`)
FastAPI routes for all authentication endpoints.

### Schemas (`app/schemas/schemas.py`)
Pydantic models for request/response validation:
- `SignUpRequest`
- `LoginRequest`
- `UserResponse`
- `ForgotPasswordRequest`

## Frontend Pages

### Login Page (`app/login/page.tsx`)
Clean login interface with:
- Email and password fields
- "Remember me" checkbox
- "Forgot password?" link
- Sign up link
- Google OAuth placeholder (disabled)
- Loading and error states

### Sign Up Page (`app/signup/page.tsx`)
Registration interface with:
- Full name, email, password fields
- Password confirmation
- Real-time password strength indicator
- Login link
- Loading and error states

### Forgot Password Page (`app/forgot-password/page.tsx`)
Password reset flow with:
- Email input
- Success confirmation message
- Security-conscious design (no email confirmation)

## Testing the System

### Test Sign Up
1. Navigate to `http://localhost:3000/signup`
2. Fill in the form with:
   - Full Name: "Test User"
   - Email: "test@example.com"
   - Password: "TestPass123"
   - Confirm Password: "TestPass123"
3. Click "Create Account"
4. Should be redirected to dashboard

### Test Login
1. Navigate to `http://localhost:3000/login`
2. Enter:
   - Email: "test@example.com"
   - Password: "TestPass123"
3. Click "Login"
4. Should be redirected to dashboard

### Test Protected Routes
1. While logged in, navigate to `/dashboard` - should work
2. Logout using the button in navigation
3. Try to access `/dashboard` - should redirect to `/login`

### Test Persistent Login
1. Log in at `http://localhost:3000/login`
2. Refresh the page - you should remain logged in
3. Check the "Hi, User Name 👋" in the navigation

## Environment Variables

### Backend (.env)
```
ENV=development
APP_NAME=SkillGraph AI
DATABASE_URL=sqlite:///./skillgraph.db
SECRET_KEY=your-secret-key-change-this-in-production
VECTOR_BACKEND=none
LLM_PROVIDER=none
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Production Considerations

1. **SECRET_KEY**: Generate a strong random key for production
2. **CORS_ORIGINS**: Update to match your production domain
3. **Secure Cookies**: Set `secure=True` in production (requires HTTPS)
4. **Database**: Use PostgreSQL in production instead of SQLite
5. **Email**: Implement actual password reset email delivery
6. **Rate Limiting**: Add rate limiting to auth endpoints
7. **HTTPS**: Use HTTPS in production for secure cookie transmission
8. **Environment Variables**: Use `.env` file that is NOT committed to version control

## Common Issues

### Issue: "Email already registered" when signing up
**Solution**: The email is already in the database. Use a different email or delete the user from the database.

### Issue: "Invalid credentials" when logging in
**Solution**: Check that email and password are correct. Passwords are case-sensitive.

### Issue: Redirects to login after refresh
**Solution**: The auth check failed. Verify backend is running and `/api/auth/me` returns 401 (expected if cookie is invalid).

### Issue: CORS errors
**Solution**: Verify `CORS_ORIGINS` in backend .env includes your frontend URL.

## Future Enhancements

- [ ] Email verification for signup
- [ ] Password reset via email
- [ ] OAuth integration (Google, GitHub)
- [ ] Two-factor authentication
- [ ] Account recovery options
- [ ] Session management (view active sessions, logout other devices)
- [ ] Account deletion
- [ ] Email change with verification

## File Structure

```
backend/
  app/
    api/
      routes/
        auth_routes.py      # Authentication endpoints
        __init__.py
    services/
      security.py          # Password hashing, JWT, validation
    schemas/
      schemas.py           # Auth request/response models
    models/
      models.py            # User model (updated)
    core/
      config.py            # Configuration (no changes needed)
    main.py                # FastAPI app (updated to include auth routes)

frontend/
  app/
    login/
      page.tsx             # Login page
    signup/
      page.tsx             # Sign up page
    forgot-password/
      page.tsx             # Forgot password page
    dashboard/
      page.tsx             # Protected dashboard (updated)
    layout.tsx             # Root layout (updated with AuthProvider)
  components/
    Nav.tsx                # Navigation (updated with auth)
    ProtectedRoute.tsx     # Protected route wrapper
  lib/
    auth.tsx               # Auth context provider
```

## Support

For questions or issues, refer to the inline code comments and this documentation.
