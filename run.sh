#!/usr/bin/env bash

python3 expense_snek_api/manage.py migrate
python3 expense_snek_api/manage.py runserver