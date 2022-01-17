# squirrel

> A way to stash and retrieve code units.


## TODO

- Make first commit
    - Write tests for squirrel commands
        - scope
    - Write tests for helpers
        - tree()
        - display_code()
    - Write tests for queries
        - insert_many_items()
        - get_all_items_in_collection()
        - get_version_field()
- Add new commands
    - leaf
        - 'scope' database for named code object
    - plant
        - insert the code object in a target file
- Learn Pytest

## Installation

Change current directory to download location and run.

Adjust values DB_NAME and TEST_DB as needed in squirrel/config.py.

```bash
pip install .
```

Or install from VCS using pip

```bash
python3 -m pip install git+https://github.com/egxdigital/pyscaffold.git#egg=Squirrel
```

## Usage

Navigate to directory where packages are located or use the --directory flag to specify it from any working directory.


```bash
squirrel scope -f <FUNCTION> [-m <MODULE> -p <PACKAGE> -d <DIRECTORY>]
squirrel stash -f <FUNCTION> [-m <MODULE> -p <PACKAGE> -d <DIRECTORY>]

squirrel <COMMAND> <function>
squirrel <COMMAND> -f <package>.<module>.<function>
squirrel <COMMAND> -f <module>.<function>
squirrel <COMMAND> -c <package>.<module>.<class>
squirrel <COMMAND> -c <module>.<function>
squirrel <COMMAND> -f <package>.<module>.<function>
```

## What I learned
- MongoDB Queries in Python.
- How to update a nested Array in a MongoDB document.
- Capture output to stdout programmatically using Python’s io.StringIO class method.
