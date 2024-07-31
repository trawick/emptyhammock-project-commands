# How-to guide and CLI for use in an Emptyhammock Docker-based Django application

## Requirements

* The Django application runs in a Docker container in your deployed environments.

## Assumptions of this documentation

* The Django application and database run natively in your development environment.
* The Django application reads environment variables from `.env`, using the `dotenv`
  package or some other mechanism.

## Documentation conventions

* `myproject` should be replaced with the name of your project.
* `local` should be replaced with the name of the Django settings module specific to your
  development environment, if different from `local`.

## Local development environment setup

### Python setup

* Your machine should have pyenv installed.
* Your project should have a `.python-version` file to specify the Python version for the project.
* Your project requirements should include `emptyhammock-project-commands`.

#### Install Python if not already installed

```shell
$ pyenv install -s
```

#### Create a virtualenv and install requirements

```shell
$ python -m venv ./venv/
$ . venv/bin/activate
$ pip install -r requirements/local.txt  # or `dev.txt` if it exists
```

### Environment variables

Set these in `.env`:

* Set `DJANGO_SETTINGS_MODULE` to `myproject.settings.local`

### Development database and media setup

As user `postgres`:

```bash
    $ createuser --createdb MYPROJECTNAME
    $ psql
    postgres=# alter user MYPROJECTNAME with password 'MYDBPASS';
    ALTER ROLE
    postgres=# \q
```

As developer:
```bash
    $ PGHOST=localhost createdb -U MYPROJECTNAME -E UTF-8 MYPROJECTNAME
    $ ./manage.py migrate
    $ ./manage.py createsuperuser
    ...
```

#### Get a database dump from the server and load into the local database

```bash
$ ehproject database get-dump production
$ ehproject database load-dump
$ ./manage.py migrate
```

#### Sync with the server media tree

```bash
$ ehproject media get-media production
```

## Managing deployed servers

### General preparation

Deployment is based on Ansible, which will be installed in the development
virtualenv or in a separate virtualenv as shown below:

```
$ python -m venv ./venv-deploy
$ . venv-deploy/bin/activate
$ pip install -r deploy/requirements.txt
    ...
```

Activate the virtualenv for deployment before running any of the shell commands
described in this section.

Configure your user and ssh public key in `deploy/devs.yml`.  After the next
deploy to a server, you'll be able to log in via `ssh`.  Ensure that the
username in `devs.yml` matches the username on your client system.

### Initial setup for VPS

The `sshpass` command must be installed on the client system.
(`sudo apt install sshpass`)

On the new server:

Fix the hostname in `/etc/hosts` and `/etc/hostname`.  Next:

```bash
# apt update && apt full-upgrade -y
# shutdown -r now
```

Code the IPv4 address in `deploy/inventory/production`, to control which server
Ansible deploys to.

For initial testing of the server, specify a self-signed certificate in
`deploy/environments/production/vars.yml`:

```
cert_source: "self-signed"
```

Normally this is `"certbot"`.  When initially bringing up the server, a
self-signed certificate is used.  After the domain name is changed, the
`obtain_certificate.sh` script is run to create a real certificate, then
`cert_source` is changed to start using it.

Only the `root` user will be available initially on a VPS, so a bootstrap step
is needed to define developer users.  Run the bootstrap step as follows:

```bash
$ ehproject playbook bootstrap production root
root password on server: 
Vault password: 
...
```

If the root password isn't needed because an ssh key is used to log in,
simply press ENTER at the password prompt.

If `.vault_pass` has been created, you won't be prompted for the vault
password.

Once the new server is operating properly, update the `maintenance` project
to include the server in regular maintenance tasks.

## Building and Pushing the Docker image

## Build

```bash
$ ehproject image build [--no-cache]
```

## Push to ECR

After authenticating to AWS:

```bash
$ ehproject image push
```

## Deploying

```bash
$ ehproject playbook deploy staging
...
$ ehproject playbook deploy production
```

If only the Docker image changed:

```bash
$ ehproject playbook run production switch_to_latest_image
```

## Running management commands on the server

Use `ehproject manage`, as in the following examples:

```
    $ ehproject manage remote production showmigrations
    Running as user myproject...
    admin
     [X] 0001_initial
     [X] 0002_logentry_remove_auto_add
    auth
     [X] 0001_initial
     [X] 0002_alter_permission_name_max_length
     [X] 0003_alter_user_email_max_length
     [X] 0004_alter_user_username_opts
    ...
    $ ehproject manage remote staging shell
    Running as user myproject...
    Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
    [GCC 5.4.0 20160609] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>>
```
