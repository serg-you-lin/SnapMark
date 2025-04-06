from SnapMark.Operations.Basic_Operations import *
from SnapMark.Checking.Checking import *
import math
from ezdxf.math import Vec3


class Aligner(Operation):

    def __init__(self):
        self.create_new = True

    def execute(self, doc, folder, file_name): # qualunque operazione vuole in ogni caso questi parametri

        msp = doc.modelspace()

        print_entities(msp)

        circles, arcs, lines, ellipses = iter_on_all_entities(msp) 
        
        num_entities = len(lines + arcs + circles + ellipses)
        if len(msp.query()) > num_entities:
            print("Alcune entità non sono supportate")

        if len(lines) > 0:
            lato, lato_lungo_is_sotto = find_longer_entity(lines)

        else:
            lato = None

        # if not lato:
        #     return
        
        # elif lato is not None:
        if lato is not None:
            print("Lato: ", lato)
            pp = get_pivot_point(lato)
            angolo = comp_inclination(lato)
            # print("Angolo: ", angolo)
                       
            add_rotated_entities_to_msp(msp, lines, arcs, circles, ellipses, pp, angolo)

            new_circles, new_arcs, new_lines, new_ellipses = iter_on_all_entities(msp)
    
            lato, lato_lungo_is_sotto = find_longer_entity(new_lines)
            pp = get_pivot_point(lato)
        
            if lato_lungo_is_sotto == False:          
                self.flip_file(msp, new_lines, new_arcs, new_circles, new_ellipses, pp, lato)
                    
            # print(f"L'angolo di inclinazione della linea più lunga rispetto all'asse X è di {math.degrees(angolo)} gradi.")
        else:
            print("Nessuna linea trovata nel file DXF.")
            


        return self.create_new

    def message(self, file_name):
        print(f"{file_name} allineato al lato più lungo sull'asse X ")

    def flip_file(self, msp, lines, arcs, circles, ellipses, pp, lato_piu_lungo):
        
        print('file ruotato di 180°')
        
        angolo_rad = comp_inclination(lato_piu_lungo)

        if angolo_rad < math.pi:
            # print("Angolo lato sotto se inf. pgreco: ", angolo_rad) 
            angolo_rad = angolo_rad + math.pi
            
        else:
            # print("Angolo lato sotto se magg. pgreco: ", angolo_rad) 
            angolo_rad = angolo_rad - math.pi
       
        add_rotated_entities_to_msp(msp, lines, arcs, circles, ellipses, pp, angolo_rad)

    

################################################################################################    


def add_rotated_entities_to_msp(msp, lines, arcs, circles, ellipses, pivot, angolo):
    # print('Entità: ', entities)
    for l in lines:
        rotated_line = rotate_line_by_pivot_point(l, pivot, -1*angolo)    
        msp.add_entity(rotated_line)    
        msp.delete_entity(l)
   
    for c in circles:
        rotated_circle = rotate_circle_by_pp(c, pivot, -1*angolo)
        msp.add_entity(rotated_circle)
        msp.delete_entity(c)

    for a in arcs:
        rotated_arc = rotate_arc_by_pp(a, pivot, -1*angolo)
        msp.add_entity(rotated_arc)
        msp.delete_entity(a)

    for e in ellipses:
        rotated_ellipse = rotate_ellipse_by_pp(e, pivot, -1*angolo)
        msp.add_entity(rotated_ellipse)
        msp.delete_entity(e)

def comp_inclination(entity):
    if entity.dxf.end.x > entity.dxf.start.x:
        deltaX = entity.dxf.end.x - entity.dxf.start.x
        deltaY = entity.dxf.end.y - entity.dxf.start.y
    else:
        deltaX = entity.dxf.start.x - entity.dxf.end.x
        deltaY = entity.dxf.start.y - entity.dxf.end.y

    angolo_rad = math.atan2(deltaY, deltaX)
   
    return angolo_rad


def get_pivot_point(entity):
    return entity.dxf.start.x, entity.dxf.start.y

def iter_on_all_entities(msp):
    lines = []
    arcs = []
    circles = []
    ellipses = []
    
    # Itera tutte le linee nel modello
    for entity in msp.query('CIRCLE'):
        circles.append(entity)
    for entity in msp.query('ARC'):
        arcs.append(entity)
    for entity in msp.query('LINE'):
        lines.append(entity)
    for entity in msp.query('ELLIPSE'):
        ellipses.append(entity)

    
    return circles, arcs, lines, ellipses


################################################################################################    
################################################################################################    


def rotate_circle_by_pp(circle, pivot, angle):
    radius = circle.dxf.radius
    rotated_center_x, rotated_center_y = rotate_point_by_pivot_point(circle.dxf.center, pivot, angle)

    rotated_circle = circle.new()
    rotated_circle.dxf.center = (rotated_center_x, rotated_center_y)
    rotated_circle.dxf.radius = radius
    
    return rotated_circle

