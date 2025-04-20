import glfw
from OpenGL.GL import *

subject_polygon = []  
clip_polygon = []     
result_polygon = []  
input_mode = 0        
angle = 0             

def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 800, "Lab5", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.5, 1.5, -1.5, 1.5, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    while not glfw.window_should_close(window):
        display(window)
    glfw.destroy_window(window)
    glfw.terminate()

def display(window):
    global angle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glRotatef(angle, 0, 0, 1)
    if input_mode == 0:
        draw_polygon(subject_polygon, (0.0, 0.0, 1.0))
    elif input_mode == 1:
        draw_polygon(subject_polygon, (0.0, 0.0, 1.0))
        draw_polygon(clip_polygon, (1.0, 0.0, 0.0))
    else:
        draw_polygon(subject_polygon, (0.0, 0.0, 1.0))
        draw_polygon(clip_polygon, (1.0, 0.0, 0.0))
        draw_polygon(result_polygon, (0.0, 1.0, 0.0))
    glfw.swap_buffers(window)
    glfw.poll_events()

def draw_polygon(polygon, color):
    if not polygon:
        return
    glColor3f(*color)
    glBegin(GL_LINE_LOOP)
    for point in polygon:
        glVertex2f(*point)
    glEnd()
    glPointSize(5.0)
    glBegin(GL_POINTS)
    for point in polygon:
        glVertex2f(*point)
    glEnd()

