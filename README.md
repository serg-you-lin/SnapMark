# SnapMark

SnapMark is a Python library for applying **customizable and intelligent text markings** to DXF (AutoCAD) files.  
Built on top of [`ezdxf`](https://ezdxf.mozman.at/), it provides a **simple but powerful API** for batch processing, automatic alignment, and sequence-based text generation.

It gives you full control over:
- **Marking position** — choose exact coordinates or automatic placement based on geometry  
- **Mark size and scaling** — adjust text size dynamically or with fixed scale factors  
- **Smart collision avoidance** — automatically avoids internal contours, holes, and cutouts  
- **Flexible automation** — process entire folders, subfolders, or single DXF files with custom pipelines  

Whether you’re marking parts for manufacturing, numbering drawings for CNC cutting, or adding production info automatically, SnapMark helps you make your workflow faster and more consistent.


[![PyPI version](https://badge.fury.io/py/snapmark.svg)](https://badge.fury.io/py/snapmark)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation
```bash
pip install snapmark
```

## Quick Start
```python
import snapmark as sm

# Mark all DXF files with their filename
sm.mark_by_name("path/to/drawings")

# Custom sequence: filename + folder name
seq = (sm.SequenceBuilder()
       .file_name()
       .folder(num_chars=2)   # firts 2 chars of folder name
       .build())

sm.mark_with_sequence("path/to/drawings", seq, scale_factor=100)
```

## Features

- ✅ **Simple API** - Mark files in one line
- ✅ **Custom sequences** - Build complex marking logic with SequenceBuilder
- ✅ **Batch operations** - Process entire folders with IterationManager
- ✅ **Built-in backup** - Automatic .bak files before modifications
- ✅ **Hole counting** - Count and analyze circles in drawings
- ✅ **Extensible** - Easy to add custom operations

## Use Cases

- **Manufacturing**: Add part numbers and quantities to production drawings
- **CAM workflows**: Automatically mark drawings before CNC processing
- **Quality control**: Count holes and verify drawing specifications
- **Batch processing**: Apply consistent markings across large drawing sets

## Examples

### Basic Marking
```python
import snapmark as sm

# Mark with filename (simplest)
sm.mark_by_name("drawings/")

# Mark with first part of filename (e.g., "PART" from "PART_123_Q5.dxf")
sm.mark_by_splitted_text("drawings/", separator='_', part_index=0)
```

### Custom Sequences
```python
import snapmark as sm

# Extract part number from filename like "S532_P5_SP4_Q2.dxf"
def extract_part_number(folder, filename):
    import re
    match = re.search(r'P(\d+)', filename)
    return f"P{match.group(1)}" if match else ""

seq = (sm.SequenceBuilder()
       .file_part(separator='_', part_index=0)  # "S532"
       .custom(extract_part_number)              # "P5"
       .build())

sm.mark_with_sequence("drawings/", seq)
# Result: "S532-P5"
```

### Count Holes
```python
import snapmark as sm

# Simple count
stats = sm.quick_count_holes("drawings/", min_diam=5, max_diam=10)
print(f"Total holes: {stats['total_count']}")

# With multiplier (extract quantity from filename, e.g. S532_P1_S235JR_SP4_Q2 where Q determines the number of identical pieces to cut) 
def get_quantity(filename):
    import re
    match = re.search(r'Q(\d+)', filename)
    return int(match.group(1)) if match else 1

stats = sm.quick_count_holes(
    "drawings/", 
    min_diam=5, 
    max_diam=10,
    multiplier=get_quantity
)
print(f"Total holes (with qty): {stats['total_count']}")
```

### Advanced Pipeline
```python
import snapmark as sm

# Multiple operations in sequence
seq = sm.SequenceBuilder().file_name().build()

manager = sm.IterationManager("drawings/", use_backup_system=True)
manager.add_operation(
    sm.Aligner(),                    # Align drawing
    sm.AddMark(seq, scale_factor=100),  # Add marking
    sm.CountHoles(sm.find_circle_by_radius(5, 10))  # Count holes
)
manager.execute()
```

### Recursive Marking (Batch Mode)
```python
import snapmark as sm

# Build a sequence: filename + first 2 chars of folder name
seq = (sm.SequenceBuilder()
       .file_name()
       .folder(num_chars=2)
       .build())

# Apply marking recursively on all DXF files in subfolders
manager = sm.IterationManager("dxfs", use_backup_system=True)
manager.add_operation(sm.AddMark(seq, scale_factor=100))
manager.execute(recursive=True)
```

### Quick pipeline on a single file
```python
import snapmark as sm

seq = sm.SequenceBuilder().file_name().build()

sm.single_file_pipeline(
    "drawing.dxf",
    sm.Aligner(),
    sm.AddMark(seq, scale_factor=100),
    sm.AddX(sm.find_circle_by_radius(5, 10), x_size=8), # Replaces 5–10mm holes with X marks for manual drilling
    use_backup=True
)
```

### Restore Backups
```python
import snapmark as sm

# Undo all changes
sm.restore_backup("drawings/")

# Restore recursively in subfolders
sm.restore_backup("drawings/", recursive=True)

# Restore but keep .bak files
sm.restore_backup("drawings/", delete_backups=False)
```

## API Overview

### Shortcuts (Simple Usage)

- `mark_by_name(folder)` - Mark with filename
- `mark_by_splitted_text(folder, separator, part_index)` - Mark with filename part
- `mark_with_sequence(folder, sequence)` - Mark with custom sequence
- `quick_count_holes(folder, min_diam, max_diam)` - Count holes
- `restore_backup(folder)` - Restore from backups
- `process_single_file(file, *operations)` - Pipeline on single file

### SequenceBuilder (Custom Sequences)
```python
seq = (sm.SequenceBuilder()
       .file_name()                    # Full filename
       .file_part(separator, index)    # Split filename
       .folder(num_chars)              # Folder name
       .literal("text")                # Fixed text
       .custom(function)               # Custom function
       .set_separator("-")             # Join character
       .build())
```

### Operations (Advanced)

- `AddMark(sequence)` - Add text marking
- `Aligner()` - Aligns the drawing along its longest side in the X direction.
- `CountHoles(find_func)` - Count circles
- `AddX(find_func, x_size)` - Add X marks
- `RemoveCircle(find_func)` - Remove circles
- `SubstituteCircle(find_func, new_radius)` - Replace circles

### IterationManager (Batch Processing)
```python
manager = sm.IterationManager(folder, use_backup_system=True)
manager.add_operation(operation1, operation2, ...)
manager.execute(recursive=False)
```

## Requirements

- Python 3.8+
- ezdxf >= 1.0.0

## Documentation

For detailed documentation and more examples, visit the [GitHub repository](https://github.com/serg-you-lin/SnapMark).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Federico Sidraschi**  
[LinkedIn](https://www.linkedin.com/in/federico-sidraschi-059a961b9/) | [GitHub](https://github.com/serg-you-lin)

## Acknowledgments

Built with [ezdxf](https://ezdxf.mozman.at/) - the excellent DXF library for Python.

---

**Keywords**: DXF, CAD, AutoCAD, marking, automation, batch processing, manufacturing, CNC, CAM