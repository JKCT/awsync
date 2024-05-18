#!/usr/bin/env bash
set -e # Exit on error

# Configure Repository settings
configure_repository () {
  # Get variables from user input
  read -p "Enter repository name: " REPO
  read -p "Enter repository owner name: " OWNER
  read -p "Enter repository token with 'pages:write' and 'administration:write' permissions: " TOKEN

  # Requires token with permissions: administration:write
  # https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#update-a-repository
  echo "Configuring repository settings..."
  echo "- Enable GitHub Issues."
  echo "- Require squash merge and set merge commit title as PR title and message as PR description."
  echo "- Delete branch on merge."
  curl -L \
    -X PATCH \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    https://api.github.com/repos/${OWNER}/${REPO} \
    -d '{"has_issues":true,"allow_squash_merge":true,"allow_merge_commit":false,"allow_rebase_merge":false,"squash_merge_commit_title":"PR_TITLE","squash_merge_commit_message":"PR_BODY","delete_branch_on_merge":true}'

  # Configure main branch protection rules
  # Requires token with permissions: administration:write
  # https://docs.github.com/en/rest/branches/branch-protection?apiVersion=2022-11-28#update-branch-protection
  echo "Setting main branch protection rules..."
  echo "- Require CICD status checks to pass."
  echo "- Require 1 review from a Code Owner that did not commit the last push."
  echo "- Require linear commit history."
  echo "- Dismiss stale reviews."
  echo "- Lock branch."
  curl -L \
    -X PUT \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    https://api.github.com/repos/${OWNER}/${REPO}/branches/main/protection \
    -d '{"required_status_checks":{"strict":true,"checks":[{"context":"cicd"}],"required_pull_request_reviews":{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1,"require_last_push_approval":true,"restrictions":null,"required_linear_history":true,"lock_branch":true}'

  # Setup GitHub Pages for Documentation
  # Requires token with permissions: pages:write and administration:write
  # https://docs.github.com/en/rest/pages/pages?apiVersion=2022-11-28#create-a-github-pages-site
  echo "Creating GitHub Pages for documentation with 'gh-pages' branch and '/docs' path..."
  curl -L \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    https://api.github.com/repos/${OWNER}/${REPO}/pages \
    -d '{"source":{"branch":"gh-pages","path":"/docs"}}'
}

configure_repository
