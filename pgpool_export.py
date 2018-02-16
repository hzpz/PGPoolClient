import logging
import sys
import csv

from pgpool_client.config import cfg_get, cfg_init
from pgpool_client.utils import pgpool_load_accounts, pgpool_mark_banned, pgpool_release_account

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

cfg_init()
if not cfg_get('pgpool_num_accounts') > 0:
    log.error('--pgpool-num-accounts must be provided')
    sys.exit()

if not cfg_get('system_id'):
    log.error('--system-id must be provided')
    sys.exit()

with open(cfg_get('accounts_file')) as accounts_file:
    reader = csv.reader(accounts_file)
    for row in reader:
        username = row[1]
        log.info('Marking account %s as banned', username)
        pgpool_mark_banned(username)
        log.info('Releasing account %s', username)
        pgpool_release_account(username)

accounts = pgpool_load_accounts(cfg_get('pgpool_num_accounts'))

with open(cfg_get('accounts_file'), 'w') as accounts_file:
    writer = csv.writer(accounts_file)
    for acc in accounts:
        username = acc['username']
        log.info('Adding account %s', username)
        writer.writerow([acc['auth_service'], username, acc['password']])
