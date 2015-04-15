# Nit

Nit as in not-git; alternatively, nit-wit, in line with Linus' original reasoning


## Purpose

Nit is a framework for experimenting with Git-like versioned storage systems. It aims to abstract the basic operations of such a system using a component model. It supports the following high-level operations:

 * `init`: initialize a repository
 * `add`: include a file in the current working tree
 * (in progress) `commit`: save the current state of the working tree
 * (in progress) `checkout`: restore the working tree to a previous state

As with Git, these operations are implemented in terms of lower-level operations.


## Components

A `Repository` object doesn't actually do a whole lot. It defines operations at a high level and then relies on parameterizable component objects for specific behavior.

 * TODO
 
