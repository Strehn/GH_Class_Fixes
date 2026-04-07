# GH_Class_Fixes

This script audits GitHub Classroom homework repositories in a specified organization and checks whether the expected student collaborator has access to each repository.
It works by:
connecting to a GitHub organization using the GitHub CLI (gh)
listing repositories that match a given homework prefix, such as hw-1
inspecting the collaborators currently assigned to each repository
inferring the expected student GitHub username from the repository name
comparing the expected student username against the existing collaborator list
automatically adding the student as a collaborator with push permission if they are missing

Requirements
Python 3
GitHub CLI (gh) installed
GitHub CLI authenticated with an account that has permission to manage the repositories
