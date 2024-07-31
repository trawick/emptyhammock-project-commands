# Changes and migration requirements

## Version 0.0.4

* Add documentation for all basic developer tasks.
* Add `ehproject database load-dump` command, removing the need for projects
  to provide a `refresh_db.sh` command.

## Version 0.0.3

* Resolve nested variable settings for `image` subcommands.

## Version 0.0.2

* Add `roles install` command for installing Ansible roles without performing
  other operations.
* Fix problem passing Ansible variables whose values contain spaces.

## Version 0.0.1

* initial version
