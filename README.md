# Restorer V2

Attempt to rewrite restoring part of criu as command interpreter.

## Repository structure:

* `restorer/` -- command generator and command interpreter (restorer) src (see [`restorer/README.md`](restorer/README.md))
* `sandbox/` -- processes to restore, which for now are used for simple testing
* `tools/` -- utility scripts

## Why to do this?

Splitting restorer logic into generator(s)/interpreter(s) parts leads to:

*  easier to understand codebase (I guess)
*  easier to support
    -  it includes much easier debugging, beacuse generator parts are not dealing with forking and stuff, they are just algorithm implementations

