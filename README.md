# Cloud Identity and Access Auditor

> **Educational cybersecurity project** — A web-based IAM (Identity and Access Management) auditing tool that reviews cloud access configurations and flags security risks.

> **Note:** This project currently uses **mock/fictional IAM data** for demonstration purposes. No real AWS, Azure, or GCP credentials are required or used. Real cloud API integration is listed under Future Scope.

---

## Project Description

Cloud IAM misconfiguration is one of the most common causes of cloud security breaches. This project demonstrates how to audit IAM user and role configurations to detect common security issues such as:

- Excessive or over-privileged permissions (admin/wildcard access)
- Inactive or stale user accounts (no login in 90+ days)
- MFA-disabled user accounts
- Risky access policies (wildcard actions or resources)
- Roles with public/anonymous access enabled

The application is built with Python (Flask) on the backend and plain HTML/CSS/JavaScript on the frontend — no external database, no cloud account, no configuration required.

---

## Features

| Feature | Description |
|---|---|
| **Health Check** | Frontend detects whether the Flask backend is running and shows a clear status |
| **Dashboard Summary Cards** | At-a-glance counts: users, inactive accounts, excessive permissions, risky policies, MFA-disabled |
| **Sample Data Loader** | One-click load of a realistic but fictional 8-user / 4-role IAM configuration |
| **JSON Input / File Upload** | Paste custom IAM JSON or upload a `.json` file |
| **Security Audit Engine** | Python backend evaluating 4 categories of IAM risk per user and role |
| **Findings Table** | Per-entity findings with severity (CRITICAL / HIGH / MEDIUM), reason, and recommendation |
| **Security Score** | 0–100 score calculated from detected findings |
| **Risk Level Indicator** | LOW / MEDIUM / HIGH / CRITICAL with visual progress bar |
| **Recommendations Panel** | Actionable remediation steps extracted from all findings |
| **Graceful Offline State** | Banner + Retry button shown when Flask server is not running |
| **One-click Startup** | `run_project.bat` starts the server and opens the browser automatically |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3, Flask-CORS |
| Frontend | HTML5, CSS3, Vanilla JavaScript (no frameworks) |
| Data | JSON (mock IAM configuration — no real cloud data) |
| API | REST (JSON over HTTP) |
| Packaging | Python venv, pip |

---

## Project Structure

```
cloud-identity-access-auditor/
|
|-- app.py                  # Flask entry point
|-- requirements.txt        # Python dependencies (Flask, Flask-CORS)
|-- run_project.bat         # Windows one-click startup script
|-- README.md               # This file
|-- .gitignore              # Git ignore rules
|
|-- backend/
|   |-- __init__.py         # Makes backend/ a Python package
|   |-- audit_engine.py     # Core IAM audit rules and security scoring
|   |-- mock_iam_data.py    # Fictional sample IAM data (8 users, 4 roles)
|   `-- routes.py           # Flask API Blueprint (/api/health, /api/sample-data, /api/audit)
|
|-- data/
|   `-- sample_iam.json     # Same sample data as a standalone JSON file
|
`-- frontend/
    |-- index.html          # Main dashboard UI
    |-- style.css           # Dark cybersecurity theme
    `-- script.js           # Interactive frontend logic
```

---

## How to Start the Project

### Windows — Recommended (one double-click)

1. Open the `cloud-identity-access-auditor` folder.
2. Double-click **`run_project.bat`**.
3. A terminal window opens, installs requirements (only on first run), starts Flask, and **automatically opens http://127.0.0.1:5000** in your browser.
4. To stop the server: close the terminal window, or press `Ctrl+C` inside it.

> The script uses relative paths and works no matter where the folder is located.

---

### Manual Start (terminal)

