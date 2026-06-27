# Security and Hardening Configurations

## Core Features
1. **Password Protection**: Admin and officer credentials are encrypted using bcrypt hashing before database storage.
2. **Access Control**: Role-based access controls (RBAC) separate `admin` and `officer` permissions.
3. **Session Management**: REST routes are secured using JWT (JSON Web Tokens) with a configurable token expiration time (default: 60 minutes).
4. **Database Protection**: The application uses SQLAlchemy's ORM parameters, which mitigates risk from SQL Injection attacks.
5. **API Limits**: The backend implements rate limiting middleware:
   - General API routes: 30 requests/second.
   - Evidence uploads: 5 requests/second.
6. **Reverse Proxy**: Nginx handles SSL termination, hides upstream server headers, and manages CORS policies.
