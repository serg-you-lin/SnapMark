import ezdxf
import numpy as np
from SnapMark.Utils.SegmentsDict import number_segments_dict
# import matplotlib as plt


# Classe per definire la sequenza di numeri
class NS:
    def __init__(self):
        self.sequence = []

    def add_number(self, number, position):
        self.sequence.append((number, position))

# Copia tutte le entità da source_msp a dest_msp
# def copy_entities(source_msp, dest_msp):
#     for entity in source_msp:
#         dest_msp.add_entity(entity.copy())

######################################################################################################################
# Costanti
        
MIN_ARC_SEGS = 15
######################################################################################################################
# Funzioni di supporto da passare nel main  (deprecata)

def comp_sf(doc, scale_factor=50):
    """Funzione per il calcolo dello scale factor in base alle dimenzioni del disegno"""
    extmax = doc.header.get('$EXTMAX')
    extmin = doc.header.get('$EXTMIN')
    drawing_width = extmax[0] - extmin[0]
    drawing_height = extmax[1] - extmin[1]

    return min(drawing_width, drawing_height) / scale_factor


######################################################################################################################

######################################################################################################################
# ALGORITMO PER POSIZIONAMENTO SEQUENZA IN POSIZIONE SEMPRE VALIDA
######################################################################################################################
# Livello 3 - Sottofunzioni per funzioni di supporto
#############################################################################################################################

# Trovo tutti i punti di incrocio tra entità nel disegno e linee orizzontali con valore a crescere in y
def find_x_intercept(y, segs):
    if y in x_intercept_cache:
        return x_intercept_cache[y]
    else:
        x_intercept = []
        for (start_x, start_y, end_x, end_y) in segs:
            if start_y >= y >= end_y or start_y <= y <= end_y:
                if start_y != end_y:
                    x = (y - start_y)/(end_y - start_y) * (end_x - start_x) + start_x
                    # print('Punto di intersezione: ', x, y)
                    x_intercept.append(x)
                    
        
        x_intercept.sort()
        x_intercept_cache[y] = x_intercept
        return x_intercept
    
