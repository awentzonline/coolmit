import os
import subprocess
import sys

from .cpu import CoolmitCPUMiner as BestCoolmitMiner


def coolmit(root_path, prefix, message, chunk_size=100000, num_workers=5):
    """Makes your commit cooler."""
    miner = BestCoolmitMiner(root_path)
    coolmit_msg, coolmit_salt, coolmit_hash = miner.mine(
        prefix, message, chunk_size=chunk_size, num_workers=num_workers)
    coolmit_msg += coolmit_salt
    # HACK: I'd rather use the --stdin option but
    # it's not quite working so I dump it to a file.
    fname = os.path.join(root_path, ".coolmit")
    with open(fname, "wb") as outfile:
        outfile.write(coolmit_msg)
    subprocess.call(
        "git hash-object -t commit -w {}".format(fname),
        shell=True, cwd=root_path
    )
    subprocess.call(
        "git reset --hard \"{}\"".format(coolmit_hash),
        shell=True, cwd=root_path
    )
    os.unlink(fname)


def run_commandline():
    # TODO: Make this more like `git commit` but cooler.
    try:
        prefix = sys.argv[1]
        message = sys.argv[2]
    except IndexError:
        print('syntax: coolmit prefix "commit message"')
    else:
        print("Mining for commit hash with prefix {}".format(prefix))
        coolmit(os.getcwd(), prefix, message)
