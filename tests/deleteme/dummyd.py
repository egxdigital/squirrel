"""Module containing dummy code objects for testing the Squirrel program with.
"""

def dummyfunc(word: str):
    """I say things to you"""
    print(f'Hello {word}!')
    print ('How are you today?')
    return 0


class DummyClass():
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def __str__(self):
        return f"{self.a} + {self.b} + {self.c}"
