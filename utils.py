from logging import getLogger
import platform
import os


logger = getLogger(__file__)


def parse_bitcoin_conf(fd):
    """Returns dict from bitcoin.conf-like configuration file from open fd"""
    conf = {}
    for line in fd:
        line = line.strip()
        if not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            conf[key] = value

    return conf


def coin_config_path(coin):
    """Returns bitcoin.conf-like configuration path for provided coin"""

    paths = {
        # FIXME use proper AppData path
        'Windows': r'~\AppData\Roaming\{0}\{0}.conf',
        'Darwin': r'~/Library/Application Support/{0}/{0}.conf',

        # Fallback path (Linux, FreeBSD...)
        None: '~/.{0}/{0}.conf',
        }

    path = paths.get(platform.system(), paths[None])

    return os.path.expanduser(path.format(coin))


def rpcurl_from_config(coin, default=None, config_path=None):
    """Returns RPC URL loaded from bitcoin.conf-like configuration of desired
    currency"""

    config_path = config_path or coin_config_path(coin)
    cookie_path = os.path.join(os.path.dirname(config_path), '.cookie')

    credentials = ''

    try:
        with open(config_path) as fd:
            conf = parse_bitcoin_conf(fd)
            if 'rpcpassword' in conf:
                # Password authentication
                credentials = '{rpcuser}:{rpcpassword}'.format(**conf)
            elif os.path.exists(cookie_path):
                # Cookie authentication
                with open(cookie_path) as cfd:
                    credentials = cfd.read().decode('utf-8').strip() \
                        .replace('/', '%2F')
            else:
                return default

            return 'http://{0}@127.0.0.1:{1}/' \
                .format(credentials, conf.get('rpcport', 8336))
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception(exc)
        return default
