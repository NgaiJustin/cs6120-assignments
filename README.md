# CS 6120 BRIL

This is a repository containing implementations of analyses, optimizations, and other tools for CS 6120
using the [Big Red Intermediate Language](https://capra.cs.cornell.edu/bril/intro.html)


## Contents

#### Main Directories:
* `bril-rs` - Simple rust library for interfacing with Bril. Most of it
is taken from [https://github.com/sampsyo/bril](https://github.com/sampsyo/bril)
* `lesson-tasks` - Tasks organised by lesson
* `benchmark` - Test directory for [TURNT](https://github.com/cucapra/turnt) snapshot tests.
Benchmarks are taken from [https://github.com/sampsyo/bril](https://github.com/sampsyo/bril) benchmarks.

#### L2-3 Additions:
* `bril_type` - Types for bril constructs.
* `utils` - Utility functions loading and manipulating bril programs.
#### L4 Additions:
* `cfg` - A simple library that construst control flow graphs from bril programs and also visualizes them in dot format.
* `dfa` - Implementations of data flow analyses using the framework (currently includes constant propagation and reaching definitions).
* `dfa_framework` - A generic solver framework for implementing data flow analyses.
* `dot_util` - A series of functions to help with manipulating dot files, most notably it can create an animation from series of dot files.
* `node` - A representation of a node in a control flow graph.