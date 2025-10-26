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
git clone https://github.com/serg-you-lin/snapmark.git
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

## Parameters:
### Object:
suffix: adding suffix on both new file and new folder.

### AddMark operation:
sequence: text put on file.
layer: choose layer where put the text
min_char/max_char: minimum/maximum heigth of text
align: part f file where mark is located ('r'->right, 'l'->left, 'c'->center)
start_y: minimum place for text on y axis
down to: allowing text toi be smaller if does not fit while min_char. 

### Sequence:
You can built a fix sequence or concatenate your sequence by file name, folder name, etc.

## Other features
### CountHoles
```bash
ToMark.add_operation(CountHoles(find_circle_by_radius(max_diam=5.2, min_diam=4.8)))
```
In this example, you can count all holes between 4.8 and 5.2 mm diameter in all files on a folder. Total and partial result.

### AddX
```bash
ToMark.add_operation(AddX(find_circle_by_radius(min_diam=2, max_diam=15), size=15, delete_hole=True, layer='Marcatura'))
```
In this example, all holes between 2 and 15 mm will be substituite from a 'X' sign of 15mm, on 'Marcatura' layer. Holes will been deleted.

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

## License
MIT License — feel free to use, modify, and share with attribution.

## Contributions
Pull requests are welcome! If you find issues or have suggestions, please open an issue in the repository.

## Author
Federico Sidraschi https://www.linkedin.com/in/federico-sidraschi-059a961b9/
