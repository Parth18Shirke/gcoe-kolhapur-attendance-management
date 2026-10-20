# Authentication & RBAC Architecture

**Document ID:** ARCH-AUTH-001  
**Project:** College Attendance Management System  
**Date:** October 2026  
**Pattern:** Email OTP behind Provider Abstraction  

---

## 1. Zero Passwords Rationale

Traditional password authentication creates significant operational and security overhead in educational institutions:
- Forgotten passwords requiring frequent administrative intervention.
- Weak or shared passwords across faculty members.
- Phishing and credential stuffing risks.

To achieve immediate production security with zero user friction, the system implements **Email OTP (One-Time Password) Authentication** transmitted directly to verified institutional email addresses.

---

## 2. OTP Security Controls

```text
User Enters Institutional Email
           │
           ▼
[Check Rate Limits: Max 3 requests / 15 mins per IP & Email]
           │
           ▼
[Generate Cryptographically Secure 6-Digit Code (secrets.choice)]
           │
           ▼
[Store SHA-256 Salted Hash in DB (Never Plaintext OTP)]
  - expires_at = now() + 10 minutes
  - attempts_remaining = 3
  - is_used = False
           │
           ▼
[Transmit OTP via Configured Email Provider (College SMTP / Console)]
           │
           ▼
User Enters 6-Digit Code
           │
           ▼
[Validate OTP Hash & Expiry & Attempts]
           ├── Valid -> Mark is_used=True, Issue Session Bearer Token, Return User Role.
           └── Invalid -> Decrement attempts_remaining. If 0, immediately invalidate.
```

---

## 3. Extensible Provider Abstraction

Authentication logic is encapsulated behind an abstract `BaseAuthProvider`:
```python
class BaseAuthProvider(ABC):
    @abstractmethod
    def initiate_login(self, identifier: str) -> dict: ...

    @abstractmethod
    def verify_login(self, identifier: str, challenge_token: str) -> UserSession: ...
```

This guarantees that when the college later introduces **Google Workspace SSO**, **Microsoft 365 OIDC**, or **Campus LDAP**, an adapter implementation can be plugged into Django settings without modifying any domain models or API endpoints.

---

## 4. Server-Side Role-Based Access Control (RBAC)

Three initial roles exist:
1. `ADMIN` — Full system administration, academic master catalogs, user role management.
2. `HOD` — Department oversight, schedule override, older correction approvals, departmental reports.
3. `FACULTY` — View personal schedule, take attendance, 24h corrections, view assigned classes.

### Permission Invariants:
- All API views enforce `IsAuthenticated` by default.
- Role permissions are verified through explicit DRF permission classes (`IsAdminUserRole`, `IsHODUserRole`, `IsFacultyUserRole`, `IsAssignedFacultyOrHOD`).
- Object-level permissions verify that faculty can only view and modify sessions to which they are formally allocated.
