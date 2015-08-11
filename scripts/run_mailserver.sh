#!/bin/env bash
# run a debugging mail server for development

python -m smtpd -n -c DebuggingServer localhost:1025
