# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_crams_inital_data_from_sql():
    from rcportal_migration.settings import BASE_DIR
    import os

    file_name = 'crams/sql/crams_initial.mysql.sql'

    sql_statements = open(os.path.join(BASE_DIR, file_name), 'r').read()


    return sql_statements


class Migration(migrations.Migration):

    dependencies = [
        ('crams', '0001_initial'),
    ]

    operations = [
         migrations.RunSQL(load_crams_inital_data_from_sql()),
    ]
