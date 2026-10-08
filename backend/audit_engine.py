"""
audit_engine.py
---------------
Core IAM audit logic. Evaluates IAM configuration data and returns
a list of findings, a security score, and recommendations.

This is intentionally kept simple and readable for a college project.
"""

from datetime import datetime

# ──────────────────────────────────────────────
# Constants – tweak these to change audit rules
# ──────────────────────────────────────────────

# How many days without login before we flag an account as inactive
INACTIVE_DAYS_THRESHOLD = 90

# Permission strings that indicate excessive / admin-level access
EXCESSIVE_PERMISSION_KEYWORDS = [
    "*",
    "admin",
    "AdministratorAccess",
    "FullAccess",
    "full_access",
    "PowerUserAccess",
    "root",
]

# Policy action patterns that are considered risky
# (specific read-only actions like iam:GetUser are intentionally excluded)
RISKY_ACTIONS = ["*", "iam:*", "s3:*", "ec2:*", "lambda:*", "sts:*"]

# Policy resource patterns that are considered risky
RISKY_RESOURCES = ["*", "arn:aws:*:*:*:*"]


# ──────────────────────────────────────────────
# Helper utilities
# ──────────────────────────────────────────────

def _days_since(date_string):
    """Return how many days have passed since a date string like '2024-01-15'."""
    try:
        last_login = datetime.strptime(date_string, "%Y-%m-%d")
        return (datetime.now() - last_login).days
    except (ValueError, TypeError):
        return None


def _contains_excessive_permission(permissions):
    """Return True if any permission in the list looks like admin/full access."""
    if not permissions:
        return False
    for perm in permissions:
        for keyword in EXCESSIVE_PERMISSION_KEYWORDS:
            if keyword.lower() in str(perm).lower():
                return True
    return False


def _is_risky_policy(policy):
    """
    Check a single policy dict for risky patterns.
    Returns (is_risky: bool, reason: str)
    """
    if not isinstance(policy, dict):
        return False, ""

    actions   = policy.get("actions",   policy.get("Action",   []))
    resources = policy.get("resources", policy.get("Resource", []))
    effect    = policy.get("effect",    policy.get("Effect",   "Allow"))

    # Normalise to lists
    if isinstance(actions, str):
        actions = [actions]
    if isinstance(resources, str):
        resources = [resources]

    risky_action   = any(a in RISKY_ACTIONS   for a in actions)
    risky_resource = any(r in RISKY_RESOURCES for r in resources)

    if risky_action and risky_resource and effect == "Allow":
        return True, "Wildcard action '*' on wildcard resource '*' grants unrestricted access"
    if risky_action and effect == "Allow":
        return True, f"Overly broad action(s) {actions} detected in policy"
    if risky_resource and effect == "Allow":
        return True, "Wildcard resource '*' detected – scope should be narrowed"

    return False, ""


# ──────────────────────────────────────────────
# Main audit function
# ──────────────────────────────────────────────