def rotate_arc_by_pp(arc, pivot, angle):
    radius = arc.dxf.radius
    #print('Angolo: ', angle)
    #print('Start prima di ruotare: ', arc.dxf.start_angle)
    #print('End prima di ruotare: ', arc.dxf.end_angle)
    rotated_start_angle = deg_to_rad(arc.dxf.start_angle) + angle
    rotated_end_angle = deg_to_rad(arc.dxf.end_angle) + angle
    if rotated_start_angle >= 2*math.pi:
        rotated_start_angle = rotated_start_angle - 2*math.pi
        if rotated_end_angle >= 2*math.pi:
            rotated_end_angle = rotated_end_angle - 2*math.pi
        else:
            rotated_start_angle, rotated_end_angle = rotated_end_angle, rotated_start_angle
    else:
        if rotated_end_angle >= 2*math.pi:
            rotated_end_angle = rotated_end_angle - 2*math.pi
            rotated_start_angle, rotated_end_angle = rotated_end_angle, rotated_start_angle


    rotated_center_x, rotated_center_y = rotate_point_by_pivot_point(arc.dxf.center, pivot, angle)

    rotated_arc = arc.new()
    rotated_arc.dxf.center = (rotated_center_x, rotated_center_y)
    rotated_arc.dxf.radius = radius
    rotated_arc.dxf.start_angle = rad_to_deg(rotated_start_angle)
    rotated_arc.dxf.end_angle = rad_to_deg(rotated_end_angle)
    #print('Start dopo di ruotare: ', rotated_arc.dxf.start_angle)
    #print('End dopo di ruotare: ', rotated_arc.dxf.end_angle)
    return rotated_arc


def rotate_ellipse_by_pp(ellipse, pivot, angle):
    #major_axis = ellipse.dxf.major_axis
    ratio = ellipse.dxf.ratio
    start_param = ellipse.dxf.start_param
    end_param = ellipse.dxf.end_param

    rotated_center_x, rotated_center_y = rotate_point_by_pivot_point(ellipse.dxf.center, pivot, angle)
    major_axis_vector = Vec3(ellipse.dxf.major_axis)
    current_angle = math.atan2(major_axis_vector.y, major_axis_vector.x)
    new_angle = current_angle + angle

    major_axis_length = major_axis_vector.magnitude
    new_major_axis = (major_axis_length * math.cos(new_angle), major_axis_length * math.sin(new_angle))
    
    rotated_major_axis_x, rotated_major_axis_y = rotate_point_by_pivot_point(ellipse.dxf.major_axis, pivot, angle)
    rotated_minor_axis_x, rotated_minor_axis_y = rotate_point_by_pivot_point(ellipse.minor_axis, pivot, angle)

    rotated_ellipse = ellipse.new()
    rotated_ellipse.dxf.center = (rotated_center_x, rotated_center_y)
    print('Nuovo centro: ', rotated_ellipse.dxf.center)
    rotated_ellipse.dxf.major_axis = new_major_axis
    print('Nuovo asse maggiore: ', rotated_ellipse.dxf.major_axis)
    rotated_ellipse.dxf.ratio = ratio
    # print('Nuova ratio: ', rotated_ellipse.dxf.ratio)
    rotated_ellipse.dxf.start_param = start_param
    # print('Nuovo start param: ', rotated_ellipse.dxf.start_param)
    rotated_ellipse.dxf.end_param = end_param
    # print('Nuovo end param: ', rotated_ellipse.dxf.end_param)
    # rotated_ellipse.minor_axis = (rotated_minor_axis_x, rotated_minor_axis_y)
    return rotated_ellipse



def rotate_line_by_pivot_point(line, pivot, angle):
    #print("original line start: ", line.dxf.start)
    #print("original line end: ", line.dxf.end)
    # Ruota l'entità attorno al pivot
    rotated_start_x, rotated_start_y = rotate_point_by_pivot_point(line.dxf.start, pivot, angle)
    rotated_end_x, rotated_end_y = rotate_point_by_pivot_point(line.dxf.end, pivot, angle)
    
    # Crea una nuova entità con le coordinate ruotate
    rotated_line = line.new()
    rotated_line.dxf.start = (rotated_start_x, rotated_start_y)
    rotated_line.dxf.end = (rotated_end_x, rotated_end_y)
    # print("L'entità ruotata è: ", rotated_line)
    #print("start: ", rotated_start_x, rotated_start_y)
    #print("end: ", rotated_end_x, rotated_end_y)

    return rotated_line

##################################################################################################
##################################################################################################
################################################################################################    


def rotate_point_by_pivot_point(point, pivot, angle):

    rotated_point_x = pivot[0] + (point[0] - pivot[0]) * math.cos(angle) - (point[1] - pivot[1]) * math.sin(angle)
    rotated_point_y = pivot[1] + (point[0] - pivot[0]) * math.sin(angle) + (point[1] - pivot[1]) * math.cos(angle)

    return rotated_point_x, rotated_point_y

def deg_to_rad(angle_deg):
    return (angle_deg * math.pi) / 180

def rad_to_deg(angle_rad):
    return (angle_rad * 180) / math.pi