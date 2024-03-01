#!/bin/bash

psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "create user ${DB_USER} with encrypted password '${DB_PASSWORD}'";
psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "create database ${DJ_DB_NAME} owner '${DB_USER}'";
