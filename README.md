[![Build Status](https://api.travis-ci.org/uw-it-aca/scheduled-job-client.svg?branch=develop)](https://travis-ci.org/uw-it-aca/scheduled-job-client)
[![Coverage Status](https://coveralls.io/repos/uw-it-aca/scheduled-job-client/badge.png?branch=develop)](https://coveralls.io/r/uw-it-aca/scheduled-job-client?branch=develop)


# Scheduled-Job-Client
This is the repository for the scheduled job manager client project, a project at the University of Washington designed to provide centralized periodic job management.

ACA AWS SNS/SQS Message App
===========================

A Django Application on which to build AWS SNS endpoints and SQS gatherers

Installation
------------

**Project directory**

Install django-aws-message in your project.

    $ cd [project]
    $ pip install -e git+https://github.com/uw-it-aca/scheduled-job-client/#egg=scheduled_job_client

Project settings.py
------------------

**Job Client App Settings**

    # add Job Client to INSTALLED_APPS
    INSTALLED_APPS += [
        'scheduled_job_client.apps.ScheduledJobClientConfig',
    ]

    # Job Client Configuration
    SCHEDULED_JOB_CLIENT = {
        'CLUSTER_NAME': '<app_cluster_name>',
        'CLUSTER_MEMBER': '<app_cluser_member_name>',
        'KEY_ID': '<aws_key_id>',
        'KEY': '<aws_key>',
        'NOTIFICATION': {
            'ENDPOINT_BASE': 'http://<your_server_name_here>',
            'PROTOCOL': 'http',
            'TOPIC_ARN': '<aws_arn_for_job_control_sns>',
        },
        'STATUS': {
            'QUEUE_ARN': '<aws_arn_for_job_sqs>',
            'QUEUE_URL': '<url_for_aws_job_sqs>'
        },
        'JOBS': {
            'joblabel1': {
                'title': '<an explanation for the label>',
                'type': '<one of method, management_command, or shell>',
                'action': '<method, management command or shell command to run>',
                'arguments': [<array of arguments to action>]
            }
            #, ...
        }
    }
