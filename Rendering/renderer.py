import pygame
import numpy as np

class Renderer:
    """
    Handles the Pygame window and all canvas-drawing operations.
    Fully isolated from physical calculations.
    """
    def __init__(self, width=800, height=600, title="Educational Physics Simulator"):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.font = pygame.font.SysFont("Consolas", 18)

    def clear(self, color=(30, 30, 40)):
        """Clears the frame buffer with a background color."""
        self.screen.fill(color)

    def draw_body(self, body, body_color=(80, 160, 240), vector_color=(250, 100, 100)):
        """
        Draws a physical body (circle) and a line representing its velocity vector.
        """
        # Render the circular body
        pos = (int(body.position[0]), int(body.position[1]))
        pygame.draw.circle(self.screen, body_color, pos, int(body.radius))
        
        # Draw a small border/outline
        pygame.draw.circle(self.screen, (255, 255, 255), pos, int(body.radius), 1)

        # Educational vector visualization: Draw velocity direction/magnitude
        vel_len = np.linalg.norm(body.velocity)
        if vel_len > 1.0:
            # Scale velocity line so it fits nicely (e.g. 0.1 scale)
            end_pos = body.position + body.velocity * 0.1
            end_pos_int = (int(end_pos[0]), int(end_pos[1]))
            pygame.draw.line(self.screen, vector_color, pos, end_pos_int, 2)

    def draw_text(self, text, x, y, color=(220, 220, 220)):
        """Draws informational text on the screen."""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def update(self):
        """Refreshes the screen display."""
        pygame.display.flip()

    def quit(self):
        """Gracefully closes the Pygame window."""
        pygame.quit()
