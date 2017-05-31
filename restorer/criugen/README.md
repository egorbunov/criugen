# CriuGen

## Install

* You'll need to install `crit` (not executable script, but python library pycriu, but script is also installed)  by CRIU
    * It can be done this way:
        
        ```bash
        cd criu  # criu repository root
        python scripts/crit-setup.py install
        ```
        This works inside *virtualenv*
    * WARN: I had troubles using `crit` from virtualenv because it can't be easily installed via pip and after switching to fresh environment I could see it in pip list, but without it's dependencies, which I've had to install manually:
        * `pip install 'protobuf==2.6.1'`
        * `pip install 'ipaddr=2.1.11'`
        
* To start using criugen do `pip install --edit .` in `criugen` directory.
