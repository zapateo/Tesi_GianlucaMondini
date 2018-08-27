import pygame
import sys

from geometria import *
from utilities import *

ENABLED_DEBUG = True

def mark_unwanted_edges(edges, primary_site):
    # FIXME quando un bordo è stato contrassegnato interrompi l'iterazione
    edges = edges[:]
    for outer_i in range(len(edges)):
        for point in (edges[outer_i].start, edges[outer_i].end):
            for inner_edge in edges:
                join_edge = Edge(primary_site, point)
                intersection = segment_intersection(inner_edge, join_edge)
                if intersection and not points_are_close(intersection, point):
                    edges[outer_i].to_be_deleted = True
    return edges

def voronoj_cell(edges, primary_site, other_sites):
    """
    In un diagramma di Voronoj delimitato da `edges` e con un insieme di siti
    composto da `primary_site` e `other_sites`, restituisce una lista di oggetti
    `Edge` che delimitano la cella di Voronoj corrispondente a `primary_site`

    Esempi/Test
    ===========

    >>> from geometria import *

    Caso in cui l'area sia quadrata

    >>> edges = [E(0, 0, 100, 0), E(100, 0, 100, 100), E(100, 100, 0, 100), E(0, 100, 0, 0)]
    >>> primary_site = Point(25, 25)
    >>> other_sites = [Point(75, 75)]
    >>> cell = voronoj_cell(edges, primary_site, other_sites)
    >>> for edge in cell:
    ...     print(edge)
    Edge_from:Point(100.0, 0.0)to:Point(0, 0)
    Edge_from:Point(0.0, 100.0)to:Point(0, 0)
    Edge_from:Point(100.0, 0.0)to:Point(0.0, 100.0)

    >>> edges = [E(100, 0, 300, 0), E(300, 0, 300, 200), E(300, 200, 200, 400), E(200, 400, 0, 200), E(0, 200, 100, 0)]
    >>> primary_site = Point(200, 300)
    >>> other_sites = [Point(100, 100), Point(100, 200)]
    >>> cell = voronoj_cell(edges, primary_site, other_sites)
    >>> for edge in cell:
    ...     print(edge)
    Edge_from:Point(300, 200)to:Point(200, 400)
    Edge_from:Point(300.0, 125.0)to:Point(300, 200)
    Edge_from:Point(100.0, 300.0)to:Point(200, 400)
    Edge_from:Point(250.0, 150.0)to:Point(300.0, 125.0)
    Edge_from:Point(100.0, 300.0)to:Point(250.0, 150.0)
    """
    #---------------------------------------------------------------------------
    for site in other_sites:
        #-----------------------------------------------------------------------
        union_edge = Edge(primary_site, site)
        #-----------------------------------------------------------------------
        perp_bisect = perpendicular_bisector(union_edge)
        #-----------------------------------------------------------------------
        intersections = []
        #-----------------------------------------------------------------------
        new_edges = []
        #-----------------------------------------------------------------------
        edges = mark_unwanted_edges(edges, primary_site)
        #-----------------------------------------------------------------------
        # for edge in edges:
        for i in range(len(edges)):
            if edges[i].to_be_deleted:
                continue
            intersect = segment_intersection(
                from_line_to_segment(perp_bisect),
                edges[i]
            )
            #-------------------------------------------------------------------
            if intersect:
                #---------------------------------------------------------------
                edges[i].to_be_deleted = True
                #---------------------------------------------------------------
                p1 = edges[i].start
                p2 = edges[i].end
                edge_p1_primary_site = Edge(p1, primary_site)
                edge_p2_primary_site = Edge(p2, primary_site)
                int1 = segment_intersection(
                    from_line_to_segment(perp_bisect),
                    edge_p1_primary_site
                )
                int2 = segment_intersection(
                    from_line_to_segment(perp_bisect),
                    edge_p2_primary_site
                )
                if int1 and not int2:
                    keep = p2
                elif not int1 and int2:
                    keep = p1
                elif int1 and int2:
                    # FIXME
                    # raise Exception("int1 and int2")
                    pass
                else:
                    raise Exception()
                #---------------------------------------------------------------

                new_edge = Edge(intersect, keep)
                new_edges.append(new_edge)
                #---------------------------------------------------------------
                add_to_intersections = True
                close_value = lambda a, b: abs(a - b) < 0.001
                for i in intersections:
                    if close_value(i.x, intersect.x) and close_value(i.y, intersect.y):
                        add_to_intersections = False
                if add_to_intersections:
                    intersections.append(intersect)
                #---------------------------------------------------------------
            # end if intersect
            #-----------------------------------------------------------------------
            edges = mark_unwanted_edges(edges, primary_site)
            #---------------------------------------------------------------------------
        # end for edge in edges
        edges = edges + new_edges
        #-----------------------------------------------------------------------
        if len(intersections) == 2:
            edges.append(
                Edge(intersections[0], intersections[1])
            )
        elif len(intersections) == 0:
            # raise Exception("no intersections..")
            pass
        else:
            drawer.clear()
            drawer.draw(from_line_to_segment(perp_bisect), "pb")
            drawer.draw_all(other_sites)
            drawer.draw(primary_site, "prim. site")
            drawer.draw_all(intersections)
            drawer.draw_all(edges)
            drawer.title("EXCEPTION!!!")
            drawer.wait()
            raise Exception(f"intersections contains {len(intersections)} elements, but it should contain 0 or 2")
        #-----------------------------------------------------------------------
        edges = list(filter(lambda e: not e.to_be_deleted, edges))
        #-----------------------------------------------------------------------
    # end for site in other_sites

    edges = mark_unwanted_edges(edges, primary_site)
    #---------------------------------------------------------------------------
    edges = list(filter(lambda e: not e.to_be_deleted, edges))
    #---------------------------------------------------------------------------
    temp_edges = []
    for edge in edges:
        insert = True
        for temp_edge in temp_edges:
            if edges_are_close(edge, temp_edge):
                insert = False
        if insert:
            temp_edges.append(edge)
    edges = temp_edges
    #---------------------------------------------------------------------------
    return edges

