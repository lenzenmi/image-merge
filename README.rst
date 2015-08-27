======
README
======

``image-merge`` is a command line program that merges multiple images using a variety of template options.

Features
--------

* outputs standard 4" X 6" (300dpi) jpeg images for printing
* automatically rotates and re-sizes images to fit


Layouts
-------

Landscape
~~~~~~~~~
* combines 2, 3, or 4 source images
* combines images by setting a maximum height in cm

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
test images are created and saved to ``/tmp/img#-0001.img`` where ``#`` is the number of images per page. 

#. install py.test:
    
    .. code:: bash
    
        pip install pytest
    
#. from the root directory run the tests:

    .. code:: bash
    
        py.test
        
If you need to change the output directory, set the environment variable ``IMAGE_MERGE_TEST_DIR`` to the directory you want.

For example:
    .. code:: bash
        
        export IMAGE_MERGE_TEST_DIR="/home/username/my-dir/"    
        py.test
    
    or
    
    .. code:: bash
        
        IMAGE_MERGE_TEST_DIR="/home/username/my-dir/" py.test     




TODO
----
If you would like to contribute to this project, I'd be happy to merge in any pull requests that enhance the features or performance.

* multi-threading
* colour profile aware
* different page sizes
* more page layout templates