# Trovo valori intermedi tra top e bottom della sequenza per intercettare eventuali piccole entità intersecanti la sequenza stessa
def find_intermediate_y(bottom_y, top_y, int_step=2):
    steps = []
    first_int = (bottom_y // int_step) * int_step + int_step
    int_y = first_int
    while int_y < top_y:
        steps.append(int_y)
        int_y += int_step
        
    return steps

#############################################################################################################################
# Livello 2 - Funzioni di supporto per algoritmo principale
#############################################################################################################################


# Trasforma ogni entità in lista di segmenti espressi in tuple.
def comp_segs_and_limits(msp, filtered_layer):



    # Inizializza le liste di segmenti per archi e linee
    round_segs = []
    line_segs = []
    
    
    # Trova i valori minimi e massimi delle coordinate tra tutte le linee
    for entity in msp.query('LINE'):
        if entity.dxf.layer == filtered_layer:
            start_point = entity.dxf.start
            end_point = entity.dxf.end
            line_segs.append((start_point.x, start_point.y, end_point.x, end_point.y))

    # for entity in msp.query('LWPOLYLINE'):
    #     pass
    #     if entity.dxf.layer == filtered_layer:
    #         # resulted_lines = [e in e for entity.dxf.explode]
    #         for f in resulted_lines:
    #             line_segs.append(())


    for entity in msp.query('CIRCLE ARC'):
        if entity.dxf.layer == filtered_layer:
            if entity.dxftype() == 'CIRCLE':
                center_x, center_y = entity.dxf.center.x, entity.dxf.center.y
                rad = entity.dxf.radius
                num_segment = MIN_ARC_SEGS + rad//2

                ang = np.linspace(0, 2 * np.pi, int(num_segment) + 1)
                x = center_x + rad * np.cos(ang)
                y = center_y + rad * np.sin(ang)
                coords = list(zip(x, y))
                circ_segs = [(coords[i][0], coords[i][1], coords[i+1][0], coords[i+1][1]) for i in range(0, len(coords) - 2)]
                circ_segs.append((coords[-1][0], coords[-1][1], coords[0][0], coords[0][1]))
                round_segs.extend(circ_segs)
            elif entity.dxftype() == 'ARC':
                # print(entity.dxftype())
                center_x, center_y = entity.dxf.center.x, entity.dxf.center.y
                rad = entity.dxf.radius
                start_angle = np.radians(entity.dxf.start_angle)
                final_angle = np.radians(entity.dxf.end_angle)
                if start_angle > final_angle:
                    final_angle += 2 * np.pi
                num_segment = MIN_ARC_SEGS + (rad//2) * ((final_angle - start_angle) / (2 * np.pi))

                ang = np.linspace(start_angle, final_angle, int(num_segment) + 1)
                x = center_x + rad * np.cos(ang)
                y = center_y + rad * np.sin(ang)
                coords = list(zip(x, y))
                arc_segs = [(coords[i][0], coords[i][1], coords[i+1][0], coords[i+1][1]) for i in range(0, len(coords) - 2)]
                round_segs.extend(arc_segs)

            
    tot_segs = round_segs + line_segs
    
    # Inizializza i valori minimi e massimi delle coordinate
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    for (start_x, start_y, end_x, end_y) in tot_segs:        
        min_x = min(min_x, start_x, end_x)
        min_y = min(min_y, start_y, end_y)
        max_x = max(max_x, start_x, end_x)
        max_y = max(max_y, start_y, end_y)

    return tot_segs, min_x, min_y, max_x, max_y



def find_space_between_interceptions(x_left, x_right, lenght_sequence, height_sequence, segs, margin, y):              
    if (lenght_sequence + 2*margin) <= (x_right - x_left):
        y_ints = find_intermediate_y(y, y + height_sequence)
        for y_int in y_ints:
            x_intercept = find_x_intercept(y_int, segs)         
            for interception in x_intercept:
                if x_right > interception > x_left:
                    return False
                
        return True
    else:
        return False
    

def find_shared_spaces(top_interceptions, bottom_interceptions):
    # print('Top: ', top_interceptions)
    # print('Bottom: ', bottom_interceptions)

    combined_interceptions = []
    for i, t_intercept in enumerate(top_interceptions):
        if i % 2 == 0:
            combined_interceptions.append((t_intercept, 't pieno'))
        else:
            combined_interceptions.append((t_intercept, 't vuoto'))

    for i, b_intercept in enumerate(bottom_interceptions):
        if i % 2 == 0:
            combined_interceptions.append((b_intercept, 'b pieno'))
        else:
            combined_interceptions.append((b_intercept, 'b vuoto'))

    combined_interceptions.sort(key = lambda interc: interc[0])
    top_statement = None
    bottom_statement = None
    top_filled_part_start = None
    bottom_filled_part_start = None
    shared_spaces = []
    for interc in combined_interceptions:
        if interc[1].startswith('t'):
            top_statement = interc[1]
            if top_statement == 't pieno':
                top_filled_part_start = interc[0]
            else:
                if bottom_statement == 'b pieno':
                    shared_spaces.append((max(top_filled_part_start, bottom_filled_part_start), interc[0]))
        else:
            bottom_statement = interc[1]
            if bottom_statement == 'b pieno':
                bottom_filled_part_start = interc[0]
            else:
                if top_statement == 't pieno':
                    shared_spaces.append((max(top_filled_part_start, bottom_filled_part_start), interc[0]))

    # print(shared_spaces)
    return shared_spaces # lista di tuple??? ogni tupla x inizio/x fine
          
##############################################################################
# Livello 1 
###################################################################################################################

# Algoritmo principale
def find_space_for_sequence(lenght_sequence, height_sequence, doc, align, start_y, step, margin, filtered_layer):
    msp = doc.modelspace()
    # filtrare le entità del layer che ci serve
    
    segs, min_x, min_y, max_x, max_y = comp_segs_and_limits(msp, filtered_layer)

    y = min_y + start_y
    start_x = None
    y_to_try = []
    # Verifico y valide salendo nel file
    if height_sequence + 1 <= max_y - min_y:
        while y < max_y - 0.5 - height_sequence:
            y_to_try.append(y)
            y += step
        # Verifico y valide scendendo nel file 
        y = min_y + start_y - step
        while y > min_y + 0.5:
            y_to_try.append(y)
            y -= step
    
        if 0.5 not in y_to_try:
            y_to_try.append(0.5)
        if max_y - height_sequence - 0.5 not in y_to_try:    
            y_to_try.append(max_y - height_sequence - 0.5)

    
    
    # Itero sulla lista per trovare uno spazio per la sequenza
    is_space = False
    for y in y_to_try:
        # print(y)
        x_intercept_bottom = find_x_intercept(y, segs)
        # print('Bottom ', x_intercept_bottom)
        if len(x_intercept_bottom) > 1: 
            # print(min_y - (y+height_sequence))
            x_intercept_top = find_x_intercept(y + height_sequence, segs)
            # print('Top ', x_intercept_top)
            # print(height_sequence)
            if len(x_intercept_top) > 1:
            
                spaces_available_list = []
                shared_spaces_list = find_shared_spaces(x_intercept_top, x_intercept_bottom)
                # for n in range(0, min(len(x_intercept_bottom) -1 , len(x_intercept_top) -1), 2):
                #     spaces_available_list.append((x_intercept_bottom[n], x_intercept_bottom[n+1], x_intercept_top[n], x_intercept_top[n+1]))
                if len(shared_spaces_list) > 0:
                    if align == 'r':
                        shared_spaces_list = shared_spaces_list[::-1]

                    elif align == 'c':
                        middle_point = (shared_spaces_list[0][0] + shared_spaces_list[-1][1]) / 2
                        shared_spaces_list.sort(key=lambda space: abs(middle_point - (space[0] + space[1]) / 2))
                        
                    for spaces in shared_spaces_list:
        
                        is_space = find_space_between_interceptions(spaces[0], spaces[1], lenght_sequence, height_sequence, segs, margin, y)
                        if is_space:
                            x_left, x_right = spaces[0], spaces[1]             
                            break

                if is_space == True: 
                    # Logica di giustificazione sequenza
                    if align == 'l':
                        start_x = x_left + margin
                    elif align == 'r':
                        start_x = x_right - lenght_sequence - margin
                    else:
                        start_x_middle = middle_point - (lenght_sequence / 2)
                        if x_right - (lenght_sequence/2) > middle_point > x_left + (lenght_sequence / 2):
                            start_x = start_x_middle
                        else:
                            start_x = ((x_right - x_left) - lenght_sequence) / 2 + x_left
                            if start_x > start_x_middle:
                                start_x = x_left + margin
                            else:
                                start_x = x_right - lenght_sequence - margin
                    start_y = y
                    break


    if start_x == None:
        if y_to_try == []:
            print('Sequenza da riscalare per via delle y')
        else:
            print('Sequenza da riscalare per via delle x')
        return None, None
    else:
        return start_x, start_y
    

# Variabile globale in cui stocco tutti i valori di y, in modo tale da richiamarli se y già calcolata.
x_intercept_cache = {}


# Funzione per riscalare la sequenza se necessario
def rescale_sequence(text, scale_factor, start_x, start_y):
    sequence = NS()
    for i, char in enumerate(text):
         if char in number_segments_dict:
              #Ottieni i segmenti per il numero specificato (dal dizionario implementato)
              segments = number_segments_dict[char]
              # Scala i segmenti in base al fattore di scala
              scaled_segments = [[x * scale_factor, y * scale_factor] for x, y in segments]
              sequence.add_number(scaled_segments, [start_x, start_y])
    return sequence
             
# Calcolo dimensione della sequenza e spaziatura dei caretteri 8sarebbe meglio avere due funzioni in casi come questo
def sequence_dim(sequence, x_pos, y_pos, space):
    x_position = x_pos
    y_position = y_pos
    lenght_sequence = 0.0
    height_sequence = 0.0
        
    for scaled_segments, position in sequence.sequence:
        number_width = max([x[0] for x in scaled_segments]) - min([x[0] for x in scaled_segments])
        number_height = max([x[1] for x in scaled_segments]) - min([x[1] for x in scaled_segments])
        height_sequence = max(number_height, height_sequence)
        if number_width == 0:
            number_height = max([x[1] for x in scaled_segments]) - min([x[1] for x in scaled_segments])
            number_width = number_height / 2  # Larghezza fissa per il numero '1'
        position[0] = x_position
        x_position += number_width * space  # Aggiorna la posizione x in base allo spaziamento
        lenght_sequence += number_width * space
    

    lenght_sequence -= number_width * (space - 1)
    
    return lenght_sequence, height_sequence

##################################################################################################################
# Livello 0
###################################################################################################################

def place_sequence(doc, text, scale_factor, filtered_layer, space=1.5, min_char=5,\
                   max_char=20, arbitrary_x=None, arbitrary_y=None,\
                   align='c', start_y=1, step=2, margin=1, down_to=None):
    """Funzione per piazzare la sequenza in un punto sempre valido dell'area del dxf"""
    x_intercept_cache.clear()   # Svuoto cache da eventuali y precedenti
    if len(text) == 0:
        raise Exception('Sequenza vuota.')
    sequence = NS()
       
    height_sequence = 0.0
    
    if arbitrary_x == None:
        x_pos = 0
    else:
        x_pos = arbitrary_x
        
    if arbitrary_y == None:
        y_pos = 0
    else:
        y_pos = arbitrary_y
    
    for i, char in enumerate(text):
         if char in number_segments_dict:
              # Ottieni i segmenti per il numero specificato (dal dizionario implementato)
              segments = number_segments_dict[char]
              # Scala i segmenti in base al fattore di scala
              scaled_segments = [[x * scale_factor, y * scale_factor] for x, y in segments]
              sequence.add_number(scaled_segments, [x_pos, y_pos])
              number_height = max([x[1] for x in scaled_segments]) - min([x[1] for x in scaled_segments])
              height_sequence = max(number_height, height_sequence)
                  
    if height_sequence < min_char:
        scale_factor = scale_factor / height_sequence * min_char
        sequence = rescale_sequence(text, scale_factor, x_pos, y_pos)
    elif height_sequence > max_char:
        scale_factor = scale_factor / height_sequence * max_char
        sequence = rescale_sequence(text, scale_factor, x_pos, y_pos)
        
    lenght_sequence, height_sequence = sequence_dim(sequence, x_pos, y_pos, space)
    
    if arbitrary_x == None or arbitrary_y == None:
        # print('Prima chiamata: ', height_sequence)
        x, y = find_space_for_sequence(lenght_sequence, height_sequence, doc, align, start_y, step, margin, filtered_layer)
        if down_to == None:
            down_to = min_char
        while x == None or y == None:
            rescale_factor = 0.8
            new_height_sequence = height_sequence * rescale_factor
            if new_height_sequence < down_to:
                break
            else:
                scale_factor = scale_factor * rescale_factor
                sequence = rescale_sequence(text, scale_factor, x_pos, y_pos)
                lenght_sequence, height_sequence = sequence_dim(sequence, x_pos, y_pos, space)
                # print('Seconda chiamata: ', height_sequence)
                x, y = find_space_for_sequence(lenght_sequence, height_sequence, doc, align, start_y, step, margin, filtered_layer)
        if x == None or y == None:
            sequence = NS()
        else:
            for scaled_segments, position in sequence.sequence:
                position[0] += x 
                position[1] += y

    
    return sequence



#######################################################################################################################################
#######################################################################################################################################

def comp_centroid(vertex):
    num_vertex = len(vertex)
    sum_x = np.sum(vertex[:, 0])
    sum_y = np.sum(vertex[:, 1])
    centroid_x = sum_x / num_vertex
    centroid_y = sum_y / num_vertex
    return (centroid_x, centroid_y)

def dxf_centroid(doc):
    msp = doc.modelspace()

    poli_points = []
    arc_points = []

    for entity in msp.query('LWPOLYLINE CIRCLE ARC'):
        if entity.dxftype() == 'LWPOLYLINE':
            vertex = [(vertex.dxf.location.x, vertex.dxf.location.y) for vertex in entity.vertices()]
            poli_points.extend(vertex)
        elif entity.dxftype() == 'CIRCLE':
            center_x, center_y = entity.dxf.center.x, entity.dxf.center.y
            rad = entity.dxf.radius
            num_segment = 20

            ang = np.linspace(0, 2 * np.pi, num_segment + 1)
            x = center_x + rad * np.cos(ang)
            y = center_y + rad * np.sin(ang)
            arc_points.extend(list(zip(x, y)))
        elif entity.dxftype() == 'ARC':
            center_x, center_y = entity.dxf.center.x, entity.dxf.center.y
            rad = entity.dxf.radius
            start_angle = np.radians(entity.dxf.start_angle)
            final_angle = np.radians(entity.dxf.end_angle)
            num_segment = 100

            ang = np.linspace(start_angle, final_angle, num_segment + 1)
            x = center_x + rad * np.cos(ang)
            y = center_y + rad * np.sin(ang)
            arc_points.extend(list(zip(x, y)))

    tot_points = poli_points + arc_points

    if tot_points:
        tot_points = np.array(tot_points)
        centroid = comp_centroid(tot_points)
        return centroid

    return 0, 0




def comp_center_point(doc):
    msp = doc.modelspace()
    
    # Inizializza i valori minimi e massimi delle coordinate
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    # Trova i valori minimi e massimi delle coordinate tra tutte le linee
    for entity in msp.query('LINE'):
        start_point = entity.dxf.start
        end_point = entity.dxf.end
        min_x = min(min_x, start_point.x, end_point.x)
        min_y = min(min_y, start_point.y, end_point.y)
        max_x = max(max_x, start_point.x, end_point.x)
        max_y = max(max_y, start_point.y, end_point.y)

    # Calcola il punto centrale
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    return center_x, center_y


def comp_start_point(doc, x_pos=1, y_pos=1):
    msp = doc.modelspace()
    
    # Inizializza i valori minimi e massimi delle coordinate
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    # Trova i valori minimi e massimi delle coordinate tra tutte le linee
    for entity in msp.query('LINE'):
        start_point = entity.dxf.start
        end_point = entity.dxf.end
        min_x = min(min_x, start_point.x, end_point.x)
        min_y = min(min_y, start_point.y, end_point.y)
        max_x = max(max_x, start_point.x, end_point.x)
        max_y = max(max_y, start_point.y, end_point.y)

    # Calcola il punto centrale
    start_x = min_x + x_pos
    start_y = min_y + y_pos

    return start_x, start_y

def comp_qualcosa_point(doc, y_pos=1):
    msp = doc.modelspace()
    
    # Inizializza i valori minimi e massimi delle coordinate
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    # Trova i valori minimi e massimi delle coordinate tra tutte le linee
    for entity in msp.query('LINE'):
        start_point = entity.dxf.start
        end_point = entity.dxf.end
        min_x = min(min_x, start_point.x, end_point.x)
        min_y = min(min_y, start_point.y, end_point.y)
        max_x = max(max_x, start_point.x, end_point.x)
        max_y = max(max_y, start_point.y, end_point.y)

    # Calcola il punto centrale
    center_x = (min_x + max_x) / 2
    center_y = min_y - y_pos

    return center_x, center_y

def extract_perimetral_entities(doc):
    
    # Estrai le entit� dal modello
    msp = doc.modelspace()

    perimetral_entities = []
    for entity in msp.query('LINE'):
        # Verifica se la linea � perimetrale (non collegata ad altre linee)
        is_perimetral = True
        for other_entity in msp.query('LINE'):
            if entity != other_entity:
                # Verifica se la linea � collegata ad altre linee
                if entity.dxf.start == other_entity.dxf.start or entity.dxf.start == other_entity.dxf.end \
                    or entity.dxf.end == other_entity.dxf.start or entity.dxf.end == other_entity.dxf.end:
                    is_perimetral = False
                    break
        
        # Se la linea � perimetrale, aggiungila alla lista delle entit� perimetrali
        if is_perimetral:
            perimetral_entities.append(entity)

    for entity in perimetral_entities:
        print(f'Tipo: {entity.dxftype()}, Punto di inizio: {entity.dxf.start}, Punto finale: {entity.dxf.end}')    
    return perimetral_entities






#######################################################################################################################################
#######################################################################################################################################

