import csv
import logging
import os.path

import configargparse

from pgpool_client.utils import pgpool_load_accounts, pgpool_mark_banned, pgpool_release_account

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def parse_args():
    parser = configargparse.ArgParser(default_config_files=['config.ini'])
    parser.add('-c', '--config', is_config_file=True, help='Specify configuration file.')
    parser.add_argument('-pgpu', '--pgpool-url', required=True,
                        help='Address of PGPool to load accounts from and/or update their details.')
    parser.add_argument('-n', '--num-accounts', required=True, type=int,
                        help='Load this many accounts.')
    accounts_group = parser.add_mutually_exclusive_group(required=True)
    accounts_group.add_argument('-af', '--accounts-file',
                                help='File to read old accounts and write new accounts to.')
    accounts_group.add_argument('-ad', '--accounts-files-dir',
                                help='Directory with accounts files.')
    parser.add_argument('-sid', '--system-id', required=True,
                        help='System ID to use when requesting accounts from PGPool and when choosing accounts file.')
    return parser.parse_args()


def pgpool_mark_banned_and_release_accounts(pgpool_url, accounts_file_name):
    with open(accounts_file_name) as accounts_file:
        reader = csv.reader(accounts_file)
        for row in reader:
            username = row[1]
            log.info('Marking account %s as banned', username)
            pgpool_mark_banned(pgpool_url, username)
            log.info('Releasing account %s', username)
            pgpool_release_account(pgpool_url, username)


def pgpool_load_and_write_new_accounts(pgpool_url, system_id, num_accounts, accounts_file_name):
    accounts = pgpool_load_accounts(pgpool_url, system_id, num_accounts)

    with open(accounts_file_name, 'w') as accounts_file:
        writer = csv.writer(accounts_file)
        for acc in accounts:
            username = acc['username']
            log.info('Adding account %s', username)
            writer.writerow([acc['auth_service'], username, acc['password']])


if __name__ == "__main__":
    args = parse_args()
    if args.accounts_file is not None:
        accounts_file_name = args.accounts_file
    else:
        accounts_file_name = os.path.join(args.accounts_files_dir, 'accounts-' + args.system_id + '.csv')
    pgpool_mark_banned_and_release_accounts(args.pgpool_url, accounts_file_name)
    pgpool_load_and_write_new_accounts(args.pgpool_url, args.system_id,
                                       args.num_accounts, accounts_file_name)
