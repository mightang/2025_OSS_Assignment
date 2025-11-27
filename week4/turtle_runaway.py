import tkinter as tk
import turtle, random, time

class EscapeMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=12, arena=330):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn
        self.arena = arena
    def _bounce_if_needed(self):
        x, y = self.pos(); bounced = False
        if abs(x) > self.arena:
            self.setx(max(min(x, self.arena), -self.arena))
            self.setheading(180 - self.heading()); bounced = True
        if abs(y) > self.arena:
            self.sety(max(min(y, self.arena), -self.arena))
            self.setheading(-self.heading()); bounced = True
        if bounced: self.forward(self.step_move)
    def run_ai(self, opp_pos, opp_heading):
        target_heading = self.towards(opp_pos) + 180
        delta = (target_heading - self.heading() + 540) % 360 - 180
        if delta > 0: self.left(min(self.step_turn, delta))
        else:        self.right(min(self.step_turn, -delta))
        step = self.step_move + random.randint(-5, 5)
        self.forward(max(2, step))
        self._bounce_if_needed()

class ManualMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10, arena=330):
        super().__init__(canvas)
        self.step_move = step_move; self.step_turn = step_turn; self.arena = arena
        canvas.onkeypress(lambda: (self.forward(self.step_move), self._clamp_to_arena()), 'Up')
        canvas.onkeypress(lambda: (self.backward(self.step_move), self._clamp_to_arena()), 'Down')
        canvas.onkeypress(lambda: self.left(self.step_turn), 'Left')
        canvas.onkeypress(lambda: self.right(self.step_turn), 'Right')
        canvas.listen()
    def _clamp_to_arena(self):
        x, y = self.pos()
        if abs(x) > self.arena: self.setx(max(min(x, self.arena), -self.arena))
        if abs(y) > self.arena: self.sety(max(min(y, self.arena), -self.arena))
    def run_ai(self, opp_pos, opp_heading):
        pass

class RunawayGame:
    def __init__(self, canvas, runner, chaser, catch_radius=50):
        self.canvas = canvas; self.runner = runner; self.chaser = chaser
        self.catch_radius2 = catch_radius ** 2
        self.runner.shape('turtle'); self.runner.color('blue'); self.runner.penup()
        self.chaser.shape('turtle'); self.chaser.color('red');  self.chaser.penup()
        self.drawer = turtle.RawTurtle(canvas); self.drawer.hideturtle(); self.drawer.penup()
        self.ai_timer_msec = 100; self.is_over = False; self.paused = False
        self.start_ts = None; self.best_time = None
        self.score = 0.0
        self.max_time = 60.0  # ★ 최대 시간(초)
        self.canvas.onkeypress(self._toggle_pause, 'p')
        self.canvas.onkeypress(self._restart, 'r')
        self.canvas.listen()

    def _toggle_pause(self):
        if self.is_over or self.start_ts is None: return
        self.paused = not self.paused

    def _restart(self):
        self.start(init_dist=400, ai_timer_msec=self.ai_timer_msec)

    def is_catched(self):
        p = self.runner.pos(); q = self.chaser.pos()
        dx, dy = p[0] - q[0], p[1] - q[1]
        return dx*dx + dy*dy < self.catch_radius2

    def start(self, init_dist=400, ai_timer_msec=100):
        self.runner.setpos((-init_dist/2, 0)); self.runner.setheading(0)
        self.chaser.setpos((+init_dist/2, 0)); self.chaser.setheading(180)
        self.ai_timer_msec = ai_timer_msec
        self.is_over = False; self.paused = False
        self.start_ts = None; self.score = 0.0
        self.drawer.clear(); self.drawer.setpos(-95, 0)
        self.drawer.write("GAME START!", font=("Arial", 18, "bold"))
        self.canvas.ontimer(self._real_start, 2000)

    def _real_start(self):
        self.drawer.clear()
        self.start_ts = time.time()           # 실제 타이머 시작
        self._draw_hud(False)
        self.canvas.ontimer(self.step, self.ai_timer_msec)

    def _draw_hud(self, is_catched):
        self.drawer.clear(); self.drawer.setpos(-330, 300)
        elapsed = 0.0 if self.start_ts is None else (time.time() - self.start_ts)
        remain = max(0.0, self.max_time - elapsed)  # ★ 남은 시간
        msg = f"Time: {elapsed:5.1f}s  Left: {remain:5.1f}s  Caught: {is_catched}  [P:Pause, R:Restart]"
        self.drawer.write(msg, font=("Arial", 12, "normal"))

    def _finish_caught(self, final_time):
        # 점수: 60 - 포획시간 (음수 방지)
        score = max(0.0, self.max_time - final_time)
        if self.best_time is None or final_time < self.best_time:
            self.best_time = final_time
        self.drawer.setpos(-160, 0)
        self.drawer.write(f"GAME OVER\nFinal Time: {final_time:5.2f}s\nScore: {score:5.2f}",
                          align="left", font=("Arial", 16, "bold"))
        self.drawer.setpos(-160, -70)
        self.drawer.write(f"Best Time: {self.best_time:5.2f}s",
                          align="left", font=("Arial", 14, "normal"))

    def _finish_failed(self):
        # 시간 내 미포획
        self.drawer.setpos(-80, 0)
        self.drawer.write("FAILED!", align="left", font=("Arial", 20, "bold"))
        self.drawer.setpos(-160, -50)
        self.drawer.write(f"Final Time: {self.max_time:5.2f}s\nScore: 0.00",
                          align="left", font=("Arial", 16, "bold"))

    def step(self):
        if self.is_over: return
        if self.paused:
            self.canvas.ontimer(self.step, self.ai_timer_msec); return
        if self.start_ts is None:
            self.canvas.ontimer(self.step, self.ai_timer_msec); return

        # 동작
        self.runner.run_ai(self.chaser.pos(), self.chaser.heading())
        self.chaser.run_ai(self.runner.pos(), self.runner.heading())

        # 판정
        elapsed = time.time() - self.start_ts
        if elapsed >= self.max_time:
            # ★ 시간 초과 실패
            self.is_over = True
            self._draw_hud(False)   # 남은시간 0.0으로 갱신
            self._finish_failed()
            return

        is_catched = self.is_catched()
        self._draw_hud(is_catched)

        if is_catched:
            self.is_over = True
            final_time = elapsed
            self._finish_caught(final_time)
            return

        self.canvas.ontimer(self.step, self.ai_timer_msec)

if __name__ == '__main__':
    root = tk.Tk(); root.title("Turtle Runaway")
    canvas = tk.Canvas(root, width=700, height=700); canvas.pack()
    screen = turtle.TurtleScreen(canvas); screen.bgcolor("#eaf6ff")
    runner = EscapeMover(screen)
    chaser = ManualMover(screen, arena=330)
    game = RunawayGame(screen, runner, chaser)
    game.start(ai_timer_msec=60)
    screen.mainloop()