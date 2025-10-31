"""
Restore DXF files from backups
===============================

This script shows how to restore files from their .bak backups.

Use cases:
- Undo unwanted modifications
- Reset files to original state
- Restore after testing
"""

import snapmark as sm

# Option 1: Restore a single file
sm.restore_backup("input/F1.dxf", delete_backup=False)

# Option 2: Restore all files in a folder
sm.restore_backup("input/", delete_backups=False, recursive=False)

# Option 3: Restore recursively and delete backups
sm.restore_backup(".", delete_backups=True, recursive=True)

print("✓ Restoration complete!")  