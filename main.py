import pygame as pg
import sys

import asyncio
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        self.mini_map = pg.Surface(RES, pg.SRCALPHA)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.level = 0
        self.new_game()

    def new_game(self):
        self.map = Map(self, self.level)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        # pg.mixer.music.play(-1)

    def update(self):
        self.map.world_map_screen.fill((0, 0, 0, 0))
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()

        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f"{self.clock.get_fps() :.1f}")

    def draw(self):
        # 3d game
        self.object_renderer.draw()
        self.weapon.draw()

        # 2d map
        self.map.draw_minimap()
        self.player.draw()
        scale_factor = 0.3
        self.world_map_scaled = pg.transform.scale(
            self.map.world_map_screen,
            (
                int(self.map.world_map_screen.get_width() * scale_factor),
                int(self.map.world_map_screen.get_height() * scale_factor),
            ),
        )

        visible_area_size = (300, 300)
        visible_area_rect = pg.Rect(
            min(
                max(self.player.x * 100 * scale_factor - visible_area_size[0] // 2, 0),
                self.world_map_scaled.get_width() - visible_area_size[0],
            ),
            min(
                max(self.player.y * 100 * scale_factor - visible_area_size[1] // 2, 0),
                self.world_map_scaled.get_height() - visible_area_size[1],
            ),
            visible_area_size[0],
            visible_area_size[1],
        )

        # border_size = 10  # Adjust the border size as needed
        # pg.draw.rect(self.map.world_map_screen, (0, 0, 0, 0), visible_area_rect.inflate(border_size, border_size))
        self.screen.blit(
            self.world_map_scaled,
            (RES[0] - visible_area_size[0], 0),
            area=visible_area_rect,
        )
        border_size = 10  # Adjust the border size as needed
        pg.draw.rect(
            self.screen,
            (0, 0, 0),
            (RES[0] - visible_area_size[0], 0, visible_area_size[0], visible_area_size[1]),
            border_size,
        )

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                pg.quit()
                sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

    def check_game_over(self):
        if self.player.health < 1:
            self.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.new_game()
            if self.startMusic:
                pg.mixer.music.play(-1)

    def check_win(self):
        if not len(self.object_handler.npc_positions):
            self.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.level += 1
            if self.level >= len(self.map.levels):
                self.level = 0
            print(self.level)
            self.new_game()
            if self.startMusic:
                pg.mixer.music.play(-1)

    async def main(self):
        self.startMusic = False
        while True:
            keys = pg.key.get_pressed()
            if keys[pg.K_SPACE]:
                if not self.startMusic:
                    pg.mixer.music.play(-1)
                self.startMusic = True

            self.check_events()
            self.update()
            self.check_game_over()
            self.check_win()
            self.draw()

            await asyncio.sleep(0)


if __name__ == "__main__":
    game = Game()
    asyncio.run(game.main())
