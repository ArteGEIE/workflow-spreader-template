"""
Github Workflow Importer
__author__ Pierre PATAKI <ppataki __AT__ sdv.fr>
"""

import os

from libraries.Colors import Colors
from libraries.Common import Common
from libraries.spreader.Configuration import Configuration
from libraries.spreader.Organization import Organization

# Rock'n'roll
if __name__ == "__main__":
    '''
    Propagates the Workflow Configurations
    '''

    org = Organization()
    configurations = Configuration.find_configurations(
        organization=org
    )

    print(
        f"\n{Colors.BOLD}"
        f"Propagating Workflows to "
        f"{str(len(configurations))} Repositories ..."
        f"{Colors.ENDC}"
    )

    for config in configurations:
        repository = org.get_repo(config.repository_name)
        workflows = []

        print(
            f" » {Colors.OKCYAN}{repository.get_full_name()}{Colors.ENDC}"
        )

        for workflow in config.data['workflows']:
            source_workflow_filename = f"./workflows/{workflow}.yml"
            dest_workflow_filename = f".github/workflows/" \
                f"{os.path.basename(workflow)}.yml"

            if repository.branch_exists(
                config.data['incoming-changes']['branch-name']
            ):
                check_branch = config.data['incoming-changes']['branch-name']
            else:
                check_branch = repository.get_default_branch()

            if not Common.diff_local_and_repo_files(
                repository=repository,
                branch_name=check_branch,
                local_file=source_workflow_filename,
                remote_file=dest_workflow_filename
            ):
                print(
                    f"   » File "
                    f"{Colors.OKBLUE}{source_workflow_filename}{Colors.ENDC}"
                    f" unchanged. Skipping file."
                )

            else:
                print(
                    f"   » File "
                    f"{Colors.OKBLUE}{source_workflow_filename}{Colors.ENDC}"
                    f" updated. Added to update list."
                )

                workflows.append(workflow)

        if len(workflows) > 0:
            repository.create_branch(
                config.data['incoming-changes']['branch-name']
            )

            for workflow in workflows:
                source_workflow_filename = f"./workflows/{workflow}.yml"
                dest_workflow_filename = f".github/workflows/" \
                    f"{os.path.basename(workflow)}.yml"

                repository.put_file(
                    config.data['incoming-changes']['branch-name'],
                    source_workflow_filename,
                    dest_workflow_filename,
                    config.data['incoming-changes']['commit-name']
                )

            pr_create_result = repository.create_pr(
                config.data['incoming-changes']['branch-name'],
                config.data['incoming-changes']['pull-request']['title'],
                'Workflow Automatic Update trigger'
            )

            if not pr_create_result:
                Common.github_output(
                    'error',
                    "Could not create Pull Request"
                )
