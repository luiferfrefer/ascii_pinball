# ASCII Pinball

A tiny terminal pinball table rendered in ASCII. Use the left and right flippers to keep the ball alive while chasing bumper points.

## Requirements
- Python 3.10+
- A terminal that supports `curses` (most Unix-like shells)

## How to play
1. Run the game:
   ```bash
   python pinball.py
   ```
2. Controls:
   - `space` (or `↑`): launch the ball
   - `A` / `a`: flip the left paddle
   - `L` / `l`: flip the right paddle
   - `q`: quit
3. Scoring:
   - Hit bumpers (`*`) for points. Different bumpers award 25, 50, or 75 points.
   - Losing the ball costs one of your three lives. When lives reach zero the game ends.

Flippers briefly raise when activated, letting you nudge the ball upward with a bit of side-spin.
