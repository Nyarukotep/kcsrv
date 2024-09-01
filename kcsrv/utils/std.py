__all__ = ['logdict']
import sys
import logging

def logdict(d: dict, indent: int = 1):
    result = ""
    for key, value in d.items():
        if isinstance(value, dict):
            result += '  ' * indent + f'{key}:\n'
            result += logdict(value, indent + 1)
        else:
            result += '  ' * indent + f'{key}: '
            result += f'{value}\n'
    return result