def mouse_button_callback(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        width, height = glfw.get_window_size(window)
        x = (x / width) * 3.0 - 1.5
        y = 1.5 - (y / height) * 3.0
        if input_mode == 0:
            subject_polygon.append((x, y))
        elif input_mode == 1:
            clip_polygon.append((x, y))

def key_callback(window, key, scancode, action, mods):
    global input_mode, subject_polygon, clip_polygon, result_polygon, angle
    if action == glfw.PRESS:
        if key == glfw.KEY_ENTER:
            if input_mode == 0 and len(subject_polygon) >= 3:
                input_mode = 1
            elif input_mode == 1 and len(clip_polygon) >= 3:
                input_mode = 2
                result_polygon = weiler_atherton_clip(subject_polygon, clip_polygon)       
        elif key == glfw.KEY_SPACE and input_mode == 2:
            input_mode = 0
            subject_polygon = []
            clip_polygon = []
            result_polygon = []
        elif key == glfw.KEY_LEFT:
            angle -= 5
        elif key == glfw.KEY_RIGHT:
            angle += 5

def weiler_atherton_clip(subject_poly, clip_poly):
    intersections = find_intersections(subject_poly, clip_poly)
    if not intersections:
        if is_point_inside_polygon(subject_poly[0], clip_poly):
            return subject_poly.copy()
        else:
            return []
    subject_list = insert_intersections(subject_poly, intersections, is_subject=True)
    clip_list = insert_intersections(clip_poly, intersections, is_subject=False)
    mark_entries_exits(subject_list, clip_list)
    result = build_result_polygon(subject_list, clip_list)
    return result

def find_intersections(subject, clip):
    intersections = []
    for i in range(len(subject)):
        s1 = subject[i]
        s2 = subject[(i+1)%len(subject)]
        for j in range(len(clip)):
            c1 = clip[j]
            c2 = clip[(j+1)%len(clip)]
            intersect = line_intersection(s1, s2, c1, c2)
            if intersect:
                intersections.append({
                    'point': intersect,
                    'subject_edge': (i, (i+1)%len(subject)),
                    'clip_edge': (j, (j+1)%len(clip))
                })
    return intersections

def line_intersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    if den == 0:
        return None 
    t = ((x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)) / den
    u = -((x1 - x2)*(y1 - y3) - (y1 - y2)*(x1 - x3)) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x1 + t*(x2 - x1)
        y = y1 + t*(y2 - y1)
        return (x, y)
    return None

def insert_intersections(polygon, intersections, is_subject):
    poly_list = []
    for i in range(len(polygon)):
        poly_list.append({
            'point': polygon[i],
            'is_intersection': False,
            'is_entry': None,
            'next': None,
            'prev': None
        })
    relevant_intersections = []
    for intersect in intersections:
        edge = intersect['subject_edge'] if is_subject else intersect['clip_edge']
        relevant_intersections.append({
            'edge': edge,
            'point': intersect['point'],
            'other_poly_intersect': intersect
        })
    relevant_intersections.sort(key=lambda x: (x['edge'][0], 
        point_position_on_edge(polygon[x['edge'][0]], polygon[x['edge'][1]], x['point'])))
    offset = 0
    current_edge = -1
    edge_intersections = []
    for intersect in relevant_intersections:
        if intersect['edge'][0] != current_edge:
            edge_intersections.sort(key=lambda x: point_position_on_edge(
                polygon[current_edge], polygon[(current_edge+1)%len(polygon)], x['point']))
            for ei in edge_intersections:
                idx = current_edge + 1 + offset
                poly_list.insert(idx, {
                    'point': ei['point'],
                    'is_intersection': True,
                    'is_entry': None,
                    'next': None,
                    'prev': None,
                    'corresponding': ei['other_poly_intersect']
                })
                offset += 1
            current_edge = intersect['edge'][0]
            edge_intersections = [intersect]
        else:
            edge_intersections.append(intersect)
    if edge_intersections:
        edge_intersections.sort(key=lambda x: point_position_on_edge(
            polygon[current_edge], polygon[(current_edge+1)%len(polygon)], x['point']))
        for ei in edge_intersections:
            idx = current_edge + 1 + offset
            poly_list.insert(idx, {
                'point': ei['point'],
                'is_intersection': True,
                'is_entry': None,
                'next': None,
                'prev': None,
                'corresponding': ei['other_poly_intersect']
            })
            offset += 1
    for i in range(len(poly_list)):
        poly_list[i]['prev'] = poly_list[(i-1)%len(poly_list)]
        poly_list[i]['next'] = poly_list[(i+1)%len(poly_list)]
    return poly_list

def point_position_on_edge(p1, p2, p):
    if p1[0] == p2[0]:
        return (p[1] - p1[1]) / (p2[1] - p1[1])
    else:
        return (p[0] - p1[0]) / (p2[0] - p1[0])

def mark_entries_exits(subject_list, clip_list):
    if not subject_list:
        return
    first_point = subject_list[0]['point']
    inside = is_point_inside_polygon(first_point, [n['point'] for n in clip_list if not n['is_intersection']])
    for node in subject_list:
        if node['is_intersection']:
            node['is_entry'] = not inside
            inside = not inside
    for node in clip_list:
        if node['is_intersection']:
            for s_node in subject_list:
                if s_node['is_intersection'] and s_node['point'] == node['point']:
                    node['is_entry'] = s_node['is_entry']
                    break

def build_result_polygon(subject_list, clip_list):
    result = []
    visited = set()
    start_node = None
    for node in subject_list:
        if node['is_intersection'] and node['is_entry'] and id(node) not in visited:
            start_node = node
            break
    if not start_node:
        if subject_list and is_point_inside_polygon(subject_list[0]['point'], 
           [n['point'] for n in clip_list if not n['is_intersection']]):
            return [n['point'] for n in subject_list if not n['is_intersection']]
        else:
            return []
    while start_node:
        current_list = subject_list
        polygon_part = []
        node = start_node
        while True:
            polygon_part.append(node['point'])
            visited.add(id(node))
            next_node = node['next'] if current_list is subject_list else node['prev']
            if next_node['is_intersection']:
                other_list = clip_list if current_list is subject_list else subject_list
                for other_node in other_list:
                    if other_node['is_intersection'] and other_node['point'] == next_node['point']:
                        node = other_node
                        current_list = other_list
                        break
                else:
                    node = next_node
            else:
                node = next_node
            if node is start_node:
                break
        result.extend(polygon_part)
        start_node = None
        for node in subject_list:
            if node['is_intersection'] and node['is_entry'] and id(node) not in visited:
                start_node = node
                break
    return result

def is_point_inside_polygon(point, polygon):
    if len(polygon) < 3:
        return False
    x, y = point
    inside = False
    n = len(polygon)    
    p1x, p1y = polygon[0]
    for i in range(n+1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

if __name__ == "__main__":
    main()
