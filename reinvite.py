#!/usr/bin/env python3

import subprocess
import json
import sys


def run_command(args, description, expect_json=True):
    result = subprocess.run(args, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error during: {description}", file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        return None

    if not expect_json:
        return result.stdout.strip()

    if not result.stdout.strip():
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON during: {description}", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        return None


def add_collaborator(full_repo_name, username):
    print(f"  -> Adding '{username}' as collaborator...")
    result = subprocess.run(
        [
            "gh", "api",
            f"repos/{full_repo_name}/collaborators/{username}",
            "-X", "PUT",
            "-f", "permission=push"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"     ! Failed to add '{username}'", file=sys.stderr)
        if result.stderr.strip():
            print(f"       {result.stderr.strip()}", file=sys.stderr)
        return False

    print(f"     ✓ Invitation/access update sent for '{username}'")
    return True


def infer_student_username(repo_name, repo_prefix):
    """
    Infer the student GitHub username from the repository {username}.
    Example:
      repo_prefix = hw-1
      repo_name = hw-1-frequency-based-entropy-estimator-{username}
      returns name
    """
    prefix_marker = f"{repo_prefix}-frequency-based-entropy-estimator-"
    if repo_name.startswith(prefix_marker):
        return repo_name[len(prefix_marker):]
    return None


def main():
    default_org = "Input Default Org Here"
    default_prefix = "Input Default Assignment Prefix Here"
    repo_limit = "1000"

    org_input = input(f"Organization [{default_org}]: ").strip()
    prefix_input = input(f"Repository prefix [{default_prefix}]: ").strip()

    organization = org_input if org_input else default_org
    repo_prefix = prefix_input if prefix_input else default_prefix

    print("Starting script...")
    print(f"Fetching repositories for organization '{organization}'...")

    repos = run_command(
        [
            "gh", "repo", "list", organization,
            "--limit", repo_limit,
            "--json", "name"
        ],
        "fetch repositories"
    )

    if repos is None:
        print("Could not fetch repositories. Exiting.", file=sys.stderr)
        sys.exit(1)

    project_repos = [
        repo for repo in repos
        if repo.get("name", "").startswith(repo_prefix)
    ]

    if not project_repos:
        print(f"No repositories found with prefix '{repo_prefix}'.")
        return

    for repo in project_repos:
        repo_name = repo["name"]
        full_repo_name = f"{organization}/{repo_name}"

        print(f"\n=== {full_repo_name} ===")

        collaborators = run_command(
            ["gh", "api", f"repos/{full_repo_name}/collaborators"],
            f"fetch collaborators for {full_repo_name}"
        )

        if collaborators is None:
            print("  -> Could not retrieve collaborators.")
            continue

        collaborator_logins = {
            c.get("login", "").lower()
            for c in collaborators
            if c.get("login")
        }

        print("Collaborators:")
        for c in collaborators:
            login = c.get("login", "unknown")
            perms = c.get("permissions", {})
            perm_summary = ", ".join(k for k, v in perms.items() if v) or "none"
            print(f"  - {login} [{perm_summary}]")

        expected_student = infer_student_username(repo_name, repo_prefix)

        if not expected_student:
            print("  -> Could not infer expected student username from repo name.")
            continue

        print(f"Expected student username: {expected_student}")

        if expected_student.lower() in collaborator_logins:
            print("  -> Student already has access.")
        else:
            print("  -> Student is missing from collaborators.")
            add_collaborator(full_repo_name, expected_student)

    print("\nDone.")


if __name__ == "__main__":
    main()