def vertices_from_edges(edges):
    """
    Restituisce la lista di vertici definiti dalla lista di segmenti `edges`

    >>> points = vertices_from_edges([E(0, 0, 1, 1)])
    >>> for point in points:
    ...     print(point)
    Point(0, 0)
    Point(1, 1)

    >>> points = vertices_from_edges([E(0, 0, 0, 1), E(0, 1, 1, 1), E(1, 1, 1, 0), E(1, 0, 0, 0)])
    >>> for point in points:
    ...     print(point)
    Point(0, 0)
    Point(0, 1)
    Point(1, 1)
    Point(1, 0)
    """
    points = []
    for e in edges:
        for candidate in (e.start, e.end):
            add = True
            for point in points:
                if points_are_close(candidate, point):
                    add = False
            if add:
                points.append(candidate)
    return points

def center_of_mass(points):
    """
    Restituisce le coordinate del centro di massa del poligono `vertices`

    Il poligono deve essere convesso e i segmenti contenuti in `edges` devono
    delimitare un perimetro chiuso

    >>> point, area = center_of_mass([Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)])
    >>> str(point)
    'Point(0.5, 0.5)'
    >>> area
    1.0

    """
    # Adattato da https://stackoverflow.com/a/46937541
    vertices = []
    for point in points:
        vertices.append((point.x, point.y))

    x_cent = y_cent = area = 0
    v_local = vertices + [vertices[0]]

    for i in range(len(v_local) - 1):
        factor = v_local[i][0] * v_local[i+1][1] - v_local[i+1][0] * v_local[i][1]
        area += factor
        x_cent += (v_local[i][0] + v_local[i+1][0]) * factor
        y_cent += (v_local[i][1] + v_local[i+1][1]) * factor

    area /= 2.0
    x_cent /= (6 * area)
    y_cent /= (6 * area)

    area = math.fabs(area)

    # return ([x_cent, y_cent], area)
    return Point(x_cent, y_cent), area

# def center_of_mass(edges):
#     """
#     Restituisce le coordinate del centro di massa del poligono `edges`
#
#     Il poligono deve essere convesso e i segmenti contenuti in `edges` devono
#     delimitare un perimetro chiuso
#
#     >>> str(center_of_mass([E(0, 0, 1, 0), E(1, 0, 1, 1), E(1, 1, 0, 1), E(0, 1, 0, 0)]))
#     'Point(0.5, 0.5)'
#     """
#     x_sum = 0
#     y_sum = 0
#     for e in edges:
#         # Aggiungo solo il punto e.start perchè
#         # il punto e.end è aggiunto automaticamente dal segmente
#         # successivo
#         x_sum += e.start.x
#         y_sum += e.start.y
#     n = len(edges)
#     return Point(x_sum/n, y_sum/n)

def mov(target_pos, actual_pos):
    dpos = target_pos - actual_pos
    if dpos == 0:
        return 0
    elif dpos > 0:
        return min(1, dpos)
    elif dpos < 0:
        return max(-1, dpos)
    else:
        assert False

if __name__ == "__main__":

    screen_width, screen_height = 1300, 900
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    global drawer
    drawer = Drawer(screen, screen_width, screen_height)

    import doctest
    doctest.testmod()

    sites = [Point(200, 300), Point(100, 100), Point(100, 200), Point(150, 200), Point(160, 203)]

    while True:

        drawer.clear()

        areas = []

        for primary_site in sites:
            edges = [E(100, -200, 300, 0), E(300, 0, 300, 200), E(300, 200, 200, 400), E(200, 400, 0, 200), E(0, 200, 100, -200)]
            other_sites = sites[:]
            other_sites.remove(primary_site)
            cell = voronoj_cell(edges, primary_site, other_sites)
            com, area = center_of_mass(vertices_from_edges(cell))
            areas.append(area)
            primary_site.new_x = com.x
            primary_site.new_y = com.y

            drawer.draw_all(cell)
            drawer.draw_all(sites)
            drawer.draw(primary_site)
            drawer.flip()
            # pygame.time.wait(3)

        for site in sites:
            site.x += mov(site.new_x, site.x)
            site.y += mov(site.new_y, site.y)

        print(" - ".join([str(round(a, 1)) for a in areas]))