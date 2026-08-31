# SkillGraph AI - Quick Start Guide (with Authentication)

## Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

## Quick Start (5 minutes)

### 1. Terminal Window 1 - Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
✓ Backend running at http://localhost:8000
✓ API docs at http://localhost:8000/docs

### 2. Terminal Window 2 - Start Frontend
```bash
cd frontend
npm install
npm run dev
```
✓ Frontend running at http://localhost:3000

### 3. Test the System

#### Sign Up (New User)
1. Go to http://localhost:3000/signup
2. Fill in the form:
   - Full Name: `Your Name`
   - Email: `your-email@example.com`
   - Password: `TestPass123` (must have 8+ chars, uppercase, number)
   - Confirm: `TestPass123`
3. Click "Create Account"
4. → Redirects to Dashboard ✓

#### Login (Return User)
1. Logout first (click "Logout" in top right)
2. Go to http://localhost:3000/login
3. Enter your email and password
4. Click "Login"
5. → Redirects to Dashboard ✓

#### Test Protected Routes
1. While logged in, you can access:
   - `/dashboard`
   - `/skill-graph`
   - `/roadmap`
   - And other pages

2. Logout, then try to visit `/dashboard`
   - → Redirects to `/login` ✓

3. Refresh page while logged in
   - → Stays logged in ✓

## What Changed?

### New Pages
- `/login` - Login page
- `/signup` - Sign up page
- `/forgot-password` - Password reset flow

### Updated Pages
- `/dashboard` - Now protected (requires login)
- Navigation - Shows user name and logout button

### New Backend Endpoints
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/logout` - Clear session
- `GET /api/auth/me` - Get current user
- `POST /api/auth/forgot-password` - Password reset request

### Updated Backend
- User model now has `full_name` and `updated_at` fields
- Added password hashing and JWT token support
- New auth routes module

### Updated Frontend
- New `AuthProvider` for global auth state
- `ProtectedRoute` component for auth-required pages
- Updated navigation with user display

## Configuration

### Backend Environment (.env)
Already configured with defaults for local development:
```
SECRET_KEY=dev-secret-change-me
DATABASE_URL=sqlite:///./skillgraph.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

For production, update `SECRET_KEY` to a strong random value.

### Frontend Environment (.env.local)
Already configured:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Demo Accounts
After signup/login, you can:
1. Try the demo roles on the home page
2. Build a custom learning path
3. Access the dashboard

## Features

✅ User Registration
✅ Secure Login/Logout
✅ Password Validation (8+ chars, uppercase, number)
✅ Protected Routes
✅ Persistent Login (survives page refresh)
✅ User Profile Display
✅ Forgot Password Page (ready for email integration)
✅ Clean, Modern UI
✅ Production-Ready Code

## Security Notes

- Passwords are hashed with bcrypt
- Auth tokens stored in HttpOnly cookies
- CORS configured for localhost
- Email validation included
- Tokens expire in 7 days

## Troubleshooting

**Backend won't start?**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version (3.8+)
python --version
```

**Frontend won't start?**
```bash
# Clear cache and reinstall
rm -r node_modules package-lock.json
npm install
npm run dev
```

**Getting CORS errors?**
- Make sure backend is running on http://localhost:8000
- Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`

**Can't sign up?**
- Email already exists → Use a different email
- Password too weak → Must have 8+ chars, uppercase, and number
- Check browser console for detailed error messages

**Keeps redirecting to login?**
- Verify backend is running
- Check network tab in browser DevTools
- Make sure cookies are enabled

## Next Steps

1. ✅ Authentication system is working
2. Optional: Configure email for password reset
3. Optional: Add Google/GitHub OAuth
4. Ready to integrate with: skill profiling, learning paths, recommendations, etc.

## Documentation

See `AUTHENTICATION.md` for:
- Detailed API documentation
- Component usage examples
- Database schema
- Production deployment guide
- Security best practices

## File Locations

**Authentication Code:**
- Backend auth: `backend/app/api/routes/auth_routes.py`
- Security utils: `backend/app/services/security.py`
- Frontend auth: `frontend/lib/auth.tsx`
- Protected routes: `frontend/components/ProtectedRoute.tsx`

**Pages:**
- Login: `frontend/app/login/page.tsx`
- Sign up: `frontend/app/signup/page.tsx`
- Forgot password: `frontend/app/forgot-password/page.tsx`
- Dashboard: `frontend/app/dashboard/page.tsx` (now protected)

## Support

For detailed information:
1. Read `AUTHENTICATION.md`
2. Check inline code comments
3. Review API docs at http://localhost:8000/docs
4. Check browser console for detailed errors

---

**Everything is ready to go!** 🚀

Start both servers and navigate to http://localhost:3000 to test the authentication system.
