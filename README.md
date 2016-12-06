coolmit
=======
Don't just commit; coolmit. Make your commits cooler with coolmit today!
[![Build Status](https://travis-ci.org/awentzonline/coolmit.png)](https://travis-ci.org/awentzonline/coolmit)
[![Coverage Status](https://coveralls.io/repos/awentzonline/coolmit/badge.png)](https://coveralls.io/r/awentzonline/coolmit)

Eliminate boring commit hashes! With *coolmit* you choose
the beginning of the commit hash, giving your commits that
*coolmit* edge. Impress your boss and aggressively flex
your toned, bronze code muscle in the faces of your peers.

This was inspired by one of the problems in Stripe's CTF3.

[Here's a nice list of words you can make with hexadecimal characters.](http://nedbatchelder.com/text/hexwords.html)

Installation
------------
`pip install coolmit` or `python setup.py install`

Usage
-----
To update the hash of the current HEAD:
`git coolmit DESIRED_PREFIX`

E.g.: `git coolmit beef`

License
-------
MIT
