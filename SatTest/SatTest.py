#!/usr/bin/env python3

"""
This is a GNU Radio script that provides four functions:
1. SignalReplay: Controls signal recording via `recording.py`, then plays signals using `playback.py`.
2. SignalFuzzing: Receives demodulated data from `Demodulation_decoding.py`, stores it, applies random or heuristic fuzzing, and sends the fuzzed data to `Modulation_coding.py` for modulation and coding.
3. SignalJamming: Configures jamming signal parameters such as frequency, power, and bandwidth, then sends through PlutoSDR.
4. GNSS Attacking: Uses GPS-SDR-SIM to generate and send fake GNSS location and time information through PlutoSDR.

Usage Instructions:
- Select the desired mode using command-line arguments.
- Example command lines:
  - SignalReplay: `python3 SatTest.py --mode SignalReplay --recordTime 60`
  - SignalFuzzing: `python3 SatTest.py --mode SignalFuzzing --fuzzing heuristic`
  - SignalJamming: `python3 SatTest.py --mode SignalJamming --freq 2.4G --power 30 --bandwidth 10M`
  - GNSS Attacking: `python3 SatTest.py --mode GNSSAttacking`
"""

import argparse
import subprocess
import random
import socket
import time

# Build common values by finding the longest repeating pattern in the data
def build_common_values_from_file(filepath):
    with open(filepath, "rb") as f:
        data = f.read()

    n = len(data)
    longest_common_substring = ""

    # Find the longest repeating pattern
    for length in range(1, n):
        for start in range(n - length):
            segment = data[start:start + length]
            count = data.count(segment)

            if count > 1 and len(segment) > len(longest_common_substring):
                longest_common_substring = segment

    return longest_common_substring


# Random fuzzing
def random_fuzz(data):
    fuzzed_data = bytearray(data)
    for i in range(len(fuzzed_data)):
        if random.random() < 0.05:
            fuzzed_data[i] = random.randint(0, 255)
    return fuzzed_data


# Check if data matches DVB-S2 or CCSDS protocol
def check_protocol(data):
    # Basic protocol detection logic
    if len(data) >= 10:
        if data[0] == 0x47:  # DVB-S2 identifier
            return "DVB-S2"
        elif data[0:3] == b'\x1A\xCF\xFC':  # CCSDS identifier
            return "CCSDS"
    return None


# Heuristic fuzzing
def heuristic_fuzz(data, common_value):
    fuzzed_data = bytearray(data)
    common_value_len = len(common_value)

    # Check if common_value is present and apply XOR
    for i in range(len(fuzzed_data) - common_value_len + 1):
        if fuzzed_data[i:i + common_value_len] == common_value:
            for j in range(common_value_len):
                fuzzed_data[i + j] ^= 0xFF  # Apply XOR

    # Check if data matches DVB-S2 or CCSDS
    protocol = check_protocol(fuzzed_data)

    # If it's DVB-S2 or CCSDS, assign values to common fields
    if protocol == "DVB-S2":
        # Assign values to common DVB-S2 fields
        fuzzed_data[1] = random.randint(0, 15)  # MODCOD
        fuzzed_data[2] = random.choice([0, 1])  # PILOT
        fuzzed_data[3] = random.randint(20, 35)  # ROLL-OFF
        fuzzed_data[4] = random.choice([16200, 64800])  # FRAME LENGTH

    elif protocol == "CCSDS":
        # Assign values to common CCSDS fields
        fuzzed_data[1] = random.randint(1, 255)  # SPACECRAFT ID
        fuzzed_data[2] = random.randint(0, 7)  # VIRTUAL CHANNEL ID
        fuzzed_data[3] = random.randint(1, 10)  # FRAME LENGTH
        fuzzed_data[4] = random.choice([True, False])  # REED-SOLOMON ENCODING

    return fuzzed_data


# Send signal parameters to SignalGeneration
def send_signal_params_to_generation(freq, power, bandwidth):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 6789))  # SignalGeneration port
    params = f"freq={freq};power={power};bandwidth={bandwidth}"
    client.send(params.encode("utf-8"))
    client.close()


