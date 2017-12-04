#!/usr/bin/env bash

python3 py_expense/manage.py migrate
python3 py_expense/manage.py runserver
