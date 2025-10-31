"""
core.py - Core components of SnapMark.

Contains IterationManager for multiple batch operations.
"""
import os
import ezdxf
from pathlib import Path
from snapmark.utils.helpers import find_dxf_files

try:
    from .utils.backup_manager import BackupManager
    BACKUP_AVAILABLE = True
except ImportError:
    BACKUP_AVAILABLE = False


class IterationManager:
    """
    Manages applying multiple operations in sequence on DXF files.
    
    Example:
        >>> manager = IterationManager("folder_path")
        >>> manager.add_operation(AddMark(...), CountHoles(...))
        >>> manager.execute()
    """
    
    def __init__(self, folder_path, use_backup_system=True):
        """
        Initializes the IterationManager with the specified folder path and backup option.

        Args:
            folder_path (str): The path of the folder containing the DXF files.
            use_backup_system (bool): If True, uses .bak for backups (recommended).
        """

        self.folder_path = folder_path
        self.operation_list = []
        self.use_backup_system = use_backup_system and BACKUP_AVAILABLE
        
        if use_backup_system and not BACKUP_AVAILABLE:
            print("⚠ BackupManager not available")
    
    def add_operation(self, *operations):
        """Adds operations to the pipeline."""
        for op in operations:
            self.operation_list.append(op)
    
    def execute(self, file_pattern="*.dxf", recursive=False):
        """
        Executes all operations on the files in the specified folder.
        
        Args:
            file_pattern (str): Pattern to filter files (e.g., "F*.dxf").
            recursive (bool): If True, includes subfolders.
        
        Returns:
            dict: Statistics containing {'processed': int, 'modified': int, 'errors': list}.
        """

        if not self.operation_list:
            print("⚠ No operations added")
            return {'processed': 0, 'modified': 0, 'errors': []}
        
        dxf_files = find_dxf_files(self.folder_path, recursive)

        if self.use_backup_system:
            print("🔧 Backup mode active")
        
        # Processa file
        stats = {'processed': 0, 'modified': 0, 'errors': []}
        
        for file_path in dxf_files:
            try:
                modified = self._process_single_file(str(file_path))
                stats['processed'] += 1
                if modified:
                    stats['modified'] += 1
            except Exception as e:
                error_msg = f"Error on {file_path.name}: {str(e)}"
                stats['errors'].append(error_msg)
                print(f"❌ {error_msg}")
        
        # Final messages
        self._final_messages()
        
        # Report
        print(f"\n✓ Processed: {stats['processed']}")
        print(f"✓ Modified: {stats['modified']}")
        if stats['errors']:
            print(f"❌ Errors: {len(stats['errors'])}")
        
        return stats
    
    def _process_single_file(self, file_path: str) -> bool:
        """Applies operations to a single file."""
        
        # Backup
        if self.use_backup_system:
            BackupManager.ensure_original(file_path)
        
        # Extract folder and filename
        folder = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        
        # Open file
        doc = ezdxf.readfile(file_path)
        
        # Apply operations
        should_save = False
        for operation in self.operation_list:
            temp_should_save = operation.execute(doc, folder, file_name)
            should_save = should_save or temp_should_save
            operation.message(file_name)
        
        # Save if necessary
        if should_save:
            doc.saveas(file_path)
            return True
        
        return False
    
    def _final_messages(self):
        """Prints final messages (e.g., from Counter)."""
        
        try:
            from .operations.counter import Counter
            for operation in self.operation_list:
                if isinstance(operation, Counter):
                    operation.count_message()
        except ImportError:
            pass
    
    def file_selection_logic(self, filter_files=None):
        """DEPRECATED: Use execute() instead."""
        import warnings
        warnings.warn(
            "file_selection_logic() is deprecated. Use execute().",
            DeprecationWarning,
            stacklevel=2
        )
        
        pattern = "*.dxf"
        if filter_files:
            if isinstance(filter_files, str):
                pattern = filter_files
            elif isinstance(filter_files, list) and filter_files:
                pattern = filter_files[0]
        
        return self.execute(file_pattern=pattern, recursive=False)


# Alias for backward compatibility with old scripts
iteration_manager = IterationManager