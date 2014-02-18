#!/bin/bash
cd /usr/lib/python2.7/dist-packages/nova/db/sqlalchemy/migrate_repo/
python manage.py upgrade $1

