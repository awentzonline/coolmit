import os
import sys

from .base import CoolmitMiner


def coolmit(prefix, message, chunk_size=50000, num_workers=5):
    """Makes your commit cooler."""
    miner = CoolmitMiner()
    coolmit_msg, coolmit_salt, coolmit_hash = miner.mine(prefix, message, chunk_size=chunk_size, num_workers=num_workers)
    coolmit_msg += coolmit_salt
    # HACK: I'd rather use the --stdin option but
    # it's not quite working so I dump it to a file.
    fname = ".coolmit"
    with open(fname, "wb") as outfile:
         outfile.write(coolmit_msg)
    os.system("git hash-object -t commit -w {}".format(fname))
    os.system('git reset --hard "{}"'.format(coolmit_hash))
    os.unlink(fname)


def run_commandline():
    try: # TODO: optparse
        prefix = sys.argv[1]
        message = sys.argv[2]
    except IndexError:
        print('syntax: coolmit prefix "commit message"')
    else:
        print("Mining for commit hash with prefix {}".format(prefix))
        coolmit(prefix, message)
