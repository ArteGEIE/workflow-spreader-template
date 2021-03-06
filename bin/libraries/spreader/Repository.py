"""
Wrapper Class for the Workflow Spreader
"""

import hashlib
import os

from github import GithubException, Team

from ..Colors import Colors
from ..Common import Common


class Repository:

    def __init__(self, github_repository):
        '''
        Repository Contructor
        '''

        self.github_repository = github_repository

    def get_full_name(self):
        '''
        Get the Repository Full Name including the Org
        '''

        return self.github_repository.full_name

    def get_name(self):
        '''
        Get the Repository Name
        '''

        return self.github_repository.name

    def get_default_branch(self):
        '''
        Returns the Repository Default Branch
        '''

        return self.github_repository.default_branch

    def branch_exists(self, branch_name):
        '''
        Checks if a Branch exists on a Repository
        '''

        try:
            self.github_repository.get_branch(branch_name)

            return True

        except GithubException:
            return False

    def create_branch(self, branch_name):
        '''
        Creating a Branch on a Repository
        '''

        try:
            self.github_repository.get_branch(branch_name)

            print(
                f"   » Branch {Colors.OKBLUE}{branch_name}{Colors.ENDC}"
                f" already exists on {Colors.OKBLUE}"
                f"{self.github_repository.full_name}{Colors.ENDC}"
            )

            return True

        except GithubException:
            print(
                f"   » Creating new branch {Colors.OKBLUE}{branch_name}"
                f"{Colors.ENDC} on {self.github_repository.full_name}"
            )

            self.github_repository.create_git_ref(
                f"refs/heads/{branch_name}",
                self.github_repository.get_commit('HEAD').sha
            )

            return False

    def get_branch_pr(self, branch_name):
        '''
        Fetch the PR for Branch
        '''

        prs = self.github_repository.get_pulls(
            state="open"
        )

        for pr in prs:
            if pr.head.ref == branch_name:
                return pr

        return False

    def has_branch_pr(self, branch_name):
        '''
        Checks if a Pull Request already exists for a Branch on Repository
        '''

        return bool(
            self.get_branch_pr(
                branch_name=branch_name
            )
        )

    def create_pr(self, branch_name, title, comment, reviewers=None):
        '''
        Create or Update a Pull Request for the Branch
        => Post that PR with Title and Initial Comment
        '''

        if self.has_branch_pr(branch_name):

            pr = self.get_branch_pr(
                branch_name=branch_name
            )

            # Beware, Pull Request ID is not stored under
            # id property, but under number
            pull_request_id = pr.number

            # If the configured PR title differs, update it
            if pr.title != title:
                self.github_repository \
                    .get_issue(pull_request_id) \
                    .edit(
                        title=title
                    )

            # Check the Reviewers for the PR
            self.setup_review_team(
                pr=pr,
                reviewers=reviewers
            )

            # Pushing a message to a Pull Request is using
            # Issue API in GithubAPIv3
            self.github_repository \
                .get_issue(pull_request_id) \
                .create_comment(
                    body=comment
                )

            return True

        else:
            pr = self.github_repository.create_pull(
                title=title,
                body=comment,
                head=branch_name,
                base=self.github_repository.default_branch
            )

            # Check the Reviewers for the PR
            self.setup_review_team(
                pr=pr,
                reviewers=reviewers
            )

            return True

    def setup_review_team(self, pr, reviewers):
        '''
        Assign teams to PR for review action
        '''

        pr_reviewers = []
        pr_all_reviewers = pr.get_review_requests()

        # the Teams are in the Tuple, position 1
        for pr_reviewer in pr_all_reviewers[1]:
            if type(pr_reviewer) is Team.Team:
                pr_reviewers.append(pr_reviewer.slug)

        # Does the current reviewer list contain the asked reviewers?
        reviewer_intersect = [
            value for value in pr_reviewers
            if value in reviewers
        ]

        if reviewer_intersect != reviewers:
            pr.create_review_request(
                # concatenate the original list of reviewers
                team_reviewers=pr_reviewers + reviewers
            )

    def file_exists(self, branch_name, path):
        '''
        Checks if a file exists on a branch
        '''

        return bool(
            self.get_file(
                branch_name=branch_name,
                path=path
            )
        )

    def get_file(self, path, branch_name=None):
        '''
        Get a file from on a Branch
        '''

        if branch_name is None:
            branch_name = self.github_repository.default_branch

        try:
            file = self.github_repository.get_contents(
                path=path,
                ref=branch_name
            )

            return file

        except GithubException:
            return False

    def hash_file(self, path, branch_name=None):
        '''
        Calculates sha256 hash of a repository file
        '''

        if branch_name is None:
            branch_name = self.github_repository.default_branch

        file_content = self.get_file(
            path=path,
            branch_name=branch_name
        )

        if file_content:
            return hashlib.sha256(
                file_content.decoded_content
            ).hexdigest()

        return False

    def put_file(self, branch_name, path, to_path, commit_text_tpl=None):
        '''
        Copy a local file to a specific Branch on a specitic to_path
        '''

        try:
            if commit_text_tpl is None:
                commit_text = f"Updating {os.path.basename(path)}"

            else:
                commit_text = commit_text_tpl.replace(
                    '{file}',
                    os.path.basename(path)
                )

            if os.path.isfile(path):
                # Get the content of the original Workflow file
                with open(path, 'r', encoding='UTF-8') as file:
                    file_content = file.read()

                    # If the file exists, we want to update it
                    # instead of creating
                    if self.file_exists(
                        branch_name=branch_name,
                        path=to_path
                    ):
                        print(
                            f"   » Updating {path} in "
                            f"{self.github_repository.full_name}:{to_path}"
                        )

                        # We need the SHA of the previous file
                        # to do the commit
                        file = self.get_file(
                            branch_name=branch_name,
                            path=to_path
                        )

                        self.github_repository.update_file(
                            path=to_path,
                            message=commit_text,
                            content=file_content,
                            branch=branch_name,
                            sha=file.sha
                        )

                    else:
                        print(
                            f"   » Copying {path} to "
                            f"{self.github_repository.full_name}:{to_path}"
                        )

                        # Create the file in the branch
                        self.github_repository.create_file(
                            path=to_path,
                            message=commit_text,
                            content=file_content,
                            branch=branch_name
                        )

                return True

            else:
                Common.github_output(
                    'error',
                    f"Cannot copy Workflow {path} : file not found"
                )

                return False

        except GithubException as ex:
            Common.github_output(
                'error',
                f"An error occured during file copy: {str(ex)}"
            )

            return False
