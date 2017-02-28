ChainSign
=========
Simple user-friendly document signing and timestamping solution based on public
cryptocurrency blockchains.

Currently only Namecoin is supported, however generic python API supporting
multiple chains is going to be released. (currently mostly contained in
`timestamper.py`)

Installation
------------
Currently installation is not-so-simple. In the future application will be
deployed using pyinstaller or some other python freezing solution, with proper
windows installer and such...

    sudo apt install python-pip libqt4-dev make
    pip install -r requirements.txt
    make run

Usage
-----
Simple Qt UI is present in `chainsign.py` (that is run by `make run` command
above)

Example bulk verification CLI is available in `timestamper.py` when run
directly (`python timestamper.py FILE1 FILE2 ...`)

Development
-----------
Currently GUI part is based on PySide (qt4). In (hopefuly near) future, when
PySide2 becomes a (stable) thing, we'll just migrate it over.

We try to target python3.