def run_audit(iam_data):
    """
    Accepts an IAM configuration dict and returns:
    {
        "security_score": int (0-100),
        "risk_level":     str,
        "summary":        dict,
        "findings":       list,
        "recommendations": list
    }
    """
    findings        = []
    recommendations = set()
    penalty         = 0   # accumulated penalty points used to compute score

    users = iam_data.get("users", [])
    roles = iam_data.get("roles", [])

    # ── Audit Users ────────────────────────────
    for user in users:
        name       = user.get("username", "Unknown")
        status     = user.get("status", "active").lower()
        mfa        = user.get("mfa_enabled", True)
        last_login = user.get("last_login", None)
        perms      = user.get("permissions", [])
        policies   = user.get("policies", [])

        # 1. Inactive account check
        if status == "inactive":
            findings.append({
                "entity":         name,
                "type":           "User",
                "finding":        "Inactive Account",
                "severity":       "HIGH",
                "reason":         "Account status is set to inactive.",
                "recommendation": "Disable or delete unused accounts to reduce attack surface.",
            })
            recommendations.add("Disable or delete inactive accounts.")
            penalty += 15
        elif last_login:
            days = _days_since(last_login)
            if days is not None and days > INACTIVE_DAYS_THRESHOLD:
                findings.append({
                    "entity":         name,
                    "type":           "User",
                    "finding":        "Stale Account",
                    "severity":       "MEDIUM",
                    "reason":         f"Last login was {days} days ago (threshold: {INACTIVE_DAYS_THRESHOLD} days).",
                    "recommendation": "Review and deactivate stale accounts.",
                })
                recommendations.add("Review accounts with no recent login activity.")
                penalty += 8

        # 2. MFA check
        if not mfa:
            findings.append({
                "entity":         name,
                "type":           "User",
                "finding":        "MFA Disabled",
                "severity":       "HIGH",
                "reason":         "Multi-Factor Authentication is not enabled for this account.",
                "recommendation": "Enable MFA immediately to protect against credential theft.",
            })
            recommendations.add("Enable MFA for all user accounts.")
            penalty += 20

        # 3. Excessive permissions check
        if _contains_excessive_permission(perms):
            findings.append({
                "entity":         name,
                "type":           "User",
                "finding":        "Excessive Permissions",
                "severity":       "CRITICAL",
                "reason":         f"User has potentially over-privileged permissions: {perms}",
                "recommendation": "Apply the Principle of Least Privilege – grant only required permissions.",
            })
            recommendations.add("Apply the Principle of Least Privilege to all users.")
            penalty += 25

        # 4. Risky policy check
        for policy in policies:
            risky, reason = _is_risky_policy(policy)
            if risky:
                findings.append({
                    "entity":         name,
                    "type":           "User Policy",
                    "finding":        "Risky Policy",
                    "severity":       "HIGH",
                    "reason":         reason,
                    "recommendation": "Restrict policy actions and resources to the minimum required.",
                })
                recommendations.add("Restrict overly broad IAM policies.")
                penalty += 18
                break   # one finding per user for risky policies is enough

    # ── Audit Roles ────────────────────────────
    for role in roles:
        name     = role.get("role_name", "Unknown Role")
        perms    = role.get("permissions", [])
        policies = role.get("policies", [])
        public   = role.get("public_access", False)

        # Excessive permissions on roles
        if _contains_excessive_permission(perms):
            findings.append({
                "entity":         name,
                "type":           "Role",
                "finding":        "Excessive Permissions",
                "severity":       "CRITICAL",
                "reason":         f"Role has over-privileged permissions: {perms}",
                "recommendation": "Scope role permissions to specific required actions only.",
            })
            recommendations.add("Scope role permissions to required actions only.")
            penalty += 25

        # Public/anonymous access
        if public:
            findings.append({
                "entity":         name,
                "type":           "Role",
                "finding":        "Public Access Enabled",
                "severity":       "CRITICAL",
                "reason":         "This role allows public/anonymous access.",
                "recommendation": "Remove public access unless absolutely necessary and document why.",
            })
            recommendations.add("Disable public/anonymous role access.")
            penalty += 30

        # Risky policies on roles
        for policy in policies:
            risky, reason = _is_risky_policy(policy)
            if risky:
                findings.append({
                    "entity":         name,
                    "type":           "Role Policy",
                    "finding":        "Risky Policy",
                    "severity":       "HIGH",
                    "reason":         reason,
                    "recommendation": "Restrict policy actions and resources to the minimum required.",
                })
                recommendations.add("Restrict overly broad IAM policies.")
                penalty += 18
                break

    # ── Summary counts ─────────────────────────
    total_users        = len(users)
    inactive_count     = sum(1 for f in findings if f["finding"] in ("Inactive Account", "Stale Account"))
    excessive_count    = sum(1 for f in findings if f["finding"] == "Excessive Permissions")
    risky_policy_count = sum(1 for f in findings if f["finding"] == "Risky Policy")
    mfa_disabled_count = sum(1 for f in findings if f["finding"] == "MFA Disabled")
    public_access_count= sum(1 for f in findings if f["finding"] == "Public Access Enabled")

    # ── Security score calculation ─────────────
    # Start at 100 and deduct penalties (capped at 0)
    security_score = max(0, 100 - penalty)

    if security_score >= 80:
        risk_level = "LOW"
    elif security_score >= 55:
        risk_level = "MEDIUM"
    elif security_score >= 30:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return {
        "security_score": security_score,
        "risk_level":     risk_level,
        "summary": {
            "total_users":           total_users,
            "total_roles":           len(roles),
            "inactive_accounts":     inactive_count,
            "excessive_permissions": excessive_count,
            "risky_policies":        risky_policy_count,
            "mfa_disabled":          mfa_disabled_count,
            "public_access":         public_access_count,
            "total_findings":        len(findings),
        },
        "findings":        findings,
        "recommendations": sorted(list(recommendations)),
    }
