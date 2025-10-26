import ezdxf
import numpy as np
from snapmark.utils.segments_dict import number_segments_dict
# import matplotlib as plt


# Classe per definire la sequenza di numeri
class NS:
    def __init__(self):
        self.sequence = []

    def add_number(self, number, position):
        self.sequence.append((number, position))

######################################################################################################################
# Costants
        
MIN_ARC_SEGS = 15
######################################################################################################################
# Support functions to pass in the main (deprecated)

def comp_sf(doc, scale_factor=50):
    """Calculates the scale factor based on the dimensions of the drawing."""
    extmax = doc.header.get('$EXTMAX')
    extmin = doc.header.get('$EXTMIN')
    drawing_width = extmax[0] - extmin[0]
    drawing_height = extmax[1] - extmin[1]

    return min(drawing_width, drawing_height) / scale_factor


######################################################################################################################

######################################################################################################################
# ALGORITHM TO ALWAYS POSITION SEQUENCE IN A VALID POSITION
######################################################################################################################
# Level 3 - Subfunctions to help supporting functions
#############################################################################################################################

# Trovo tutti i punti di incrocio tra entità nel disegno e linee orizzontali con valore a crescere in y
def find_x_intercept(y, segs):
    """Finds x-intercepts for a given y value from a list of segments."""
    if y in x_intercept_cache:
        return x_intercept_cache[y]
    else:
        x_intercept = []
        for (start_x, start_y, end_x, end_y) in segs:
            if start_y >= y >= end_y or start_y <= y <= end_y:
                if start_y != end_y:
                    x = (y - start_y)/(end_y - start_y) * (end_x - start_x) + start_x
                    x_intercept.append(x)
                    
        
        x_intercept.sort()
        x_intercept_cache[y] = x_intercept
        return x_intercept
    

