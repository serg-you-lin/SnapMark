"""
BACKWARD COMPATIBILITY: All existing code continues to work identically.
NEW FEATURES: Each operation can now work on single files + static method for folders.
"""
import os
import ezdxf
from abc import ABC, abstractmethod
from pathlib import Path

# Import BackupManager if available
try:
    from snapmark.utils.backup_manager import BackupManager
    BACKUP_AVAILABLE = True
except ImportError:
    BACKUP_AVAILABLE = False

from snapmark.mark_algorithm.mark_algorithm import *
from snapmark.entities.add_entities import *
from snapmark.checking.checking import *
from snapmark.utils.helpers import find_dxf_files


class Operation(ABC):
    """
    Base class for all operations on DXF files.

    Supports three modes of use:
    1. Legacy: execute(doc, folder, file_name) - used by iteration_manager
    2. Single file: execute_single(file_path, **kwargs) - works on a single file
    3. Batch: process_folder(folder_path, **kwargs) - static method for folders
    """
    
    def __init__(self):
        self.create_new = True 
        self.message_text = None
    
    # ========== LEGACY METHODS (kept for backward compatibility) ==========

    @abstractmethod
    def execute(self, doc, folder, file_name):
        """
        Legacy method for compatibility with iteration_manager.
        Subclasses MUST implement this method.
        """
        pass
    
    def message(self, file_name):
        """Prints a completion message for the operation."""
        if self.message_text:
            print(self.message_text)
        else:
            print(f"Operation complete on {file_name}")
    
    # ========== NEW METHODS (Phase 2) ==========
    
    def execute_single(self, file_path: str, use_backup: bool = True) -> bool:
        """
        Executes the operation on a single file.
        
        Args:
            file_path: Full path of the DXF file.
            use_backup: If True, uses BackupManager to preserve the original.
            
        Returns:
            bool: True if the file was modified, False otherwise.
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File non trovato: {file_path}")
        
        # Backup handling
        if use_backup and BACKUP_AVAILABLE:
            BackupManager.ensure_original(file_path)
        
        # Extract folder and filename from path
        folder = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        
        # Open the file
        doc = ezdxf.readfile(file_path)
        
        # Execute operation (calls the legacy method)
        modified = self.execute(doc, folder, file_name)
        
        # Save if modified
        if modified:
            doc.saveas(file_path)
            self.message(file_name)
            return True
        
        return False
    
    @classmethod
    def process_folder(cls, folder_path: str, operation_instance: 'Operation', 
                      use_backup: bool = True, recursive: bool = False,
                      file_pattern: str = "*.dxf") -> dict:
        """
        Static method to apply an operation to all DXF files in a folder.
        
        Args:
            folder_path: Path of the folder.
            operation_instance: Instance of the operation to apply.
            use_backup: If True, creates .bak backups of the original files.
            recursive: If True, processes subfolders as well.
            file_pattern: Pattern to filter files (default: "*.dxf").
            
        Returns:
            dict: Statistics containing {'processed': int, 'modified': int, 'errors': list}.
        """

        stats = {
            'processed': 0,
            'modified': 0,
            'errors': []
        }

        dxf_files = find_dxf_files(folder_path, recursive=recursive)
        
        for file_path in dxf_files:
            try:
                modified = operation_instance.execute_single(str(file_path), use_backup=use_backup)
                stats['processed'] += 1
                if modified:
                    stats['modified'] += 1
            except Exception as e:
                error_msg = f"Error on {file_path.name}: {str(e)}"
                stats['errors'].append(error_msg)
                print(f"❌ {error_msg}")
        
        # Final report
        print(f"\n✓ Processed: {stats['processed']}")
        print(f"✓ Modified: {stats['modified']}")
        if stats['errors']:
            print(f"❌ Errors: {len(stats['errors'])}")
        
        return stats


# ========== CONCRETE IMPLEMENTATIONS ==========

class AddMark(Operation):
    """Aggiunge marcatura numerica ai file DXF."""
    
    def __init__(self, sequence, scale_factor=50, space=1.5, min_char=5,
                 max_char=20, arbitrary_x=None, arbitrary_y=None, align='c',
                 start_y=1, step=2, margin=1, down_to=None, layer='MARK', 
                 filtered_layer="0"):
        """
        Initializes the AddMark operation with the specified parameters.

        Args:
            sequence: The sequence of numbers to be added.
            scale_factor (float): The scaling factor for the sequence (default is 50).
            space (float): The spacing between characters (default is 1.5).
            min_char (float): The minimum height for characters (default is 5).
            max_char (float): The maximum height for characters (default is 20).
            arbitrary_x (float, optional): The arbitrary x-coordinate for placement (default is None).
            arbitrary_y (float, optional): The arbitrary y-coordinate for placement (default is None).
            align (str): The alignment of the sequence ('l' for left, 'c' for center, 'r' for right; default is 'c').
            start_y (float): The starting y-coordinate for the search (default is 1).
            step (float): The step size for incrementing or decrementing the y-coordinate during the search (default is 2).
            margin (float): The margin to be added around the sequence (default is 1).
            down_to (float, optional): The minimum height to which the sequence can be resized (default is None).
            layer (str): The layer on which to place the markings (default is 'MARK').
            filtered_layer (str): The layer from which to filter entities for placement (default is "0").
        """

        super().__init__()
        self.sequence = sequence
        self.scale_factor = scale_factor
        self.space = space
        self.min_char = min_char
        self.max_char = max_char
        self.arbitrary_x = arbitrary_x
        self.arbitrary_y = arbitrary_y
        self.align = align
        self.start_y = start_y
        self.step = step
        self.margin = margin
        self.down_to = down_to
        self.layer = layer
        self.filtered_layer = filtered_layer
        self.sequence_position = NS()

    def __repr__(self):
        return f"AddMark(sequence={self.sequence})"

    def execute(self, doc, folder, file_name):
        """Legacy method - maintains original logic for compatibility."""
        # Decidi fattore scala
        scale_factor = comp_sf(doc, self.scale_factor)
        
        sequence = self.sequence.get_sequence_text(folder, file_name)
        
        start_x, start_y = comp_center_point((doc))
        self.sequence_position = place_sequence(
            doc, sequence, scale_factor, self.filtered_layer, self.space, 
            self.min_char, self.max_char, self.arbitrary_x, self.arbitrary_y, 
            self.align, self.start_y, self.step, self.margin, self.down_to
        )

        # Add numbers to the 'MARK' layer
        add_numbers_to_layer(doc, self.sequence_position, self.layer)
        return self.create_new
                     
    def message(self, file_name):
        if len(self.sequence_position.sequence) == 0:
            self.message_text = f"⚠ No space found for the sequence in file {file_name}." 
        else:
            self.message_text = f"✓ Sequence added to {file_name}"
        print(self.message_text)


class SubstituteCircle(Operation):
    """Replaces existing circles with new circles of a different radius."""
    
    def __init__(self, find_circle_function, new_radius=None, new_diameter=None, layer='0'):
        """
        Initializes the SubstituteCircle operation with the specified parameters.

        Args:
            find_circle_function: A function to find circles in the document.
            new_radius (float, optional): The new radius for the circles (default is None).
            new_diameter (float, optional): The new diameter for the circles (default is None).
            layer (str): The layer on which to place the new circles (default is '0').

        Raises:
            ValueError: If neither new_radius nor new_diameter is specified.
        """

        super().__init__()
        self.find_circle_function = find_circle_function
        self.new_radius = new_radius 
        self.new_diameter = new_diameter
        self.layer = layer
        
        if self.new_radius is None and self.new_diameter is None:
            raise ValueError('You must specify either new_radius or new_diameter.')

    def execute(self, doc, folder, file_name):
        """Executes the operation to replace circles in the document."""

        holes = self.find_circle_function(doc)

        if self.new_diameter:
            self.new_radius = self.new_diameter / 2

        center_holes = find_circle_centers(holes)
        add_circle(doc, center_holes, radius=self.new_radius, layer=self.layer)
        delete_circle(doc, holes)

        return self.create_new
    
    def message(self, file_name):
        if self.new_diameter:
            self.message_text = f"✓ Holes in {file_name}: nuovo diametro {self.new_diameter}"
        else:
            self.message_text = f"✓ Holes in {file_name}: nuovo raggio {self.new_radius}"
        print(self.message_text)


class AddX(Operation):
    """Adds an 'X' shape at the locations of circles."""
    
    def __init__(self, find_circle_function, x_size=8, layer='MARK', delete_hole=True):
        """
        Initializes the AddX operation with the specified parameters.

        Args:
            find_circle_function: A function to find circles in the document.
            x_size (float): The size of the 'X' shape (default is 8).
            layer (str): The layer on which to place the 'X' shapes (default is 'MARK').
            delete_hole (bool): If True, deletes the original circles (default is True).
        """

        super().__init__()
        self.find_circle_function = find_circle_function
        self.x_size = x_size
        self.layer = layer
        self.delete_hole = delete_hole

    def execute(self, doc, folder, file_name):
        """Executes the operation to add 'X' shapes at the locations of circles."""
        holes = self.find_circle_function(doc)
        center_holes = find_circle_centers(holes)
        
        if self.delete_hole:
            delete_circle(doc, holes)
            
        add_x(doc, center_holes, x_size=self.x_size, layer=self.layer)
        return self.create_new
    
    def message(self, file_name):
        self.message_text = f"✓ 'X' added to {file_name}"
        print(self.message_text)


class RemoveCircle(Operation):
    """Removes circles from the file."""
    
    def __init__(self, find_circle_function):
        """
        Initializes the RemoveCircle operation with the specified parameters.

        Args:
            find_circle_function: A function to find circles in the document.
        """

        super().__init__()
        self.find_circle_function = find_circle_function

    def execute(self, doc, folder, file_name):
        """Executes the operation to remove circles from the document."""
        holes = self.find_circle_function(doc)
        delete_circle(doc, holes)
        return self.create_new
    
    def message(self, file_name):
        self.message_text = f"✓ Holes removed from {file_name}"
        print(self.message_text)


class RemoveLayer(Operation):
    """Removes a layer from the file."""
    
    def __init__(self, layer):
        """
        Initializes the RemoveLayer operation with the specified parameters.

        Args:
            layer (str): The name of the layer to be removed.
        """

        super().__init__()
        self.layer = layer

    def execute(self, doc, folder, file_name):
        """Executes the operation to remove the specified layer from the document."""
        delete_layer(doc, self.layer)
        return self.create_new

    def message(self, file_name):
        self.message_text = f"✓ Layer '{self.layer}' removed from {file_name}"
        print(self.message_text)


class PrintLayers(Operation):
    """Prints the layers present in the file (does not modify)."""
    
    def __init__(self):
        super().__init__()
        self.create_new = False

    def execute(self, doc, folder, file_name):
        print_layers(doc)
        return self.create_new
    
    def message(self, file_name):
        self.message_text = f"Layer presenti in {file_name}:"
        print(self.message_text)

