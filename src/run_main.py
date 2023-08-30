#!/usr/bin/env python3
from typing import List

import main
import sys


def command_line(args: List[str]) -> None:
    if len(args) != 1:
        raise ValueError(f'Length of args should be 1, not {len(args)}')
    command_name = args[0]
    if not hasattr(main, command_name):
        raise ValueError(f'Unknown command {command_name}')
    getattr(main, command_name)(None)


command_line(sys.argv[1:])
