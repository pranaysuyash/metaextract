# MetaExtract Authentication System Documentation

## Overview

The MetaExtract authentication system provides secure user authentication with industry-standard security practices. It includes features like JWT-based authentication, rate limiting, password policies, two-factor authentication, and comprehensive session management.

## Features

### 1. Secure Token Handling
- **JWT Access Tokens**: Short-lived tokens (15 minutes by default) for API requests
- **JWT Refresh Tokens**: Longer-lived tokens (7 days by default) stored in httpOnly cookies
- **Token Rotation**: Automatic refresh token rotation to prevent token theft abuse

### 2. Password Security
- **Strong Password Requirements**: Configurable minimum length and character requirements
- **BCrypt Hashing**: Industry-standard password hashing with configurable rounds
- **Password Strength Validation**: Real-time validation of password strength

### 3. Rate Limiting
- **Login Attempts**: Limits failed login attempts to prevent brute force attacks
- **API Rate Limiting**: Prevents abuse of API endpoints
- **IP-based Limits**: Protects against distributed attacks

### 4. Two-Factor Authentication (2FA)
- **TOTP Support**: Time-based one-time passwords compatible with authenticator apps
- **QR Code Setup**: Easy setup with QR codes
- **Backup Codes**: Recovery options for lost devices

### 5. Account Security
- **Email Verification**: Confirms user email addresses
- **Account Lockout**: Temporary lockout after multiple failed attempts
- **Session Management**: Tracks and manages active sessions

## Configuration

The authentication system is configured through environment variables:

```bash
# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here
JWT_REFRESH_SECRET=your-super-secret-refresh-jwt-key-here
JWT_EXPIRATION=15m
JWT_REFRESH_EXPIRATION=7d

# Password Policy
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SYMBOLS=true

# Security Limits
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900000  # 15 minutes in milliseconds
BCRYPT_ROUNDS=12
```

## API Endpoints

### Authentication Endpoints

#### `POST /api/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "firstName": "John",
  "lastName": "Doe"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "emailVerified": false
  },
  "accessToken": "jwt-token"
}
```

#### `POST /api/auth/login`
Authenticate a user and obtain tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "twoFactorEnabled": false
  },
  "accessToken": "jwt-token"
}
```

If 2FA is enabled, the response will include:
```json
{
  "error": "Two-factor authentication required",
  "twoFactorRequired": true
}
```

#### `POST /api/auth/logout`
Log out the current user.

**Response:**
```json
{
  "message": "Logout successful"
}
```

#### `POST /api/auth/refresh`
Refresh the access token using the refresh token (sent via cookie).

**Response:**
```json
{
  "accessToken": "new-jwt-token"
}
```

### Two-Factor Authentication Endpoints

#### `POST /api/auth/2fa/enable`
Enable two-factor authentication for the current user.

**Response:**
```json
{
  "secret": "base32-encoded-secret",
  "qrCodeUrl": "data:image/png;base64,...",
  "manualEntryKey": "human-readable-key"
}
```

#### `POST /api/auth/2fa/verify`
Verify and complete 2FA setup.

**Request Body:**
```json
{
  "token": "6-digit-code-from-app",
  "secret": "base32-encoded-secret"
}
```

**Response:**
```json
{
  "message": "Two-factor authentication enabled successfully",
  "twoFactorEnabled": true
}
```

#### `POST /api/auth/2fa/disable`
Disable two-factor authentication.

**Response:**
```json
{
  "message": "Two-factor authentication disabled successfully",
  "twoFactorEnabled": false
}
```

### Password Management Endpoints

#### `POST /api/auth/password/reset/request`
Request a password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If an account exists with this email, a reset link has been sent"
}
```

#### `POST /api/auth/password/reset`
Reset password using a reset token.

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "newPassword": "NewSecurePassword123!"
}
```

**Response:**
```json
{
  "message": "Password reset successfully"
}
```

#### `POST /api/auth/password/change`
Change password for authenticated user.

**Request Body:**
```json
{
  "currentPassword": "current-password",
  "newPassword": "NewSecurePassword123!"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

### Profile Management Endpoints

#### `GET /api/auth/profile`
Get current user profile.

**Response:**
```json
{
  "id": "user-id",
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "emailVerified": true,
  "twoFactorEnabled": false,
  "createdAt": "2023-01-01T00:00:00.000Z",
  "updatedAt": "2023-01-01T00:00:00.000Z"
}
```

#### `PUT /api/auth/profile`
Update user profile information.

**Request Body:**
```json
{
  "firstName": "Jane",
  "lastName": "Smith"
}
```

**Response:**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "firstName": "Jane",
    "lastName": "Smith",
    "emailVerified": true,
    "twoFactorEnabled": false
  }
}
```

## Security Best Practices

### Token Security
- Access tokens are short-lived to minimize exposure
- Refresh tokens are stored in httpOnly cookies to prevent XSS access
- Tokens are signed with strong secrets that should be rotated regularly

### Password Security
- All passwords are hashed using BCrypt with salt
- Password policies enforce strong passwords
- Password reset tokens expire after 15 minutes

### Rate Limiting
- Login attempts are limited to prevent brute force
- API endpoints have rate limits to prevent abuse
- Suspicious activity triggers additional protections

### Session Management
- Sessions are tracked and can be invalidated
- Automatic logout after periods of inactivity
- Multiple device support with session management

## Implementation Notes

### Frontend Integration
The authentication system is designed to work seamlessly with the frontend:

1. Access tokens are included in the Authorization header: `Bearer <token>`
2. Refresh tokens are automatically included via httpOnly cookies
3. The frontend should handle token expiration and refresh automatically
4. 2FA setup can be guided through QR code scanning

### Error Handling
The system provides clear error messages for different scenarios:
- Invalid credentials
- Account lockout
- Expired tokens
- 2FA requirements
- Password policy violations

### Testing
The system includes comprehensive testing capabilities:
- Mock authentication for development
- Test user creation script
- Integration test endpoints
- Security vulnerability testing

## Migration Guide

To migrate from the previous authentication system:

1. Update environment variables with new JWT secrets
2. Run database migrations to add new fields (if any)
3. Update frontend to handle httpOnly cookies for refresh tokens
4. Test all authentication flows thoroughly
5. Monitor logs for any authentication issues

## Troubleshooting

### Common Issues
- **Token Expiration**: Access tokens expire quickly; implement automatic refresh
- **Cookie Issues**: Ensure proper CORS and SameSite settings
- **2FA Problems**: Verify time synchronization between server and authenticator app
- **Rate Limiting**: Adjust limits based on legitimate usage patterns

### Debugging
- Check server logs for authentication errors
- Verify JWT secrets match between services
- Confirm proper HTTPS setup in production
- Test with the provided test user script