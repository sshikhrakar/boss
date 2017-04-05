'''
Module for slack API.
'''

import json
from fabric.api import local, parallel
from ..config import get as _get_config

DEPLOYING_MESSAGE = '{user} is deploying branch {branch_link} to {server_link} server.'
DEPLOYED_SUCCESS_MESSAGE = 'Finished deploying branch {branch_link} to {server_link} server.'


def config():
    ''' Get slack configuration. '''
    return _get_config()['services']['slack']


def is_enabled():
    ''' Check if slack is enabled or not. '''
    return config()['enabled']


def create_link(url, title):
    ''' Create a link for slack payload. '''
    return '<{url}|{title}>'.format(
        url=url,
        title=title
    )


@parallel
def notify(payload):
    ''' Send a notification on Slack. '''
    command = 'curl -X POST -H "Content-type: application/json" --data \'{data}\' {url}'
    # TODO: Don't rely on curl to do this.

    local(command.format(
        data=json.dumps(payload),
        url=config()['base_uri'] + config()['endpoint']
    ))


def notify_deploying(**params):
    ''' Send Deploying notification on Slack. '''
    branch_link = create_link(params['branch_url'], params['branch'])
    server_link = create_link(params['public_url'], params['host'])
    server_short_link = create_link(
        params['public_url'], params['server_name']
    )

    text = DEPLOYING_MESSAGE.format(
        user=params['user'],
        branch_link=branch_link,
        server_link=server_short_link
    )

    payload = {
        "text": text,
        "attachments": [
            {
                "title": "Deploying",
                "color": config()['deploying_color'],
                "fields": [
                    {
                        "title": "Branch",
                        "value": branch_link,
                        "short": True
                    },
                    {
                        "title": "To",
                        "value": server_link,
                        "short": True
                    }
                ]
            }
        ]
    }

    # Notify on slack
    notify(payload)


def notify_deployed(**params):
    ''' Send Deployed notification on Slack. '''
    branch_link = create_link(params['branch_url'], params['branch'])
    server_link = create_link(params['public_url'], params['host'])
    server_short_link = create_link(
        params['public_url'], params['server_name']
    )

    text = DEPLOYED_SUCCESS_MESSAGE.format(
        branch_link=branch_link,
        server_link=server_short_link
    )

    payload = {
        "text": text,
        "attachments": [
            {
                "title": "Finished Deploying",
                "color": config()['deployed_color'],
                "fields": [
                    {
                        "title": "Branch",
                        "value": branch_link,
                        "short": True
                    },
                    {
                        "title": "To",
                        "value": server_link,
                        "short": True
                    }
                ]
            }
        ]
    }

    # Notify on slack
    notify(payload)
