import pygame
from settings import LAYERS
from random import randint
from timer import Timer


class Cow(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, z=LAYERS['main']):
        super().__init__(groups)

        # --- animation ---
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.3, -self.rect.height * 0.4)

        # --- game time ---
        self.game_time = [6, 0]

        # --- state machine ---
        # States: 'idle', 'munch', 'sit', 'sit_idle', 'sleep', 'stand_up'
        self.state = 'idle'
        self.stand_up_done = False

        # Timers
        self.state_timer = Timer(randint(2000, 4000))
        self.state_timer.activate()

    # ------------------------------------------------------------------ #
    #  Setup helpers called by level.py                                    #
    # ------------------------------------------------------------------ #
    def setup_important_positions(self, name, pos):
        pass  # No movement, positions unused

    def setup_cow_collision_tiles(self, collision_group):
        pass  # No movement, collision unused

    def setup_time(self, game_time):
        self.game_time = game_time

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #
    @property
    def hour(self):
        return self.game_time[0]

    def _is_night(self):
        return self.hour >= 20 or self.hour < 6

    def _is_daytime(self):
        return 6 <= self.hour < 20

    # ------------------------------------------------------------------ #
    #  Animation                                                           #
    # ------------------------------------------------------------------ #
    def animate(self, dt):
        frames = self.frames.get(self.state, self.frames['idle'])
        self.frame_index += 6 * dt

        if self.state == 'stand_up':
            # Play once then flag done
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1
                self.stand_up_done = True
        elif self.state == 'sit':
            # Play sit-down animation once, then hold on last frame
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1
        else:
            if self.frame_index >= len(frames):
                self.frame_index = 0

        self.image = frames[int(self.frame_index)]

    # ------------------------------------------------------------------ #
    #  State transitions                                                   #
    # ------------------------------------------------------------------ #
    def _enter_state(self, new_state):
        self.state = new_state
        self.frame_index = 0
        self.stand_up_done = False

        if new_state == 'idle':
            self.state_timer = Timer(randint(2000, 4000))
            self.state_timer.activate()

        elif new_state == 'munch':
            self.state_timer = Timer(randint(4000, 7000))
            self.state_timer.activate()

        elif new_state == 'sit':
            # sit plays once; transition to sit_idle is handled in animate check
            self.state_timer = None

        elif new_state == 'sit_idle':
            self.state_timer = Timer(randint(5000, 10000))
            self.state_timer.activate()

        elif new_state == 'sleep':
            self.state_timer = None  # sleep until morning

        elif new_state == 'stand_up':
            self.state_timer = None

    # ------------------------------------------------------------------ #
    #  State machine                                                       #
    # ------------------------------------------------------------------ #
    def _update_state(self):
        if self.state_timer:
            self.state_timer.update()

        # --- Night: go to sleep ---
        if self._is_night():
            if self.state not in ('sit', 'sit_idle', 'sleep', 'stand_up'):
                self._enter_state('sit')
            return

        # --- Day logic ---
        if self.state == 'idle':
            if not self.state_timer.active:
                # Randomly eat or sit for a bit
                if randint(0, 1) == 0:
                    self._enter_state('munch')
                else:
                    self._enter_state('sit')

        elif self.state == 'munch':
            if not self.state_timer.active:
                self._enter_state('idle')

        elif self.state == 'sit':
            # Wait for sit animation to finish (frame held at end)
            frames = self.frames.get('sit', self.frames['idle'])
            if self.frame_index >= len(frames) - 1:
                self._enter_state('sit_idle')

        elif self.state == 'sit_idle':
            if not self.state_timer.active:
                self._enter_state('stand_up')

        elif self.state == 'stand_up':
            if self.stand_up_done:
                self._enter_state('idle')

        elif self.state == 'sleep':
            if self._is_daytime():
                self._enter_state('stand_up')

    # ------------------------------------------------------------------ #
    #  Main update                                                         #
    # ------------------------------------------------------------------ #
    def update(self, dt):
        self._update_state()
        self.animate(dt)