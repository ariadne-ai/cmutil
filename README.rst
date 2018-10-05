======
cmutil
======

``cmutil`` is a Python script to convert between (Py)KNOSSOS and
CATMAID annotations. `CATMAID's export feature`_ creates JSON files of your
annotation. With ``cmutil``, you can convert those JSON files to
KNOSSOS-readable NML files [1]_, and vice versa.

.. _CATMAID's export feature: https://catmaid.readthedocs.io/en/stable/importing_data.html
.. [1] For more information about NML files, visit https://github.com/scalableminds/nml-spec.

Disclaimer
==========

``cmutil`` is not affiliated with CATMAID, but was developed internally at
*ariadne-service gmbh* by simply parsing the output of CATMAID's export
feature. This is not an official conversion script.

*Thanks* to `Tom Kazimiers`_ for insights into CATMAID's data structure and
other helpful hints.

.. _Tom Kazimiers: https://github.com/tomka

Installation
============

Currently, ``cmutil`` only has a single dependency: ``declxml``. For
convenience, ``declxml`` is included directly inside ``cmutil``'s source tree.
This way, ``cmutil`` is easily packaged as an executable Python zip archive,
and should be able to run on any Python 3 environment.

Go to `Releases <https://github.com/ariadne-service/cmutil/releases>`_ to
download the self-contained zip file.

Requirements
============

Minimum Python version is 3.

**Note:** We recommend to set up CATMAID using Python >3 as well, since
CATMAID's import/export feature seems to behave differently using Python 2.

Conversion between KNOSSOS and CATMAID files was tested on Python 3.5.2.

Usage
=====

::

	$ python3 cmutil.pyz
	usage: cmutil.pyz [-h] -convert {nml,catmaid} [-o OUTPUT] [-u USER]
	                  [-pyknossos]
	                  [source]
	cmutil.pyz: error: the following arguments are required: -convert

================  =============================================================
Argument          Description
================  =============================================================
-convert          Either *nml* or *catmaid*. Specifies **output** format.
-o                Path to output file. If not specified, output is printed to stdout.
-u                CATMAID user ID. If not specified, user ID will be asked for during conversion.
-pyknossos        (Flag) If this flag is set, input file is treated as PyKNOSSOS NML file.
[source]          (Positional) Path to input file. If not specified, input is read from stdin.
================  =============================================================

There a subtle differences between NML files created from KNOSSOS and those
created from PyKNOSSOS. Because of this, you need to explicitly add the
``-pyknossos`` flag if your source file was created in PyKNOSSOS.

License
=======

Other than ``declxml`` (released under MIT License), all of ``cmutil``'s files
are released under the zlib license (c.f. ``LICENSE``).
