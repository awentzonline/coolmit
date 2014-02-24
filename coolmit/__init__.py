#!/usr/bin/env python

import base64
import hashlib
import os
import subprocess
import time
from multiprocessing import Pool


def check_hash_range(v):
    """The cool miner worker."""
    prefix, msg_template, start_i, end_i = v
    coolmit_msg, coolmit_hash = None, None
    for i in range(start_i, end_i):
        b64count = base64.b64encode(str(i)).replace("=", "")
        body = msg_template.format(b64count)
        msg = "commit {}\0{}".format(len(body), body)
        s = hashlib.sha1(msg.encode())
        commit_hash = s.hexdigest()
        if commit_hash[:len(prefix)] == prefix:
            coolmit_msg = body
            coolmit_hash = commit_hash
            break
    return coolmit_msg, coolmit_hash, i
            

def coolmit(prefix, message, chunk_size=50000, show_hps=True, num_workers=5):
    """Makes your commit cooler."""
    user_name = subprocess.check_output("git config user.name".split(" ")).strip()
    user_email = subprocess.check_output("git config user.email".split(" ")).strip()
    if not (user_email or user_name):
        raise Exception("You need to git config user.name and email")
    tree = subprocess.check_output(["git", "write-tree"]).strip()
    try:
        parent = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
    except:
        parent = ""
    timestamp = int(time.time())
    if parent:
        body = """tree {tree}
parent {parent}
author {name} <{email}> {timestamp} -0600
committer {name} <{email}> {timestamp} -0600

{message} {{}}""".format(
            tree=tree, parent=parent, timestamp=timestamp, message=message,
            name=user_name, email=user_email
        )
    else: # no parent commit
        body = """tree {tree}
author {name} <{email}> {timestamp} -0600
committer {name} <{email}> {timestamp} -0600

{message} {{}}""".format(
            tree=tree, timestamp=timestamp, message=message,
            name=user_name, email=user_email
        )
    i0 = 0
    pool = Pool(num_workers)
    coolmit_msg, coolmit_hash = None, None
    while coolmit_msg is None:
        start_t = time.time()
        params = []
        for w in range(num_workers):
            i1 = i0 + chunk_size
            params.append((prefix, body, i0, i1))
            i0 = i1
        results = pool.map(check_hash_range, params)
        if show_hps:
            now = time.time()
            dt = now - start_t
            num_processed = chunk_size * num_workers
            hps = num_processed / dt
            print("{} hps".format(hps))
        # check for successful hash with lowest value 
        lowest_i = None
        for msg, msg_hash, i in results:
            if msg:
                if lowest_i is None or lowest_i > i:
                    coolmit_msg = msg
                    coolmit_hash = msg_hash
                    lowest_i = i
    # HACK: I'd rather use the --stdin option but
    # it's not quite working so I dump it to a file.
    fname = ".coolmit"
    with open(fname, "wb") as outfile:
         outfile.write(coolmit_msg)
    os.system("git hash-object -t commit -w {}".format(fname))
    os.system('git reset --hard "{}"'.format(coolmit_hash))
    os.unlink(fname)


def run_commandline():
    import sys
    try: # TODO: optparse
        prefix = sys.argv[1]
        message = sys.argv[2]
    except IndexError:
        print('syntax: coolmit prefix "commit message"')
    else:
        print("Mining for commit hash with prefix {}".format(prefix))
        coolmit(prefix, message)
