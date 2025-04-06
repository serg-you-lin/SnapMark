from SnapMark.MarkAlgorithm.MarkAlgorithm import *
from SnapMark.AddEntities.AddEntities import *
from SnapMark.Checking.Checking import *

class Operation:

    def execute(self, doc, folder, file_name): # qualunque operazione vuole in ogni caso questi parametri
        pass

    def message(self, file_name):
        print("Occhio che non hai messo il metodo nell'operazione")

class AddMark(Operation):
    def __init__(self, sequence, scale_factor=50, space=1.5, min_char=5,\
                 max_char=20, arbitrary_x=None, arbitrary_y=None, align='c',\
                 start_y=1, step=2, margin=1, down_to=None, layer='MARCATURA', filtered_layer="0"):
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
        self.create_new = True
        self.message_text = None
        self.sequence_position = NS()
        self.filtered_layer = filtered_layer

    def __repr__(self):
        return f"{self.sequence}"

    def execute(self, doc, folder, file_name):
        # esempio per filtrare le entità del modelspace con self.filtered_layer
        # Lista per conservare i segmenti di linea del layer "0"
        temporary_msp = doc.modelspace()

        #filtered_entities = [e for e in temporary_msp if e.dxf.layer != self.filtered_layer]

        # # Itera attraverso tutte le entità nel modelspace
        # for entity in doc.modelspace():
        #     if entity.dxf.layer == self.filtered_layer:
        #         filtered_entities.append()

        # Esegui le operazioni desiderate sui segmenti di linea del layer "0"
        # for line in filtered_entities:
        #     print(line)

        # for e in filtered_entities:
        #     temporary_msp.delete_entity(e)

        # Decidi fattore scala
        scale_factor = comp_sf(doc, self.scale_factor)
        
        sequence = self.sequence.get_sequence_text(folder, file_name)
        
        start_x, start_y = comp_center_point((doc))
        self.sequence_position = place_sequence(doc, sequence, scale_factor, self.filtered_layer, self.space, self.min_char, \
                                       self.max_char, self.arbitrary_x, self.arbitrary_y, self.align,\
                                        self.start_y, self.step, self.margin, self.down_to)
        # print(file_sequence_position)

        # Ricordarsi di rimettere le entità filtrate nel file
        # for e in filtered_entities:
        #     temporary_msp.add_entity(e) 

        # Aggiungi i numeri al layer 'marcatura' nelle posizioni specificate
        add_numbers_to_layer(doc, self.sequence_position, self.layer)
        return self.create_new
                     
    def message(self, file_name):
        if len(self.sequence_position.sequence) == 0:
            self.message_text = f"Nessuno spazio trovato per la sequenza nel file {file_name}."
        else:
            self.message_text = f"Sequenza aggiunta a {file_name}"
        print(self.message_text)

class AddCircle(Operation):
    pass

class SubstituteCircle(Operation):
    def __init__(self, find_circle_function, new_radius=None, new_diameter=None, layer='0'):
        self.find_circle_function = find_circle_function
        self.new_radius = new_radius 
        self.new_diameter = new_diameter
        self.layer = layer
        self.create_new = True
        self.message_text = None
        if self.new_radius == None and self.new_diameter == None:  # gli input si validano qui!!!
            raise Exception('Non hai immesso la dimensione del nuovo foro.')

    def execute(self, doc, folder, file_name):
        holes = self.find_circle_function(doc)

        if self.new_diameter:
            self.new_radius = self.new_diameter / 2

        center_holes = find_circle_centers(holes)
        # Cosa fa uscire find_circle_center?? usiamo un unit coso così vediamo come si utilizza???

        add_circle(doc, center_holes, radius=self.new_radius, layer=self.layer)

        delete_circle(doc, holes)

        return self.create_new
    
    def message(self, file_name):
        if self.new_diameter:
            self.message_text = f"i fori selezionati nel file {file_name} hanno un nuovo diametro di {self.new_diameter}"
        else:
            self.message_text = f"i fori selezionati nel file {file_name} hanno un nuovo raggio di {self.new_radius}"
        print(self.message_text)
    
class AddX(Operation):
    def __init__(self, find_circle_function, size=8, layer='MARCATURA', delete_hole=True):
        self.find_circle_function = find_circle_function
        self.size = size
        self.layer = layer
        self.delete_hole = delete_hole
        self.create_new = True
        self.message_text = None

    def execute(self, doc, folder, file_name):
        holes = self.find_circle_function(doc)
    
        center_holes = find_circle_centers(holes)
        if self.delete_hole:
            delete_circle(doc, holes)
            
        add_x(doc, center_holes, size=self.size, layer=self.layer)

        return self.create_new
    
    def message(self, file_name):
        self.message_text = f"'X' Aggiunte al posto dei fori a {file_name}"
        print(self.message_text)

class RemoveCircle(Operation):
    def __init__(self, find_circle_function, size=8, layer='0'):
        self.find_circle_function = find_circle_function
        self.size = size
        self.layer = layer
        self.create_new = True
        self.message_text = None

    def execute(self, doc, folder, file_name):
        holes = self.find_circle_function(doc)
        delete_circle(doc, holes)

        return self.create_new
    
    def message(self, file_name):
        self.message_text = f"Fori rimossi da {file_name}"
        print(self.message_text)


class RemoveLayer(Operation):
    def __init__(self, layer):
        self.layer = layer
        self.create_new = True
        self.message_text = None

    def execute(self, doc, folder, file_name):
        delete_layer(doc, self.layer)
        return self.create_new

    def message(self, file_name):
        self.message_text = f"Layer {self.layer} eliminato da {file_name}"
        print(self.message_text)


class PrintLayers(Operation):
    def __init__(self):
        self.create_new = False
        self.message_text = None

    def execute(self, doc, folder, file_name):
        print_layers(doc)
        return self.create_new
    
    def message(self, file_name):
        self.message_text = f"Layer presenti in {file_name}:\n"
        print(self.message_text)