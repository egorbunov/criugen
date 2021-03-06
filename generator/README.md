# CriuGen

CRIU dump analyser and restoration commands generator for the task of process tree restoration in 
Linux operating system.   

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

## Usage

Read help for the `criugen` utility: `./criugen.py -h`. Example usage:
  
* Generate program for interpreter (final restoration program):
    ```bash
    ./criugen.py program -d /path/to/process/dump -o program.json
    ```
* Generate Intermediate abstract actions for restoration (using json dump files as example) and
 print them to the stdout:
    ```bash
    ./criugen.py actions-ir  -d /path/to/process/jsondump --json_img
    ```
    
* Visualize intermediate representation actions graph, which does not contain actions with Virtual Memory Area resources;
  This command execution also shows render immediately and also saves it to specified (`-o` option) file
    ```bash
    ./criugen.py actions-graph -d /path/to/process/dump --skip vmas --type pdf --show -o /tmp/mygraph
    ```
    
* Visualize intermediate actions (ordered) list:
    ```bash
    ./criugen.py actions-graph -d /path/to/process/dump --sorted --type pdf --show -o /tmp/actlist
    ```

* Visualize initial process tree with resources
    ```bash
    ./criugen.py pstree -d /path/to/process/dump --notmp
    ```

## Requirements

As mentioned above you will need `crit`, it is essential. Also, if you want to
use actions graph or process tree visualization you will have to install next dependencies:

* `graphviz` (use `pip install graphviz` after `apt install graphviz` or whatever on your system)
