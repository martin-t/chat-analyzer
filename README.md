Chat-analyzer
=============

A small script to create some graphs from facebook chat history

Installation
------------

1. Install matplotlib - it doesn't seem to play nicely with virtualenvs so use ```sudo apt-get install python3-matplotlib```

2. Activate virtualenv (```workon xon-activity-stats``` using virtualenvwrapper)

3. ```pip install -r requirements.txt```

4. ```toggleglobalsitepackages``` to enable the systemwide matplotlib

Or if you don't use virtualenvs, skip 2-4 and just install the dependencies globally (```sudo pip3 install -r requirements.txt```).

Usage
-----

Download and unzip your facebook data into facebook-downloaded.

Set 'my_name' to your name.

