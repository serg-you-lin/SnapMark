import sys
import os

# Aggiungi la cartella 'SnapMark' al percorso di ricerca dei moduli
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SnapMark')))

# Ora importa il modulo
from SnapMark.SnapMark import *

# Cartella contenente i file DXF
folder_path = r'Examples/Input'

name_files = []
list_files = []

fix = '012'

# sequence = FixSeq(fix)
sequence = Conc(Conc.FIRST_FOLDER_CHAR, Conc.LAST_FILE_CHAR_IF_LETTER)
#sequence = Conc(Conc.FILE_NAME)
ToMark = iteration_manager(folder_path, suffix='Marked')

ToMark.add_operation(AddMark(sequence, min_char=10, max_char=20, align='c', scale_factor=100, down_to=2))



ToMark.file_selection_logic()
