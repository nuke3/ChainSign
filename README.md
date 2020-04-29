ChainSign
=========
Simple user-friendly document signing and timestamping solution based on public
cryptocurrency blockchains.

Currently only Namecoin is supported, however generic python API supporting
multiple chains is going to be released. (currently mostly contained in
`timestamper.py`)

Installation
------------
Linux:
Currently installation is not-so-simple. In the future application will be
deployed using pyinstaller or some other python freezing solution, with proper
windows installer and such...

    sudo apt install python3-pip qtbase5-dev make
    pip3 install -r requirements.txt
    make run

For Windows
https://github.com/nuke3/ChainSign/releases

iOS and MacOS: installer soon, but you can install it in linux way 

Usage
-----
Simple Qt UI is present in `chainsign.py` (that is run by `make run` command
above)

Example bulk verification CLI is available in `timestamper.py` when run
directly (`python timestamper.py FILE1 FILE2 ...`)

Do not forget to run namecoin NODE!
Remember to create namecoin.conf or copy from this repo
The location of namecoin.conf depends on your operating system:

Windows XP             C:\Documents and Settings\<username>\Application Data\Namecoin\namecoin.conf
Windows Vista, 7, 10   C:\Users\<username>\AppData\Roaming\Bitcoin\namecoin.conf                                      
Linux                  /home/<username>/.namecoin/namecoin.conf                                                           
Mac OSX                /Users/<username>/Library/Application Support/Namecoin/namecoin.conf

Development
-----------
Currently GUI part is based on PySide2 (qt5).
We target python3.
