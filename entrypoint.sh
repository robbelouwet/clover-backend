#!/bin/bash

az login --identity

az account show

python3 start.py