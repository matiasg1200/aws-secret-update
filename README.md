# AWS Secrets Manager Updater

A lightweight CLI tool to interactively update and merge AWS Secrets Manager values using local configuration files.

---

AWS secrets manager doesn't allow to programatically add new key/value pairs to existing secrets in a straight forward manner, insted of just adding your new key value pair you need to upload the entire text payload of the secret that will include **all** keys, not just new ones. 

This scirpts helps to update secrets that store a large amount of keys safely in a programatic way by adding a validation step and taking special use caes into account, such as keys with multiline values. 

It also offers a rollback method in case it is needed.

---

## Features
* **Interactive UI:** Uses `click` for guided selection of workloads, environments, and regions.
* **Safety First:** Generates a local `updated_secret.json` for review before any AWS changes are committed.
* **Rollbacks:** Support rollbacks in case of issues through the `rollback_secret` method

## Setup

### 1. Install Dependencies
Run the following command to install the required libraries:
`pip install boto3 click pydantic inquirer`

### 2. Configure AWS
Ensure your environment is authenticated via the AWS CLI:
`aws configure`

---

## Usage

### Run the Updater
Execute the script and follow the interactive prompts:
`python secret_manager.py update-secret`


### Input File Format
Create a simple text file (e.g., `secrets.txt`) in the same directory as the script:
```text
DB_PASSWORD=my_secure_password
API_TOKEN=12345abcde
SOME_MULTI_LINE_SECRET=abc\nefg
DEBUG_MODE=true
```

---

## To do list
- Add method to remove existing keys
- Add method to update existing keys
- Add feature to check on which regions secrets are created and replace the manually populated region list by a dynamic one
- Add feature to update all secrets or multiple secrets in a single run
- Add small script to create python venv to start using the application or add some python dependcy handler