```bash
# 1. Navigate into the project folder
cd cloud-identity-access-auditor

# 2. Create and activate virtual environment (first time only)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac / Linux

# 3. Install dependencies (first time only)
pip install -r requirements.txt

# 4. Start the server
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

---

## How to Use the Dashboard

1. **Open** http://127.0.0.1:5000 in your browser.
2. **Load data** — Click **"Load Sample Data"** to fill the editor with a fictional IAM configuration, OR paste your own IAM JSON, OR upload a `.json` file.
3. **Run audit** — Click **"Run Security Audit"**.
4. **Review results:**
   - Summary cards show counts of each risk category.
   - The **Security Score** (0–100) and **Risk Level** give an overall picture.
   - The **Findings Table** lists every specific issue found, with severity, reason, and recommendation.
   - The **Recommendations Panel** lists unique remediation actions.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend health check |
| `GET` | `/api/sample-data` | Returns the built-in mock IAM configuration |
| `POST` | `/api/audit` | Accepts IAM JSON, returns full audit report |

### POST /api/audit — Request Format

```json
{
  "users": [
    {
      "username": "alice",
      "status": "active",
      "mfa_enabled": true,
      "last_login": "2025-01-10",
      "permissions": ["ReadOnlyAccess"],
      "policies": []
    }
  ],
  "roles": []
}
```

### POST /api/audit — Response Format

```json
{
  "security_score": 45,
  "risk_level": "HIGH",
  "summary": {
    "total_users": 8,
    "inactive_accounts": 2,
    "excessive_permissions": 3,
    "risky_policies": 3,
    "mfa_disabled": 3,
    "total_findings": 14
  },
  "findings": [ ... ],
  "recommendations": [ ... ]
}
```

---

## Sample Audit Findings

The built-in mock data produces findings like these:

| User / Role | Finding | Severity | Reason |
|---|---|---|---|
| `bob.smith` | MFA Disabled | HIGH | MFA is not enabled for this account |
| `bob.smith` | Excessive Permissions | CRITICAL | Has `AdministratorAccess` |
| `bob.smith` | Risky Policy | HIGH | Wildcard action `*` on wildcard resource `*` |
| `carol.davis` | Inactive Account | HIGH | Account status is inactive |
| `dave.wilson` | Stale Account | MEDIUM | Last login was 200+ days ago |
| `dave.wilson` | MFA Disabled | HIGH | MFA is not enabled |
| `frank.nguyen` | Excessive Permissions | CRITICAL | Has `admin` permission |
| `LegacyMigrationRole` | Excessive Permissions | CRITICAL | Role has `*` wildcard permission |
| `PublicDataRole` | Public Access Enabled | CRITICAL | Role allows public/anonymous access |

---

## Audit Rules

### 1. Inactive Account Detection
- `status == "inactive"` → **HIGH** severity
- Last login > 90 days ago → **MEDIUM** severity (Stale Account)

### 2. MFA Check
- `mfa_enabled == false` → **HIGH** severity

### 3. Excessive Permissions
- Keywords scanned: `*`, `admin`, `AdministratorAccess`, `FullAccess`, `root`, `PowerUserAccess`
- Applies to both Users and Roles → **CRITICAL** severity

### 4. Risky Policy Detection
- Wildcard action `*` on wildcard resource `*` → **HIGH**
- Any overly broad action (e.g. `ec2:*`) → **HIGH**
- Public access on a role → **CRITICAL**

### Security Score
Starts at 100, deducts per finding:
- MFA Disabled: −20 | Excessive Permissions: −25 | Risky Policy: −18
- Inactive Account: −15 | Stale Account: −8 | Public Access: −30

---

## Screenshots

> _Add screenshots of the dashboard here after your first run._

| Dashboard | Audit Results |
|---|---|
| _(screenshot)_ | _(screenshot)_ |

---

## Future Scope

1. **Real Cloud Integration** — Connect to AWS IAM API (`boto3`), Azure AD, or GCP IAM
2. **Authentication** — Add login to protect the auditor dashboard
3. **Export Reports** — Download findings as PDF or CSV
4. **Scheduled Audits** — Run audits automatically on a schedule
5. **More Rules** — Password age, access key rotation, unused service accounts
6. **Database** — Store and compare historical audit results
7. **Notifications** — Email/Slack alerts for critical findings

---

## Academic Note

This is an **educational project** demonstrating cloud IAM security auditing concepts using **entirely fictional mock data**.

- It does **not** connect to any real cloud provider (AWS, Azure, GCP)
- It does **not** store or transmit any credentials
- It does **not** require any cloud account or API key
- All IAM data is invented for demonstration purposes only

---

## Author

*College Cybersecurity Portfolio Project — Cloud Security and IAM Auditing*
