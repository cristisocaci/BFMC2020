Templates
=========

Template contains all classes, which have role to define a custom template. The templates are base classes for defining the base functionality of a worker, which has to variants, a thread based and a process based. 
Each types of worker communicate with the others through input and output pipes. 

.. image:: ../diagrams/pics/ClassDiaStartUp_Templates.png
    :align: center

.. automodule:: src.utils.templates.workerprocess
.. automodule:: src.utils.templates.threadwithstop
.. automodule:: src.utils.templates.workerthread
