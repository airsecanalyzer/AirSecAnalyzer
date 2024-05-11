# AirSecAnalyzer

AirSecAnalyzer is designed for testing the security of satellite modems through satellite communication interface. This project contains multiple scripts to perform different functions, including signal replay, signal fuzzing, signal jamming and GNSS attack. It is compatible with PlutoSDR/USRP B210 for signal transmission and reception.

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
  - [SignalReplay](#signalreplay)
  - [SignalFuzzing](#signalfuzzing)
  - [SignalJamming](#signaljamming)
  - [GNSS Attacking](#gnss-attacking)
- [Components](#components)
- [Contributing](#contributing)
- [License](#license)

## Description
AirSecAnalyzer allows users to perform the following signal-related operations, including:
- **SignalReplay**: Record and replay signals.
- **SignalFuzzing**: Fuzz signals with random and heuristic methods.
- **SignalJamming**: Configure and transmit jamming signals.
- **GNSS Attacking**: Generate and send false GNSS signals.


## Installation

### Connecting Hardware

To ensure proper connection and operation, follow these steps to connect your computer, SDR, and satellite modem:

![Connecting Hardware Diagram](images/airSecAnalyzer_hardware_connection.png)


1. **Computer to SDR**:
   - Use a USB cable to connect your computer to SDR. 
   - Once connected, check that the SDR is recognized by your operating system. On Linux, you can use `lsusb` to list USB devices.

2. **SDR to Satellite Modem**:
   - Depending on your setup, you might need two coaxial cables (such as SMA to SMA) to connect the output of SDR to the RF input (RF_IN) of the satellite modem and connect the input of SDR to the RF output (RF_OUT) of the satellite modem.
   - Ensure the connections are secure and that the impedance matches the requirements of your equipment. Typically, 50-ohm coaxial cables are used in these applications. In some scenarios, you can also complete the corresponding tests with an RF antenna, such as in signal replay, signal jamming, or GNSS spoofing scenarios.

### Software Configuration


To install and use AirSecAnalyzer, ensure that the following prerequisites are met:
- GNU Radio: Ensure GNU Radio is installed and properly configured. For Windows, you can use Conda to install GNU Radio.
- SDR: Ensure SDR is connected and operational.

Install GNU Radio on your system:
```bash
# Ubuntu
sudo apt-get update
sudo apt-get install gnuradio

# Conda (cross-platform)
conda install -c conda-forge gnuradio
```

## Usage
AirSecAnalyzer has multiple modes, each associated with a specific script and function. Below are usage examples for each mode.

### SignalReplay
Controls signal recording via `recording.py` and playback via `playback.py`. The upper-level application can send TCP commands to start or stop recording.

- Start signal replay: `python3 SatTest.py --mode SignalReplay --recordTime 60`

60 is a sample time for recording and replaying. You can configure your own timing. 
### SignalFuzzing
Fuzzes signals with random and heuristic methods. The fuzzed signals are sent to `Modulation_coding.py` for modulation and coding.

- Random fuzzing: `python3 SatTest.py --mode SignalFuzzing --fuzzing random`
- Heuristic fuzzing: `python3 SatTest.py --mode SignalFuzzing --fuzzing heuristic`

### SignalJamming
Configures and transmits jamming signals. Users can set frequency, power, and bandwidth.

- Jamming with specified parameters: `python3 SatTest.py --mode SignalJamming --freq 2.4G --power 30 --bandwidth 10M`

### GNSS Attacking
Uses GPS-SDR-SIM to generate and send false GNSS signals.

- Generate and send false GNSS signals: `python3 SatTest.py --mode GNSSAttacking --lat 37.7749 --lon -122.4194 --altitude 10 --time 1592653589`

## Components
AirSecAnalyzer comprises several scripts, each with its own function:
- **SatTest.py**: Upper-level control for managing different modes and operations.
- **Modulation_coding.py**: Modulates and encodes signals based on TCP-received data.
- **Demodulation_decoding.py**: Demodulates and decodes signals from PlutoSDR.
- **SignalGeneration.py**: Generates and sends signals based on received parameters.
- **Recording.py**: Records signals based on TCP control commands.
- **Playback.py**: Plays back recorded signals based on TCP control commands.

## Contributing
Contributions to AirSecAnalyzer are welcome. Please follow the project's coding standards and ensure compatibility with GNU Radio and corresponding SDR.

## License
This project is licensed under the MIT License. For more information, see the LICENSE file.
