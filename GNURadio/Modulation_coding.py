#!/usr/bin/env python3

"""
Description and Usage:

This GNU Radio script receives data packets from a TCP source, encodes and modulates them based on user-selected options, then sends the modulated signal to PlutoSDR.

- Encoding options include DVB-S2 and CCSDS.
- Modulation options include BPSK, QPSK, and 8-PSK.

The main steps in this program are:
1. Receive data packets from TCP.
2. Encode the data based on user selection (DVB-S2 or CCSDS).
3. Modulate the data based on user selection (BPSK, QPSK, or 8-PSK).
4. Send the modulated signal to PlutoSDR.

Usage Instructions:
- Use command-line arguments to choose the encoding and modulation method.
- Example command lines:
  python3 modulation_coding.py --encoding DVB-S2 --modulation QPSK

To stop the program, press Enter or use a keyboard interrupt (Ctrl + C).
"""

import argparse
from gnuradio import gr
from gnuradio import blocks
from gnuradio import digital
from gnuradio import fec
from gnuradio import uhd


# Define a function to select DVB-S2 or CCSDS encoding
def get_encoder(encoding):
    if encoding.lower() == "dvb-s2":
        # Example DVB-S2 encoding with RSC and LDPC encoders
        return fec.cc_encoder_make(
            7,  # K
            2,  # rate
            0b1111001,  # generator polynomial
            0,  # initial state
            fec.CC_STREAMING,
            False,
        )
    elif encoding.lower() == "ccsds":
        # Example CCSDS encoding with Reed-Solomon encoder
        return fec.reed_solomon_encoder_make(
            255,  # n
            223,  # k
            8,  # symbol size
        )
    else:
        raise ValueError("Invalid encoding selected. Choose 'DVB-S2' or 'CCSDS'.")


# Define a function to choose the modulation scheme
def get_modulator(modulation):
    if modulation.lower() == "bpsk":
        return digital.psk.psk_mod(
            constellation_points=2,  # BPSK
            mod_code="none",
            differential=False,
            samples_per_symbol=2,
            excess_bw=0.35,
        )
    elif modulation.lower() == "qpsk":
        return digital.psk.psk_mod(
            constellation_points=4,  # QPSK
            mod_code="none",
            differential=False,
            samples_per_symbol=2,
            excess_bw=0.35,
        )
    elif modulation.lower() == "8-psk":
        return digital.psk.psk_mod(
            constellation_points=8,  # 8-PSK
            mod_code="none",
            differential=False,
            samples_per_symbol=2,
            excess_bw=0.35,
        )
    else:
        raise ValueError("Invalid modulation selected. Choose 'BPSK', 'QPSK', or '8-PSK'.")

# Define the GNU Radio flowgraph
class TCPToPlutoSDR(gr.top_block):
    def __init__(self, encoding, modulation):
        gr.top_block.__init__(self)

        # Receive data packets from TCP
        self.tcp_source = blocks.tcp_source(
            itemsize=gr.sizeof_char,
            addr="127.0.0.1",
            port=4567,
            server=True,
        )

        # Set encoder based on chosen encoding
        self.encoder = get_encoder(encoding)

        # Set modulator based on chosen modulation
        self.modulator = get_modulator(modulation)

        # Define the PlutoSDR sink
        self.pluto_sink = uhd.usrp_sink(
            "pluto",  # PlutoSDR device address
            uhd.stream_args("fc32"),
        )

        # Connect the blocks
        self.connect((self.tcp_source, 0), (self.encoder, 0))
        self.connect((self.encoder, 0), (self.modulator, 0))
        self.connect((self.modulator, 0), (self.pluto_sink, 0))


# Process command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP to PlutoSDR with configurable encoding and modulation.")
    parser.add_argument("--encoding", type=str, choices=["DVB-S2", "CCSDS"], required=False, help="Choose encoding: DVB-S2 or CCSDS")
    parser.add_argument("--modulation", type=str, choices=["BPSK", "QPSK", "8-PSK"], required=True, help="Choose modulation: BPSK, QPSK, or 8-PSK")

    args = parser.parse_args()

    tb = TCPToPlutoSDR(args.encoding, args.modulation)  # Use the selected encoding and modulation
    tb.start()  # Start the flowgraph

    try:
        input("Press Enter to quit...")  # Wait for user to stop
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt
    finally:
        tb.stop()  # Stop the flowgraph
        tb.wait()  # Wait for the flowgraph to stop
