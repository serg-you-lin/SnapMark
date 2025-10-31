

def add_circle(doc, hole_list, radius, layer='0'):
    """Adds circles at specified positions in the document."""
    msp = doc.modelspace()  # Access the model space of the drawing
    for center_x, center_y in hole_list:
        center = (center_x, center_y)
        # print(center_x, center_y)
        msp.add_circle(center=center, radius=radius, dxfattribs={'layer': layer}) 


def add_circle_with_handle(doc, center_x, center_y, radius=10, layer='0', handle=68):
    """Adds a circle at a specified position with a specific handle."""
    msp = doc.modelspace()  # Access the model space of the drawing
    center = center_x, center_y
    
    # Create a new circle with the specified handle
    circle = msp.add_circle(center=center, radius=radius, dxfattribs={'layer': layer})
    circle.dxf.handle = handle  # Set the specified handle
    
    return circle


def add_x(doc, hole_list, x_size=8, layer='0'):
    """Adds an 'X' shape at specified positions in the document."""
    msp = doc.modelspace()
    for center_x, center_y in hole_list:
        # Calculate the coordinates for the 'x'
        x1 = center_x - (x_size / 1.4141) /2
        y1 = center_y - (x_size / 1.4141) /2
        x2 = center_x + (x_size / 1.4141) /2
        y2 = center_y + (x_size / 1.4141) /2
        
        # Add diagonal lines to form an 'x'
        msp.add_line(start=(x1, y1), end=(x2, y2), dxfattribs={'layer': layer})
        msp.add_line(start=(x1, y2), end=(x2, y1), dxfattribs={'layer': layer})



def add_numbers_to_layer(doc, sequence, layer = '0'):
    """Adds a sequence of lines to a specified layer in the document."""
    msp = doc.modelspace()
   
    for scaled_segments, position in sequence.sequence:        

        # Add lines based on the segments at the scaled position
        scaled_position = position  # The position has already been scaled
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
    """Deletes circles from the model based on the provided list."""
    msp = doc.modelspace()
    
    for hole in hole_list:
        msp.delete_entity(hole)


def delete_layer(doc, layer_name):
    """Deletes a specific layer and all entities associated with."""
    msp = doc.modelspace()

    # Find all entities belonging to the specified layer
    entities_to_remove = [entity for entity in msp.query('*[layer=="{}"]'.format(layer_name))]

    # Delete all entities associated with the layer
    for entity in entities_to_remove:
        msp.delete_entity(entity)

    # Delete the layer
    doc.layers.remove(layer_name)


            
def copy_entities_but_2(source_msp, dest_msp, holes_to_exclude=[]):
    """Copies entities from source model space to target, excluding specified entities."""

    for entity in source_msp.query('*'):
        if entity not in holes_to_exclude:
            dest_msp.add_entity(entity)
            
            

def copy_entities_but(source_msp, target_msp, entities_to_exclude=[]):
    """Copies entities from source model space to target, excluding specified entities."""
    for entity in source_msp.query('*'):
        exclude = False
        for exclude_entity in entities_to_exclude:
            if entity.dxf.handle == exclude_entity.dxf.handle:
                exclude = True
                break
        if not exclude:
            target_msp.add_entity(entity.clone())

def remove_entities(msp, entities_to_remove):
    """Removes specified entities from the model space."""
    # Create a new list of entities excluding those to remove
    new_entities = [entity for entity in msp.query('*') if entity not in entities_to_remove]
    
    # Delete all entities from the model space
    msp.delete_all_entities()
    
    # Add the new entities to the model space
    for entity in new_entities:
        msp.add_entity(entity.clone())




