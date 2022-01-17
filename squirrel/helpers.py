"""Squirrel Helpers

This module contains the helper function definitions for the Squirrel program.

Examples
    python -m unittest tests.test_helpers
"""
import sys
import ast
from pprint import pprint
from pathlib import Path, PurePath
from typing import Any, List, Union
from collections import OrderedDict

from pygments import highlight
from pygments.lexers import PythonLexer

from squirrel.config import *


def sort_list_of_objects_by(criteria: str, lt: List[dict], ascending: bool=True) -> List[dict]:
    return sorted(lt, key=lambda i: i[criteria], reverse=ascending)


def error(cmd: str, msg: str, *details):
    message = f"{colors.BOLD}{cmd}{colors.ENDC}: {colors.FAIL}{msg}{colors.ENDC}"
    for detail in details:
        if detail == details[-1]:
            message += f": {colors.WARNING}{detail}{colors.ENDC}"
            return message
        if isinstance(detail, float):
            detail = "{:.1f}".format(detail)
        message += f": {colors.WARNING}{detail}{colors.ENDC}"
    return message


def plural(st: str) -> str:
    """Pluralise most strings.

    Parameters
    ----------
    st : str
        string representing any word ending in ss or not

    Returns
    -------
    str
        plural form of string st
    """
    if st[-2:] not in ['ss']:
        return f'{st}s'
    return f'{st}es'


def dict_list_to_str(lt: List[dict]) -> str:
    res = ""
    for dt in lt:
        if dt == lt[0]:
            res += '\n'
        for k, v in dt.items():
            res += f'    {k}: {v}\n'
        if dt != lt[-1]:
            res += '\n'
    return res


def replace_last_item(inp: List, repl: List):
    if repl is None:
        return inp
    return inp[:-1] + repl


def split_commas(st: str) -> List[str]:
    if st is None:
        return None
    return st.split(',')


def get_docstring(code_segment: str, obj_name: str, obj_type: str):
    if code_segment == None:
        return None

    citizens = {
        'function': ast.FunctionDef,
        'class': ast.ClassDef,
    }

    ast_object = ast.parse(code_segment)

    try:
        nodes = [node for node in ast_object.body if isinstance(
            node, citizens[obj_type])]
        lookup = {node.name: node for node in nodes}
        target_node = lookup[obj_name]
    except Exception as e:
        message(get_current_func_name(), e)
        return None
    else:
        return ast.get_docstring(target_node)


def filter_dict(dt: dict, callback):
    new = dict()

    for key, value in dt.items():
        if callback((key, value)):
            new[key] = value

    return new


def message(*args):
    res = ""
    for arg in args:
        if arg == args[-1]:
            res += f"{arg}"
            return res
        res += f"{arg}: "
    return res


def get_current_func_name(up=1):
    return sys._getframe(up).f_code.co_name


def tree(directory: Path):
    """Thanks Jan Bodnar for providing this solution @ https://zetcode.com/python/pathlib/"""
    res = f'+ {directory}/\n'

    def isDeep(depth):
        if depth > 1:
            return '|'
        return ''

    for path in sorted(Path(directory).rglob('*')):
        depth = len(path.relative_to(directory).parts)
        # print(depth)
        spacer = '    ' * depth

        # print(f'{spacer}+ {path.name}')
        if path.is_file():
            lin = f'{spacer}{isDeep(depth)} {path.name}\n'
            res += lin
            #print(lin)
        else:
            lin = f'{spacer}{isDeep(depth)} {path.name}/\n'
            res += lin
            #print(lin)
    
    return res


def get_valid_directories(d: Path) -> List[Path]:
    return [_ for _ in Path(d).iterdir() if Path(_).is_dir()
            and Path(_).name not in avoid_directories and not Path(_).name.endswith('egg-info')]


def get_py_files(d: Path) -> List[Path]:
    return [_ for _ in Path(d).iterdir() if Path(_).is_file()
            and Path(_).suffix in ['.py']]


