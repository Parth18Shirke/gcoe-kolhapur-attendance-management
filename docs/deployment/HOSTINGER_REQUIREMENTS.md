# Hostinger Infrastructure Requirements & Verification Checklist

**Document ID:** DOC-DEP-HST-001  
**Project:** College Attendance Management System  
**Date:** October 2026  

---

## 1. Hosting Tier Evaluation

The college has an existing Hostinger subscription. The exact plan tier dictates deployment capabilities:

| Hostinger Tier | Viability | Capabilities & Limitations | Action Plan |
| :--- | :---: | :--- | :--- |
| **KVM VPS (Recommended)** | **Optimal** | Full root access, Ubuntu OS, systemd service management, Docker capability, native PostgreSQL 15+, unrestricted background workers and cron jobs. | Proceed with standard Gunicorn + Nginx + PostgreSQL production architecture. |
| **Cloud Hosting (Managed hPanel)**| **Viable with Constraints**| Isolated resources, managed Python WSGI setup, MySQL standard (PostgreSQL may require external host or add-on), no root/systemd. Background cron possible via hPanel. | Configure Django to use WSGI application runner, adapt DB if required, run email dispatcher via hPanel cron. |
| **Shared Web Hosting** | **High Risk** | Severe process timeouts, limited RAM (512MB-1GB), no root access, restricted long-running daemons. | Strongly recommend upgrading to Hostinger KVM VPS (typically comparable in annual cost). |

---

## 2. Pre-Deployment Verification Checklist for College IT

Before beginning production deployment on Hostinger, obtain verification on:

- [ ] **Plan Confirmation:** Verify whether the subscription is VPS 1, VPS 2, Cloud Startup, or Shared.
- [ ] **Access Credentials:** SSH access IP, port, and root/sudo user credentials.
- [ ] **Domain / DNS:** College subdomain assignment (e.g. `attendance.college.edu` pointing to Hostinger IP).
- [ ] **Inbound Ports:** Verify port 80 (HTTP) and port 443 (HTTPS) are open.
- [ ] **Outbound SMTP:** Verify outbound TCP ports 587 or 465 are not blocked by Hostinger firewall.
- [ ] **Storage Allocation:** Minimum 20 GB SSD storage available for OS, PostgreSQL database, and document generation caches.
