halonctl
========

A commandline utility for managing Halon SP nodes and clusters.

Requirements
------------

* Python 2.7 <small>3.x support coming</small>
* pip

Mac, Linux and Windows are officially supported, though one of the former two are recommended.

Installation (development)
--------------------------

*(For end-users, more convenient packages will soon be available.)*

1. Install `virtualenv`
   
   `pip install virtualenv` (may need to be prefixed with `sudo`)

2. Set up a virtualenv in the source directory
   
   `virtualenv .`

3. Activate the virtualenv; you need to do this once per terminal/tab, and will
   put you in `halonctl`'s isolated little world, with its own packages, etc.
   
   `. bin/activate` (short for `source bin/activate`)
   
   To deactivate it again, just run: `deactivate`
   
4. Install requirements; you need to do this again if you see the file
   `requirements.txt` change, or if you see errors about missing modules.
   
   Make sure to do this with an activated `virtualenv`, or all dependencies
   will incorrectly be installed globally, where they may cause conflicts!
   
   `pip install -r requirements.txt`

5. Run `halonctl` - again, make sure to have an activated `virtualenv`, or it
   won't find its dependencies:
   
   `./halonctl.py --help` or `python halonctl.py --help`
