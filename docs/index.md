# SnapMark Documentation

Welcome to SnapMark.

SnapMark is a Python library that generates laser-engraving DXF paths
for labeling and identifying parts. This documentation will guide you through:

- Available parameters → see parameters.md
- Built-in shortcuts → see shortcuts.md
- Processing pipelines → see pipeline.md
- Sequence systems → see sequences.md
- Backup system → backup.md 

## Examples and Usage

SnapMark comes with a set of ready-to-run examples located in the `examples/` folder.  
These examples demonstrate common operations, including:

- **Basic Marking** → `01_basic_marking.py`: simple text marking on DXF files.  
- **Custom Sequence** → `02_custom_sequence.py`: how to create and apply a custom marking sequence to DXF files, allowing for flexible text placement and ordering.  
- **Counting Holes** → `03_count_holes.py`: counts holes in a folder of DXF files, with optional multipliers.  
- **Pipelines** → `04_pipeline_advanced.py`: build and execute a processing pipeline, combining multiple operations (marking, hole counting, etc.) in a single automated workflow.
- **Restore Backup** → `05_restore_backup.py`: shows how to restore original DXF files from backups.

> ⚠️ Note: The restore operation always works on the original file as it was before any modifications, provided `use_backup=True`. This ensures that multiple trials or tests never accumulate changes on the same DXF file.

Each example can be run directly, and paths are relative to the project root. For more details, see the comments inside each script.

