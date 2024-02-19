#!/bin/bash

export APPSETTING_WEBSITE_SITE_NAME=DUMMY

az login -i --allow-no-subscription

az account show

python3 start.py