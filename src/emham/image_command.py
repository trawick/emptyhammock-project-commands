import base64
from contextlib import contextmanager
import json
import subprocess
from pathlib import Path

import boto3
import docker
import yaml

import click


def _build(cache: bool, project_name: str):
    cache_args = [] if cache else ["--no-cache", "--pull"]
    subprocess.run(
        [
            "docker",
            "image",
            "build",
        ]
        + cache_args
        + [
            "-t",
            project_name,
            ".",
        ],
        check=True,
    )


@contextmanager
def _flush_existing_login(registry: str) -> None:
    """handles the known bug
    where existing stale creds cause login
    to fail.
    https://github.com/docker/docker-py/issues/2256
    """
    config = Path(Path.home() / ".docker" / "config.json")
    original = config.read_text()
    as_json = json.loads(original)
    as_json['auths'].pop(registry, None)
    config.write_text(json.dumps(as_json))
    try:
        yield
    finally:
        config.write_text(original)


def _push(project_name: str, aws_account_id: str, aws_region: str):
    # get AWS ECR login token
    ecr_client = boto3.client(
        'ecr',
        # aws_access_key_id=access_key_id,
        # aws_secret_access_key=secret_access_key,
        region_name=aws_region,
    )
    ecr_credentials = ecr_client.get_authorization_token()['authorizationData'][0]

    ecr_username = 'AWS'

    ecr_password = (
        base64.b64decode(ecr_credentials['authorizationToken'])
        .replace(b'AWS:', b'')
        .decode('utf-8')
    )

    ecr_url = ecr_credentials['proxyEndpoint']
    # get Docker to login/authenticate with ECR
    docker_client = docker.from_env()
    docker_client.login(
        username=ecr_username,
        password=ecr_password,
        # See https://github.com/docker/docker-py/issues/2256
        # Yanking "https://" and setting reauth is a workaround for a stale
        # ~/.docker/config.json (from docker CLI) breaking login, which
        # manifests itself during the push.
        registry=ecr_url.replace("https://", ""),
        reauth=True,
    )

    # tag image for AWS ECR
    repo_name = f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{project_name}"
    docker_image = docker_client.images.get(name="liamtrawickmusic")
    docker_image.tag(repo_name, tag='latest')

    # push image to AWS ECR
    output = docker_client.images.push(repo_name, tag='latest')
    print(output)


@click.command()
@click.argument("mode", type=click.Choice(["build", "push"]))
@click.option("--cache/--no-cache", default=True)
def image(mode: str, cache: bool) -> None:
    with open("deploy/environments/all/vars.yml", encoding="utf-8") as f:
        all_vars = yaml.safe_load(f.read())
    aws_account_id = all_vars["aws_account_id"]
    aws_region = all_vars["aws_region"]
    project_name = all_vars["project_name"]
    if mode == "build":
        _build(cache, project_name)
    elif mode == "push":
        _push(project_name, aws_account_id, aws_region)
