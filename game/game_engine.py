import pygame
from .paddle import Paddle
from .ball import Ball

# Game Engine
WHITE = (255, 255, 255)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)

        # Ball is slightly larger for visibility; speeds controlled in Ball
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0

        self.font = pygame.font.SysFont("Arial", 30)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self):
        # Move once for coarse vertical wall handling
        self.ball.move()
        # Then perform swept collision checks vs paddles and vertical bounds
        self.ball.check_collision(self.player, self.ai)

        # Scoring and reset if ball exits screen horizontally
        if self.ball.x <= 0:
            self.ai_score += 1
            self.ball.reset()
        elif self.ball.x + self.ball.width >= self.width:
            self.player_score += 1
            self.ball.reset()

        # Simple AI tracking
        self.ai.auto_track(self.ball, self.height)

    def render(self, screen):
        screen.fill((0, 0, 0))

        # Draw center line
        for y in range(0, self.height, 20):
            pygame.draw.rect(screen, WHITE, pygame.Rect(self.width // 2 - 1, y, 2, 10))

        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.rect(screen, WHITE, self.ball.rect())

        # Scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width // 4 - player_text.get_width() // 2, 20))
        screen.blit(ai_text, (3 * self.width // 4 - ai_text.get_width() // 2, 20))
