import csv
import logging
import os.path
import sys

import configargparse

from pgpool_client.utils import pgpool_load_accounts, pgpool_mark_banned, pgpool_release_account

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def parse_args():
    parser = configargparse.ArgParser(default_config_files=['config.ini'])
    parser.add_argument('-c', '--config', is_config_file=True, help='Specify configuration file.')
    parser.add_argument('-pgpu', '--pgpool-url', required=True,
                        help='Address of PGPool to load accounts from and/or update their details.')

    accounts_group = parser.add_mutually_exclusive_group(required=True)
    accounts_group.add_argument('-n', '--num-accounts', type=int,
                                help='Load this many accounts.')
    accounts_group.add_argument('-ab', '--accounts-banned', nargs='+',
                                help='List of accounts that are banned and should to be replaced.')

    accounts_file_group = parser.add_mutually_exclusive_group(required=True)
    accounts_file_group.add_argument('-af', '--accounts-file',
                                     help='File to read old accounts and write new accounts to.')
    accounts_file_group.add_argument('-ad', '--accounts-files-dir',
                                     help='Directory with accounts files.')
    parser.add_argument('-sid', '--system-id', required=True,
                        help='System ID to use when requesting accounts from PGPool and when choosing accounts file.')
    return parser.parse_args()


def read_accounts(accounts_file_name):
    accounts = []
    with open(accounts_file_name) as accounts_file:
        reader = csv.reader(accounts_file)
        for acc in reader:
            accounts.append(acc)
    return accounts


def write_accounts(accounts_file_name, accounts):
    with open(accounts_file_name, 'w') as accounts_file:
        writer = csv.writer(accounts_file)
        for acc in accounts:
            writer.writerow(acc)


def get_accounts_file_name(args):
    if args.accounts_file is not None:
        accounts_file_name = args.accounts_file
    else:
        accounts_file_name = os.path.join(args.accounts_files_dir, 'accounts-' + args.system_id + '.csv')
    return accounts_file_name


def get_num_new_accounts(args):
    if args.num_accounts is not None:
        num_accounts = args.num_accounts
    else:
        num_accounts = len(args.accounts_banned)
    return num_accounts


def pgpool_mark_banned_and_release_accounts(pgpool_url, accounts, accounts_banned):
    for acc in accounts:
        username = acc[1]
        if username in accounts_banned:
            log.info('Marking account %s as banned', username)
            pgpool_mark_banned(pgpool_url, username)
            log.info('Releasing account %s', username)
            pgpool_release_account(pgpool_url, username)


def merge_accounts(existing_accounts, pgpool_accounts, accounts_banned):
    accounts = []
    for acc in existing_accounts:
        username = acc[1]
        if username in accounts_banned:
            pgpool_account = pgpool_accounts.pop()
            pgpool_username = pgpool_account['username']
            log.info('Adding account %s', pgpool_username)
            accounts.append([pgpool_account['auth_service'], pgpool_username, pgpool_account['password']])
        else:
            accounts.append(acc)
    return accounts


def verify_accounts_banned(existing_accounts, accounts_banned):
    if accounts_banned is None:
        return

    existing_accounts_usernames = []
    for acc in existing_accounts:
        existing_accounts_usernames.append(acc[1])

    for acc in accounts_banned:
        if acc not in existing_accounts_usernames:
            log.error('Cannot find banned account %s in existing accounts %s', acc, existing_accounts_usernames)
            sys.exit(1)


def main():
    args = parse_args()
    accounts_file_name = get_accounts_file_name(args)
    existing_accounts = read_accounts(accounts_file_name)
    verify_accounts_banned(existing_accounts, args.accounts_banned)
    pgpool_mark_banned_and_release_accounts(args.pgpool_url, existing_accounts, args.accounts_banned)
    num_new_accounts = get_num_new_accounts(args)
    pgpool_accounts = pgpool_load_accounts(args.pgpool_url, args.system_id, num_new_accounts)
    merged_accounts = merge_accounts(existing_accounts, pgpool_accounts, args.accounts_banned)
    write_accounts(accounts_file_name, merged_accounts)


if __name__ == "__main__":
    main()
