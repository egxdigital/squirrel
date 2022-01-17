"""Squirrel Test Helpers

This module contains the test case for the Squirrel helpers module.

Examples
    python -m unittest tests.test_helpers
"""
import os
import io
import unittest
from pprint import pprint
from pathlib import Path, PurePath, PosixPath
from collections import OrderedDict

from pygments import highlight
from pygments.lexers import PythonLexer

from squirrel.helpers import *

class SquirrelHelpersTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.function = OrderedDict({
            "package": None,
            "module": None,
            "function": "function"
        })

        self.module_function = OrderedDict({
            "package": None,
            "module": "module",
            "function": "function"
        })

        self.package_module_function = OrderedDict({
            "package": "package",
            "module": "module",
            "function": "function"
        })

        self.dummy_class_display = (
            "\nDummyClass:\n"
            "class DummyClass():\n"
            "\t\"\"\"A class for testing scope\"\"\"\n"
            "\tpass\n"
        )
       
        self.dummy_class = (
            "class DummyClass():\n"
            "\t\"\"\"A class for testing scope\"\"\"\n"
            "\tpass"
        )

        self.DummyClassPy = Path(
            PurePath(Path().cwd(), 'tests', 'DummyClass.py'))
        self.DummyClassPy.touch()
        #print(self.DummyClassPy, self.DummyClassPy.is_file())
        self.DummyClassPy.write_text(self.dummy_class)

        self.valid_packages = [
            Path('/home/engineer/source/python/projects/Squirrel/tests/'),
            Path('/home/engineer/source/python/projects/Squirrel/squirrel/')
        ]

        self.contents = [
            Path('/home/engineer/source/python/projects/Squirrel/setup.py'),
            self.DummyClassPy,
            Path('/home/engineer/source/python/projects/Squirrel/tests/deleteme/__init__.py'),
            Path(
                '/home/engineer/source/python/projects/Squirrel/tests/deleteme/dummya.py'),
            Path(
                '/home/engineer/source/python/projects/Squirrel/tests/deleteme/dummyb.py'),
            Path(
                '/home/engineer/source/python/projects/Squirrel/tests/deleteme/dummyc.py'),
            Path(
                '/home/engineer/source/python/projects/Squirrel/tests/deleteme/dummyd.py'),
            Path('/home/engineer/source/python/projects/Squirrel/tests/test_squirrel.py'),
            Path('/home/engineer/source/python/projects/Squirrel/tests/test_helpers.py'),
            Path('/home/engineer/source/python/projects/Squirrel/tests/test_queries.py'),
            Path('/home/engineer/source/python/projects/Squirrel/squirrel/helpers.py'),
            Path('/home/engineer/source/python/projects/Squirrel/squirrel/__main__.py'),
            Path('/home/engineer/source/python/projects/Squirrel/squirrel/fragments.py'),
            Path('/home/engineer/source/python/projects/Squirrel/squirrel/squirrel.py'),
            Path('/home/engineer/source/python/projects/Squirrel/squirrel/__init__.py'),
            Path('/home/engineer/source/python/projects/Squirrel/squirrel/schemas.py'),
            Path('/home/engineer/source/python/projects/Squirrel/squirrel/queries.py'),
            Path('/home/engineer/source/python/projects/Squirrel/squirrel/config.py')
        ]

    def tearDown(self):
        if self.DummyClassPy.is_file():
            os.remove(self.DummyClassPy)
    
    def test_sort_list_of_objects_by(self):
        pass
    
    def test_error(self):
        pass
    
    def test_plural(self):
        cases = {
            'ass':'asses',
            'grass': 'grasses',
            'lass': 'lasses',
            'mast': 'masts',
            'function': 'functions',
            'class': 'classes'
        }

        for sing, plu in cases.items():
            self.assertEqual(plural(sing), plu)

    def test_dict_list_to_str(self):
        a = [
            {'name': 'Mark', 'age': 24, 'gender': 'M'},
            {'name': 'Petr', 'age': 32, 'gender': 'M'},
            {'name': 'Sandra', 'age': 22, 'gender': 'F'}
        ]

        x = (
            '\n'
            '    name: Mark\n'
            '    age: 24\n'
            '    gender: M\n'
            '\n'
            '    name: Petr\n'
            '    age: 32\n'
            '    gender: M\n'
            '\n'
            '    name: Sandra\n'
            '    age: 22\n'
            '    gender: F\n'
        )

        res = dict_list_to_str(a)
        self.assertEqual(dict_list_to_str(a), x)
    
    def test_replace_last_item(self):
        a = ['command', 'comma,separated,arguments']
        x = ['command', 'comma','separated','arguments']
        self.assertEqual(replace_last_item(
            a, ['comma', 'separated', 'arguments']), x)
        self.assertEqual(replace_last_item(x, None), x)
    
    def test_split_commas(self):
        a = 'helpers.list_hist,queries.insert_item,squirrel.squirrel.find_function'
        b = 'helpers.list.hist'
        c = None
        x = [
            'helpers.list_hist',
            'queries.insert_item',
            'squirrel.squirrel.find_function'
        ]
        self.assertEqual(split_commas(a), x)
        self.assertEqual(split_commas(b), [b])
        self.assertEqual(split_commas(c), None)
  
    def test_get_docstring(self):
        pass
    
    def test_filter_dict(self):
        a = filter_dict(self.function, lambda elem : elem[0] not in ['module', 'package'])
        b = filter_dict(self.module_function, lambda elem: elem[0] not in [
                        'package'])
        self.assertEqual(a, {'function': 'function'})
        self.assertEqual(b, {'module': 'module', 'function': 'function'})

    def test_message(self):
        cases = OrderedDict({
            ("grandparent", "parent"): "grandparent: parent",
            ("grandparent", "parent", "child"): "grandparent: parent: child",
            ("grandparent", "parent", "child", "grandchild"): "grandparent: parent: child: grandchild",
        })
        for no, case in cases.items():
            self.assertEqual(message(*no), case)
        self.assertEqual(message("grandparent"), "grandparent")
    
    def test_current_func_name(self):
        def enclose():
            return get_current_func_name()

        self.assertEqual(enclose(), 'enclose')
        self.assertEqual(get_current_func_name(), 'test_current_func_name')    
      
    def test_tree(self):
        pass
    
    def test_get_valid_directories(self):
        curr = Path.cwd()
        self.assertEqual(get_valid_directories(curr), self.valid_packages)
    
    def test_get_py_files(self):
        dir = Path().cwd()
        res = get_py_files(dir)       
        self.assertEqual(res, self.contents[:1])
    
    def test_seek_py_files(self):
        dir = Path().cwd()
        p = get_py_files(dir)
        d = get_valid_directories(dir)
        res = seek_py_files(p, d)
        self.assertCountEqual(res, self.contents)
    
    def test_return_colon(self):
        self.assertEqual(return_colon(''), '')
        self.assertEqual(return_colon('notempty'), ':')

    def test_display_code(self):
        cases = OrderedDict({
            ("test", "string"): highlight("\nstring:\ntest\n", PythonLexer(), TERM_FORMATTER),
            (self.dummy_class, "DummyClass"): self.dummy_class_display
        })
        for no, case in cases.items():
            capturedOutput = io.StringIO()
            sys.stdout = capturedOutput
            display_code(*no)
            sys.stdout = sys.__stdout__
            #self.assertEqual(capturedOutput.getvalue(), case)
            pass

    def test_display(self):
        cases = OrderedDict({
            ("test", "string"): "'\\nstring:\\ntest'\n",
            ("a longer string with spaces", "statement"): "'\\nstatement:\\na longer string with spaces'\n",
        })
        for no, case in cases.items():
            capturedOutput = io.StringIO()
            sys.stdout = capturedOutput
            display(*no)
            sys.stdout = sys.__stdout__
            self.assertEqual(capturedOutput.getvalue(), case)
    
    def test_modulify(self):
        self.assertEqual(modulify('mod'), 'mod.py')
        self.assertEqual(modulify('  mod'), 'mod.py')
        self.assertEqual(modulify('__init__'), '__init__.py')
     
    def test_get_code_segment_from_file_contents(self):
        contents = self.DummyClassPy.read_text()
        self.assertEqual(get_code_segment_from_file_contents(contents, 'DummyClass', 'class'), self.dummy_class)

    def test_return_file_content_as_string(self):
        self.assertEqual(return_file_content_as_string(self.DummyClassPy), self.dummy_class)
    
    def test_is_package(self):
        pkg = PurePath(Path.cwd(), 'squirrel')
        not_pkg = PurePath(Path.cwd(), 'bin')
        self.assertTrue(is_package(pkg))
        self.assertFalse(is_package(not_pkg))

    def test_return_valid_containing_file(self):
        d = OrderedDict({'package':'pyscaffold', 'module': 'tests', 'function': 'main'})
        p = return_valid_containing_file(Path('/home/engineer/source/python/projects/Pyscaffold'), d)
        self.assertEqual(p, Path('/home/engineer/source/python/projects/Pyscaffold/pyscaffold/tests'))

    def test_list_hist(self):
        cases = [
            [0, 0, 0], # valid
            [0, 0, 1], # valid
            [0, 1, 0], # valid
            [0, 1, 1], # not valid
            [1, 0, 0], # valid
            [1, 0, 1], # not valid
            [1, 1, 0], # not valid
            [1, 1, 1]  # not valid
        ]

        self.assertEqual(list_hist(cases[0]), {0: 3})
        self.assertEqual(list_hist(cases[1]), {0: 2, 1: 1})
        self.assertEqual(list_hist(cases[2]), {0: 2, 1: 1})
        self.assertEqual(list_hist(cases[3]), {0: 1, 1: 2})
        self.assertEqual(list_hist(cases[4]), {0: 2, 1: 1})
        self.assertEqual(list_hist(cases[5]), {0: 1, 1: 2})
        self.assertEqual(list_hist(cases[6]), {0: 1, 1: 2})
        self.assertEqual(list_hist(cases[7]), {1: 3})

    def test_return_argument_parts(self):
        cases = [
            'function',
            'module.function',
            'module/function',
            'module+function',
            'package.module.function',
            'package/module/function',
            'package+module+function'
        ]

        bad_cases = [
            'module.',
            'package.module.',
            'package.module.function.',
            'package.module.function...',
            'package/module.function',
            'package.module/function',
            'package+module.function',
            'package.module+function',
            'package/module+function',
            'package+module/function',
            'package.module+function.module..'
        ]

        module_named_function = OrderedDict({
            "package": None,
            "module": "function",
            "function": None
        })

        package_module = OrderedDict({
            "package": "module",
            "module": "function",
            "function": None
        })

        a = return_argument_parts(cases[0], 'function')
        b = return_argument_parts(cases[1], 'function')
        c = return_argument_parts(cases[2], 'function')
        d = return_argument_parts(cases[3], 'function')
        e = return_argument_parts(cases[4], 'function')
        f = return_argument_parts(cases[5], 'function')
        g = return_argument_parts(cases[6], 'function')
        #h = return_argument_parts(cases[0], 'module')
        i = return_argument_parts(cases[1], 'module')
    
        self.assertEqual(a, self.function)
        self.assertEqual(b, self.module_function)
        self.assertEqual(c, self.module_function)
        self.assertEqual(d, self.module_function)
        self.assertEqual(e, self.package_module_function)
        self.assertEqual(f, self.package_module_function)
        self.assertEqual(g, self.package_module_function)
        #self.assertEqual(h, module_named_function)
        self.assertEqual(i, package_module)

        for case in bad_cases:
            res = return_argument_parts(case, 'module')
            self.assertEqual(res, None)
    

if __name__ == '__main__':
   unittest.main()
