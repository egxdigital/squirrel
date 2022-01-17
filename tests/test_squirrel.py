"""Test Squirrel

This module contains the test case for the Squirrel program.

Examples
    python -m unittest tests.test_squirrel
"""
import unittest
from squirrel.helpers import *
from squirrel.squirrel import *
from squirrel.queries import *
from squirrel.config import *


class SquirrelTest(unittest.TestCase):
    def setUp(self):
        print(get_current_func_name(1))
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
        
        self.parser = parser

        def run_command(command: argparse.Namespace):
            args = command
            options = vars(args)
            squirrel = Squirrel(self.parser, options)
            return squirrel
        
        self.run_command = run_command

        self.command1 = argparse.Namespace(
            directory=TESTS,
            packages=None,
            classes=None,
            functions=None,
            module=None,
            version=None,
            database=TEST_DB,
            commands=['stash', 'deleteme.dummya.dummyfunc']
        )
        self.command2 = argparse.Namespace(
            directory=TESTS,
            packages=None,
            classes=None,
            functions=None,
            module=None,
            version=None,
            database=TEST_DB,
            commands=['stash', 'deleteme.dummyb.dummyfunc']
        )
        self.command3 = argparse.Namespace(
            directory=TESTS,
            packages=None,
            classes=None,
            functions=None,
            module=None,
            version=None,
            database=TEST_DB,
            commands=['stash', 'deleteme.dummyc.dummyfunc']
        )
        self.command4 = argparse.Namespace(
            directory=TESTS,
            packages=None,
            classes=None,
            functions=None,
            module=None,
            version='dummyfunc-say-things',
            database=TEST_DB,
            commands=['stash', 'deleteme.dummyd.dummyfunc']
        )
 
    def tearDown(self):
       self.delete_test_db()

    def delete_test_db(self):
        print(get_current_func_name(1))
        client = MongoClient()
        client.drop_database(TEST_DB)
        new_dbs = client.list_database_names()
        self.assertNotIn(TEST_DB, new_dbs)
    
    def check_state_of_test_db(self):
        result = get_all_items_in_collection(TEST_DB, 'functions')
        pprint(result)
        return result
    
    def test_squirrel_stash(self):
        print(get_current_func_name(1))
        print("Initial state:")
        self.check_state_of_test_db()
        print("running command 1: new unnamed stash")
        squirrel = self.run_command(self.command1)
        #print("State after command 1:")
        #self.check_state_of_test_db()
        stashed = get_item(TEST_DB, COLLECTIONS['function'], {
                           "name": "dummyfunc"})
        self.assertIsNotNone(stashed)

        print("running command 2: unnamed version change in docstring")
        squirrel = self.run_command(self.command2)
        #print("State after command 2:")
        #self.check_state_of_test_db()
        dummyfunc = get_item(
            TEST_DB,
            'functions',
            {"name": "dummyfunc"},
            **{"versions": 1}
        )
        
        versions = dummyfunc['versions']
        
        for version in versions:
            if version['version_name'] == 'default':
                self.assertEqual(version['docstring'], "I do things")

        src = (
            "def dummyfunc(word: str):\n"
            "    \"\"\"I do things\"\"\"\n"
            "    print(f'Hello {word}!')\n"
            "    return 0"
        )

        print("running command 3: unnamed version change in source")
        squirrel = self.run_command(self.command3)
        #print("State after command 3:")
        #self.check_state_of_test_db()

        updated_source = get_version_field(
            TEST_DB, 'source', 'function', 'dummyfunc', 'default')
        self.assertEqual(updated_source, src)

        print("running command 4: new named version")
        squirrel = self.run_command(self.command4)
        print("State after command 4:")        
        state = self.check_state_of_test_db()
        self.assertEqual(len(state), 1)
        ver_names = [ver['version_name'] for ver in state[0]['versions']]
        self.assertIn("dummyfunc-say-things", ver_names)

if __name__ == '__main__':
    unittest.main()