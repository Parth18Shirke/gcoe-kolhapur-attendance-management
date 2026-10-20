# Backup & Disaster Recovery Strategy

**Document ID:** DOC-DEP-BCK-001  
**Project:** College Attendance Management System  
**Date:** October 2026  

---

## 1. Backup Strategy Overview

Academic attendance data is statutory institutional record. A multi-tier backup routine guarantees protection against accidental deletion, hardware failure, or host corruption.

### 1.1 Automated Daily Database Dumps
- **Command:** `pg_dump -U ams_user -Fc ams_db > /var/backups/ams/ams_db_$(date +%Y%m%d_%H%M%S).dump`
- **Schedule:** Nightly at 02:00 AM IST via Linux cron.
- **Retention:** Keep last 30 daily backups locally; compress older backups.

### 1.2 Off-Site Secondary Replication
- Automated synchronization of `.dump` files to institutional cloud storage (AWS S3, Google Drive for Education, or on-premise college NAS).

---

## 2. Disaster Recovery Protocol

1. **New Host Provisioning:** Provision clean Ubuntu LTS instance.
2. **Repository Deployment:** Checkout master branch and configure `.env`.
3. **Database Restoration:**
   ```bash
   createdb -U postgres ams_db
   pg_restore -U ams_user -d ams_db /var/backups/ams/ams_db_YYYYMMDD_HHMMSS.dump
   ```
4. **Migration & State Verification:**
   ```bash
   python manage.py showmigrations
   python manage.py verify_attendance_integrity
   ```
5. **DNS Cutover:** Update campus DNS A-record to the new server IP.
