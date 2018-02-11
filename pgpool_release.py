import csv
import logging

from pgpool_client.utils import pgpool_release_account
from pgpool_client.config import cfg_init, cfg_get

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

cfg_init()

with open(cfg_get('accounts_file')) as accounts_file:
    reader = csv.reader(accounts_file)
    for row in reader:
        username = row[1]
        log.info('Releasing account %s', username)
        pgpool_release_account(username)
