#!/usr/bin/env python3
# import sys

# import main


# def command_line(args: list[str]) -> None:
#     if len(args) < 1:
#         msg = f"Length of args should be at least 1, not {len(args)}"
#         raise ValueError(msg)
#     command_name = args[0]
#     if not hasattr(main, command_name):
#         msg = f"Unknown command {command_name}"
#         raise ValueError(msg)
#     getattr(main, command_name)(None, args=args[1:])


# command_line(sys.argv[1:])
