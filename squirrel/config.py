from pygments.formatters.terminal256 import Terminal256Formatter
from pathlib import Path, PurePath


ROOT = Path(__file__).resolve().parent.parent
PKG = Path(__file__).resolve().parent
DATA = Path(PurePath(ROOT, 'data'))
TESTS = Path(PurePath(ROOT, 'tests'))
TEST_DATA = Path(PurePath(TESTS, 'data'))
TEST_DELETEME = Path(PurePath(TESTS, 'deleteme'))

TEST_DB = 'deleteme_code_library'
DB_NAME = 'python_code_library'

COLLECTIONS = {
    'function': 'functions',
    'class': 'classes'
}

avoid_directories = [
    'bin',
    'data',
    'docs',
    'env',
    '__pycache__',
    '.pytest_cache'
]

TERM_FORMATTER = Terminal256Formatter(style='monokai')

class ERROR:
    bad_command = 'invalid command!'
    bad_directory = 'invalid destination directory!'
    bad_qual_syntax = 'bad qualification syntax'
    bad_argument = "invalid argument. try 'package.module.function' or 'module.function' or 'function'"
    no_arg = 'no argument provided'
    no_commas = 'invalid arguments. comma separated args not allowed'

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
