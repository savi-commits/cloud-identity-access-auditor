"""
mock_iam_data.py
----------------
Fictional IAM configuration data used as the default sample.
No real credentials or personal information is included.

When real cloud integration is added later, replace get_mock_iam_data()
with a function that calls AWS/Azure/GCP IAM APIs.
"""


def get_mock_iam_data():
    """
    Returns a realistic-looking but completely fictional IAM configuration.
    Contains a mix of secure and insecure accounts to demonstrate all audit rules.
    """
    return {
        "account_name": "demo-cloud-account",
        "account_id":   "123456789000",
        "region":       "us-east-1",
        "generated_at": "2026-07-01",

        # ── Users ──────────────────────────────────────────────────────────
        "users": [
            {
                # Secure user – no findings expected
                "username":    "alice.johnson",
                "status":      "active",
                "mfa_enabled": True,
                "last_login":  "2026-06-28",
                "permissions": ["ReadOnlyAccess"],
                "policies": [
                    {
                        "policy_name": "S3ReadOnly",
                        "actions":     ["s3:GetObject", "s3:ListBucket"],
                        "resources":   ["arn:aws:s3:::my-app-bucket/*"],
                        "effect":      "Allow",
                    }
                ],
            },
            {
                # RISK: MFA disabled + excessive permissions + risky policy
                "username":    "bob.smith",
                "status":      "active",
                "mfa_enabled": False,
                "last_login":  "2026-06-20",
                "permissions": ["AdministratorAccess"],
                "policies": [
                    {
                        "policy_name": "FullAdmin",
                        "actions":     ["*"],
                        "resources":   ["*"],
                        "effect":      "Allow",
                    }
                ],
            },
            {
                # RISK: inactive account
                "username":    "carol.davis",
                "status":      "inactive",
                "mfa_enabled": True,
                "last_login":  "2026-01-10",
                "permissions": ["ReadOnlyAccess"],
                "policies":    [],
            },
            {
                # RISK: stale account (last login > 90 days) + MFA disabled + risky policy
                "username":    "dave.wilson",
                "status":      "active",
                "mfa_enabled": False,
                "last_login":  "2025-12-01",
                "permissions": ["EC2FullAccess"],
                "policies": [
                    {
                        "policy_name": "EC2Wildcard",
                        "actions":     ["ec2:*"],
                        "resources":   ["*"],
                        "effect":      "Allow",
                    }
                ],
            },
            {
                # Secure user – no findings expected
                "username":    "eve.martinez",
                "status":      "active",
                "mfa_enabled": True,
                "last_login":  "2026-06-25",
                "permissions": ["S3ReadAccess", "CloudWatchReadOnly"],
                "policies": [
                    {
                        "policy_name": "LimitedS3",
                        "actions":     ["s3:GetObject"],
                        "resources":   ["arn:aws:s3:::reports-bucket/*"],
                        "effect":      "Allow",
                    }
                ],
            },
            {
                # RISK: excessive permissions (admin keyword)
                "username":    "frank.nguyen",
                "status":      "active",
                "mfa_enabled": True,
                "last_login":  "2026-06-15",
                "permissions": ["admin"],
                "policies":    [],
            },
            {
                # RISK: MFA disabled + stale account
                "username":    "grace.lee",
                "status":      "active",
                "mfa_enabled": False,
                "last_login":  "2025-12-10",
                "permissions": ["LambdaBasicExecution"],
                "policies":    [],
            },
            {
                # Secure developer account
                "username":    "henry.patel",
                "status":      "active",
                "mfa_enabled": True,
                "last_login":  "2026-06-30",
                "permissions": ["DeveloperAccess", "S3ReadAccess"],
                "policies": [
                    {
                        "policy_name": "DevPolicy",
                        "actions":     ["s3:PutObject", "s3:GetObject", "lambda:InvokeFunction"],
                        "resources":   ["arn:aws:s3:::dev-bucket/*"],
                        "effect":      "Allow",
                    }
                ],
            },
        ],

        # ── Roles ──────────────────────────────────────────────────────────
        "roles": [
            {
                # Secure role
                "role_name":     "AppServerRole",
                "description":   "Role attached to application EC2 instances",
                "permissions":   ["S3ReadAccess", "CloudWatchLogsAccess"],
                "public_access": False,
                "policies": [
                    {
                        "policy_name": "AppServerPolicy",
                        "actions":     ["s3:GetObject", "logs:PutLogEvents"],
                        "resources":   ["arn:aws:s3:::app-bucket/*"],
                        "effect":      "Allow",
                    }
                ],
            },
            {
                # RISK: wildcard permissions on a role + risky wildcard policy
                "role_name":     "LegacyMigrationRole",
                "description":   "Temporary role created during migration – never cleaned up",
                "permissions":   ["*"],
                "public_access": False,
                "policies": [
                    {
                        "policy_name": "LegacyWildcard",
                        "actions":     ["*"],
                        "resources":   ["*"],
                        "effect":      "Allow",
                    }
                ],
            },
            {
                # RISK: public access enabled
                "role_name":     "PublicDataRole",
                "description":   "Accidentally left with public access enabled",
                "permissions":   ["S3ReadAccess"],
                "public_access": True,
                "policies": [
                    {
                        "policy_name": "PublicS3",
                        "actions":     ["s3:GetObject"],
                        "resources":   ["arn:aws:s3:::public-data/*"],
                        "effect":      "Allow",
                    }
                ],
            },
            {
                # Secure role – scoped resources, no wildcard actions
                "role_name":     "ReadOnlyAuditRole",
                "description":   "Used by the security team for read-only audits",
                "permissions":   ["SecurityAuditAccess", "ReadOnlyAccess"],
                "public_access": False,
                "policies": [
                    {
                        "policy_name": "AuditPolicy",
                        "actions":     ["iam:GetUser", "iam:ListUsers", "s3:ListBuckets"],
                        "resources":   ["arn:aws:iam:::user/*", "arn:aws:s3:::audit-bucket"],
                        "effect":      "Allow",
                    }
                ],
            },
        ],
    }