def seek_py_files(py_files: List[Union[Path, str]], dirs: List[Union[Path, str]]):
    if len(dirs) == 0:
        return list(py_files)

    py_files += get_py_files(dirs[0])
    dirs = dirs[1:] + get_valid_directories(dirs[0])

    return seek_py_files(py_files, dirs)


def return_colon(lbl):
    if lbl == '':
        return lbl
    return ':'


def display_code(code: str, label: str = ''):
    header = f"{label}{return_colon(label)}"
    body = code
    print(f"\n{header}")
    print(highlight(body, PythonLexer(), TERM_FORMATTER))


def display(a: Any, label: str = ''):
    header = f"{label}{return_colon(label)}"
    body = a
    res = f"\n{header}\n{body}"
    pprint(res)


def modulify(st: str) -> str:
    return f"{st.strip()}.py"


def get_code_segment_from_file_contents(contents: str, name: str, citizen: str = 'function') -> str:
    citizens = {
        'function': ast.FunctionDef,
        'class': ast.ClassDef,
    }

    module = ast.parse(contents)

    try:
        nodes = [node for node in module.body if isinstance(
            node, citizens[citizen])]
        lookup = {node.name: node for node in nodes}
        target_node = lookup[name]
    except Exception as e:
        message(get_current_func_name(), e)
        return None
    else:
        #print('NODE\n', target_node)
        return ast.get_source_segment(contents, target_node, padded=True)


def return_file_content_as_string(p: Path) -> str:
    try:
        return Path(p).read_text()
    except Exception as e:
        print(e)
        sys.exit()


def is_package(p: Path) -> bool:
    return '__init__.py' in [_.name for _ in Path(p).iterdir()]


def return_valid_containing_file(base: Path, dt: OrderedDict) -> Path:
    """Takes an OrderedDict with three keys and base directory and returns a valid pathname
    to the module"""
    try:
        return Path(PurePath(base, *list(dt.values())[:2]))
    except Exception as e:
        print(e)
        return None


def list_hist(lt: list) -> dict:
    """Returns a histogram for a given list"""
    d = dict()
    for _ in lt:
        if _ in d.keys():
            d[_] += 1
        else:
            d[_] = 1
    return d


def return_argument_parts(st: str, obj: str) -> OrderedDict:
    """Takes a string and returns a dictionary containing up to three values.
    Returns None if an invalid string is passed"""

    result = OrderedDict({
        "package": '',
        "module": '',
        obj: ''
    })

    qualifiers = {
        '.': 0,
        '/': 0,
        '+': 0
    }

    for ch in st:
        if ch in qualifiers.keys():
            qualifiers[ch] += 1

    if set(list(qualifiers.values())) == {0}:
        result[obj] = st
        for _ in result.keys():
            if obj != _:
                result[_] = None
        return result

    zeroes = list_hist(list(qualifiers.values()))[0]

    if zeroes == 1 or zeroes == 0:
        print(
            f"{ERROR.bad_qual_syntax}! use only {' or '.join(list(qualifiers.keys()))}")
        return None

    for k, v in qualifiers.items():
        if v > 2 or '' in st.split(k):
            print(f"{ERROR.bad_argument} NOT '{st}'")
            return None

        if v == 1 and len(st.split(k)) == 2 and obj != 'module':
            result["package"] = None
            result["module"] = st.split(k)[0]
            result[obj] = st.split(k)[1]
            return result

        if v == 1 and len(st.split(k)) == 2 and obj == 'module':
            result["package"] = st.split(k)[0]
            result["module"] = st.split(k)[1]
            result[st.split(k)[1]] = None
            return result

        if v == 2 and len(st.split(k)) == 3:
            result["package"] = st.split(k)[0]
            result["module"] = st.split(k)[1]
            result[obj] = st.split(k)[2]
            return result
