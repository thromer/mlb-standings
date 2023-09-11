#!/usr/bin/env python3
import sys


def main(args):
    year = int(args[0])
    # If year is already in toc, return
    # Make a copy of the newest row in toc, staying in the same folder (can a cloud function do that?)
    # # # OOG To do stuff in drive, we really should be doing proper OAuth and having the GCF service
    # account impersonate tromer@gmail.com (with a boatload of permissions most likely)
    # Rename it
    # Clear out al_uploaded and nl_uploaded
    # Add it to toc
    pass

main(sys.argv[1:])