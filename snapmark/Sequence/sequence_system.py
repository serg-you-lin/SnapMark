"""
Sequence system for SnapMark - Hybrid version.

Maintains Conc for compatibility, introduces SequenceBuilder as the main API.
"""

import os
from typing import List, Callable
from abc import ABC, abstractmethod


# ========== BASE INTERFACE ==========

class Sequence(ABC):
    """Base interface for all sequence types."""
    
    @abstractmethod
    def get_sequence_text(self, folder: str, file_name: str) -> str:
        """Generates the sequence text based on the provided folder and file name."""
        pass


# ========== NEW SYSTEM: COMPONENTS ==========

class SequenceComponent(ABC):
    """Base component - a piece of the sequence."""
    
    @abstractmethod
    def extract(self, folder: str, file_name: str) -> str:
        """Extracts the relevant text based on the provided folder and file name."""
        pass


class LiteralComponent(SequenceComponent):
    """Represents fixed text in the sequence."""

    def __init__(self, text: str):
        """
        Initializes the LiteralComponent with the specified text.

        Args:
            text (str): The fixed text to be included in the sequence.
        """

        self.text = text
    
    def extract(self, folder: str, file_name: str) -> str:
        """Returns the fixed text."""
        return self.text


class FileNameComponent(SequenceComponent):
    """Represents the file name without extension."""

    def extract(self, folder: str, file_name: str) -> str:
        """Returns the file name without its extension."""
        return os.path.splitext(file_name)[0]


class FolderNameComponent(SequenceComponent):
    """Represents the folder name (optionally the first N characters)."""

    def __init__(self, num_chars: int = None):
        """
        Initializes the FolderNameComponent with an optional character limit.

        Args:
            num_chars (int, optional): The number of characters to return from the folder name (default is None).
        """

        self.num_chars = num_chars
    
    def extract(self, folder: str, file_name: str) -> str:
        """Returns the folder name, limited to the specified number of characters if provided."""

        folder_name = os.path.basename(os.path.normpath(folder))
        if self.num_chars:
            return folder_name[:self.num_chars]
        return folder_name


class FilePartComponent(SequenceComponent):
    """Represents a part of the file name using a specified separator."""
    
    def __init__(self, separator: str = '_', part_index: int = 0):
        """
        Initializes the FilePartComponent with a separator and part index.

        Args:
            separator (str): The character used to separate parts of the file name (default is '_').
            part_index (int): The index of the part to extract (default is 0).
        """

        self.separator = separator
        self.part_index = part_index
    
    def extract(self, folder: str, file_name: str) -> str:
        """Returns the specified part of the file name based on the separator."""
        base_name = os.path.splitext(file_name)[0]
        parts = base_name.split(self.separator)
        if 0 <= self.part_index < len(parts):
            return parts[self.part_index]
        return ""


class CustomComponent(SequenceComponent):
    """Represents a custom component with a user-defined function."""

    def __init__(self, func: Callable[[str, str], str]):
        """
        Initializes the CustomComponent with a specified function.

        Args:
            func (Callable[[str, str], str]): A function that takes a folder and file name and returns a string.
        """

        self.func = func
    
    def extract(self, folder: str, file_name: str) -> str:
        """Returns the result of the custom function applied to the folder and file name."""

        return self.func(folder, file_name)


# ========== BUILDER ==========

class SequenceBuilder:
    """
    Builds sequences in a readable and composable manner.

    Examples:
        # Simple file name
        seq = SequenceBuilder().file_name().build()
        
        # File name + folder
        seq = (SequenceBuilder()
               .file_name()
               .folder(num_chars=2)
               .build())
        
        # First part of the name (split on '_')
        seq = (SequenceBuilder()
               .file_part(separator='_', part_index=0)
               .build())
    """
    
    def __init__(self):
        """Initializes the SequenceBuilder with an empty list of components and a default separator."""

        self.components: List[SequenceComponent] = []
        self.separator = "-"
    
    def literal(self, text: str) -> 'SequenceBuilder':
        """Adds fixed text to the sequence."""
        self.components.append(LiteralComponent(text))
        return self
    
    def file_name(self) -> 'SequenceBuilder':
        """Adds the full file name (without extension) to the sequence."""
        self.components.append(FileNameComponent())
        return self
    
    def folder(self, num_chars: int = None) -> 'SequenceBuilder':
        """
        Adds the folder name to the sequence.
        
        Args:
            num_chars (int, optional): If specified, takes only the first N characters of the folder name.
        """

        self.components.append(FolderNameComponent(num_chars))
        return self
    
    def file_part(self, separator: str = '_', part_index: int = 0) -> 'SequenceBuilder':
        """
        Adds a part of the file name after splitting it.
        
        Example:
            File: "PART_123_A_5mm.dxf"
            - part_index=0 → "PART"
            - part_index=1 → "123"
            - part_index=2 → "A"
        
        Args:
            separator (str): The character used to separate parts (default is '_').
            part_index (int): The index of the part to extract (default is 0).
        """

        self.components.append(FilePartComponent(separator, part_index))
        return self
    
    def custom(self, func: Callable[[str, str], str]) -> 'SequenceBuilder':
        """Adds a custom component with a user-defined function."""

        self.components.append(CustomComponent(func))
        return self
    
    def set_separator(self, sep: str) -> 'SequenceBuilder':
        """
        Sets the separator between components (default is '-').
        
        Args:
            sep (str): The separator to use between components.
        """

        self.separator = sep
        return self
    
    def build(self) -> 'ComposedSequence':
        """Constructs the final sequence."""
        return ComposedSequence(self.components, self.separator)


