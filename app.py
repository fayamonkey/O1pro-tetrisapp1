import streamlit as st
import pygame
import numpy as np
import time
import random

# ------------------------------
# Global Constants
# ------------------------------
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 20  # for rendering in pygame
FPS = 60

# Define Tetris shapes (each shape is a list of lists showing the 2D layout)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1],
     [1, 1]],        # O
    [[0, 1, 0],
     [1, 1, 1]],     # T
    [[1, 1, 0],
     [0, 1, 1]],     # S
    [[0, 1, 1],
     [1, 1, 0]],     # Z
    [[1, 0, 0],
     [1, 1, 1]],     # J
    [[0, 0, 1],
     [1, 1, 1]],     # L
]

# Colors for shapes (R, G, B)
SHAPE_COLORS = [
    (0, 255, 255),   # I - cyan
    (255, 255, 0),   # O - yellow
    (128, 0, 128),   # T - purple
    (0, 255, 0),     # S - green
    (255, 0, 0),     # Z - red
    (0, 0, 255),     # J - blue
    (255, 165, 0),   # L - orange
]

# ------------------------------
# Tetris Game Logic
# ------------------------------
class Tetris:
    def __init__(self, rows=BOARD_HEIGHT, cols=BOARD_WIDTH):
        self.rows = rows
        self.cols = cols
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.score = 0
        self.game_over = False

        # current piece info
        self.current_shape = None
        self.current_color = None
        self.current_row = 0
        self.current_col = 0

        # spawn the first piece
        self.new_piece()

    def new_piece(self):
        shape_id = random.randint(0, len(SHAPES) - 1)
        self.current_shape = SHAPES[shape_id]
        self.current_color = SHAPE_COLORS[shape_id]
        self.current_row = 0
        self.current_col = self.cols // 2 - len(self.current_shape[0]) // 2

        # if the new piece immediately collides, game over
        if not self.is_valid_position(self.current_shape, self.current_row, self.current_col):
            self.game_over = True

    def rotate_shape(self, shape):
        # Rotate clockwise
        return list(zip(*shape[::-1]))

    def move_left(self):
        if not self.game_over:
            if self.is_valid_position(self.current_shape, self.current_row, self.current_col - 1):
                self.current_col -= 1

    def move_right(self):
        if not self.game_over:
            if self.is_valid_position(self.current_shape, self.current_row, self.current_col + 1):
                self.current_col += 1

    def move_down(self):
        # Try moving down; if not possible, place piece
        if not self.game_over:
            if self.is_valid_position(self.current_shape, self.current_row + 1, self.current_col):
                self.current_row += 1
            else:
                self.lock_piece()
                self.clear_lines()
                self.new_piece()

    def drop(self):
        # Move piece down until it can no longer move
        if not self.game_over:
            while self.is_valid_position(self.current_shape, self.current_row + 1, self.current_col):
                self.current_row += 1
            self.lock_piece()
            self.clear_lines()
            self.new_piece()

    def rotate(self):
        if not self.game_over:
            new_shape = self.rotate_shape(self.current_shape)
            # Convert tuple-of-tuples back to list-of-lists
            new_shape = [list(row) for row in new_shape]
            if self.is_valid_position(new_shape, self.current_row, self.current_col):
                self.current_shape = new_shape

    def is_valid_position(self, shape, row, col):
        for r in range(len(shape)):
            for c in range(len(shape[r])):
                if shape[r][c] == 1:
                    new_r = row + r
                    new_c = col + c
                    if (new_r < 0 or new_r >= self.rows or 
                        new_c < 0 or new_c >= self.cols or
                        self.board[new_r][new_c] != 0):
                        return False
        return True

    def lock_piece(self):
        # lock current piece into the board
        for r in range(len(self.current_shape)):
            for c in range(len(self.current_shape[r])):
                if self.current_shape[r][c] == 1:
                    self.board[self.current_row + r][self.current_col + c] = self.current_color

    def clear_lines(self):
        lines_cleared = 0
        for r in range(self.rows):
            # check if row is full
            if 0 not in self.board[r]:
                del self.board[r]
                self.board.insert(0, [0 for _ in range(self.cols)])
                lines_cleared += 1
        self.score += lines_cleared ** 2  # simple scoring: 1 line=1pt, 2 lines=4pts, 3=9, 4=16

    def get_board_state_with_piece(self):
        # Return a 2D array with both the locked blocks and the current piece
        temp_board = [[self.board[r][c] for c in range(self.cols)] for r in range(self.rows)]
        if not self.game_over:
            for r in range(len(self.current_shape)):
                for c in range(len(self.current_shape[r])):
                    if self.current_shape[r][c] == 1:
                        temp_board[self.current_row + r][self.current_col + c] = self.current_color
        return temp_board


