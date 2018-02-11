import logging
import sys

import configargparse

log = logging.getLogger(__name__)
args = None


def cfg_get(key):
    global args
    return getattr(args, key)


def cfg_set(key, val):
    global args
    setattr(args, key, val)


def parse_args():
    global args
    defaultconfigfiles = []
    if '-c' not in sys.argv and '--config' not in sys.argv:
        defaultconfigfiles = ['config.ini']

    parser = configargparse.ArgParser(
        default_config_files=defaultconfigfiles)

    parser.add_argument('-c', '--config',
                        is_config_file=True, help='Specify configuration file.')

    parser.add_argument('-p', '--proxies-file',
                        help='Load proxy list from text file (one proxy per line).')

    parser.add_argument('-pgpmin', '--pgpool-min-level', type=int, default=1,
                        help="Minimum trainer level to request from PGPool")

    parser.add_argument('-pgpmax', '--pgpool-max-level', type=int, default=40,
                        help="Maximum trainer level to request from PGPool")

    parser.add_argument('-pgpu', '--pgpool-url', required=True,
                        help='Address of PGPool to load accounts from and/or update their details.')

    parser.add_argument('-pgpn', '--pgpool-num-accounts', type=int,
                        help='Load this many banned or new accounts from PGPool.')

    parser.add_argument('-a', '--accounts-file', required=True,
                      help='TODO')

    parser.add_argument('-sid', '--system-id',
                        help='System ID to use when requesting accounts from PGPool.')

    parser.add_argument('-reuse', type=bool, default=False,
                        help='Reuse accounts assigned to the given system ID.')

    args = parser.parse_args()


def cfg_init():
    global args

    log.info("Loading PGPool client configuration.")

    parse_args()

    if cfg_get('pgpool_min_level') > 1 or cfg_get('pgpool_max_level') < 40:
        log.info("Only getting accounts with trainer level {} to {}.".format(cfg_get('pgpool_min_level'),
                                                                             cfg_get('pgpool_max_level')))
