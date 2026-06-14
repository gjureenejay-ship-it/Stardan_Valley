import pygame
import random
from settings import *
from os import path
from support import import_folder
import os


class Overlay:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player

        overlay_path = '../graphics/overlay/'
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}

        self.chara_box_surf = pygame.image.load(path.join(overlay_path, 'stats', 'character_box.png')).convert_alpha()
        self.chara_box_rect = self.chara_box_surf.get_rect(topleft=OVERLAY_POSITIONS['character_box'])

        # load emote folders
        emotes_path = path.join(overlay_path, 'teemo_emotes')
        self.teemo_emotes = {
            folder: frames
            for folder in sorted(os.listdir(emotes_path))
            if path.isdir(fp := path.join(emotes_path, folder)) and (frames := import_folder(fp))
        } if path.exists(emotes_path) else {}

        self.status = next(iter(self.teemo_emotes), None)
        self.previous_status = self.status
        self.frame_index = 0

        self.idle_timer = 0
        self.idle_threshold = 10
        self.variation_timer = 0
        self.variation_interval = random.uniform(5, 10)
        self.idle_variations = [v for v in ('idle_ears', 'idle_lick') if v in self.teemo_emotes]

    def character_box_display(self, dt):
        self.display_surface.blit(self.chara_box_surf, self.chara_box_rect)
        if not self.status:
            return

        moving = self.player.direction.magnitude() > 0
        is_variation = self.status in self.idle_variations

        if not is_variation:
            if moving:
                self.idle_timer = 0
                if self.status == 'idle_sleep':
                    self.status = self.previous_status = 'idle'
                    self.frame_index = 0

                # variation timer only while moving
                self.variation_timer += dt
                if self.variation_timer >= self.variation_interval and self.idle_variations:
                    self.variation_timer = 0
                    self.variation_interval = random.uniform(5, 10)
                    self.previous_status = self.status
                    self.status = random.choice(self.idle_variations)
                    self.frame_index = 0
            else:
                self.idle_timer += dt
                self.variation_timer = 0
                if self.idle_timer >= self.idle_threshold and self.status != 'idle_sleep':
                    self.status = self.previous_status = 'idle_sleep'
                    self.frame_index = 0

        frames = self.teemo_emotes[self.status]
        self.frame_index += 4 * dt

        if self.frame_index >= len(frames):
            self.status = self.previous_status if is_variation else self.status
            self.frame_index = 0

        self.image = frames[min(int(self.frame_index), len(frames) - 1)]
        self.image_rect = self.image.get_rect(topleft=self.chara_box_rect.topleft + Vector2(27, 30))
        self.display_surface.blit(self.image, self.image_rect)

    def display(self, dt: float):
        tool_surf = self.tools_surf[self.player.selected_tool]
        self.display_surface.blit(tool_surf, tool_surf.get_rect(midbottom=OVERLAY_POSITIONS['tool']))

        seed_surf = self.seeds_surf[self.player.selected_seed]
        self.display_surface.blit(seed_surf, seed_surf.get_rect(midbottom=OVERLAY_POSITIONS['seed']))

        self.character_box_display(dt)