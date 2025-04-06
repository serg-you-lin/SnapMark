# SnapMark
SnapMark is a Python-based tool designed to apply customizable markings to DXF files using a flexible sequence logic. It leverages the ezdxf library to manipulate DXF files and supports operations like adding counters, alignment, character scaling, and more.

## Features
Automatic DXF file scanning and processing

Flexible character sequencing (e.g., counters, file-based naming, custom patterns)

Text scaling, alignment, and positioning

Modular structure for extending operations

Easy integration into existing workflows

# Quick Start
## 1. Clone the repository:

```bash
git clone https://github.com/tuo-utente/snapmark.git
```
## 2. Install the dependencies:


```bash
pip install -r requirements.txt
```
## 3.Run the example:

```bash
python examples/run_example.py
```
The script will process the sample DXF files located in examples/input/ and save the marked versions to a new folder (e.g., examples/input_Marked/).

# Project Structure
```bash
SnapMark/
│
├── snapmark/                # Main package
│   ├── snapmark.py          # Main module combining logic
│   ├── operations/          # Marking operations
│   ├── sequence/            # Sequence logic
│   ├── checking/            # Input validation
│   └── __init__.
```
