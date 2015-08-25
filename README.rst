======
README
======

``image-merge`` is a command line program that merges 2, 3, or 4 images into a single image suitable for printing. 

Features
--------

* outputs standard 4" X 6" (300dpi) jpeg images for printing
* combines 2, 3, or 4 source images into each page
* automatically rotates and re-sizes images to fit

Installation
------------
Clone master branch. From a terminal inside the cloned directory type:

.. code:: bash

    python setup.py install
    
Usage
-----
.. code:: bash

    image-merge --help

Testing
-------
#. install py.test:
    
    .. code:: bash
    
        pip install pytest
    
#. from the root directory run the tests:

    .. code:: bash
    
        py.test




TODO
----
If you would like to contribute to this project, I'd be happy to merge in any pull requests that enhance the features or performance.

* multi-threading
* colour profile aware
* different page sizes
* more page layout templates
