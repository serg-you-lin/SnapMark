import sys
import os
import ezdxf
from SnapMark.MarkAlgorithm.MarkAlgorithm import *
from SnapMark.AddEntities.AddEntities import *


# Print the names of the layers
def print_layers(doc):
    # print("Layers:")
    for layer in doc.layers:
        print(layer.dxf.name)
        return print(layer.dxf.name)
    

# Cerca fori specifici
def find_spec_holes(doc, diametro_minimo=0, diametro_massimo=float('inf')):
    holes = []  # Lista per memorizzare le entità circolari

    msp = doc.modelspace()  # Accedi al modello spaziale del disegno

    # Itera attraverso tutte le entità nel modello spaziale
    for entity in msp.query('CIRCLE'):  # Filtra solo le entità di tipo cerchio
        diametro = entity.dxf.radius * 2  # Calcola il diametro del cerchio
        if diametro_minimo <= diametro <= diametro_massimo:
            holes.append(entity)
            # print(entity)# Aggiungi l'entità circolare alla lista se rientra nel range di diametri
        
    return holes

def find_entities(file_path, entity_type):
    # Carica il file DXF utilizzando ezdxf
    doc = ezdxf.readfile(file_path)
    
    # Estrai le entità dal modello
    msp = doc.modelspace()

    entities = []

    # Itera tutte le linee nel modello
    for entity in msp.query(entity_type):
        entities.append(entity)

    return entities

def print_entities(msp):
    for e in msp.query():
        print(e)
        #print(e.dxf.flags)
        #print(e.dxf.degree)
        #print(e.control_points)


def find_longer_entity(entities):

    lato_piu_lungo = None
    lunghezza_lato_piu_lungo = 0
    lato_piu_lungo_is_sotto = True
    minimum_point = float('inf')
    # Itera tutte le linee nel modello
    for entity in entities:
        minimum_point = min(entity.dxf.start.y, entity.dxf.end.y, minimum_point)      
        # Calcola la lunghezza della linea utilizzando il teorema di Pitagora
        lunghezza = ((entity.dxf.start.x - entity.dxf.end.x) ** 2 + (entity.dxf.start.y - entity.dxf.end.y) ** 2) ** 0.5
        # Se la lunghezza della linea è maggiore della lunghezza massima finora trovata, aggiornala
        if lunghezza > lunghezza_lato_piu_lungo:
            lunghezza_lato_piu_lungo = lunghezza
            lato_piu_lungo = entity
    
    # Controllare che il lato più lungo sia una linea perimetrale
    # print('Lato + lungo', lunghezza_lato_piu_lungo)
    # print('Minimum point: ', minimum_point)
    # print('Start y l+l: ', lato_piu_lungo.dxf.start.y)
    # print('End y l+l: ', lato_piu_lungo.dxf.end.y)
    if min(lato_piu_lungo.dxf.start.y, lato_piu_lungo.dxf.end.y) > minimum_point:
        lato_piu_lungo_is_sotto = False
    # print("Minimum point: ", minimum_point)
    # print("Punto inferiore del lato più lungo: ", min(lato_piu_lungo.dxf.start.y, lato_piu_lungo.dxf.end.y))
    return lato_piu_lungo, lato_piu_lungo_is_sotto

    

# conta i fori in una lista

def count_holes(hole_list):
    holes = []  # Lista per memorizzare le entità circolari

    # Itera attraverso tutte i fori
    for hole in hole_list:  
        holes.append(hole)  # Aggiungi l'entità circolare alla lista
        
    num_holes = len(holes)
    # print(f"Nel file {filename} sono presenti {num_holes} fori dal diametro selezionato")
    return num_holes


# Trova centro di lista di fori
def find_circle_centers(holes_list):
    centers = []  # Lista per memorizzare i centri dei cerchi

    # Itera attraverso le entità circolari nella lista holes_list
    for circle in holes_list:  # Utilizza la lista passata come argomento
        center_x = circle.dxf.center.x  # Estrai la coordinata x del centro del cerchio
        center_y = circle.dxf.center.y  # Estrai la coordinata y del centro del cerchio
        centers.append((center_x, center_y))  # Aggiungi le coordinate x e y del centro alla lista
        
    return centers

# Cerca i fori di un file e rileva il centro.
def find_circle_centers_2(doc):
    centers = []  # Lista per memorizzare i centri dei cerchi

    msp = doc.modelspace()  # Accedi al modello spaziale del disegno

    # Itera attraverso tutte le entità nel modello spaziale
    for circle in msp.query('CIRCLE'):  # Filtra solo le entità di tipo cerchio
        center_x = circle.dxf.center.x  # Estrai la coordinata x del centro del cerchio
        center_y = circle.dxf.center.y  # Estrai la coordinata y del centro del cerchio
        centers.append((center_x, center_y))  # Aggiungi le coordinate x e y del centro alla lista
        
    return centers


def change_layer(entities, new_layer):
    for entity in entities:
        entity.set_dxf_attrib('layer', new_layer)



# Funzione principale da chiamare in tutti gli script su cui vogliamo itereare in intera cartella.
def iter_on_a_folder(folder_path, main):
    
    # Estrai il nome dell'ultima directory (il nome della cartella) dalla variabile folder_path
    output_folder_name = os.path.basename(folder_path)

    # Aggiungi "_numerata" al nome della cartella
    output_folder_name += "_AddMark"

    # Combina il nuovo nome della cartella con il percorso del genitore per ottenere il percorso completo della nuova cartella di output
    output_folder = os.path.join(os.path.dirname(folder_path), output_folder_name)
    
    # Esegui lo script per tutti i file nella cartella specificata
    try:

        # Cartella alternativa per i nuovi file
        os.makedirs(output_folder, exist_ok=True)

        # Elenco dei file nella cartella
        dxf_files = [f for f in os.listdir(folder_path) if f.endswith(".DXF") or f.endswith(".dxf")]

        for dxf_file in dxf_files:
            file_path = os.path.join(folder_path, dxf_file)


            # Apri il file DXF originale
            original_doc = ezdxf.readfile(file_path)
            
            copied_doc = main(original_doc, dxf_file)

            
            # Salva il file DXF modificato nella cartella di output con lo stesso nome del file originale
            new_filename = os.path.splitext(dxf_file)[0] + "_MARK.dxf"
            output_file_path = os.path.join(output_folder, new_filename)
            copied_doc.saveas(output_file_path)
            
        
            print(f"Numeri aggiunti a '{new_filename}'")
            
    except IOError:
        print(f"Non è un file DXF o si è verificato un errore I/O generico.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"File DXF non valido o corrotto.")
        sys.exit(2)



