python-netconfig
================

This package contains a set of utilities that can be used to configure low-level Linux
networking features.

These tools tend to provide better performance but way fewer features vs.
pyroute2, we used them in conjunction to provide better over-all performance

asyncio
-------

Some of the APIs include coroutines which are intended to be used with python's asyncio features.
If using asyncio the blocking calls can be called with a run_in_executor so that
they don't block the mainloop (though most of the call are fast enough it shouldn't
make a difference).
