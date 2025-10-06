import pygame
from .paddle import Paddle
from .ball import Ball

WHITE = (255, 255, 255)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)

        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 64)

        # Game over state
        self.game_over = False
        self.winner_text = ""
        self.target_score = 5
        self.game_over_displayed_at = None  # pygame.time.get_ticks() timestamp
        self.game_over_hold_ms = 2000       # 2 seconds

    def handle_input(self):
        # Allow quitting and ignore movement if game over
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def _check_game_over(self):
        if self.player_score >= self.target_score and not self.game_over:
            self.game_over = True
            self.winner_text = "Player Wins!"
            self.game_over_displayed_at = pygame.time.get_ticks()
        elif self.ai_score >= self.target_score and not self.game_over:
            self.game_over = True
            self.winner_text = "AI Wins!"
            self.game_over_displayed_at = pygame.time.get_ticks()

        # After showing message for a short delay, close pygame
        if self.game_over and self.game_over_displayed_at is not None:
            elapsed = pygame.time.get_ticks() - self.game_over_displayed_at
            if elapsed >= self.game_over_hold_ms:
                pygame.quit()
                raise SystemExit

    def update(self):
        if self.game_over:
            # Freeze gameplay while showing winner; still process _check_game_over for timed exit
            self._check_game_over()
            return

        self.ball.move()
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

        # Check for game over
        self._check_game_over()

    def render(self, screen):
        screen.fill((0, 0, 0))

        # Center dashed line
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

        # Winner banner
        if self.game_over:
            banner = self.big_font.render(self.wwinner_text_safe(), True, WHITE)
            banner_rect = banner.get_rect(center=(self.width // 2, self.height // 2))
            screen.blit(banner, banner_rect)

    def wwinner_text_safe(self):
        # Defensive helper to ensure non-empty string for render
        return self.winner_text if self.winner_text else "Game Over"
