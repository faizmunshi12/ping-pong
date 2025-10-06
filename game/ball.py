import pygame
import random

class Ball:
    def __init__(self, x, y, width, height, screen_width, screen_height):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])
        self.max_speed_x = 9
        self.max_speed_y = 7

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def move(self):
        # Sub-step movement to reduce tunneling on top/bottom walls
        remaining_x = self.velocity_x
        remaining_y = self.velocity_y
        steps = int(max(1, max(abs(remaining_x), abs(remaining_y))))
        step_x = remaining_x / steps
        step_y = remaining_y / steps

        for _ in range(steps):
            self.x += step_x
            self.y += step_y

            # Vertical bounds bounce with snap and invert
            if self.y <= 0:
                self.y = 0
                self.velocity_y = -abs(self.velocity_y)
                step_y = -abs(step_y)
            elif self.y + self.height >= self.screen_height:
                self.y = self.screen_height - self.height
                self.velocity_y = abs(self.velocity_y) * -1
                step_y = -abs(step_y)

    def _apply_bounce_angle(self, paddle_rect, is_left):
        # Compute relative impact location to shape angle
        paddle_center = paddle_rect.centery
        ball_center = self.rect().centery
        offset = (ball_center - paddle_center) / (paddle_rect.height / 2)
        offset = max(-1, min(1, offset))

        # Increase base horizontal speed slightly on each hit, clamp to max
        new_speed_x = min(self.max_speed_x, abs(self.velocity_x) + 0.3)
        self.velocity_x = (new_speed_x if not is_left else -new_speed_x)

        # Adjust vertical velocity based on impact offset, clamp
        self.velocity_y = max(-self.max_speed_y, min(self.max_speed_y, self.velocity_y + offset * 3))

    def _swept_collide_with_paddle(self, paddle_rect, is_left):
        # Simple overlap check then resolve by snapping to paddle edge and reflecting
        if not self.rect().colliderect(paddle_rect):
            return False

        if is_left:
            # Snap just to the right of left paddle
            self.x = paddle_rect.right
        else:
            # Snap just to the left of right paddle
            self.x = paddle_rect.left - self.width

        # Apply bounce and slight positional nudge to avoid immediate re-collision
        self._apply_bounce_angle(paddle_rect, is_left)
        self.x += (1 if not is_left else -1)
        return True

    def check_collision(self, player, ai):
        # Perform micro-stepped sweep along current velocity to avoid tunneling through paddles
        steps = int(max(1, max(abs(self.velocity_x), abs(self.velocity_y))))
        step_x = self.velocity_x / steps
        step_y = self.velocity_y / steps

        collided = False
        for _ in range(steps):
            # advance
            self.x += step_x
            self.y += step_y

            # Check paddle collisions at each micro-step
            if self._swept_collide_with_paddle(player.rect(), True):
                collided = True
                break
            if self._swept_collide_with_paddle(ai.rect(), False):
                collided = True
                break

            # Top/bottom handled here as well to respect the sweep path
            if self.y <= 0:
                self.y = 0
                self.velocity_y = -abs(self.velocity_y)
            elif self.y + self.height >= self.screen_height:
                self.y = self.screen_height - self.height
                self.velocity_y = abs(self.velocity_y) * -1

        return collided

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        # Launch back toward last scorer’s side by flipping x, randomize y
        self.velocity_x = -self.velocity_x if self.velocity_x != 0 else random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])
