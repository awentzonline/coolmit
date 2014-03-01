#!/usr/bin/env python

import base64
import hashlib
import os
import string
import subprocess
import time
from multiprocessing import Pool


def coolmit_probe_worker(args):
    """Coolmit worker which helps find that cool commit hash you crave."""
    prefix, msg_template, charset, worker_id, num_workers, start_offset, probe_length, work_chunk_size = args
    hf = hashlib.sha1
    len_charset = len(charset)
    for i in xrange(start_offset + worker_id, start_offset + work_chunk_size, num_workers):
        salt = ''
        remaining = i
        for j in xrange(probe_length):
            salt += charset[remaining % len_charset]
            remaining = remaining // len_charset
        m = msg_template + salt
        h = hf(m).hexdigest()
        if h.startswith(prefix):
            return salt, h


class CoolmitMiner(object):
    """Finds you a cool comit."""
    def __init__(self, charset=None):
        if charset is None:
            charset = string.ascii_letters
        self.charset = charset

    def prepare_message(self, message):
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

{message} """.format(
                tree=tree, parent=parent, timestamp=timestamp, message=message,
                name=user_name, email=user_email
            )
        else: # no parent commit
            body = """tree {tree}
author {name} <{email}> {timestamp} -0600
committer {name} <{email}> {timestamp} -0600

{message} """.format(
                tree=tree, timestamp=timestamp, message=message,
                name=user_name, email=user_email
            )
        return body

    def prepare_git_object(self, body, probe_length):
        return "commit {}\0{}".format(len(body) + probe_length, body)

    def mine(self, prefix, message, max_probe_length=10, num_workers=4, chunk_size=100000):
        """Find a git commit which has a hash containing a desired prefix."""
        result = None
        self.pool = Pool(num_workers)
        for probe_length in range(1, max_probe_length + 1):
            result = self._probe(prefix, message, probe_length, num_workers, chunk_size)
            if result:
                return result

    def _probe(self, prefix, message, probe_length, num_workers, chunk_size):
        work_chunk_size = num_workers * chunk_size
        num_combinations = len(self.charset) ** probe_length
        
        coolmit_msg = self.prepare_message(message)
        template = self.prepare_git_object(coolmit_msg, probe_length)
        start_offset = 0
        start_t = time.time()
        while start_offset < num_combinations:
            params = [
                (prefix, template, self.charset, worker_id, num_workers, start_offset, probe_length, work_chunk_size) \
                for worker_id in range(num_workers)
            ]
            results = self.pool.map(coolmit_probe_worker, params)
            for result in results:
                if result:
                    salt, hash_ = result
                    return coolmit_msg, salt, hash_ 
            start_offset += work_chunk_size
            if start_offset % (work_chunk_size * 5) == 0:
                dt = time.time() - start_t
                print("{} hashes at {} hashes/s".format(start_offset, start_offset / dt))


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
    import sys
    try: # TODO: optparse
        prefix = sys.argv[1]
        message = sys.argv[2]
    except IndexError:
        print('syntax: coolmit prefix "commit message"')
    else:
        print("Mining for commit hash with prefix {}".format(prefix))
        coolmit(prefix, message)
