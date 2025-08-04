#!/usr/bin/env python3
import sys
from typing import List

import main


def command_line(args: List[str]) -> None:
    if len(args) < 1:
        raise ValueError(f'Length of args should be at least 1, not {len(args)}')
    command_name = args[0]
    if not hasattr(main, command_name):
        raise ValueError(f'Unknown command {command_name}')
    getattr(main, command_name)(None, args=args[1:])


command_line(sys.argv[1:])
