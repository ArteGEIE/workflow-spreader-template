# Github Actions Workflow Spreader
`One Repository to rule them all, One Repository to find them, One Repository to bring them all, and in the Workflow bind them`

[![Code Quality Check](https://github.com/DevOpsActions/workflow-spreader/actions/workflows/code-quality.yml/badge.svg)](https://github.com/DevOpsActions/workflow-spreader/actions/workflows/code-quality.yml)


---

## Philosophy

This project responds to the need of sharing multiple workflows across multiple Repositories inside an Organization.

When a Workflow is updated inside this Repository, the implemented Github Actions will scan the Organization Repositories and will create a Branch and an associated Pull Request for updating 

### Setup

1. Fork this project into your Github Organization
2. Then you will need to generate a [`Personal Access Token`](https://github.com/settings/tokens) from a priviledged user in the Organization with those scopes : 
  - `admin:org`
  - `repo`
  - `workflow`
3. Add those Organization Secrets, or a Repository Secrets if your Organization has only a Github free-plan :
  - `WORKFLOW_SPREADER_ACCESS_TOKEN` with the value of the `PAT` you generated just before
  - `WORKFLOW_CONFIG_PATH` with the name of the folder where you will store the Workflow Spreader configuration in your Organization Repositories
4. Associate Secrets to your forked Repository

We recommend you set up an expiry date for the `PAT` for obvious security reasons.

### Spreading Workflows

The available Workflows for spreading across Organization Repositories are stored in the `./workflows` folder and supports subdirectories. Feel free to add all the needed Workflows for your Organization.

Once you update this Repository with some Workflow changes, the Project Workflow `./.github/workflows/publish-workflows.yml` will scan Repositories across the Organization for any project having a Workflow Spreader configuration file. Refer to the proper section for more informations about this configuration.

The updated Workflows will come into Organization Repositories on a new git branch and an associated Pull Request will be created (or updated if already exists).

#### Spread configuration

##### In-Repository Configuration

These rules must be stored in Repositories under the same Organization.

The default path where the Spreader will look after the file is  `./.github/.workflows.json`.

You can override this by setting an Action Secret named `WORKFLOW_CONFIG_PATH` with the full path to the JSON file containing the configuration.

##### Centralized Repository Configuration

You can also store Workflow Configuration for your Organization Repositories inside the Spreader Repository.

The configuration has to be stored in the `configurations` folder and be named `repository-name.json`.

If you set two Configurations for the same Repository, only the Configuration stored in-Repository will be taken in account.

##### Workflow Configuration Format

In all cases, the JSON file must have this structure :

```json
{
  "workflow-autoupdate": true,
  "incoming-changes": {
    "branch-name": "created-branch-with-workflows",
    "commit-name": "commit-text",
    "pull-request": {
       "title": "pull-request-title"
    }
  },
  "reviewers": [
    "first-team",
    "second-team"
  ],
  "workflows": [
    "common/check-conventional-naming",
    "php/example-workflow-1"
  ]
}
```

The `incoming-changes` node is not mandatory if you have setted up a default configuration in `./configurations/_default.json` file :

```json
{
  "incoming-changes": {
    "branch-name": "created-branch-with-workflows",
    "commit-name": "commit-text",
    "pull-request": {
       "title": "pull-request-title"
    }
  }
}
```

The Spreader is validating this format and all invalid Configurations will be ignored.

| Key                                   | Type                | Description |
| ------------------------------------- | ------------------- | ----------- |
| `workflow-autoupdate`                 | `true` or `false`   | Enables the Workflow Auto Update on the Repository. |
| `incoming-changes.branch-name`        | `string`            | Name of the Branch that will be created by the Spreader, where will be commited the workflow changes. |
| `incoming-changes.commit-name`        | `string`            | Template to use in commit text when a workflow is updated. |
| `incoming-changes.pull-request.title` | `string`            | Name of the Pull Request that will be created by the Spreader. |
| `reviewers`                           | `array` of `string` | List of Teams that will be associated to PR Review. The Team must be assigned to the Github Project or it will be ignored. |
| `workflows`                           | `array` of `string` | Array of Workflows that will be spread in the Repository on Master Repo update. |

#### Templating

You can also use some templating tags in values of the `incoming-changes` :

| Tag             | Description | Example |
| --------------- | ----------- | ------- |
| `{date:format}` | Print current date using `format` in [C standard](https://docs.python.org/fr/3.6/library/datetime.html#strftime-strptime-behavior) | `{date:%Y%m%d}` will be translated `20210930` |
| `{file}`        | Placeholder for the commited file. Only usable in `commit-name`. | `{file}` will be translated by the filename of the updated workflow |

---
