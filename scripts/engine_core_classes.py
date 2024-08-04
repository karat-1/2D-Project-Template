import pygame
import math


class Line:
    """
    Mathematicians will literally shit themselves in anger because this is not actually a line but a segment
    Dont forget to update your line coordinates via the update function before using its functions

     mousevector = pygame.Vector2(pygame.mouse.get_pos()).elementwise() / pygame.Vector2(self.game.window.scale_ratio)  # mouse in screenspace
        cam = pygame.Vector2(self.game.world.camera.pos)  # cameras position
        mouse_world_pos = mousevector + cam  # mouse in world space
        examplevec = pygame.Vector2(self.pos[0] + 50 * self.face[0], self.pos[1])
        self.lineObj.update(self.pos[0], self.pos[1], examplevec.x, examplevec.y)
        collision_point = self.lineObj.raycast(self.game.world.tile_map.map['Layer_05'], examplevec, 16)

        if collision_point:
            pygame.draw.circle(self.game.window.display, (255, 255, 255), collision_point - cam, 5, 1)
        line = self.lineObj.start_point - cam
        pygame.draw.line(self.game.window.display, (0, 255, 0, 0), line, collision_point - cam)
        pygame.draw.circle(self.game.window.display, (255, 255, 0), line, 5, 1)

    """

    def __init__(self, x1, y1, x2, y2):
        self.__x1 = x1
        self.__x2 = x2
        self.__y1 = y1
        self.__y2 = y2

    @property
    def start_point(self):
        """
        :return: the x and y coordinates of the startpoint as a Vector2
        """
        return pygame.Vector2(self.__x1, self.__y1)

    @property
    def end_point(self):
        """
        :return: the x and y coordinates of the endpoint as a Vector2
        """
        return pygame.Vector2(self.__x2, self.__y2)

    @property
    def length(self):
        """
        :return: the total length of a line in pixels
        """
        return math.sqrt((self.__x2 - self.__x1) ** 2 + (self.__y2 - self.__y1) ** 2)

    @staticmethod
    def __calculate_orientation(p, q, r):
        val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
        if val > 0:
            return 1
        elif val < 0:
            return 2
        else:
            return 0

    @staticmethod
    def __onSegment(p, q, r):
        if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
                (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
            return True
        return False

    def raycast(self, tile_map: dict, target_position: pygame.Vector2, tile_size: int) -> pygame.Vector2:
        """
        Calculates the pixel position of where the line object intersects with the tiles on a tilemap
        E.g. if you want to test the line of sight you pass in the target_position of the enemy or the player_entities as vector2
        If the function returns False, meaning your line does not collide with a rect, there is line of sight as no tiles obstruct the view
        :param tile_map: the tilemap as a dictionary with a tuple containing the x and y coordinates as keys: tile_map[(5,5)] = Tile()
        :param target_position: the x and y coordinates of target cell as a pygame.Vector2
        :param tile_size: the tile dimensions of the tile map. Only works with tiles where height == width
        :return: False if no collision or a pygame.Vector2 containing the exact point of collision
        """
        target_cell = target_position / tile_size  # tile size
        vec_ray_start = pygame.Vector2(self.__x1 / tile_size, self.__y1 / tile_size)
        vec_ray_dir = (target_cell - vec_ray_start)
        vec_ray_dir = vec_ray_dir.normalize()

        # to account for divide by zero exceptions
        vec_ray_dir.x += 0.000000001
        vec_ray_dir.y += 0.000000001

        vec_ray_stepsize = pygame.Vector2(math.sqrt(1 + (vec_ray_dir.y / vec_ray_dir.x) * (vec_ray_dir.y / vec_ray_dir.x)),
                                          math.sqrt(1 + (vec_ray_dir.x / vec_ray_dir.y) * (vec_ray_dir.x / vec_ray_dir.y)))

        vec_map_check = pygame.Vector2(int(vec_ray_start.x), int(vec_ray_start.y))
        vec_ray_length_1d = pygame.Vector2()

        vec_step = pygame.Vector2()

        if vec_ray_dir.x < 0:
            vec_step.x = -1
            vec_ray_length_1d.x = (vec_ray_start.x - vec_map_check.x) * vec_ray_stepsize.x
        else:
            vec_step.x = 1
            vec_ray_length_1d.x = (vec_map_check.x + 1 - vec_ray_start.x) * vec_ray_stepsize.x

        if vec_ray_dir.y < 0:
            vec_step.y = -1
            vec_ray_length_1d.y = (vec_ray_start.y - vec_map_check.y) * vec_ray_stepsize.y
        else:
            vec_step.y = 1
            vec_ray_length_1d.y = (vec_map_check.y + 1 - vec_ray_start.y) * vec_ray_stepsize.y

        tile_found = False
        max_dist = 100
        dist = 0
        while not tile_found and dist < max_dist:
            if vec_ray_length_1d.x < vec_ray_length_1d.y:
                vec_map_check.x += vec_step.x
                dist = vec_ray_length_1d.x
                vec_ray_length_1d.x += vec_ray_stepsize.x
            else:
                vec_map_check.y += vec_step.y
                dist = vec_ray_length_1d.y
                vec_ray_length_1d.y += vec_ray_stepsize.y
            if (int(vec_map_check.x), int(vec_map_check.y)) in tile_map:
                tile_found = True

        if tile_found:
            vec_intersection = vec_ray_start * tile_size + vec_ray_dir * tile_size * dist
            return vec_intersection
        else:
            return False

    def colliderect(self, rect: pygame.Rect) -> bool:
        """
        Checks if the line object collides with a given rectangle
        :param rect: rectangle of the object collisions should be checked with
        :return: True or False wether or not the line collides with given rectangle
        """
        edges = {'top': [pygame.Vector2(rect.topright), pygame.Vector2(rect.topleft)],
                 'bottom': [pygame.Vector2(rect.bottomright), pygame.Vector2(rect.bottomleft)],
                 'left': [pygame.Vector2(rect.topleft), pygame.Vector2(rect.bottomleft)],
                 'right': [pygame.Vector2(rect.topright), pygame.Vector2(rect.bottomright)]}

        for key in edges:
            if self.collideline(edges[key][0], edges[key][1]):
                return True
        return False

    def collideline(self, sp_targetline: pygame.Vector2, ep_targetline: pygame.Vector2) -> bool:
        """
        Checks if the line object intersects with a given line
        :param sp_targetline: startpoint of the line we want to test collisions for
        :param ep_targetline: endpoint of the line we want to test collisions for
        :return: True if a collision happens, False if no Collision is detected
        """
        o1 = self.__calculate_orientation(self.start_point, self.end_point, sp_targetline)
        o2 = self.__calculate_orientation(self.start_point, self.end_point, ep_targetline)
        o3 = self.__calculate_orientation(sp_targetline, ep_targetline, self.start_point)
        o4 = self.__calculate_orientation(sp_targetline, ep_targetline, self.end_point)

        # General case
        if (o1 != o2) and (o3 != o4):
            return True

        # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
        if (o1 == 0) and self.__onSegment(self.start_point, sp_targetline, self.end_point):
            return True

        # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
        if (o2 == 0) and self.__onSegment(self.start_point, ep_targetline, self.end_point):
            return True

        # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
        if (o3 == 0) and self.__onSegment(sp_targetline, self.start_point, ep_targetline):
            return True

        # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
        if (o4 == 0) and self.__onSegment(sp_targetline, self.end_point, ep_targetline):
            return True

        # If none of the cases
        return False

    def update(self, x1, y1, x2, y2) -> None:
        """
        :param x1: x of startposition
        :param y1: y of startposition
        :param x2: x of endposition
        :param y2: y of endposition
        :return: Nothing
        """
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2


    def render(self, surf, offset, color=(0, 255, 0)):
        pygame.draw.line(surf, color, (self.__x1 - offset.x, self.__y1 - offset.y), (self.__x2 - offset.x, self.__y2 - offset.y))