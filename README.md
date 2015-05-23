# Nit

`nit` as in "not-[git](http://git-scm.org)"; alternatively, "nit-wit", in line with Linus' [original reasoning](https://github.com/git/git/blob/master/README)


`nit` is a framework for experimenting with `git`-like versioned storage systems. It aims to abstract the basic operations of such a system using a component model ([strategy pattern](http://en.wikipedia.org/wiki/Strategy_pattern)).


## Purpose

* An excuse to use Python 3 for an interesting large-scale project (with minimal use of third-party libraries)
* A sandbox for exploring modern version control systems and [content-addressable storage](http://en.wikipedia.org/wiki/Content-addressable_storage)
* An experiment in reverse-engineering (the first release version is based on the git documentation and unicorns, but intentionally no source code)
* In the near future, a [new library](https://xkcd.com/927/) for [interacting with git repositories from python](https://github.com/gitpython-developers/GitPython). Using `nit` in any production situation is not recommended. By design, `nit` encourages experimentation with backwards-incompatible innovations, and I make exactly zero guarantees:

```python
from nit import guarantees
assert len(guarantees) == 0
```


## `git` Compatibility

`nit` is not `git`, and the command-line script `nit` does not attempt to be a `git` clone. However, the design of the `nit` *library* employs a component architecture (or [strategy pattern](http://en.wikipedia.org/wiki/Strategy_pattern)). This allows high-level operations to be performed while allowing for a wide range of DVCS design decisions.

For example, the base `nit` storage strategy does not use file compression when storing objects; this makes it easy to inspect a repository when experimenting with your DVCS design. `git`, on the other hand, optimizes storage performance by using `zlib` to deflate/inflate every object.

Thus, the `nit` library is designed in such a way that the serialization process can be easily modified if desired (`import zlib` plus a few lines of code in a subclass of `BaseSerializer`).

With all of the above said, the python package `nit.components.git` exists to facilitate the implementation of a a pythonic `git` clone over time.


## Usage

**NOTE:** `nit` is only compatible with Python 3.2+

Update your tools, and get the repository!

```
sudo pip install -U setuptools pip virtualenv  # always! 
git clone git@github.com:b33j0r/nit.git
```

Create a virtual environment and activate it in your bash shell:

```
virtualenv -p python3 nit_venv
. nit_venv/bin/activate
```

Install the requirements in your virtual environment:

```
cd nit
pip install -r nit/requirements.txt
```

Add the nit project to your virtual environment in develop mode:

```
python setup.py develop
```

Try `nit`:

```bash
(nit_env) ~/nit_test_proj2$ nit
usage: nit [-h] {test,init,config,status,cat,diff,add,commit,log,checkout} ...

The commandline client for nit, a pythonic framework for experimenting with
git-like version control systems. http://www.github.com/b33j0r/nit

positional arguments:
  {test,init,config,status,cat,diff,add,commit,log,checkout}
    init                Initializes an empty repository
    config              read and save variables in ${REPO}/config or
                        ~/.nitconfig (if --global is specified)
    status              report the diff between the HEAD commit, the index,
                        and the working tree
    cat                 print the contents of an object in the database
    diff                report the diff between the HEAD commit and the
                        working tree
    add                 include a file from the current working tree in the
                        index (the next tree to be committed)
    commit              save the current state of the index to the database
                        and link HEAD to the resulting object
    log                 print the HEAD commit and its ancestors
    checkout            (in progress) restore the working tree to a tree in
                        the repository's history

optional arguments:
  -h, --help            show this help message and exit
```


**TODO**

`nit` supports the following high-level operations:

 * `init`: initialize a repository
 * `config`: read and save variables in `${REPO}/config` or `~/.nitconfig` (if `--global` is specified)
 * `status`: report the diff between the HEAD commit, the index, and the working tree
 * `cat`: print the contents of an object in the database, referenced by its key (typically, a `git`-like SHA value)
 * `add`: include a file from the current working tree in the index (the next tree to be committed)
 * `commit`: save the current state of the working tree to the database
 * `log`: print the HEAD commit and its ancestors
 * (in progress) `diff`: report the diff between the HEAD commit and the working tree
 * (in progress) `checkout`: restore the working tree to a previous state

As with `git`, these operations are implemented in terms of lower-level operations.

**TODO**


## Components

A `Repository` object doesn't actually do a whole lot. It defines operations at a high level and then relies on parameterizable component objects for specific behavior.

**TODO: Explain the component design :o**
 
 
## Contributing

 * Please do!
 * In my personal projects, I usually use a narrow line width of 80 characters because I like to review code on my phone or tablet; this is a loose standard, but there is a greater probability of getting your pull request accepted if you adopt it :)


## Author

Initially created by [Brian Jorgensen](http://brianjorgensen.com) on nights and weekends; submit your awesome pull request and we'll add you here!
