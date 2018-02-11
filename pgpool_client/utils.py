import json
import logging

import requests
import time

from pgpool_client.config import cfg_get

log = logging.getLogger(__name__)


def pgpool_load_accounts(num):
    request = {
        'system_id': cfg_get('system_id'),
        'count': num,
        'min_level': cfg_get('pgpool_min_level'),
        'max_level': cfg_get('pgpool_max_level'),
        'reuse': cfg_get('reuse')
    }

    while True:
        try:
            r = requests.get("{}/account/request".format(cfg_get('pgpool_url')), params=request)
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


def pgpool_mark_banned(username):
    url = '{}/account/update'.format(cfg_get('pgpool_url'))
    data = {
        'username': username,
        'banned': True
    }
    requests.post(url, data=json.dumps(data))



def pgpool_release_account(username):
    url = '{}/account/release'.format(cfg_get('pgpool_url'))
    data = {
        'username': username
    }
    requests.post(url, data=json.dumps(data))
