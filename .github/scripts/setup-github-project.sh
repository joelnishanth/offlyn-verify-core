#!/usr/bin/env bash
# Set up GitHub Project v2 for Offlyn Verify Core - Robotics Roadmap
# Prerequisites:
#   gh auth refresh -h github.com -s project,read:project
set -euo pipefail

REPO="joelnishanth/offlyn-verify-core"
OWNER="joelnishanth"
PROJECT_TITLE="Offlyn Verify Core - Robotics Roadmap"

if ! gh auth status 2>&1 | grep -q "project"; then
  echo "ERROR: gh token missing 'project' scope."
  echo "Run: gh auth refresh -h github.com -s project,read:project"
  exit 1
fi

echo "Creating GitHub Project..."
PROJECT_JSON=$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json)
PROJECT_NUMBER=$(echo "$PROJECT_JSON" | jq -r '.number')
PROJECT_ID=$(echo "$PROJECT_JSON" | jq -r '.id')

echo "Project #$PROJECT_NUMBER created (ID: $PROJECT_ID)"

echo "Linking project to repository..."
gh project link "$PROJECT_NUMBER" --owner "$OWNER" --repo "$REPO"

echo "Creating custom fields..."

create_select_field() {
  local name="$1"
  shift
  gh project field-create "$PROJECT_NUMBER" --owner "$OWNER" \
    --name "$name" --data-type "SINGLE_SELECT" \
    --single-select-options "$@" 2>/dev/null || echo "  (field '$name' may already exist)"
}

create_select_field "Phase" \
  "Phase 1 - Robotics MVP" \
  "Phase 2 - Security & Hardening" \
  "Phase 3 - Attestation Runtime" \
  "Phase 4 - Hardware Integration" \
  "Phase 5 - Fleet, Ecosystem & Silicon Path"

create_select_field "Priority" "P0 Critical" "P1 High" "P2 Medium" "P3 Low"

create_select_field "Component" \
  "ROS 2" "Policy Gate" "OPA / Rego" "Action Schema" "Simulator" \
  "Audit Log" "Dashboard" "Attack Tests" "TPM / Attestation" \
  "Secure Boot" "Signed Policy" "Edge Controller" "Hardware Boundary" \
  "Fleet Management" "Documentation" "Paper" "Demo Video"

create_select_field "Risk Level" "High" "Medium" "Low"
create_select_field "Demo Impact" "Critical" "Important" "Nice-to-have"

gh project field-create "$PROJECT_NUMBER" --owner "$OWNER" \
  --name "Target Date" --data-type "DATE" 2>/dev/null || true

echo "Adding all open issues to project..."
gh issue list --repo "$REPO" --state open --limit 300 --json number --jq '.[].number' | while read -r num; do
  echo "  Adding issue #$num..."
  gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" \
    --url "https://github.com/$REPO/issues/$num" 2>/dev/null || true
done

echo ""
echo "GitHub Project setup complete!"
echo "View at: https://github.com/users/$OWNER/projects/$PROJECT_NUMBER"
echo ""
echo "Configure the built-in Status field in GitHub UI with these options:"
echo "  Backlog | Ready | In Progress | Blocked | Needs Review | Done"
