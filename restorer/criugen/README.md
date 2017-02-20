# CriuGen

## Install

* You'll need to install `crit` by CRIU
    * `crit` can be installed using `make install` at root dir of CRIU project
    * WARN: I had troubles using `crit` from virtualenv because it can't be easily installed via pip and after switching to fresh environment I could see it in pip list, but without it's dependencies, which I've had to install manually:
        * `pip install 'protobuf==2.6.1'`
        * `pip install 'ipaddr=2.1.11'`
        
* After `crit` is installed you just `pip install --edit .` in `criugen` directory.
