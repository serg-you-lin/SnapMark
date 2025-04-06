

# Aggiungi un foro in posizione specificata
def add_circle(doc, hole_list, radius, layer = '0'):
    msp = doc.modelspace()  # Accedi al modello spaziale del disegno
    for center_x, center_y in hole_list:
        center = (center_x, center_y)
        #print(center_x, center_y)
        msp.add_circle(center=center, radius=radius, dxfattribs={'layer': layer}) 
    
# Aggiungi un foro in posizione specificata con handle specifico
def add_circle_with_handle(doc, center_x, center_y, radius=10, layer='0', handle=68):
    msp = doc.modelspace()  # Accedi al modello spaziale del disegno
    center = center_x, center_y
    
    # Crea un nuovo cerchio con l'handle specificato
    circle = msp.add_circle(center=center, radius=radius, dxfattribs={'layer': layer})
    circle.dxf.handle = handle  # Imposta l'handle specificato
    
    return circle


def add_x(doc, hole_list, size=8, layer='0'):
    msp = doc.modelspace()
    for center_x, center_y in hole_list:
        # Calcola le coordinate per la 'x'
        x1 = center_x - (size / 1.4141) /2
        y1 = center_y - (size / 1.4141) /2
        x2 = center_x + (size / 1.4141) /2
        y2 = center_y + (size / 1.4141) /2
        
        # Aggiungi le linee diagonali a forma di 'x'
        msp.add_line(start=(x1, y1), end=(x2, y2), dxfattribs={'layer': layer})
        msp.add_line(start=(x1, y2), end=(x2, y1), dxfattribs={'layer': layer})


# Aggiungi 'X' in posizione specificata
def add_x_old(doc, center_x, center_y, size=8, layer='0'):
    msp = doc.modelspace()  # Accedi al modello spaziale del disegno
    
    # Calcola le coordinate per la 'x'
    x1 = center_x - (size / 1.4141) /2
    y1 = center_y - (size / 1.4141) /2
    x2 = center_x + (size / 1.4141) /2
    y2 = center_y + (size / 1.4141) /2
    
    # Aggiungi le linee diagonali a forma di 'x'
    msp.add_line(start=(x1, y1), end=(x2, y2), dxfattribs={'layer': layer})
    msp.add_line(start=(x1, y2), end=(x2, y1), dxfattribs={'layer': layer})


# Aggiungi la sequenza al file
def add_numbers_to_layer(doc, sequence, layer = '0'):
    msp = doc.modelspace()
   
    for scaled_segments, position in sequence.sequence:        

        # Aggiungi linee basate sui segmenti nella posizione scalata
        scaled_position = position  # La posizione è già stata scalata
        for i in range(len(scaled_segments) - 1):
            start_point = (
                scaled_segments[i][0] + scaled_position[0],
                scaled_segments[i][1] + scaled_position[1]
            )
            end_point = (
                scaled_segments[i + 1][0] + scaled_position[0],
                scaled_segments[i + 1][1] + scaled_position[1]
            )

            msp.add_line(start=start_point, end=end_point, dxfattribs={'layer': layer})
    
       
    
def delete_circle(doc, hole_list):
    msp = doc.modelspace()
    # Elimina il cerchio dal modello
    for hole in hole_list:
        msp.delete_entity(hole)


def delete_layer(doc, layer_name):
    # Ottieni il modello spaziale
    msp = doc.modelspace()

    # Trova tutte le entità appartenenti al layer specificato
    entities_to_remove = [entity for entity in msp.query('*[layer=="{}"]'.format(layer_name))]

    # Elimina tutte le entità associate al layer
    for entity in entities_to_remove:
        msp.delete_entity(entity)

    # Elimina il layer
    doc.layers.remove(layer_name)


            
def copy_entities_but_2(source_msp, dest_msp, holes_to_exclude=[]):
    # Itera attraverso tutte le entità nello spazio modello di origine
    for entity in source_msp.query('*'):
        if entity not in holes_to_exclude:
            # Copia l'entità nel target_msp (documento copiato)
            dest_msp.add_entity(entity)
            
            
def copy_entities_but(source_msp, target_msp, entities_to_exclude=[]):
    for entity in source_msp.query('*'):
        exclude = False
        for exclude_entity in entities_to_exclude:
            if entity.dxf.handle == exclude_entity.dxf.handle:
                exclude = True
                break
        if not exclude:
            target_msp.add_entity(entity.clone())

def remove_entities(msp, entities_to_remove):
    # Crea una nuova lista di entità escludendo quelle da rimuovere
    new_entities = [entity for entity in msp.query('*') if entity not in entities_to_remove]
    
    # Cancella tutte le entità dallo spazio modello
    msp.delete_all_entities()
    
    # Aggiungi le nuove entità allo spazio modello
    for entity in new_entities:
        msp.add_entity(entity.clone())




