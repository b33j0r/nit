# Nit

`nit` as in not-[git](http://git-scm.org); alternatively, nit-wit, in line with Linus' [original reasoning](https://github.com/git/git/blob/master/README)


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

## Usage

**TODO**

`nit` supports the following high-level operations:

 * `init`: initialize a repository
 * `config`: read and save variables in `${REPO}/config` or `~/.nitconfig` (if `--global` is specified)
 * `status`: print the diff between the HEAD commit, the index, and the working tree
 * `cat`: print the contents of an object in the database
 * `add`: include a file from the current working tree in the index (the next tree to be committed)
 * `commit`: save the current state of the working tree to the database
 * `log`: print the HEAD commit and its ancestors
 * (in progress) `diff`: report the diff between the HEAD commit and the working tree
 * (in progress) `checkout`: restore the working tree to a previous state

As with `git`, these operations are implemented in terms of lower-level operations.


## Git-Compatibility

**TODO**


## Components

A `Repository` object doesn't actually do a whole lot. It defines operations at a high level and then relies on parameterizable component objects for specific behavior.

**TODO**
 
 
## Contributing

 * Please do!
 * In my personal projects, I usually use a narrow line width of 80 characters because I like to review code on my phone or tablet; this is a loose standard, but there is a greater probability of getting your pull request accepted if you adopt it :)


## Author

Initially created by [Brian Jorgensen](http://brianjorgensen.com) on nights and weekends; submit your awesome pull request and we'll add you here!
