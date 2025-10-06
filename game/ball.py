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
        self.prev_x = x
        self.prev_y = y
        self.game_engine = None  # Will be set by GameEngine to allow sound access

    def set_game_engine(self, game_engine):
        """Allow ball to access game engine for playing sounds"""
        self.game_engine = game_engine

    def move(self):
        self.prev_x = self.x
        self.prev_y = self.y
        
        self.x += self.velocity_x
        self.y += self.velocity_y

        if self.y <= 0 or self.y + self.height >= self.screen_height:
            self.velocity_y *= -1

    def check_collision(self, player, ai):
        ball_rect = self.rect()
        
        # Store previous velocity to detect changes
        prev_velocity_x = self.velocity_x
        
        # Check collision with player paddle
        if self.velocity_x < 0:
            if self.continuous_collision_detection(player, ball_rect):
                self.handle_paddle_collision(player)
        
        # Check collision with AI paddle  
        elif self.velocity_x > 0:
            if self.continuous_collision_detection(ai, ball_rect):
                self.handle_paddle_collision(ai)

        # Play paddle hit sound if velocity changed due to collision
        if self.velocity_x != prev_velocity_x and self.game_engine:
            self.game_engine.paddle_hit_sound.play()

    def continuous_collision_detection(self, paddle, ball_rect):
        paddle_rect = paddle.rect()
        
        if ball_rect.colliderect(paddle_rect):
            return True
        
        if self.velocity_x != 0 or self.velocity_y != 0:
            move_rect = pygame.Rect(
                min(self.prev_x, self.x),
                min(self.prev_y, self.y),
                abs(self.velocity_x) + self.width,
                abs(self.velocity_y) + self.height
            )
            
            if move_rect.colliderect(paddle_rect):
                return True
        
        return False

    def handle_paddle_collision(self, paddle):
        paddle_rect = paddle.rect()
        ball_rect = self.rect()
        
        relative_intersect_y = (paddle_rect.centery - ball_rect.centery) / (paddle_rect.height / 2)
        
        self.velocity_x *= -1
        self.velocity_y = -relative_intersect_y * 5
        
        min_speed = 3
        if abs(self.velocity_y) < min_speed:
            self.velocity_y = min_speed if self.velocity_y > 0 else -min_speed
        
        speed_increase = 1.05
        self.velocity_x *= speed_increase
        self.velocity_y *= speed_increase
        
        if self.velocity_x > 0:
            self.x = paddle_rect.right + 1
        else:
            self.x = paddle_rect.left - self.width - 1

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])
        self.prev_x = self.x
        self.prev_y = self.y

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)