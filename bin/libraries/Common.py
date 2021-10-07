"""
Useful Commands for the Workflow Spreader
"""

import hashlib
import os
import re
from datetime import date

from .Colors import Colors


class Common:

    def github_output(msg_type, text):
        '''
        Prints an output in the Github Actions Format
        Uses Colors for more joy
        '''

        color = Colors.ENDC

        if msg_type == 'warning':
            color = Colors.WARNING

        if msg_type == 'error':
            color = Colors.FAIL

        print(
            f"{color}::{msg_type}::{msg_type.upper()}: {text}{Colors.ENDC}"
        )

    def diff_local_and_repo_files(
            repository, branch_name, local_file, remote_file):
        '''
        Check if there are differences between a local file and a remote file
        Returns False if there is no change between files, True otherwise
        '''

        local_hash = Common.hash_file(
            path=local_file
        )
        remote_hash = repository.hash_file(
            path=remote_file,
            branch_name=branch_name
        )

        if local_hash and remote_hash and local_hash == remote_hash:
            return False

        return True

    def hash_file(path):
        '''
        Calculate sha256 hash of a local file
        '''

        if os.path.isfile(path):
            with open(path, 'r', encoding='UTF-8') as file:
                file_content = file.read().encode('utf-8')

                return hashlib.sha256(file_content).hexdigest()

        return False

    def replace_template_tags(configurations):
        '''
        Transform templating tags in Configuration Object
        '''

        date_pattern = r"({date:([%[a-zA-Z/-]+)})"
        today_date = date.today()

        if configurations['incoming-changes']:
            incoming_changes = configurations['incoming-changes']

            # Handle Templating on Branch Name
            if incoming_changes['branch-name']:
                results = re.findall(
                    date_pattern,
                    incoming_changes['branch-name']
                )

                for match in results:
                    incoming_changes['branch-name'] = \
                        incoming_changes['branch-name'] \
                        .replace(match[0], today_date.strftime(match[1]))

            # Handle Templating on Commit Name
            if incoming_changes['commit-name']:
                results = re.findall(
                    date_pattern,
                    incoming_changes['commit-name']
                )

                for match in results:
                    incoming_changes['commit-name'] = \
                        incoming_changes['commit-name'] \
                        .replace(match[0], today_date.strftime(match[1]))

            # Handle Templating on Pull Request Title
            if incoming_changes['pull-request']:
                if incoming_changes['pull-request']['title']:
                    results = re.findall(
                        date_pattern,
                        incoming_changes['pull-request']['title']
                    )

                    for match in results:
                        incoming_changes['pull-request']['title'] = \
                            incoming_changes['pull-request']['title'] \
                            .replace(match[0], today_date.strftime(match[1]))

        return configurations
