#!/usr/bin/env python3

"""
Description and Usage:

This GNU Radio script plays a local signal file based on TCP control signals from an upper-level application and sends the signal via PlutoSDR.
Program flow:
1. Upon starting, it listens for control signals from the upper-level application.
2. When the "START" command is received, it plays the local signal file `recorded_signal.dat`.
3. When the "STOP" command is received, it stops playback.
4. Sends the signal through PlutoSDR.

The upper-level application can control playback status through TCP connection.
By default, the program listens for TCP connections on `127.0.0.1:5678`.
The following commands can be sent from the upper-level application:
- "START": Start playing the signal file.
- "STOP": Stop playing.

Usage Instructions:
1. Run the program.
2. Use a TCP client to send commands to control playback status.
"""

from gnuradio import gr
from gnuradio import blocks
from gnuradio import uhd
import socket
import threading


# GNU Radio flowgraph for signal playback and sending through PlutoSDR
class SignalPlayback(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        # PlutoSDR sink block for sending signals
        self.pluto_sink = uhd.usrp_sink(
            "pluto",  # PlutoSDR device address
            uhd.stream_args("fc32"),  # Complex float32 data stream
        )

        # Initialize with an empty file source
        self.file_source = None

        # TCP server to receive control commands from the upper-level application
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind(("127.0.0.1", 5678))
        self.tcp_server.listen(1)  # Listen for incoming connections

        # Thread for listening to control commands
        self.server_thread = threading.Thread(target=self.listen_for_commands)
        self.server_thread.start()

    def listen_for_commands(self):
        # Listen to the TCP server and receive control commands from the upper-level application
        while True:
            conn, addr = self.tcp_server.accept()
            command = conn.recv(1024).decode("utf-8").strip()
            if command == "START":
                self.start_playback()  # Start playback
            elif command == "STOP":
                self.stop_playback()  # Stop playback
            conn.close()

    def start_playback(self):
        # Start playing the local signal file
        self.file_source = blocks.file_source(gr.sizeof_gr_complex, "recorded_signal.dat", True)
        self.connect((self.file_source, 0), (self.pluto_sink, 0))  # Connect file source to PlutoSDR sink
        print("Playback started.")

    def stop_playback(self):
        # Stop playback
        if self.file_source:
            self.disconnect((self.file_source, 0), (self.pluto_sink, 0))  # Disconnect the connection
            self.file_source = None
            print("Playback stopped.")


# Main program block
if __name__ == "__main__":
    tb = SignalPlayback()  # Create the SignalPlayback flowgraph
    tb.start()  # Start the flowgraph

    try:
        input("Press Enter to quit...")  # Wait for user input to stop
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt
    finally:
        tb.stop()  # Stop the flowgraph
        tb.wait()  # Wait for the flowgraph to complete
        tb.server_thread.join()  # Ensure the listening thread ends
