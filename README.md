# Nit

Nit as in not-git; alternatively, nit-wit, in line with Linus' original reasoning


## Purpose

Nit is a framework for experimenting with Git-like versioned storage systems. It aims to abstract the basic operations of such a system using a component model. It supports the following high-level operations:

 * `init`: initialize a repository
 * `config`: read and save variables in `${REPO}/config` or `~/.nitconfig` (if `--global` is specified)
 * `status`: print the diff between the HEAD commit, the index, and the working tree
 * `cat`: print the contents of an object in the database
 * `add`: include a file from the current working tree in the index (the next tree to be committed)
 * `commit`: save the current state of the working tree to the database
 * `log`: print the HEAD commit and its ancestors
 * (in progress) `diff`: report the diff between the HEAD commit and the working tree
 * (in progress) `checkout`: restore the working tree to a previous state

As with Git, these operations are implemented in terms of lower-level operations.


## Components

A `Repository` object doesn't actually do a whole lot. It defines operations at a high level and then relies on parameterizable component objects for specific behavior.

 * TODO
 
