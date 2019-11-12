[![Build Status](https://travis-ci.org/SlashGordon/pyeasysocket.svg?branch=master)](https://travis-ci.org/SlashGordon/pyeasysocket)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pyeasysocket?style=plastic)
[![Coverage Status](https://coveralls.io/repos/github/SlashGordon/pyeasysocket/badge.svg?branch=master)](https://coveralls.io/github/SlashGordon/pyeasysocket?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/30808a98d54b4f24bf26f5a89b92501a)](https://www.codacy.com/manual/SlashGordon/pyeasysocket?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=SlashGordon/pyeasysocket&amp;utm_campaign=Badge_Grade)

# pyeasysocket
Python TCP and UDP sockets made easy.

## install

```shell
pip install pyeasysocket
```

## quick start

Create a TCPReceiver:

```python
from pyeasysocket.udp import UDPReceiver
from pyeasysocket.tcp import TCPReceiver

receiver_udp = UDPReceiver('localhost', 8001)
receiver = TCPReceiver('localhost', 8000)
try:
    # run background thread for receive
    receiver.start()
    # wait for data
    received_data = receiver.data
finally:
    receiver.join() # closes the background thread
```

Or use the advantage of a with statement with the guarantee that the connection will be closed.

```python
import time
from pyeasysocket.tcp import TCPReceiver, TCPClient

client = TCPClient('localhost', 8000)
with TCPReceiver('localhost', 8000) as receiver:
    client.send('test')
    time.sleep(0.2) # only for timing purpose
    received_data = receiver.data # test
```
## issue tracker

[https://github.com/SlashGordon/pyeasysocket/issuese](https://github.com/SlashGordon/pyeasysocket/issues")
