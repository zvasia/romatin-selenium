SEARCH_URL = 'https://www3.wipo.int/madrid/monitor/en'
PAGE_SIZE = 100
MYSQL_CONFIG = {
    'user': 'root',
    'password': 'root',
    'port': '8889',
    'host': '127.0.0.1',
    'database': 'romarin',
    'raise_on_warnings': True,
}

try:
    from local_settings import *
except ImportError:
    pass
