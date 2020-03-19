# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

import threading
from src.data.gpstracker.server_data import ServerData
from src.data.gpstracker.server_listener import ServerListener
from src.data.gpstracker.server_subscriber import ServerSubscriber
from src.data.gpstracker.position_listener import PositionListener

import time

class GpsTracker(threading.Thread):
    
    def __init__(self, outP):
        """ GpsTracker targets to connect on the server and to receive the messages, which incorporates 
        the coordinate of the robot on the race track. It has two main state, the setup state and the listening state. 
        In the setup state, it creates the connection with server. It's receiving  the messages from the server in the listening
        state. 

        It's a thread, so can be running parallel with other threads. You can access to the received parameters via 'coor' function.

        Examples
        --------
        Here you can find a simple example, where the GpsTracker are running 10 second:
            | gpstracker = GpsTracker()
            | gpstracker.start()
            | time.sleep(10)
            | gpstracker.stop()
            | gpstracker.join()

        """
        super().__init__()
        self.outP = outP
        #: serverData object with server parameters
        self.__server_data = ServerData()
        #: discover the parameters of server
        self.__server_listener = ServerListener(self.__server_data)
        #: connect to the server
        self.__subscriber = ServerSubscriber(self.__server_data,1)
        #: receive and decode the messages from the server
        self.__position_listener = PositionListener(self.__server_data)
        
        self.__running = True

    def setup(self):
        """Actualize the server's data and create a new socket with it.
        """
        # Running while it has a valid connection with the server
        while(self.__server_data.socket == None and self.__running):
            # discover the parameters of server
            self.__server_listener.find()
            if self.__server_data.is_new_server and self.__running:
                # connect to the server 
                self.__subscriber.subscribe()
        
    
    def listen(self):
        """ Listening the coordination of robot
        """
        self.__position_listener.listen()

    def coor(self):
        """Access to the last receive coordinate
        
        Returns
        -------
        dictionary
            coordinate and timestamp
        """
        return self.__position_listener.coor
    
    def run(self):
        while(self.__running):
            self.setup()
            self.listen()
            self.outP.send(self.coor())

    def stop(self):
        """Terminate the thread running.
        """
        self.__running = False
        self.__server_listener.stop()
        self.__position_listener.stop()

if __name__ == '__main__':
    gpstracker = GpsTracker()
    gpstracker.start()

    time.sleep(10)
    gpstracker.stop()

    gpstracker.join()