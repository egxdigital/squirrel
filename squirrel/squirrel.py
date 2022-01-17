"""Squirrel

This module contains the main function definitions for the Squirrel program.
Squirrel assumes that the function or class to be stashed can be found in 
relation to the current working directory.

Examples
    squirrel [stash, scope] [-f, -c] package.module.[function, class]
    squirrel [stash, scope] [-f, -c] module.[function, class]
    squirrel [stash, scope] [-f, -c] [function, class]
    
    squirrel stash -f FUNCTION
    squirrel stash -c CLASS
    squirrel stash FUNCTION
    squirrel stash FUNCTION -v VERSION-NAME
    squirrel stash FUNCTION -v NEW-VERSION-NAME
"""
import os
import sys
import ast
import json
import argparse
from pprint import pprint
from datetime import datetime
from pathlib import Path, PurePath
from pymongo import MongoClient
from squirrel.config import *
from squirrel.helpers import *
from squirrel.queries import *
from squirrel.schemas import *
from squirrel.fragments import squirrely


class Squirrel():
    def __init__(self, parser, options: dict):    
        self.valid_commands = [
            'scope',
            'stash'
        ]
        self.switches = [
            'class'
            'directory',
            'function',
            'module',
        ]

        self.parser = parser
        self.options = options
        #pprint(options)
        self.command = self.options['commands'][0]
        self.directory = self.options['directory']
        self.database = self.options['database']
        self.version = self.options['version']
        self.functions = []
        self.classes = []
        self.payloads = []

        self.validate_command()
        self.set_directory()
        self.set_database()
        self.set_version()
        self.parse_and_clean_arguments()
        self.make_payloads('function')
        self.make_payloads('class')

        for payload in self.payloads:
            self.evaluate_payload(payload)
            
    def __str__(self):
        return (
            '\n'
            'command: {}\n'
            'directory: {}\n'
            'functions: {}\n'
            'classes: {}\n'
            'payloads: {}\n'
        ).format(
            self.command,
            self.directory,
            self.functions,
            self.classes,
            dict_list_to_str(self.payloads))
    
    def validate_command(self):
        if self.command not in self.valid_commands:
            self.parser.error(ERROR.bad_command)
    
    def set_directory(self):
        if self.options['directory'] is None:
            self.directory = Path.cwd()
    
    def set_database(self):
        if self.options['database'] is None:
            self.database = DB_NAME
    
    def set_version(self):
        if self.options['version'] is None:
            self.version = 'default'
    
    def parse_and_clean_arguments(self):
        cmds = self.options['commands']
        cla = self.options['classes']
        dr = self.options['directory']
        fun = self.options['functions']
        ver = self.options['version']
        cmd_len = len(cmds)

        if cla is None and fun is None and cmd_len == 1:
            self.parser.error(f"{ERROR.no_arg} to {self.command}")

        if cla is None and fun is None and cmd_len == 2:
            cmd_arg = cmds[1]
            if ',' in cmd_arg:
                self.parser.error(ERROR.no_commas)
            # args are read as functions by default
            self.functions += [cmd_arg]
        
        if cla is None and fun is None and cmd_len > 2:
            self.functions = self.options['commands'][1:]

        if fun is not None:            
            for _ in self.options['functions']:
                if ',' in _:
                    self.parser.error(ERROR.no_commas)
            self.functions += self.options['functions']
            
        if cla is not None:            
            for _ in self.options['classes']:
                if ',' in _:
                    self.parser.error(ERROR.no_commas)            
            self.classes += self.options['classes']

    def make_payloads(self, obj_type: str):
        payload = OrderedDict({
            'directory': self.directory,
            'type':obj_type,
            'package': None,
            'module': None
        })

        objects = {
            'function': self.functions,
            'class': self.classes
        }
        
        if objects[obj_type] == None:
            return
        
        for obj in objects[obj_type]:
            parts = return_argument_parts(obj, obj_type)
            unit = {**payload, **parts}
            self.payloads.append(unit)
    
    def evaluate_payload(self, payload: OrderedDict):
        citizens = {
            'function': self.find_function,
            'class': self.find_class
        }

        if payload['package'] is not None and payload['module'] is not None:
            message(get_current_func_name(), "package.module.function specified!")
            try:
                source_segment = citizens[payload['type']](
                    PurePath(payload['directory'], payload['package'], modulify(payload['module'])), payload[payload['type']])
            except Exception as e:
                self.parser.error(error(get_current_func_name(), f"{type(e)} {e}"))
            else:
                self.run_command(source_segment, payload)

        if payload['package'] is None and payload['module'] is not None:
            message(get_current_func_name(),"module.function specified!")
            try:
                m = self.search_packages_for_module(payload['directory'], payload['module'])
                source_segment = citizens[payload['type']](PurePath(payload['directory'], m), payload[payload['type']])
            except Exception as e:
                self.parser.error(error(get_current_func_name(), f"{type(e)} {e}"))
            else:
                self.run_command(source_segment, payload)

        if payload['package'] is None and payload['module'] is None:
            message(get_current_func_name(), "function specified!") 
            init_p = get_py_files(payload['directory'])
            init_d = get_valid_directories(payload['directory'])
            py_files = seek_py_files(init_p, init_d)

            result = None

            try:
                for fd in py_files:
                    code = citizens[payload['type']](fd, payload[payload['type']])
                    if code is not None:
                        message(get_current_func_name(),f"found segment at {str(fd)}!")
                        result = code
            except Exception as e:
                self.parser.error(error(get_current_func_name(), f"{type(e)} {e}", payload[payload['type']]))
            else:
                self.run_command(result, payload)

    def run_command(self, source: str, payload: OrderedDict):
        label = f"{self.command}ing {payload['type']}: {payload[payload['type']]}"
        if source is not None:
            self.result = source
            if self.command == 'scope':
                display_code(source, label)
            if self.command == 'stash':
                self.change_database(source, payload)
            return source
        print(f"{payload['type']} {payload[payload['type']]} not found!")
        return False

    def find_function(self, p: Path, func_name: str) -> str:
        """Find function source code by name in a Python file.

        Parameters
        ----------
        p : Path
            Python file to search.
        class_name : str
            Name of function definition.

        Returns
        -------
        str
            Source code for function definition.
        """
        try:
            module = return_file_content_as_string(p)
            code_segment = get_code_segment_from_file_contents(module, func_name)
        except Exception as e:
            parser.error(message(get_current_func_name(), e, func_name))
        else:
            return code_segment 

    def find_class(self, p: Path, class_name: str) -> str:
        """Find class source code by name in a Python file.

        Parameters
        ----------
        p : Path
            Python file to search.
        class_name : str
            Name of class definition.

        Returns
        -------
        str
            Source code for class definition.
        """
        try:
            source_code = return_file_content_as_string(p)
            code = get_code_segment_from_file_contents(
                source_code, class_name, citizen='class')
        except Exception as e:
            self.parser.error(error(get_current_func_name(), f"{type(e)} {e}", class_name))
        else:
            return code        

    def search_packages_for_module(self, dr: Path, mod: str) -> Path:
        """Search a directory for a module by name.

        Parameters
        ----------
        dr : Path
            Pathname of directory to search.
        mod : str
            Name of the module.

        Returns
        -------
        Path
            Pathname of module.
        """
        try:
            packages = self.search_packages(dr)
            
            if packages == []:
                msg = message('no valid Python packages found at', dr)
                sys.exit(msg)
                
            for pkg in packages:
                pkg_contents = [(_.name, _) for _ in pkg.iterdir()]
                lookup = dict(pkg_contents)
                result = lookup[modulify(mod)]
        except Exception as e:
            parser.error(message(get_current_func_name(), e, mod))
        else:
            return Path(result)

    def search_packages(self, dr: Path) -> List[Path]:
        """Search a directory for packages.

        Parameters
        ----------
        dr : Path
            Pathname of the directory to search.

        Returns
        -------
        List[Path]
            List of package pathnames.
        """
        try:
            packages = [_ for _ in Path(dr).iterdir() if Path(_).is_dir() and is_package(_)]
        except Exception as e:
            self.parser.error(error(get_current_func_name(), f"{type(e)} {e}"))
        else:
            return packages

    def scope_module(self, options: dict):
        """Display full text of module.

        Parameters
        ----------
        options : dict
            Arguments passed at command line.
        """
        try:
            dr = options.get('directory')
            pkg = options.get('package')
            mod = options.get('module')
        except Exception as e:
            parser.error(message(get_current_func_name(), e))
        else:
            print(f"scoping directory {dr} for module {mod}")
            if pkg is None:
                m = self.search_packages_for_module(dr, mod)
                display_code(Path(m).read_text())

            if pkg is not None:
                p = PurePath(dr, pkg, modulify(mod))
                display_code(Path(p).read_text())

    def scope_package(self, options: dict):
        """Display a directory tree in the terminal.

        Parameters
        ----------
        options : dict
            Arguments passed at the command line.
        """
        try:
            dr = options.get('directory')
            pkg = options.get('package')
        except Exception as e:
            self.parser.error(error(get_current_func_name(), f"{type(e)} {e}"))
        else:
            if is_package(Path(PurePath(dr, pkg))):
                tree(Path(PurePath(dr, pkg)))
                return
            else:
                self.parser.error(error(
                    get_current_func_name(), 'package not found', pkg))

    def change_database(self, source, payload):
        document = self.build_document(source, payload)
        target_collection = COLLECTIONS[document['type']]
        
        if not has_database(self.database):
            create_database(self.database, target_collection)
            it = insert_item(self.database, target_collection, document)
            return
        
        obj = {'name': document['name']}
        
        if has_database(self.database):
            item = get_item(
                self.database,
                target_collection,
                obj,
                **{'name': 1, 'type': 1, 'versions': 1}
            )

            if item is not None:
                exists = True
            if item is None:
                exists = False

            if not exists:
                insert_item(self.database, target_collection, document)
                return
            
            if exists:
                item = get_item(
                    self.database, 
                    target_collection,
                    obj, 
                    **{'name': 1, 'type': 1,'versions':1}
                )
                handle_code_change(
                    db_name=self.database,
                    col=target_collection,
                    incoming=document,
                    existing=item,
                    named=self.version
                )
                return            

    def build_document(self, source: str, payload: OrderedDict):     
        obj_type = payload['type']
        doc = document
        ver = version_instance

        doc['name'] = payload[obj_type]
        doc['type'] = obj_type
        
        ver['created'] = datetime.today().replace(microsecond=0)
        ver['version_name'] = self.version
        ver['docstring'] = get_docstring(source, payload[obj_type], obj_type)
        ver['source'] = source
        
        doc['versions'] += [ver]

        return doc