# ========== COMPOSED SEQUENCE ==========

class ComposedSequence(Sequence):
    """A sequence composed of multiple components."""
    
    def __init__(self, components: List[SequenceComponent], separator: str = "-"):
        """
        Initializes the ComposedSequence with the specified components and separator.

        Args:
            components (List[SequenceComponent]): A list of components that make up the sequence.
            separator (str): The separator to use between components (default is "-").
        """

        self.components = components
        self.separator = separator
    
    def get_sequence_text(self, folder: str, file_name: str) -> str:
        """
        Generates the sequence text based on the provided folder and file name.

        Args:
            folder (str): The folder path where the file is located.
            file_name (str): The name of the file.

        Returns:
            str: The constructed sequence text in uppercase.
        """

        parts = [comp.extract(folder, file_name) for comp in self.components]
        
        parts = [p for p in parts if p]
        result = self.separator.join(parts)
        return result.upper()


# ========== COMMON SHORTCUTS ==========

def from_file_name() -> ComposedSequence:
    """Shortcut: sequence with only the file name."""

    return SequenceBuilder().file_name().build()


def from_splitted_text(separator: str = '_', part_index: int = 0) -> ComposedSequence:
    """Shortcut: first part of the filename based on a separator."""
    return SequenceBuilder().file_part(separator, part_index).build()


def from_literal(text: str) -> ComposedSequence:
    """Shortcut: fixed text component."""
    return SequenceBuilder().literal(text).build()


# ========== OLD SYSTEM (DEPRECATED) ==========

class Conc(Sequence):
    """
    DEPRECATED: Use SequenceBuilder instead.
    
    Mantein for compatibility with existent code.
    Will be removed in 3.0.0 version.
    """
    
    FIRST_FOLDER_CHAR = '[FDFC]'
    FOLDER_NAME = '[FDN]'
    LAST_FILE_CHAR_IF_LETTER = '[LIL]'
    FILE_NAME = '[FLN]'
    FILE_NAME_CAMPANA = '[FLC]'
    PART_NUMBER_CAMPANA = '[PNC]'
    LETTERA_DIVERSA_OGNI_NOME = '[LDON]'
    OEP_FILE_NAME = '[OEPFN]'
    
    def __init__(self, *text):
        self.text = text
        self.number = 1
    
    def num_char(self, number=1):
        self.number = number
        return self
    
    def get_sequence_text(self, folder: str, file_name: str) -> str:
        text_list = []
        for t in self.text:
            if t == Conc.FIRST_FOLDER_CHAR:
                folder_name = os.path.basename(os.path.normpath(folder))
                first_char_folder = folder_name[:self.number]
                text_list.append(first_char_folder)
            
            elif t == Conc.FILE_NAME:
                last_dot = file_name.rfind('.')
                text_list.append(file_name[:last_dot])
            
            elif t == Conc.FILE_NAME_CAMPANA:
                first_underscore = file_name.find('_')
                text_list.append(file_name[:first_underscore])
            
            elif t == Conc.PART_NUMBER_CAMPANA:
                first_underscore = file_name.find("_")
                second_underscore = file_name.find("_", first_underscore + 1)
                name = file_name[first_underscore:second_underscore]
                text_list.append(name)
            
            elif t == Conc.LAST_FILE_CHAR_IF_LETTER:
                first_underscore = file_name.find('_')
                if first_underscore > 0:
                    last_char = file_name[first_underscore - 1]
                    if last_char.isalpha():
                        text_list.append(last_char)
            
            else:
                text_list.append(t)
        
        return '-'.join(text_list)


class FixSeq(Sequence):
    """Sequenza con testo fisso. DEPRECATO: usa from_literal() invece."""
    def __init__(self, text: str):
        self.text = text
    
    def get_sequence_text(self, folder: str, file_name: str) -> str:
        return self.text

