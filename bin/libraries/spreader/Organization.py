"""
Wrapper Class for the Workflow Spreader
"""

import os
import sys

import github

from ..Common import Common
from .Repository import Repository


class Organization:

    org = None

    def __init__(self):
        '''
        Organization Contructor
        '''

        # Some Environment Variable Checks
        if not os.getenv('GITHUB_TOKEN'):
            Common.github_output(
                'error',
                'Missing GITHUB_TOKEN environment variable'
            )
            sys.exit(1)

        github_connector = github.Github(os.getenv("GITHUB_TOKEN"))

        if os.getenv('ORGANIZATION_NAME'):
            if os.getenv('ORGANIZATION_NAME'):
                # Get the Organization from API
                self.org = github_connector.get_organization(
                    os.getenv('ORGANIZATION_NAME')
                )

        else:
            if os.getenv('GITHUB_REPOSITORY'):
                # Get the Organization Name
                org_name = github_connector.get_repo(
                    os.getenv('GITHUB_REPOSITORY')
                ).organization.login

                # Get the Organization from API
                self.org = github_connector.get_organization(
                    org_name
                )

            else:
                Common.github_output(
                    'error',
                    'Could not retrieve Organization Name'
                )
                sys.exit(1)

    def get_repo(self, repository_name):
        '''
        Retrieve Unique Organization Repository by Name
        '''

        return Repository(
            self.org.get_repo(repository_name)
        )

    def get_repos(self):
        '''
        Retrieve Organization Repositories
        '''

        repos = []

        for repo in self.org.get_repos():
            repos.append(
                Repository(
                    github_repository=repo
                )
            )

        return repos

    def repo_exists(self, repo_name):
        '''
        Checks if a Repository exists in an Organization
        '''

        for repo in self.org.get_repos():
            if repo.name.lower() == repo_name.lower():
                return True

        return False

    def get_name(self):
        '''
        Return the Organization Name
        '''

        return self.org.login
