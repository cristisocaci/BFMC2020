Camera Steamer 
==============

Camera streamer and camera receiver classes can be used for transferring the frames captured by the camera to a remote device. 
The streamer connects to the other process or thread through the first input pipe and transfers the frames to the predefined remote client.
The receiver connects to the remote server and shows the frames received from the streamer.  

.. image:: ../diagrams/pics/ClassDiaStartUp_CameraStreamer.png
    :align: center

.. automodule:: src.utils.camerastreamer.camerastreamer
.. automodule:: src.utils.camerastreamer.camerareceiver


