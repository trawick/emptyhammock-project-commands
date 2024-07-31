#!/usr/bin/env bash

if test $# -ne 1; then
    echo "Usage: $0 project-name" 1>&2
    exit 1
fi

PROJECT_NAME=$1
shift

. .env

# defaults should match those in <projectname>.settings.base
export PGUSER=${DB_USER:-${PROJECT_NAME}}
export PGPASSWORD=${DB_PASSWORD:-${PROJECT_NAME}}
export PGHOST=${DB_HOST:-localhost}
export PGPORT=${DB_PORT:-5432}

if ! dropdb --if-exists ${PROJECT_NAME}; then
    exit 1
fi

if ! createdb -E UTF-8 ${PROJECT_NAME}; then
    exit 1
fi

if ! zcat project.sql.gz | psql ${PROJECT_NAME}; then
    exit 1
fi
