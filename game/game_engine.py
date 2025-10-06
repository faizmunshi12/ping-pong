import pygame
from .paddle import Paddle
from .ball import Ball

WHITE = (255, 255, 255)

class GameEngine:
    def __init__(self, width, height):
        # Initialize audio mixer early
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.width = width
        self.height = height

        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)

        # Load sounds
        try:
            self.snd_paddle = pygame.mixer.Sound("assets/paddle.wav")
            self.snd_wall = pygame.mixer.Sound("assets/wall.wav")
            self.snd_score = pygame.mixer.Sound("assets/score.wav")
        except Exception:
            # Fallback: create silent sounds if assets missing to avoid crashes
            self.snd_paddle = None
            self.snd_wall = None
            self.snd_score = None

        # Ball with sound effects
        self.ball = Ball(
            width // 2, height // 2, 7, 7, width, height,
            sounds={"paddle": self.snd_paddle, "wall": self.snd_wall}
        )

        self.player_score = 0
        self.ai_score = 0

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 64)
        self.small_font = pygame.font.SysFont("Arial", 22)

        # Game state for replay flow (from Task 3)
        self.game_over = False
        self.winner_text = ""
        self.target_score = 5
        self.show_winner_until = None
        self.winner_hold_ms = 1200
        self.showing_menu = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if self.showing_menu and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_3:
                    self._start_new_match(best_of=3)
                elif event.key == pygame.K_5:
                    self._start_new_match(best_of=5)
                elif event.key == pygame.K_7:
                    self._start_new_match(best_of=7)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

        if self.game_over or self.showing_menu:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def _start_new_match(self, best_of: int):
        self.target_score = (best_of + 1) // 2
        self.player_score = 0
        self.ai_score = 0
        self.player.y = self.height // 2 - self.paddle_height // 2
        self.ai.y = self.height // 2 - self.paddle_height // 2
        self.ball.reset()
        self.game_over = False
        self.winner_text = ""
        self.showing_menu = False
        self.show_winner_until = None

    def _maybe_enter_menu(self):
        if self.game_over and not self.showing_menu and self.show_winner_until is not None:
            if pygame.time.get_ticks() >= self.show_winner_until:
                self.showing_menu = True

    def _check_game_over(self):
        if self.game_over:
            self._maybe_enter_menu()
            return

        if self.player_score >= self.target_score:
            self.game_over = True
            self.winner_text = "Player Wins!"
            self.show_winner_until = pygame.time.get_ticks() + self.winner_hold_ms
        elif self.ai_score >= self.target_score:
            self.game_over = True
            self.winner_text = "AI Wins!"
            self.show_winner_until = pygame.time.get_ticks() + self.winner_hold_ms

    def update(self):
        if self.game_over or self.showing_menu:
            self._maybe_enter_menu()
            return

        self.ball.move()
        self.ball.check_collision(self.player, self.ai)

        # Scoring and reset if ball exits screen horizontally
        if self.ball.x <= 0:
            self.ai_score += 1
            if self.snd_score:
                self.snd_score.play()
            self.ball.reset()
        elif self.ball.x + self.ball.width >= self.width:
            self.player_score += 1
            if self.snd_score:
                self.snd_score.play()
            self.ball.reset()

        # Simple AI
        self.ai.auto_track(self.ball, self.height)

        self._check_game_over()

    def render(self, screen):
        screen.fill((0, 0, 0))

        for y in range(0, self.height, 20):
            pygame.draw.rect(screen, WHITE, pygame.Rect(self.width // 2 - 1, y, 2, 10))

        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.rect(screen, WHITE, self.ball.rect())

        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        target_text = self.small_font.render(f"First to {self.target_score}", True, WHITE)
        screen.blit(player_text, (self.width // 4 - player_text.get_width() // 2, 20))
        screen.blit(ai_text, (3 * self.width // 4 - ai_text.get_width() // 2, 20))
        screen.blit(target_text, (self.width // 2 - target_text.get_width() // 2, 20))

        if self.game_over and not self.showing_menu:
            banner = self.big_font.render(self._winner_text_safe(), True, WHITE)
            banner_rect = banner.get_rect(center=(self.width // 2, self.height // 2))
            screen.blit(banner, banner_rect)

        if self.showing_menu:
            header = self.font.render("Play Again?", True, WHITE)
            opt1 = self.font.render("Best of 3  - press 3", True, WHITE)
            opt2 = self.font.render("Best of 5  - press 5", True, WHITE)
            opt3 = self.font.render("Best of 7  - press 7", True, WHITE)
            opt4 = self.font.render("Exit       - press Esc", True, WHITE)

            start_y = self.height // 2 - 60
            screen.blit(header, (self.width // 2 - header.get_width() // 2, start_y))
            screen.blit(opt1, (self.width // 2 - opt1.get_width() // 2, start_y + 40))
            screen.blit(opt2, (self.width // 2 - opt2.get_width() // 2, start_y + 75))
            screen.blit(opt3, (self.width // 2 - opt3.get_width() // 2, start_y + 110))
            screen.blit(opt4, (self.width // 2 - opt4.get_width() // 2, start_y + 145))

    def _winner_text_safe(self):
        return self.winner_text if self.winner_text else "Game Over"