# ------------------------------
# Simple AI for Tetris
# ------------------------------
def ai_move(tetris: Tetris):
    """
    A very basic "AI" that tries all possible placements/rotations
    and picks one that yields the highest immediate score after line clears.
    """
    if tetris.game_over:
        return

    best_score = -1
    best_row = tetris.current_row
    best_col = tetris.current_col
    best_shape = tetris.current_shape

    original_shape = tetris.current_shape
    original_row = tetris.current_row
    original_col = tetris.current_col

    # Try all rotations
    possible_rotations = []
    shape_to_try = original_shape
    for _ in range(4):
        shape_to_try = [list(row) for row in zip(*shape_to_try[::-1])]
        # avoid duplicates if shape is symmetrical
        if shape_to_try not in possible_rotations:
            possible_rotations.append(shape_to_try)

    for shape in possible_rotations:
        # For each column
        for col in range(tetris.cols - len(shape[0]) + 1):
            # Move piece all the way down
            row = 0
            while tetris.is_valid_position(shape, row + 1, col):
                row += 1

            # Lock the piece temporarily
            saved_board = [row_[:] for row_ in tetris.board]
            saved_score = tetris.score

            tetris.current_shape = shape
            tetris.current_row = row
            tetris.current_col = col
            tetris.lock_piece()
            tetris.clear_lines()
            final_score = tetris.score

            # Evaluate
            score_gained = final_score - saved_score
            if score_gained > best_score:
                best_score = score_gained
                best_row = row
                best_col = col
                best_shape = shape

            # revert changes
            tetris.board = saved_board
            tetris.score = saved_score

    # After finding best placement
    tetris.current_shape = best_shape
    tetris.current_row = best_row
    tetris.current_col = best_col

    # Move down immediately (place the piece)
    while tetris.is_valid_position(tetris.current_shape, tetris.current_row + 1, tetris.current_col):
        tetris.current_row += 1

    tetris.lock_piece()
    tetris.clear_lines()
    tetris.new_piece()

    # Restore original for next turn if needed, but we actually
    # want the AI to "commit" to that placement
    # so do nothing extra here.

# ------------------------------
# Pygame Surface Rendering
# ------------------------------
def draw_tetris_to_surface(tetris: Tetris):
    pygame.init()
    surface = pygame.Surface((tetris.cols * BLOCK_SIZE, tetris.rows * BLOCK_SIZE))
    surface.fill((0, 0, 0))

    # Draw locked blocks + current piece
    board_state = tetris.get_board_state_with_piece()

    for r in range(tetris.rows):
        for c in range(tetris.cols):
            val = board_state[r][c]
            if val != 0:
                # It's a color
                color = val
                pygame.draw.rect(
                    surface,
                    color,
                    (c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    0
                )
                # Draw small border
                pygame.draw.rect(
                    surface,
                    (255, 255, 255),
                    (c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    1
                )

    return surface

# ------------------------------
# Streamlit App
# ------------------------------
def main():
    st.title("Tetris vs. AI in Streamlit")

    # Initialize session state
    if "user_tetris" not in st.session_state:
        st.session_state.user_tetris = Tetris()
    if "ai_tetris" not in st.session_state:
        st.session_state.ai_tetris = Tetris()
    if "game_running" not in st.session_state:
        st.session_state.game_running = False

    user_tetris = st.session_state.user_tetris
    ai_tetris = st.session_state.ai_tetris

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Your Tetris")
        # Display user board
        user_surface = draw_tetris_to_surface(user_tetris)
        user_array = pygame.surfarray.array3d(pygame.transform.rotate(user_surface, 270))
        # We rotated the surface by 270 degrees for the correct orientation for st.image
        # Alternatively, we can just transpose it. For simplicity, do rotation here.
        user_array = np.flipud(user_array)  # flip because of rotation
        st.image(user_array, use_column_width=True)
        st.write(f"Score: {user_tetris.score}")

        # Controls
        if st.button("◀️ Left"):
            user_tetris.move_left()
            st.experimental_rerun()
        if st.button("▶️ Right"):
            user_tetris.move_right()
            st.experimental_rerun()
        if st.button("🔄 Rotate"):
            user_tetris.rotate()
            st.experimental_rerun()
        if st.button("⬇️ Down"):
            user_tetris.move_down()
            st.experimental_rerun()
        if st.button("⏬ Drop"):
            user_tetris.drop()
            st.experimental_rerun()

    with col2:
        st.subheader("AI's Tetris")
        ai_surface = draw_tetris_to_surface(ai_tetris)
        ai_array = pygame.surfarray.array3d(pygame.transform.rotate(ai_surface, 270))
        ai_array = np.flipud(ai_array)
        st.image(ai_array, use_column_width=True)
        st.write(f"Score: {ai_tetris.score}")

    st.write("---")

    if not st.session_state.game_running:
        if st.button("Start Game"):
            st.session_state.game_running = True
            st.experimental_rerun()
    else:
        if st.button("Reset"):
            st.session_state.user_tetris = Tetris()
            st.session_state.ai_tetris = Tetris()
            st.session_state.game_running = False
            st.experimental_rerun()

    # If the game is running and neither side is over, do one step for AI
    if st.session_state.game_running and not user_tetris.game_over and not ai_tetris.game_over:
        # Make AI move
        ai_move(ai_tetris)

        # Also apply gravity to the user's game if you want it to drop slowly:
        user_tetris.move_down()

        # Re-run automatically after a short pause to simulate "time steps"
        time.sleep(0.5)
        st.experimental_rerun()

    # Check for game over
    if user_tetris.game_over or ai_tetris.game_over:
        if user_tetris.game_over and ai_tetris.game_over:
            st.warning("Game Over! It's a draw!")
        elif user_tetris.game_over:
            st.warning("Game Over! AI Wins!")
        else:
            st.success("Game Over! You Win!")
        st.session_state.game_running = False


if __name__ == "__main__":
    main()