def find_intermediate_y(bottom_y, top_y, int_step=2):
    """Finds intermediate y values between bottom and top for potential intersections."""
    steps = []
    first_int = (bottom_y // int_step) * int_step + int_step
    int_y = first_int
    while int_y < top_y:
        steps.append(int_y)
        int_y += int_step
        
    return steps

#############################################################################################################################
# LEVEL 2 - Supporting functions to main algorithm
#############################################################################################################################


# Trasforma ogni entità in lista di segmenti espressi in tuple.
def comp_segs_and_limits(msp, filtered_layer):
    """
    Converts entities in the model space to a list of line segments and their limits.

    Args:
        msp: The model space containing the entities to be processed.
        filtered_layer: The layer from which to filter the entities for segment conversion.

    Returns:
        A tuple containing:
            - tot_segs: A list of segments represented as tuples (start_x, start_y, end_x, end_y).
            - min_x: The minimum x-coordinate among all segments.
            - min_y: The minimum y-coordinate among all segments.
            - max_x: The maximum x-coordinate among all segments.
            - max_y: The maximum y-coordinate among all segments.
    """

    # Initializes lists for arcs and lines
    round_segs = []
    line_segs = []
    
    # Finds the minimum and maximum coordinate values among all lines    
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
    
    # Initializes the minimum and maximum coordinate values
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    for (start_x, start_y, end_x, end_y) in tot_segs:        
        min_x = min(min_x, start_x, end_x)
        min_y = min(min_y, start_y, end_y)
        max_x = max(max_x, start_x, end_x)
        max_y = max(max_y, start_y, end_y)

    return tot_segs, min_x, min_y, max_x, max_y



def find_space_between_interceptions(x_left, x_right, lenght_sequence, height_sequence, segs, margin, y):   
    """
    Checks if there is enough space between interceptions for a given sequence.

    Args:
        x_left (float): The left boundary of the space to check.
        x_right (float): The right boundary of the space to check.
        lenght_sequence (float): The length of the sequence to be placed.
        height_sequence (float): The height of the sequence to be placed.
        segs (list): A list of segments to check for interceptions.
        margin (float): The margin to be added to the sequence length.
        y (float): The y-coordinate to check for interceptions.

    Returns:
        bool: True if there is enough space for the sequence, False otherwise.
    """           

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
    """
    Finds shared spaces between top and bottom interceptions.

    Args:
        top_interceptions (list): A list of x-coordinates for the top interceptions.
        bottom_interceptions (list): A list of x-coordinates for the bottom interceptions.

    Returns:
        list: A list of tuples representing shared spaces, where each tuple contains the start and end x-coordinates.
    """
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

    return shared_spaces 
          
##############################################################################
# Level 1 -- Main algorithm functions 
###################################################################################################################

# Main algorithm to find space for a sequence
def find_space_for_sequence(lenght_sequence, height_sequence, doc, align, start_y, step, margin, filtered_layer):
    """
    Finds a valid space for placing a sequence of specified length and height within a drawing.

    Args:
        lenght_sequence (float): The length of the sequence to be placed.
        height_sequence (float): The height of the sequence to be placed.
        doc: The document containing the model space where the sequence will be placed.
        align (str): The alignment of the sequence ('l' for left, 'c' for center, 'r' for right).
        start_y (float): The starting y-coordinate for the search.
        step (float): The step size for incrementing or decrementing the y-coordinate during the search.
        margin (float): The margin to be added around the sequence.
        filtered_layer (str): The layer from which to filter entities for segment conversion.

    Returns:
        tuple: A tuple containing:
            - start_x (float): The x-coordinate where the sequence can be placed.
            - start_y (float): The y-coordinate where the sequence can be placed.
            Returns (None, None) if no valid space is found.

    Overview:
        This function calculates potential y-coordinates for placing a sequence based on the height of the sequence
        and the available space in the model. It checks for valid x-coordinates by finding intersections with existing
        entities in the drawing. The function considers alignment options and margins when determining the final
        placement coordinates for the sequence.
    """

    msp = doc.modelspace()
    
    # Filter entities from the specified layer    
    segs, min_x, min_y, max_x, max_y = comp_segs_and_limits(msp, filtered_layer)

    y = min_y + start_y
    start_x = None
    y_to_try = []
    # Check valid y-coordinates while moving up in the file
    if height_sequence + 1 <= max_y - min_y:
        while y < max_y - 0.5 - height_sequence:
            y_to_try.append(y)
            y += step
        # Check valid y-coordinates while moving down in the file  
        y = min_y + start_y - step
        while y > min_y + 0.5:
            y_to_try.append(y)
            y -= step
    
        if 0.5 not in y_to_try:
            y_to_try.append(0.5)
        if max_y - height_sequence - 0.5 not in y_to_try:    
            y_to_try.append(max_y - height_sequence - 0.5)

    
    
    # Iterate through the list to find a space for the sequence
    is_space = False
    for y in y_to_try:
        x_intercept_bottom = find_x_intercept(y, segs)
        
        if len(x_intercept_bottom) > 1: 
            x_intercept_top = find_x_intercept(y + height_sequence, segs)
            if len(x_intercept_top) > 1:
            
                spaces_available_list = []
                shared_spaces_list = find_shared_spaces(x_intercept_top, x_intercept_bottom)

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
                    # Logic for sequence justification
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
            print('Sequence needs to be adjusted due to y values.')
        else:
            print('Sequence needs to be adjusted due to x values.')
        return None, None
    else:
        return start_x, start_y
    

# Global variable to store all y values, allowing retrieval if y has already been calculated.
x_intercept_cache = {}


# Rescale sequence if necessary
def rescale_sequence(text, scale_factor, start_x, start_y):
    sequence = NS()
    for i, char in enumerate(text):
         if char in number_segments_dict:
              # Get the segments for the specified number (from the implemented dictionary)
              segments = number_segments_dict[char]
              # Scaled segments based on the scale factor
              scaled_segments = [[x * scale_factor, y * scale_factor] for x, y in segments]
              sequence.add_number(scaled_segments, [start_x, start_y])
    return sequence
             

def sequence_dim(sequence, x_pos, y_pos, space):
    """
    Calculates the dimensions of a sequence and updates the positions of its components.

    Args:
        sequence: An object containing the sequence of segments and their positions.
        x_pos (float): The initial x-coordinate for positioning the sequence.
        y_pos (float): The initial y-coordinate for positioning the sequence (not used in calculations).
        space (float): The spacing factor between characters in the sequence.

    Returns:
        tuple: A tuple containing:
            - lenght_sequence (float): The total length of the sequence after accounting for spacing.
            - height_sequence (float): The maximum height of the sequence components.

    Overview:
        This function iterates through the segments of the sequence to calculate the total width and height.
        It updates the x-coordinate for each segment based on the specified spacing and returns the total dimensions.
    """

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
# Level 0 -- Function to place sequence on valid point of model space
###################################################################################################################

def place_sequence(doc, text, scale_factor, filtered_layer, space=1.5, min_char=5,\
                   max_char=20, arbitrary_x=None, arbitrary_y=None,\
                   align='c', start_y=1, step=2, margin=1, down_to=None):
    """
    Places a sequence of characters at a valid position within the DXF area.

    Args:
        doc: The document where the sequence will be placed.
        text (str): The sequence of characters to be placed.
        scale_factor (float): The scaling factor for the sequence dimensions.
        filtered_layer (str): The layer from which to filter entities for placement.
        space (float): The spacing factor between characters (default is 1.5).
        min_char (float): The minimum height for characters (default is 5).
        max_char (float): The maximum height for characters (default is 20).
        arbitrary_x (float, optional): The arbitrary x-coordinate for placement (default is None).
        arbitrary_y (float, optional): The arbitrary y-coordinate for placement (default is None).
        align (str): The alignment of the sequence ('l' for left, 'c' for center, 'r' for right; default is 'c').
        start_y (float): The starting y-coordinate for the search (default is 1).
        step (float): The step size for incrementing or decrementing the y-coordinate during the search (default is 2).
        margin (float): The margin to be added around the sequence (default is 1).
        down_to (float, optional): The minimum height to which the sequence can be resized (default is None).

    Returns:
        NS: The sequence object containing the placed characters and their positions.

    Raises:
        Exception: If the input text is empty.

    Overview:
        This function calculates the dimensions of the sequence based on the characters provided and attempts to
        place it within the specified document. It checks for valid positions based on the provided alignment and
        spacing, and resizes the sequence if necessary to fit within the defined constraints. If a valid position
        cannot be found, the function will attempt to rescale the sequence until it either finds a valid position
        or reaches the minimum height limit.
    """
    
    x_intercept_cache.clear()   # Svuoto cache da eventuali y precedenti
    if len(text) == 0:
        raise Exception('Empty sequence.')
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
              # Get segments for the specified character from the implemented dictionary
              segments = number_segments_dict[char]
              # Scale the segments based on the scale factor
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
    """Calculates the centroid of a given set of vertices."""
    num_vertex = len(vertex)
    sum_x = np.sum(vertex[:, 0])
    sum_y = np.sum(vertex[:, 1])
    centroid_x = sum_x / num_vertex
    centroid_y = sum_y / num_vertex
    return (centroid_x, centroid_y)

def dxf_centroid(doc):
    """Calculates the centroid of all relevant entities in a DXF document."""
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
    """Calculates the center point of all lines in the DXF document."""
    msp = doc.modelspace()
    
    # Inizializes the minimum and maximum coordinate values
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    # Find the minimum and maximum coordinate values among all lines
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
    """Calculates a starting point based on the minimum coordinates of lines in the DXF document."""
    msp = doc.modelspace()
    
    # Inizialize the minimum and maximum coordinate values
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

