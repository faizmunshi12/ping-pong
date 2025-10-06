import pygame
import os
from .paddle import Paddle
from .ball import Ball

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Load sound effects
        self.load_sounds()

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.winning_score = 5
        self.game_over = False
        self.winner = None
        self.show_replay_menu = False
        
        self.font = pygame.font.SysFont("Arial", 30)
        self.large_font = pygame.font.SysFont("Arial", 50)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)
        self.ball.set_game_engine(self)

    def load_sounds(self):
        """Load all sound effects with fallback to silent sounds if files not found"""
        try:
            # Try to load sound files - replace these paths with your actual sound files
            self.paddle_hit_sound = pygame.mixer.Sound("sounds/paddle_hit.wav")
            self.wall_bounce_sound = pygame.mixer.Sound("sounds/wall_bounce.wav")
            self.score_sound = pygame.mixer.Sound("sounds/score.wav")
        except:
            print("Sound files not found. Creating silent fallback sounds.")
            # Create silent sounds as fallback
            self.create_silent_sounds()

    def create_silent_sounds(self):
        """Create silent sounds as fallback when sound files are missing"""
        # Create a silent sound (0.1 seconds of silence)
        silent_buffer = pygame.sndarray.array(pygame.Surface((1, 1)))
        self.paddle_hit_sound = pygame.mixer.Sound(buffer=silent_buffer)
        self.wall_bounce_sound = pygame.mixer.Sound(buffer=silent_buffer)
        self.score_sound = pygame.mixer.Sound(buffer=silent_buffer)
        
        # Set volume to 0 to ensure complete silence
        self.paddle_hit_sound.set_volume(0)
        self.wall_bounce_sound.set_volume(0)
        self.score_sound.set_volume(0)

    def handle_input(self):
        if self.show_replay_menu:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_3]:
                self.start_new_match(3)
            elif keys[pygame.K_5]:
                self.start_new_match(5)
            elif keys[pygame.K_7]:
                self.start_new_match(7)
            elif keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        
        if self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.show_replay_menu = True
            elif keys[pygame.K_q]:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self):
        if self.game_over or self.show_replay_menu:
            return
            
        # Store previous velocity to detect changes
        prev_velocity_x = self.ball.velocity_x
        prev_velocity_y = self.ball.velocity_y
        
        self.ball.move()
        self.ball.check_collision(self.player, self.ai)

        # Check for wall bounce (y-velocity change)
        if self.ball.velocity_y != prev_velocity_y and prev_velocity_y != 0:
            self.wall_bounce_sound.play()

        # Check for scoring
        if self.ball.x <= 0:
            self.ai_score += 1
            self.score_sound.play()
            self.check_game_over()
            self.ball.reset()
        elif self.ball.x >= self.width:
            self.player_score += 1
            self.score_sound.play()
            self.check_game_over()
            self.ball.reset()

        self.ai.auto_track(self.ball, self.height)

    def check_game_over(self):
        if self.player_score >= self.winning_score:
            self.game_over = True
            self.winner = "Player"
        elif self.ai_score >= self.winning_score:
            self.game_over = True
            self.winner = "AI"

    def start_new_match(self, match_length):
        self.winning_score = match_length
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.show_replay_menu = False
        self.winner = None
        self.ball.reset()
        
        self.player.y = self.height // 2 - 50
        self.ai.y = self.height // 2 - 50

    def render(self, screen):
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        if not self.game_over and not self.show_replay_menu:
            pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))

        match_info = self.small_font.render(f"First to {self.winning_score}", True, GRAY)
        screen.blit(match_info, (self.width//2 - match_info.get_width()//2, 50))

        if self.game_over and not self.show_replay_menu:
            self.render_game_over(screen)
        elif self.show_replay_menu:
            self.render_replay_menu(screen)

    def render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        winner_text = self.large_font.render(f"{self.winner} Wins!", True, WHITE)
        screen.blit(winner_text, (self.width//2 - winner_text.get_width()//2, self.height//2 - 80))

        score_text = self.font.render(f"Final Score: {self.player_score} - {self.ai_score}", True, WHITE)
        screen.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height//2 - 30))

        replay_text = self.font.render("Press SPACE to play again", True, WHITE)
        screen.blit(replay_text, (self.width//2 - replay_text.get_width()//2, self.height//2 + 20))

        quit_text = self.small_font.render("Press Q to Quit", True, GRAY)
        screen.blit(quit_text, (self.width//2 - quit_text.get_width()//2, self.height//2 + 70))

    def render_replay_menu(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title_text = self.large_font.render("Choose Match Length", True, WHITE)
        screen.blit(title_text, (self.width//2 - title_text.get_width()//2, self.height//2 - 120))

        option_y = self.height//2 - 40
        option_spacing = 60
        
        bo3_text = self.font.render("3 - Best of 3", True, WHITE)
        screen.blit(bo3_text, (self.width//2 - bo3_text.get_width()//2, option_y))
        
        bo5_text = self.font.render("5 - Best of 5", True, WHITE)
        screen.blit(bo5_text, (self.width//2 - bo5_text.get_width()//2, option_y + option_spacing))
        
        bo7_text = self.font.render("7 - Best of 7", True, WHITE)
        screen.blit(bo7_text, (self.width//2 - bo7_text.get_width()//2, option_y + option_spacing * 2))

        exit_text = self.font.render("ESC - Exit Game", True, GRAY)
        screen.blit(exit_text, (self.width//2 - exit_text.get_width()//2, option_y + option_spacing * 3 + 20))

        instruct_text = self.small_font.render("Press the corresponding number key to select", True, GRAY)
        screen.blit(instruct_text, (self.width//2 - instruct_text.get_width()//2, self.height - 80))