#!/usr/bin/env python

import hashlib
import subprocess
import time
from multiprocessing import Pool

from .base import CoolmitMiner


def coolmit_probe_worker(args):
    """Coolmit worker which helps find that cool commit hash you crave."""
    prefix, msg_header, msg_body, charset, worker_id, num_workers, start_offset, probe_length, work_chunk_size = args
    hf = hashlib.sha1
    len_charset = len(charset)
    msg_h = hf(msg_header)
    for i in xrange(start_offset + worker_id, start_offset + work_chunk_size, num_workers):
        salt = ''
        remaining = i
        for j in xrange(probe_length):
            salt += charset[remaining % len_charset]
            remaining = remaining // len_charset
        h = msg_h.copy()
        h.update(salt)
        h.update(msg_body)
        h = h.hexdigest()
        if h.startswith(prefix):
            return salt, h


class CoolmitCPUMiner(CoolmitMiner):
    """Finds you a cool commit with the CPU."""
    def __init__(self, *args, **kwargs):
        self.num_workers = kwargs.pop("num_workers", 8)
        super(CoolmitCPUMiner, self).__init__(*args, **kwargs)

    def pre_mine(self):
        self.pool = Pool(self.num_workers)

    def _probe(self, prefix, header, body, probe_length, chunk_size):
        work_chunk_size = self.num_workers * chunk_size
        num_combinations = len(self.charset) ** probe_length

        start_offset = 0
        start_t = time.time()
        while start_offset < num_combinations:
            params = [
                (prefix, header, body, self.charset, worker_id, self.num_workers, start_offset, probe_length, work_chunk_size) \
                for worker_id in range(self.num_workers)
            ]
            results = self.pool.map(coolmit_probe_worker, params)
            for result in results:
                if result:
                    return result
            start_offset += work_chunk_size
            if start_offset % (work_chunk_size * 1) == 0:
                dt = time.time() - start_t
                print("{} hashes at {} hashes/s".format(start_offset, start_offset / dt))
