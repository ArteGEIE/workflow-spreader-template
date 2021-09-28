"""
Wrapper Class for the Workflow Spreader
"""

import os
from json import JSONDecodeError, loads

from jsonschema import ValidationError, validate

from ..Colors import Colors
from ..Common import Common


class Configuration:
    config_path = './configurations'
    remote_config_path = os.getenv(
        'WORKFLOW_CONFIG_PATH',
        '.github/.workflows.json'
    )
    config_validation_schema = {
        "type": "object",
        "properties": {
            "workflow-autoupdate": {
                "type": "boolean"
            },
            "incoming-changes": {
                "type": "object",
                "properties": {
                    "branch-name": {
                        "type": "string"
                    },
                    "commit-name": {
                        "type": "string"
                    },
                    "pull-request": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string"
                            }
                        }
                    }
                }
            },
            "workflows": {
                "type": "array"
            }
        }
    }

    def __init__(self, repository_name, repository_type, path, data):
        '''
        Configuration Constructor
        '''

        self.repository_name = repository_name
        self.repository_type = repository_type
        self.path = path
        self.data = data

    def validate_configuration_schema(self):
        '''
        Validate the integrity of a JSON Workflow Configuration
        '''

        try:
            validate(
                instance=self.data,
                schema=Configuration.config_validation_schema
            )

            return True

        except ValidationError:
            return False

    def get_remote_configurations(organization):
        '''
        Retrieve Configurations from Organization Repositories
        '''

        configurations = []

        for repo in organization.get_repos():
            config = repo.get_file(
                path=Configuration.remote_config_path
            )

            if config:
                try:
                    # Read Auto-Update Configuration
                    data = loads(
                        config
                        .decoded_content.decode('UTF-8')
                    )

                except TypeError:
                    data = {}

                except JSONDecodeError:
                    data = {}

                configurations.append(
                    Configuration(
                        repository_name=repo.get_name(),
                        repository_type="remote",
                        path=Configuration.remote_config_path,
                        data=data
                    )
                )

        return configurations

    def get_local_configurations():
        '''
        Retrieve Configurations from Local Repository
        '''

        configurations = []

        for config in os.listdir(f"{os.getcwd()}/{Configuration.config_path}"):
            if config.endswith('.json'):
                configuration_path = f"{Configuration.config_path}/{config}"

                with open(configuration_path, 'r', encoding='UTF-8') as file:
                    file_content = file.read()

                    try:
                        data = loads(file_content)

                    except TypeError:
                        data = {}

                    except JSONDecodeError:
                        data = {}

                configurations.append(
                    Configuration(
                        repository_name=config.replace('.json', ''),
                        repository_type="local",
                        path=configuration_path,
                        data=data
                    )
                )

        return configurations

    def find_local_configurations(organization):
        '''
        Finds configurations stored in this repo. Will be overridden by remote
        configurations if we found any
        '''

        configurations = {}

        print(
            f"{Colors.BOLD}Inspecting Local Workflow Configurations ..."
            f"{Colors.ENDC}"
        )

        for config in Configuration.get_local_configurations():

            if not organization.repo_exists(config.repository_name):
                Common.github_output(
                    "warning",
                    "Local Workflow Configuration exists for Repository "
                    f"{organization.get_name()}/{config.repository_name} "
                    f"but Repository not found"
                )

            else:
                if not config.validate_configuration_schema():
                    Common.github_output(
                        "error",
                        f"Workflow Configuration {config.path} invalid."
                    )

                else:
                    if 'workflow-autoupdate' in config.data:
                        print(
                            f" » Repository {Colors.OKCYAN}"
                            f"{config.repository_name}{Colors.ENDC} has"
                            " activated Workflow Auto-Update ...\n"
                            f"   Workflows : {Colors.OKGREEN}"
                            f"{', '.join(config.data['workflows'])}"
                            f"{Colors.ENDC}"
                        )

                        configurations[config.repository_name] = config

        if len(configurations) == 0:
            print(
                f" » {Colors.FAIL}No Local Workflow Configuration found"
                f"{Colors.ENDC}"
            )

        return configurations

    def find_github_configurations(organization):
        '''
        Get Organization Repositories that have activated Workflow Autoupdate
        Organization Name is provided by Environment Variable _ORGANIZATION
        '''

        configurations = {}

        print(
            f"\n{Colors.BOLD}Inspecting {organization.get_name()}"
            f" Organization Repositories ...{Colors.ENDC}"
        )

        for config in Configuration.get_remote_configurations(organization):

            if not config.validate_configuration_schema():
                Common.github_output(
                    "error",
                    f"Workflow Configuration {config.path} invalid."
                )

            else:
                if 'workflow-autoupdate' in config.data:
                    print(
                        f" » Repository {Colors.OKCYAN}"
                        f"{config.repository_name}{Colors.ENDC} "
                        "has activated Workflow Auto-Update ...\n"
                        f"   Workflows : {Colors.OKGREEN}"
                        f"{', '.join(config.data['workflows'])}{Colors.ENDC}"
                    )

                    configurations[config.repository_name] = config

        if len(configurations) == 0:
            print(
                f" » {Colors.FAIL}No Repository with Workflow "
                f"Auto-Update found{Colors.ENDC}"
            )

        return configurations

    def find_configurations(organization):
        '''
        Locates Configurations in Local and Remote Repositories
        '''

        local_configs = Configuration \
            .find_local_configurations(organization)
        github_configs = Configuration \
            .find_github_configurations(organization)

        configurations = []

        for repository_name, github_config in github_configs.items():
            if repository_name in local_configs:
                Common.github_output(
                    "warning",
                    f"Local Workflow Configuration for {repository_name}"
                    " will be overriden by Repository Configuration"
                )

            else:
                configurations.append(github_config)

        for repository_name, local_config in local_configs.items():
            if repository_name not in configurations:
                configurations.append(local_config)

        return configurations
