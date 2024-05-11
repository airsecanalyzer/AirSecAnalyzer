#!/usr/bin/env python3

"""
Description and Usage:

This GNU Radio script allows an upper-level application to control signal recording via TCP commands.
The program flow is as follows:
1. After the program starts, it begins receiving signals from PlutoSDR.
2. When it receives a control signal from the upper-level application, it starts or stops recording.
3. The signal is stored in a local file.

Usage Instructions:
- Run the program.
- Use a TCP connection to send commands to control recording status. The default TCP port is `127.0.0.1:5678`.
"""

from gnuradio import gr
from gnuradio import blocks
from gnuradio import uhd
import socket
import threading


class SignalRecorder(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        # Receive signals from PlutoSDR
        self.pluto_source = uhd.usrp_source(
            "pluto",  # PlutoSDR device address
            uhd.stream_args("fc32"),  # Complex float32 data stream
        )

        # Initialize with an empty file sink
        self.file_sink = None

        # TCP server to receive control commands from the upper-level application
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind(("127.0.0.1", 5678))
        self.tcp_server.listen(1)  # Listen for incoming connections

        # Thread for listening to control commands
        self.server_thread = threading.Thread(target=self.listen_for_commands)
        self.server_thread.start()

    def listen_for_commands(self):
        # Listen to the TCP server, receiving control commands from the upper-level application
        while True:
            conn, addr = self.tcp_server.accept()  # Accept incoming connections
            command = conn.recv(1024).decode("utf-8").strip()  # Read the command
            if command == "START":
                self.start_recording()  # Start recording
            elif command == "STOP":
                self.stop_recording()  # Stop recording
            conn.close()

    def start_recording(self):
        # Create a File Sink to start recording
        self.file_sink = blocks.file_sink(gr.sizeof_gr_complex, "recorded_signal.dat")
        self.file_sink.set_unbuffered(True)  # Write data immediately
        self.connect((self.pluto_source, 0), (self.file_sink, 0))  # Connect PlutoSDR to File Sink
        print("Recording started.")

    def stop_recording(self):
        # Stop recording
        if self.file_sink:
            self.disconnect((self.pluto_source, 0), (self.file_sink, 0))  # Disconnect PlutoSDR from File Sink
            self.file_sink = None
            print("Recording stopped.")


# Main program block
if __name__ == "__main__":
    tb = SignalRecorder()  # Instantiate the SignalRecorder flowgraph
    tb.start()  # Start the flowgraph

    try:
        input("Press Enter to quit...")  # Wait for user input to stop
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt
    finally:
        tb.stop()  # Stop the flowgraph
        tb.wait()  # Wait for the flowgraph to complete
        tb.server_thread.join()  # Ensure the listening thread ends
