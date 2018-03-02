import datetime
import json
import logging
import time

import requests

log = logging.getLogger(__name__)


def pgpool_load_accounts(pgpool_url, system_id, num):
    request = {
        'system_id': system_id,
        'count': num
    }

    while True:
        try:
            r = requests.get("{}/account/request".format(pgpool_url), params=request)
            if r.status_code == 200:
                acc_json = r.json()
                if isinstance(acc_json, dict):
                    acc_json = [acc_json]

                return acc_json
            else:
                log.error("Could not request accounts from PGPool. Status {}: {} - Retrying...", r.status_code,
                          repr(r.content))
        except Exception as e:
            log.error("Error requesting accounts from PGPool: {} - Retrying...", repr(e))

        time.sleep(2)


def pgpool_update_account(pgpool_url, data):
    url = '{}/account/update'.format(pgpool_url)
    requests.post(url, data=json.dumps(data))


def pgpool_mark_banned(pgpool_url, username):
    data = {
        'username': username,
        'banned': True
    }
    pgpool_update_account(pgpool_url, data)


def pgpool_account_heartbeat(pgpool_url, username):
    data = {
        'username': username,
        'last_modified': datetime.datetime.now()
    }
    pgpool_update_account(pgpool_url, data)


def pgpool_release_account(pgpool_url, username):
    url = '{}/account/release'.format(pgpool_url)
    data = {
        'username': username
    }
    requests.post(url, data=json.dumps(data))