# Generate and send fake GNSS signal with GPS-SDR-SIM
def generate_and_send_gnss_signal(lat, lon, altitude, time):
    default_nav_file = "brdc3540.14n"  # Default navigation data file
    cmd = [
        "gps-sdr-sim",
        "-e", default_nav_file,
        "-l", f"{lat},{lon},{altitude}",
        "-t", str(time),
        "-s", "pluto",  # Use PlutoSDR to send
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        raise RuntimeError(f"Error in GPS-SDR-SIM: {error.decode()}")
    else:
        print("GNSS Signal Generation Output:", output.decode())


# Run GNU Radio script
def run_gnuradio_script(script, args=None):
    if args:
        cmd = ["python3", script] + args
    else:
        cmd = ["python3", script]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        print("Error:", error.decode())
    else:
        print("Output:", output.decode())


# Command-line argument parsing
parser = argparse.ArgumentParser(description="SatTest for controlling GNU Radio functions.")

parser.add_argument("--mode", type=str, choices=["SignalReplay", "SignalFuzzing", "SignalJamming", "GNSSAttacking"], required=True, help="Select operation mode.")

# 在SignalReplay模块中添加参数解析器
parser.add_argument("--recordTime", type=int, default=60, help="Recording time in seconds (default: 60)")

# SignalFuzzing mode parameters
parser.add.argument("--fuzzing", type=str, choices=["random", "heuristic"], required=True, help="Select fuzzing strategy.")

# SignalJamming mode additional parameters
parser.add.argument("--freq", type=str, help="Set jamming signal frequency.")
parser.add.argument("--power", type.str, help="Set jamming signal power.")
parser.add.argument("--bandwidth", type.str, help="Set jamming signal bandwidth.")

# GNSSAttacking mode parameters
parser.add.argument("--lat", type.float, required=True, help="Set GNSS signal latitude.")
parser.add.argument("--lon", type.float, required=True, help="Set GNSS signal longitude.")
parser.add.argument("--altitude", type.float, required=True, help="Set GNSS signal altitude.")
parser.add.argument("--time", type.int, required=True, help="Set GNSS signal time.")


args = parser.parse_args()

if args.mode == "SignalReplay":
    # Use TCP to start or stop recording in `recording.py`
    def send_command_to_recording(command):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 5678))
        client.send(command.encode("utf-8"))
        client.close()

    # Start recording
    send_command_to_recording("START")
    time.sleep(args.recordTime)  # Record for recordTime seconds
    send_command_to_recording("STOP")

    # Call `playback.py` to play signal
    run_gnuradio_script("playback.py")

elif args.mode == "SignalFuzzing":
    # Receive signal data and store it
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 1234))
    server.listen(1)

    conn, addr = server.accept()
    data = conn.recv(1024)

    with open("flow_data.bin", "wb") as f:
        f.write(data)

    # Build common values
    common_value = build_common_values_from_file("flow_data.bin")

    # Apply fuzzing based on the selected strategy
    if args.fuzzing == "random":
        fuzzed_data = random_fuzz(data)
    elif args.fuzzing == "heuristic":
        fuzzed_data = heuristic_fuzz(data, common_value)

    # Send fuzzed data through TCP to Modulation_coding.py
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect(("127.0.0.1", 4567))  # Port for Modulation_coding.py
    tcp_client.send(fuzzed_data)
    tcp_client.close()

elif args.mode == "SignalJamming":
    # Get frequency, power, and bandwidth
    freq = args.freq if args.freq else "2.4G"  # Default to 2.4 GHz
    power = args.power if args.power else "30"  # Default to 30 dBm
    bandwidth = args.bandwidth if args.bandwidth else "10M"  # Default to 10 MHz

    # Send signal parameters to SignalGeneration
    send_signal_params_to_generation(freq, power, bandwidth)

elif args.mode == "GNSSAttacking":
    lat = args.lat
    lon = args.lon
    altitude = args.altitude
    time = args.time

    # Generate and send fake GNSS signal
    generate_and_send_gnss_signal(lat, lon, altitude, time)
