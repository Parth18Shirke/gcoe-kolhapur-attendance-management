# API Error Model & Exception Handling

**Document ID:** DOC-API-ERR-001  
**Project:** College Attendance Management System  
**Date:** October 2026  

---

## 1. Unified Error Envelope

All API errors return a standard JSON structure with consistent keys across all endpoints:

```json
{
  "success": false,
  "error": {
    "code": "SESSION_LOCKED",
    "message": "This lecture session has been finalized and cannot accept direct attendance submissions.",
    "details": {
      "session_id": 105,
      "finalized_at": "2026-10-05T12:00:00Z"
    }
  },
  "timestamp": "2026-10-05T12:05:00Z"
}
```

---

## 2. Standard Error Codes

| HTTP Status | Error Code | Description / Context |
| :---: | :--- | :--- |
| `400` | `VALIDATION_ERROR` | Malformed request body, invalid field format, or constraint violation. |
| `401` | `AUTHENTICATION_REQUIRED` | Missing, expired, or invalid session token. |
| `401` | `OTP_INVALID` | Invalid 6-digit verification code. |
| `401` | `OTP_EXPIRED` | OTP verification attempt after 10-minute expiry window. |
| `403` | `PERMISSION_DENIED` | User lacks role authority (e.g., faculty attempting HOD approval). |
| `404` | `NOT_FOUND` | Target entity does not exist. |
| `409` | `TIMETABLE_CONFLICT` | Faculty, Division, or Room collision during timetable creation. |
| `409` | `SYNC_CONFLICT` | Offline submission contradicts server state (e.g., session already finalized). |
| `422` | `INCOMPLETE_ROSTER` | Finalization attempted with unmarked student records. |
| `429` | `RATE_LIMIT_EXCEEDED` | Exceeded 3 OTP requests in 15 minutes. |
| `500` | `INTERNAL_SERVER_ERROR` | Unhandled server exception (stack trace logged internally, sanitized for client). |
