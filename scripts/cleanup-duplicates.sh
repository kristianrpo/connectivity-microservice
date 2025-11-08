#!/bin/bash
# Script to clean up duplicate AWS resources created during pipeline runs

set -e

REGION="${AWS_REGION:-us-east-1}"

echo "=== Cleaning up duplicate AWS resources ==="
echo "Region: $REGION"
echo ""

# Keep only the most recent suffix: d7cf
KEEP_SUFFIX="d7cf"

echo "Keeping resources with suffix: $KEEP_SUFFIX"
echo "Deleting all others..."
echo ""

# ============================================================================
# 1. Delete old Secrets Manager secrets
# ============================================================================
echo "=== Deleting old Secrets Manager secrets ==="

# Old suffixes to delete
OLD_SUFFIXES=("be43" "31b6" "bcef" "929a" "14a5")

for suffix in "${OLD_SUFFIXES[@]}"; do
  echo "Deleting secrets with suffix: $suffix"
  
  # Delete connections secrets
  aws secretsmanager delete-secret \
    --secret-id "connectivity-production/connections-${suffix}" \
    --force-delete-without-recovery \
    --region "$REGION" 2>/dev/null && echo "  ✓ Deleted connections-${suffix}" || echo "  ✗ connections-${suffix} not found"
  
  # Delete application secrets
  aws secretsmanager delete-secret \
    --secret-id "connectivity-production/application-${suffix}" \
    --force-delete-without-recovery \
    --region "$REGION" 2>/dev/null && echo "  ✓ Deleted application-${suffix}" || echo "  ✗ application-${suffix} not found"
  
  # Delete RDS secrets
  aws secretsmanager delete-secret \
    --secret-id "connectivity-production/rds/postgresql-${suffix}" \
    --force-delete-without-recovery \
    --region "$REGION" 2>/dev/null && echo "  ✓ Deleted rds/postgresql-${suffix}" || echo "  ✗ rds/postgresql-${suffix} not found"
done

echo ""

# ============================================================================
# 2. Delete old IAM policies
# ============================================================================
echo "=== Deleting old IAM policies ==="

# List all connectivity policies
POLICIES=$(aws iam list-policies \
  --scope Local \
  --query 'Policies[?starts_with(PolicyName, `connectivity-production`)].{Name:PolicyName,Arn:Arn}' \
  --output json)

echo "Found policies:"
echo "$POLICIES" | jq -r '.[] | "  - \(.Name)"'
echo ""

# Delete policies that don't match the current timestamp pattern
echo "$POLICIES" | jq -r '.[] | select(.Name | contains("20251108012759") | not) | .Arn' | while read -r policy_arn; do
  if [ -n "$policy_arn" ]; then
    POLICY_NAME=$(echo "$POLICIES" | jq -r --arg arn "$policy_arn" '.[] | select(.Arn == $arn) | .Name')
    echo "Deleting policy: $POLICY_NAME"
    
    # First, detach from all roles
    ATTACHED_ROLES=$(aws iam list-entities-for-policy \
      --policy-arn "$policy_arn" \
      --query 'PolicyRoles[].RoleName' \
      --output text 2>/dev/null || echo "")
    
    if [ -n "$ATTACHED_ROLES" ]; then
      for role in $ATTACHED_ROLES; do
        echo "  Detaching from role: $role"
        aws iam detach-role-policy \
          --role-name "$role" \
          --policy-arn "$policy_arn" 2>/dev/null || echo "  ✗ Failed to detach from $role"
      done
    fi
    
    # Delete the policy
    aws iam delete-policy --policy-arn "$policy_arn" 2>/dev/null && echo "  ✓ Deleted $POLICY_NAME" || echo "  ✗ Failed to delete $POLICY_NAME"
  fi
done

echo ""

# ============================================================================
# 3. Summary
# ============================================================================
echo "=== Cleanup Summary ==="
echo ""
echo "Remaining Secrets Manager secrets:"
aws secretsmanager list-secrets \
  --region "$REGION" \
  --query 'SecretList[?starts_with(Name, `connectivity-production`)].Name' \
  --output table

echo ""
echo "Remaining IAM policies:"
aws iam list-policies \
  --scope Local \
  --query 'Policies[?starts_with(PolicyName, `connectivity-production`)].PolicyName' \
  --output table

echo ""
echo "=== Cleanup complete! ==="