def main():
    global parser
    parser = argparse.ArgumentParser(
        prog='squirrel',
        fromfile_prefix_chars='@',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage='squirrel[stash, scope][-f, -c] package.module.[function, class]',
        description='Stash and retrieve Python code units',
        epilog=squirrely)

    # Add arguments here
    parser.add_argument('-p', '--packages',
                        action='store',
                        nargs='+',
                        type=str,
                        required=False,
                        help='squirrel scope -p [package.module., module.]function')

    parser.add_argument('-c', '--classes',
                           action='store',
                           nargs='+',
                           type=str,
                           required=False,
                           help='squirrel [stash, scope] -c [package.module., module.]class')

    parser.add_argument('-f', '--functions',
                           action='store',
                           nargs='+',
                           type=str,
                           required=False,
                           help='squirrel [stash, scope] -f [package.module., module.]function')

    parser.add_argument('-m', '--module',
                        action='store',
                        type=str,
                        required=False,
                        help='squirrel scope -m module')
    
    parser.add_argument('-d', '--directory',
                           action='store',
                           type=str,
                           required=False,
                           help='specify a directory')
    
    parser.add_argument('-s', '--database',
                        action='store',
                        type=str,
                        required=False,
                        help='specify a database')
    
    parser.add_argument('-v', '--version',
                        action='store',
                        type=str,
                        required=False,
                        help='specify code object version name')

    parser.add_argument('commands',
                           nargs='+',
                           help="squirrel stash -f function")

    args = parser.parse_args()

    options = vars(args)

    #pprint(options)

    squirrel = Squirrel(parser, options)
