import curses
import random
import time
from typing import List, Tuple

BoardPoint = Tuple[int, int]


class Paddle:
    def __init__(self, x: int, y: int, is_left: bool) -> None:
        self.base_x = x
        self.base_y = y
        self.is_left = is_left
        self.flip_timer = 0

    def flip(self) -> None:
        self.flip_timer = 4

    def tick(self) -> None:
        if self.flip_timer > 0:
            self.flip_timer -= 1

    def positions(self) -> List[BoardPoint]:
        if self.flip_timer > 0:
            return self._raised_positions()
        return self._rest_positions()

    def _rest_positions(self) -> List[BoardPoint]:
        if self.is_left:
            return [
                (self.base_y, self.base_x + i)
                for i in range(4)
            ]
        return [
            (self.base_y, self.base_x - i)
            for i in range(4)
        ]

    def _raised_positions(self) -> List[BoardPoint]:
        if self.is_left:
            return [
                (self.base_y - 1, self.base_x + i)
                for i in range(3)
            ] + [(self.base_y - 2, self.base_x + 3)]
        return [
            (self.base_y - 1, self.base_x - i)
            for i in range(3)
        ] + [(self.base_y - 2, self.base_x - 3)]

    def handle_ball(self, ball: "Ball") -> None:
        for py, px in self.positions():
            if int(ball.y) == py and int(ball.x) == px:
                ball.vy = -abs(ball.vy) if ball.vy >= 0 else ball.vy
                if self.is_left:
                    ball.vx = abs(ball.vx) + 0.2
                else:
                    ball.vx = -abs(ball.vx) - 0.2
                break


class Ball:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.ready = True

    def launch(self) -> None:
        if not self.ready:
            return
        self.vx = random.choice([-0.7, -0.4, 0.4, 0.7])
        self.vy = -1.0
        self.ready = False

    def reset(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.ready = True

    def step(self) -> None:
        if self.ready:
            return
        self.x += self.vx
        self.y += self.vy


class Bumper:
    def __init__(self, x: int, y: int, value: int) -> None:
        self.x = x
        self.y = y
        self.value = value

    def collide(self, ball: Ball) -> bool:
        if int(ball.x) == self.x and int(ball.y) == self.y:
            ball.vx *= -1
            ball.vy *= -1
            return True
        return False


class Game:
    def __init__(self, stdscr: "curses._CursesWindow") -> None:
        self.stdscr = stdscr
        self.width = 54
        self.height = 26
        self.score = 0
        self.lives = 3
        self.bumper_values = [25, 50, 75]
        self.bumpers: List[Bumper] = []
        self.ball = Ball(self.width // 2, self.height - 3)
        self.left_paddle = Paddle(8, self.height - 3, True)
        self.right_paddle = Paddle(self.width - 9, self.height - 3, False)
        self.last_time = time.time()
        self._create_bumpers()

    def _create_bumpers(self) -> None:
        pairs = [
            (12, 6), (self.width - 13, 6),
            (10, 10), (self.width - 11, 10),
            (self.width // 2, 8),
        ]
        for idx, (x, y) in enumerate(pairs):
            value = self.bumper_values[idx % len(self.bumper_values)]
            self.bumpers.append(Bumper(x, y, value))

    def draw(self) -> None:
        self.stdscr.clear()
        # Top bar
        self.stdscr.addstr(0, 2, f"ASCII Pinball | Score: {self.score} | Lives: {self.lives} | q to quit")
        # Walls
        for x in range(self.width):
            self.stdscr.addch(1, x, '#')
            self.stdscr.addch(self.height - 1, x, '#')
        for y in range(1, self.height):
            self.stdscr.addch(y, 0, '#')
            self.stdscr.addch(y, self.width - 1, '#')

        # Bumpers
        for bumper in self.bumpers:
            self.stdscr.addch(bumper.y, bumper.x, '*')

        # Paddles
        for y, x in self.left_paddle.positions():
            if 0 < x < self.width - 1 and 1 < y < self.height - 1:
                self.stdscr.addch(y, x, '/')
        for y, x in self.right_paddle.positions():
            if 0 < x < self.width - 1 and 1 < y < self.height - 1:
                self.stdscr.addch(y, x, '\\')

        # Ball
        self.stdscr.addch(int(self.ball.y), int(self.ball.x), 'o' if not self.ball.ready else 'O')

        # Instructions
        self.stdscr.addstr(self.height, 2, "Space: launch | A: left flip | L: right flip")
        if self.ball.ready:
            self.stdscr.addstr(self.height + 1, 2, "Launch the ball to begin!")

        self.stdscr.refresh()

    def handle_collisions(self) -> None:
        if self.ball.ready:
            return

        if int(self.ball.y) <= 2:
            self.ball.y = 2.0
            self.ball.vy *= -1
        if int(self.ball.x) <= 1:
            self.ball.x = 1.0
            self.ball.vx = abs(self.ball.vx)
        if int(self.ball.x) >= self.width - 2:
            self.ball.x = float(self.width - 2)
            self.ball.vx = -abs(self.ball.vx)

        for bumper in self.bumpers:
            if bumper.collide(self.ball):
                self.score += bumper.value

        self.left_paddle.handle_ball(self.ball)
        self.right_paddle.handle_ball(self.ball)

    def reset_ball(self) -> None:
        self.ball.reset(self.width // 2, self.height - 3)

    def update(self) -> None:
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        gravity = 0.12 * dt * 60
        if not self.ball.ready:
            self.ball.vy += gravity
        self.ball.step()
        self.handle_collisions()
        if int(self.ball.y) >= self.height - 1:
            self.lives -= 1
            if self.lives > 0:
                self.reset_ball()
            else:
                self.game_over()

    def game_over(self) -> None:
        self.stdscr.clear()
        msg = "GAME OVER"
        self.stdscr.addstr(self.height // 2, (self.width - len(msg)) // 2, msg)
        self.stdscr.addstr(self.height // 2 + 1, (self.width - 20) // 2, f"Final score: {self.score}")
        self.stdscr.addstr(self.height // 2 + 3, (self.width - 30) // 2, "Press q to quit or r to restart")
        self.stdscr.refresh()
        while True:
            key = self.stdscr.getch()
            if key == ord('q'):
                raise SystemExit
            if key == ord('r'):
                self.score = 0
                self.lives = 3
                self.reset_ball()
                return

    def input_loop(self) -> None:
        self.stdscr.nodelay(True)
        while True:
            key = self.stdscr.getch()
            if key == -1:
                break
            if key in (ord('q'), ord('Q')):
                raise SystemExit
            if key in (ord(' '), curses.KEY_UP):
                self.ball.launch()
            if key in (ord('a'), ord('A')):
                self.left_paddle.flip()
            if key in (ord('l'), ord('L')):
                self.right_paddle.flip()

    def tick(self) -> None:
        self.left_paddle.tick()
        self.right_paddle.tick()

    def run(self) -> None:
        self.stdscr.timeout(0)
        curses.curs_set(0)
        while True:
            self.input_loop()
            self.update()
            self.tick()
            self.draw()
            time.sleep(0.016)


def main(stdscr: "curses._CursesWindow") -> None:
    game = Game(stdscr)
    try:
        game.run()
    except SystemExit:
        pass


if __name__ == "__main__":
    curses.wrapper(main)
