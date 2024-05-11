#!/usr/bin/env python3

"""
Description and Usage:

This is a GNU Radio script for generating signals based on parameters received from an upper-level application via TCP and sending them through PlutoSDR.
- Input: Signal parameters such as frequency, power, and bandwidth, sent from the upper-level application via TCP.
- Output: A signal generated based on the parameters and sent through PlutoSDR.

Usage Instructions:
- Ensure PlutoSDR is correctly connected and configured.
- After starting the program, use a TCP connection to send signal parameters.
"""

import socket
import time
from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
from gnuradio import uhd


# Receive signal parameters from an upper-level application
def receive_signal_params():
    # Create a TCP server to listen for connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 6789))
    server.listen(1)  # Listen for incoming connections

    conn, addr = server.accept()  # Accept an incoming connection
    data = conn.recv(1024).decode("utf-8")  # Read the signal parameters

    # Extract parameters from the received data
    params = {}
    for item in data.strip().split(";"):
        key, value = item.split("=")
        params[key.strip()] = value.strip()  # Store key-value pairs

    conn.close()  # Close the connection
    server.close()  # Close the server

    return params


# GNU Radio flowgraph for signal generation and sending through PlutoSDR
class SignalGeneration(gr.top_block):
    def __init__(self, freq, power, bandwidth):
        gr.top_block.__init__(self)

        # Set PlutoSDR frequency, power, and bandwidth
        self.pluto_sink = uhd.usrp_sink(
            "pluto",  # PlutoSDR device address
            uhd.stream_args("fc32"),  # Complex float32 data stream
        )

        # Configure frequency, power, and bandwidth
        self.pluto_sink.set_center_freq(float(freq))  # Frequency
        self.pluto_sink.set_gain(float(power))  # Power
        self.pluto_sink.set_bandwidth(float(bandwidth))  # Bandwidth

        # Generate a simple sine wave signal
        self.signal_source = analog.sig_source_c(  # Sine wave signal
            32000,  # Sample rate
            analog.GR_SIN_WAVE,  # Waveform type
            1000,  # Frequency (internal signal frequency)
            1.0,  # Amplitude
        )

        # Connect the signal source to PlutoSDR sink
        self.connect((self.signal_source, 0), (self.pluto_sink, 0))


# Main flow
if __name__ == "__main__":
    # Receive signal parameters
    signal_params = receive_signal_params()  # Get signal parameters from TCP

    # Get frequency, power, bandwidth from the parameters
    freq = signal_params.get("freq", "2.4G")  # Default 2.4 GHz
    power = signal_params.get("power", "30")  # Default 30 dBm
    bandwidth = signal_params.get("bandwidth", "10M")  # Default 10 MHz

    # Create the flowgraph and set signal generation parameters
    tb = SignalGeneration(freq, power, bandwidth)
    tb.start()  # Start the flowgraph

    try:
        input("Press Enter to stop the signal generation...")  # Wait for user input to stop
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt
    finally:
        tb.stop()  # Stop the flowgraph
        tb.wait()  # Wait for the flowgraph to end
