#!/usr/bin/env python3
import json
import boto3
import click
import inquirer
from pathlib import Path
from pydantic import BaseModel

class SecretConfig(BaseModel):
   secret_id: str
   region: str
   file_path: Path | None = None


def get_available_secrets(region):
   client = boto3.client('secretsmanager', region_name=get_aws_region(region))

   secrets = []
   paginator = client.get_paginator('list_secrets')
   for page in paginator.paginate():
     for secret in page['SecretList']:
        secrets.append(secret['Name'])

   return sorted(secrets)


def get_aws_region(region_code):
   region_map = {
   'us': 'us-east-1',
   'ca': 'ca-central-1',
   'uk': 'eu-west-2',
   }
   return region_map[region_code]


def interactive_menu():
   click.secho("\n=== AWS Secrets Manager Updater ===\n", fg="cyan", bold=True)

   questions = [
   inquirer.List('region',
   message="Select Region",
   choices=['us', 'ca', 'uk'])
   ]
   answer = inquirer.prompt(questions)
   region = answer['region']

   available_secrets = get_available_secrets(region)

   questions = [
   inquirer.List('secret',
   message="Select Secret",
   choices=available_secrets)
   ]
   answer = inquirer.prompt(questions)
   secret_id = answer['secret']


   script_dir = Path(__file__).parent
   while True:
     file_name = click.prompt(
     click.style("Name of file with secrets (in current directory)", fg="yellow"),
     )
     file_path = script_dir / file_name

     if file_path.exists():
       break
     else:
       click.secho(f"✗ File '{file_name}'", fg="red")


   click.secho(f"✓ Selected Region: {region}", fg="green")
   click.secho(f"✓ Secret ID: {secret_id}\n", fg="green")
   
   config = SecretConfig(secret_id=secret_id, region=region, file_path=file_path)
   return config


def parse_secrets_file(file_path):
   secrets = {}
   with open(file_path) as f:
     for line in f:
       line = line.strip()
       if line and '=' in line:
         key, value = line.split('=', 1)
         secrets[key] = value
   return secrets


@click.group()
def cli():
   pass


@cli.command()
def update_secret():
   config = interactive_menu()

   while True:
     if config.file_path.exists():
       break
     else:
       click.secho(f"✗ File with new secrets does not exist", fg="red")

   client = boto3.client('secretsmanager', region_name=get_aws_region(config.region))
   secret = json.loads(client.get_secret_value(SecretId=config.secret_id)['SecretString'])
   new_secrets = parse_secrets_file(config.file_path)
   updated_secret = {**secret, **new_secrets}


   output_file = Path(__file__).parent / "updated_secret.json"
   with open(output_file, 'w') as f:
     json.dump(updated_secret, f, indent=2)


   click.secho(f"\n Updated secret written to: {output_file.name}", fg="cyan")
   click.secho(f"   Review the file before confirming.\n", fg="cyan")


   if not click.confirm("Do you want to update AWS Secrets Manager with these values?", default=False):
     click.secho("Update cancelled", fg="red")
     return


   client.put_secret_value(SecretId=config.secret_id, SecretString=json.dumps(secret))
   click.secho(f"✓ Updated secret '{config.secret_id}' in region '{config.region}'", fg="green")


def rollback_secret():
   config = interactive_menu()
   
   client = boto3.client('secretsmanager', config.region)
   previous = client.get_secret_value(SecretId=config.secret_id, VersionStage='AWSPREVIOUS')
   previous_version_id = previous['VersionId']

   client.update_secret_version_stage(
   SecretId=config.secret_id,
   VersionStage='AWSCURRENT',
   MoveToVersionId=previous_version_id,
   )

   click.secho(f"✓ Rolled back to version {previous_version_id}", fg="green")

if __name__ == "__main__":
   cli()