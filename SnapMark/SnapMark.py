import os
import sys

# Importa i moduli dalla cartella SnapMark (usando la nuova struttura)
from SnapMark.Sequence.Sequence import *        # Importa Sequence
from SnapMark.Operations.Aligner import *               # Importa Aligner
from SnapMark.Operations.Counter import *               # Importa Counter
from SnapMark.Operations.Basic_Operations import *      # Importa Basic_Operations
from SnapMark.Utils.SegmentsDict import *           # Importa number_segments (dizionario)

def __filter_file(folder, dxf_file, filtered_files):
    if dxf_file.lower() in filtered_files:
        return True
    else:
        return False

def select_files(filtered_files):
    filtered_files = [f.lower() for f in filtered_files]
    return lambda folder, dxf_file: __filter_file(folder, dxf_file, filtered_files)

def find_circle_by_radius(min_diam=0, max_diam=float('inf')):
    return lambda doc: find_spec_holes(doc, min_diam, max_diam)

def mult_campana(file_name):
    Q_underscore = file_name.find("_Q")
    quantity = file_name[Q_underscore:]
    factor = ''
    for q in quantity:
        if q.isdigit():
            factor += q
    # print('fattore: ', factor)
    if len(factor) > 0:
        return int(factor)
    else:
        return 1




# Spostere entità da un layer ad un'altro


class iteration_manager:
    def __init__(self, folder_path, suffix='_AddMark'):
        self.folder_path = folder_path  # Inizializzo Attributo
        self.suffix = '_' + suffix
        self.operation_list = []
        self.message = [] # non sono sicuro che serva

    # Metodi della classe
    def add_operation(self, *operation):
        for o in operation:
            self.operation_list.append(o)
        

    def file_selection_logic(self, filter_files=None):
        # Ottieni il nome della cartella principale
        main_folder_name = os.path.basename(self.folder_path)

        # Nome della cartella di destinazione con la marcatura
        output_folder_name = main_folder_name + self.suffix

        # Percorso completo della cartella di destinazione
        output_main_folder_path = os.path.join(os.path.dirname(self.folder_path), output_folder_name)

        # Itera su tutte le sottocartelle nella cartella principale
        # Crea la struttura delle cartelle di destinazione una sola volta
        for folder, _, _ in os.walk(self.folder_path):
            relative_path = os.path.relpath(folder, self.folder_path)
            if relative_path != '.':
                relative_split = relative_path.split(os.sep)   # Separatore sistema operativo
                new_relative_path = ''
                for f in relative_split:
                    new_relative_path += f + self.suffix + os.sep
                relative_path = new_relative_path
            output_subfolder = os.path.join(output_main_folder_path, relative_path)


            # Esegui lo script per tutti i file nella cartella specificata
            try:
            
                # Elenco dei file nella cartella
                dxf_files = [f for f in os.listdir(folder) if f.endswith(".DXF") or f.endswith(".dxf")]
            
                for dxf_file in dxf_files:
                    if filter_files != None:
                        if isinstance(filter_files, str):
                            filter_files = [filter_files]
                        f = select_files(filter_files)
                        if f(folder, dxf_file) == False:
                            continue
                    
                    file_path = os.path.join(folder, dxf_file)
            
            
                    # Apri il file DXF originale
                    doc = ezdxf.readfile(file_path)

                    new_filename = os.path.splitext(dxf_file)[0] + self.suffix + ".dxf"
                    create_new = False
                    #print(self.operation_list)
                    for operation in self.operation_list:
                        #print(type(operation))
                        temp_create_new = operation.execute(doc, folder, dxf_file)
                        # ora sceglie sempre un True se presente
                        create_new = create_new or temp_create_new
                        if temp_create_new == True:
                            operation.message(new_filename)
                        else:
                            operation.message(dxf_file)

                          
                    if create_new == True:
                        os.makedirs(output_subfolder, exist_ok=True)
                        # Salva il file DXF modificato nella cartella di output con lo stesso nome del file originale
                        output_file_path = os.path.join(output_subfolder, new_filename)
                        doc.saveas(output_file_path)
                    
                        
                        
                    
                    

            
            except IOError as e:
                # print(f"Non è un file DXF o si è verificato un errore I/O generico.")
                print(e)
                sys.exit(1)
            except ezdxf.DXFStructureError:
                print(f"File DXF non valido o corrotto.")
                sys.exit(2)

        for operation in self.operation_list:
            if isinstance(operation, Counter):
                operation.count_message()




# Questo software è soggetto alla licenza MIT.
# Una copia della licenza è inclusa nella radice del progetto
# nel file LICENSE o al seguente URL:
# https://opensource.org/licenses/MIT

# Questa applicazione utilizza la libreria ezdxf, la quale è soggetta alla licenza MIT:
# https://opensource.org/licenses/MIT

# Copyright (c) 2023 Federico Sidraschi

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.