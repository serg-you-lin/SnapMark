# Backup System

SnapMark includes a built-in **backup system** to ensure your DXF files are safe during processing.

---

## ⚡ How it works

### 1. **Automatic restoration**
- Before executing any operation, SnapMark **checks if a backup exists**.
- If a backup exists, it **automatically restores the original file**, ensuring every operation works on a clean, unmodified file.
- This guarantees that **multiple processing attempts do not accumulate changes** or corrupt your file.

### 2. **Backup creation**
- By default, SnapMark creates a backup **before modifying any DXF file**.
- The backup is stored in the same folder with a `.bak` extension.
- **Example**: `part.dxf` → `part.dxf.bak`

### 3. **Behavior during read-only operations**
- Operations like `CountHoles` **do not modify files** and therefore do not create backups.
- However, they will still restore the file from backup if one exists, ensuring consistent results.

---

## ⚙️ Configuration

### Backup enabled by default

The backup system is active by default (`use_backup=True`).

### Disable backup per operation

You can disable backup for specific operations if needed:
```python
operation.execute_single("path/to/file.dxf", use_backup=False)
```

⚠️ **Warning**: Disabling backup makes modifications permanent. Use with caution.

---

## 🔧 Manual restoration

If you need to manually restore files from backups, SnapMark provides the `restore_backup()` function.

### Basic syntax
```python
import snapmark as sm

# Restore a single file
sm.restore_backup("path/to/file.dxf", delete_backups=False)
```

### Parameters

- **`path`**: Path to file or folder to restore
- **`delete_backups`**: If `True`, deletes `.bak` files after restoration (default: `False`)
- **`recursive`**: If `True`, recursively processes all subfolders (default: `False`)

### Usage examples
```python
import snapmark as sm

# Option 1: Restore a single file (keeps backup)
sm.restore_backup("input/F1.dxf", delete_backups=False)

# Option 2: Restore all files in a folder (deletes backups)
sm.restore_backup("input/", delete_backups=True, recursive=False)

# Option 3: Restore recursively in all subfolders
sm.restore_backup(".", delete_backups=True, recursive=True)

print("✓ Restoration complete!")
```

### Common use cases

- **Undo unwanted modifications**: Quickly restore files to original state
- **Reset after testing**: Return files to clean version after experiments
- **Project cleanup**: Delete backups after confirming modifications are correct

> **📖 For more details and complete examples**, see:  
> [`examples/restore_backups.py`](../examples/05_restore_backup.py)

---

## ✅ Best practices

### 1. Always keep backups enabled
Unless you are absolutely sure modifications are irreversible, keep the backup system active.

### 2. Regularly check `.bak` files
Periodically verify the integrity of your backups to ensure they are usable when needed.

### 3. Use manual restoration wisely
- **Keep backups** (`delete_backups=False`) during development and testing
- **Delete backups** (`delete_backups=True`) only when you are sure modifications are final

---

## 🛠️ Advanced programmatic restoration

For advanced use cases, you can access the `BackupManager` directly:
```python
from snapmark.utils.backup_manager import BackupManager

# Restore a specific file
BackupManager.restore("path/to/file.dxf")
```

> **Note**: The `sm.restore_backup()` function is a more convenient shortcut and is recommended for everyday use.