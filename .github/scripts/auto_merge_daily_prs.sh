#!/usr/bin/env bash
set -euo pipefail

REPO="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
MERGE_METHOD="${MERGE_METHOD:-squash}"
REQUIRE_CODE_CHANGE="${REQUIRE_CODE_CHANGE:-true}"
REQUIRED_CHECK_NAMES="${REQUIRED_CHECK_NAMES:?REQUIRED_CHECK_NAMES is required}"
CHECK_TIMEOUT_SECONDS="${CHECK_TIMEOUT_SECONDS:-900}"
CHECK_POLL_SECONDS="${CHECK_POLL_SECONDS:-10}"
CHECK_REGISTRATION_GRACE_SECONDS="${CHECK_REGISTRATION_GRACE_SECONDS:-10}"
BASE_SHA="$(git rev-parse HEAD)"

log() {
  printf '[%s] %s\n' "$(date --iso-8601=seconds)" "$*" >&2
}

gh_retry() {
  local attempt
  for attempt in 1 2 3; do
    if gh "$@"; then
      return 0
    fi
    log "gh $* failed on attempt $attempt/3"
    sleep $((attempt * 10))
  done
  return 1
}

is_docs_only() {
  local pr="$1"
  local files
  files="$(gh_retry pr diff "$pr" --repo "$REPO" --name-only)"

  while IFS= read -r file; do
    case "$file" in
      docs/*|README.md|*.md|.github/daily-pr/backlog.json)
        ;;
      *)
        return 1
        ;;
    esac
  done <<< "$files"

  return 0
}

linked_issue_number() {
  local pr="$1"
  gh_retry pr view "$pr" --repo "$REPO" --json body --jq '.body // ""' \
    | grep -Eo 'Closes #[0-9]+' \
    | head -n 1 \
    | grep -Eo '[0-9]+' || true
}

run_pr_tests() {
  local head="$1"
  git fetch --no-tags origin "$head"
  git checkout --force FETCH_HEAD
  python -m unittest discover -s tests
  git checkout --force "$BASE_SHA"
}

wait_for_pr_checks() {
  local pr="$1"
  local deadline
  local result
  local status

  log "PR #$pr: allowing ${CHECK_REGISTRATION_GRACE_SECONDS}s for check registration"
  sleep "$CHECK_REGISTRATION_GRACE_SECONDS"
  deadline=$((SECONDS + CHECK_TIMEOUT_SECONDS))

  while (( SECONDS < deadline )); do
    if result="$(
      gh_retry pr view "$pr" --repo "$REPO" --json statusCheckRollup \
        | python .github/scripts/check_gate.py \
            --required "$REQUIRED_CHECK_NAMES"
    )"; then
      log "PR #$pr: $result"
      return 0
    else
      status=$?
    fi

    if [[ "$status" -eq 2 ]]; then
      log "PR #$pr skipped: $result"
      return 1
    fi

    log "PR #$pr: $result; retrying in ${CHECK_POLL_SECONDS}s"
    sleep "$CHECK_POLL_SECONDS"
  done

  log "PR #$pr skipped: required checks did not complete within ${CHECK_TIMEOUT_SECONDS}s"
  return 1
}

merge_pr() {
  local pr="$1"
  local title
  title="$(gh_retry pr view "$pr" --repo "$REPO" --json title --jq '.title')"

  case "$MERGE_METHOD" in
    merge)
      gh_retry pr merge "$pr" --repo "$REPO" --merge --delete-branch --subject "$title"
      ;;
    rebase)
      gh_retry pr merge "$pr" --repo "$REPO" --rebase --delete-branch
      ;;
    squash)
      gh_retry pr merge "$pr" --repo "$REPO" --squash --delete-branch --subject "$title"
      ;;
    *)
      log "PR #$pr skipped: unsupported MERGE_METHOD=$MERGE_METHOD"
      return 1
      ;;
  esac
}

main() {
  if [[ -z "${GH_TOKEN:-}" ]]; then
    log "DAILY_AUTOMATION_TOKEN is required so merges are performed as the configured user."
    return 1
  fi

  local prs
  prs="$(gh_retry pr list \
    --repo "$REPO" \
    --state open \
    --json number,isDraft,headRefName,title \
    --jq '.[] | select(.headRefName | startswith("daily/")) | [.number, .isDraft, .headRefName, .title] | @tsv')"

  if [[ -z "$prs" ]]; then
    log "No open daily PRs."
    return 0
  fi

  while IFS=$'\t' read -r pr draft head title; do
    [[ -z "${pr:-}" ]] && continue

    if [[ "$draft" == "true" ]]; then
      log "PR #$pr skipped: draft"
      continue
    fi

    if [[ "$title" != daily:* || "$head" != daily/* ]]; then
      log "PR #$pr skipped: title/head guard failed"
      continue
    fi

    if [[ "$REQUIRE_CODE_CHANGE" == "true" ]] && is_docs_only "$pr"; then
      log "PR #$pr skipped: docs-only diff"
      continue
    fi

    if ! wait_for_pr_checks "$pr"; then
      continue
    fi

    run_pr_tests "$head"

    issue="$(linked_issue_number "$pr")"
    if [[ -n "$issue" ]]; then
      gh_retry issue comment "$issue" \
        --repo "$REPO" \
        --body "GitHub Actions auto-merge: PR #$pr passed generated test checks and repository guards."
    fi

    merge_pr "$pr"
    log "PR #$pr merged"
  done <<< "$prs"
}

main "$@"
