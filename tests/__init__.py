import os
import tempfile
import shutil
import subprocess
import unittest

import coolmit


def touch(path):
    with open(path, "a"):
        os.utime(path, None)


class BaseCoolmitTestCase(unittest.TestCase):
    def setUp(self):
        self.root_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root_path)

    def sp_call(self, *args, **kwargs):
        kwargs["cwd"] = self.root_path
        return subprocess.call(*args, **kwargs)

    def init_repo(self):
        return self.sp_call("git init", shell=True)

    def setup_test_user(self, name="Steve Ballmer", email="bigpoppa@microsoft.com"):
        self.sp_call("git config user.name \"{}\"".format(name), shell=True)
        self.sp_call("git config user.email \"{}\"".format(email), shell=True)

    def touch_file(self, name):
        return touch(os.path.join(self.root_path, name))


class CoolmitMetaTestCase(BaseCoolmitTestCase):
    """Tests the tests."""
    def test_init_repo(self):
        self.assertEqual(self.init_repo(), 0)

    def test_touch_file(self):
        filename = "foobar"
        abs_path = os.path.join(self.root_path, filename)
        self.assertFalse(os.path.exists(abs_path))
        self.touch_file(filename)
        self.assertTrue(os.path.exists(abs_path))


class CoolmitTestCase(BaseCoolmitTestCase):
    def test_coolmit_headless(self):
        self.init_repo()
        self.setup_test_user()
        self.touch_file("AirWolf.plans")
        self.sp_call("git add .", shell=True)
        prefix = "beef"
        message = "just a coolmit"
        coolmit.coolmit(
            self.root_path, prefix, message,
            chunk_size=10000, num_workers=5
        )

    def test_coolmit_has_head(self):
        self.init_repo()
        self.setup_test_user()
        self.touch_file("StringfellowHawkeLakeCelloMusic.mp3")
        self.sp_call("git add .", shell=True)
        self.sp_call("git commit -m \"test\"", shell=True)
        prefix = "f00d"
        message = "made code cooler"
        coolmit.coolmit(
            self.root_path, prefix, message,
            chunk_size=10000, num_workers=5
        )
