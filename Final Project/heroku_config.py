#!/usr/bin/env python3
# -*- coding: utf-8 -*-

deploy_dir = 'exdth_test'
deploy_path = '~/Documents/CUNY/Data608'
app_name = 'exdth-test'
virtual_env = deploy_dir + '_env'
dependencies = ['gunicorn',
                'dash',
                'numpy',
                'pandas']
exclude = ['us_state_abbreviation.py']
gitignore = ['*~' # Emacs backup files
             ]
python_version = '3.7'