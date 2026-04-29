"""
Grid World Environment — Wumpus World Style
============================================
A 4x4 grid world with:
  - Agent  (@) that can move, shoot, grab gold
  - Wumpus (W) — deadly monster
  - Pits   (P) — deadly traps
  - Gold   (G) — the goal
  - Breeze (B) — felt when adjacent to a pit
  - Stench (S) — smelt when adjacent to the Wumpus
  - Glitter    — sensed when gold is in the same cell

Actions:
  move_forward, turn_left, turn_right, shoot, grab, climb
"""

import random
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
# Direction helpers
# ─────────────────────────────────────────────
DIRECTIONS = ["EAST", "NORTH", "WEST", "SOUTH"]  # clockwise order
DELTAS = {"EAST": (1, 0), "NORTH": (0, 1), "WEST": (-1, 0), "SOUTH": (0, -1)}

COLORS = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "red":    "\033[91m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "cyan":   "\033[96m",
    "blue":   "\033[94m",
    "magenta":"\033[95m",
    "grey":   "\033[90m",
    "white":  "\033[97m",
}

def c(color: str, text: str) -> str:
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


# ─────────────────────────────────────────────
# World cell
# ─────────────────────────────────────────────
@dataclass
class Cell:
    has_wumpus: bool = False
    has_pit: bool = False
    has_gold: bool = False
    has_breeze: bool = False
    has_stench: bool = False
    visited: bool = False

    @property
    def is_deadly(self) -> bool:
        return self.has_wumpus or self.has_pit


# ─────────────────────────────────────────────
# Agent state
# ─────────────────────────────────────────────
@dataclass
class Agent:
    x: int = 0
    y: int = 0
    direction: str = "EAST"
    has_arrow: bool = True
    has_gold: bool = False
    score: int = 0
    is_alive: bool = True

    def turn_left(self):
        idx = DIRECTIONS.index(self.direction)
        self.direction = DIRECTIONS[(idx + 1) % 4]

    def turn_right(self):
        idx = DIRECTIONS.index(self.direction)
        self.direction = DIRECTIONS[(idx - 1) % 4]

    def facing_cell(self, size: int) -> Optional[tuple]:
        dx, dy = DELTAS[self.direction]
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < size and 0 <= ny < size:
            return nx, ny
        return None


# ─────────────────────────────────────────────
# Grid World
# ─────────────────────────────────────────────
class GridWorld:
    def __init__(self, size: int = 4, seed: Optional[int] = None):
        self.size = size
        self.rng = random.Random(seed)
        self.wumpus_alive = True
        self.game_over = False
        self.won = False
        self.message = ""
        self.percepts_log: list[str] = []
        self.action_log: list[str] = []

        self.grid: list[list[Cell]] = [
            [Cell() for _ in range(size)] for _ in range(size)
        ]
        self.agent = Agent()
        self._place_elements()
        self._mark_derivations()
        self.grid[0][0].visited = True

    # ── placement ──────────────────────────────
    def _safe_cells(self) -> list[tuple[int, int]]:
        """All cells except (0,0)."""
        return [(x, y) for x in range(self.size)
                for y in range(self.size) if (x, y) != (0, 0)]

    def _place_elements(self):
        safe = self._safe_cells()
        self.rng.shuffle(safe)

        # Wumpus
        wx, wy = safe.pop()
        self.grid[wx][wy].has_wumpus = True

        # Pits (~20 % of remaining cells, at least 1)
        n_pits = max(1, int(len(safe) * 0.20))
        for _ in range(n_pits):
            if safe:
                px, py = safe.pop()
                self.grid[px][py].has_pit = True

        # Gold
        if safe:
            gx, gy = safe.pop()
            self.grid[gx][gy].has_gold = True

    def _mark_derivations(self):
        for x in range(self.size):
            for y in range(self.size):
                for nx, ny in self._neighbors(x, y):
                    if self.grid[nx][ny].has_pit:
                        self.grid[x][y].has_breeze = True
                    if self.grid[nx][ny].has_wumpus:
                        self.grid[x][y].has_stench = True

    def _neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        result = []
        for dx, dy in DELTAS.values():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                result.append((nx, ny))
        return result

    # ── percepts ───────────────────────────────
    def current_percepts(self) -> dict:
        x, y = self.agent.x, self.agent.y
        cell = self.grid[x][y]
        return {
            "stench":  cell.has_stench,
            "breeze":  cell.has_breeze,
            "glitter": cell.has_gold,
            "bump":    False,   # set by move_forward if wall hit
            "scream":  False,   # set by shoot if wumpus killed
        }

    # ── actions ────────────────────────────────
    def move_forward(self) -> dict:
        self.agent.score -= 1
        percepts = self.current_percepts()
        facing = self.agent.facing_cell(self.size)
        result = {"action": "MOVE_FORWARD"}

        if facing is None:
            percepts["bump"] = True
            result["msg"] = "Bumped into a wall!"
        else:
            self.agent.x, self.agent.y = facing
            cell = self.grid[self.agent.x][self.agent.y]
            cell.visited = True
            percepts = self.current_percepts()

            if cell.has_wumpus and self.wumpus_alive:
                self.agent.is_alive = False
                self.game_over = True
                self.agent.score -= 1000
                result["msg"] = "You were eaten by the Wumpus! 💀"
            elif cell.has_pit:
                self.agent.is_alive = False
                self.game_over = True
                self.agent.score -= 1000
                result["msg"] = "You fell into a pit! 💀"
            else:
                result["msg"] = f"Moved to ({self.agent.x}, {self.agent.y})"

        result["percepts"] = percepts
        self._log_action(result)
        return result

    def turn_left(self) -> dict:
        self.agent.score -= 1
        self.agent.turn_left()
        result = {"action": "TURN_LEFT",
                  "msg": f"Now facing {self.agent.direction}",
                  "percepts": self.current_percepts()}
        self._log_action(result)
        return result

    def turn_right(self) -> dict:
        self.agent.score -= 1
        self.agent.turn_right()
        result = {"action": "TURN_RIGHT",
                  "msg": f"Now facing {self.agent.direction}",
                  "percepts": self.current_percepts()}
        self._log_action(result)
        return result

    def shoot(self) -> dict:
        self.agent.score -= 10
        result = {"action": "SHOOT"}

        if not self.agent.has_arrow:
            result["msg"] = "No arrow left!"
            result["percepts"] = self.current_percepts()
            self._log_action(result)
            return result

        self.agent.has_arrow = False
        percepts = self.current_percepts()
        # Shoot along the facing direction
        ax, ay = self.agent.x, self.agent.y
        dx, dy = DELTAS[self.agent.direction]
        killed = False
        while True:
            ax += dx; ay += dy
            if not (0 <= ax < self.size and 0 <= ay < self.size):
                break
            if self.grid[ax][ay].has_wumpus and self.wumpus_alive:
                self.wumpus_alive = False
                self.grid[ax][ay].has_wumpus = False
                # Remove stenches
                for nx, ny in self._neighbors(ax, ay):
                    self.grid[nx][ny].has_stench = False
                killed = True
                break

        percepts["scream"] = killed
        result["percepts"] = percepts
        result["msg"] = "Wumpus KILLED! 🏹" if killed else "Arrow missed."
        self._log_action(result)
        return result

    def grab(self) -> dict:
        self.agent.score -= 1
        x, y = self.agent.x, self.agent.y
        result = {"action": "GRAB"}
        if self.grid[x][y].has_gold:
            self.grid[x][y].has_gold = False
            self.agent.has_gold = True
            self.agent.score += 100
            result["msg"] = "Gold GRABBED! 💰 Now climb out at (0,0)."
        else:
            result["msg"] = "No gold here."
        result["percepts"] = self.current_percepts()
        self._log_action(result)
        return result

    def climb(self) -> dict:
        self.agent.score -= 1
        result = {"action": "CLIMB"}
        if self.agent.x == 0 and self.agent.y == 0:
            self.game_over = True
            if self.agent.has_gold:
                self.won = True
                self.agent.score += 1000
                result["msg"] = "You escaped with the gold! 🏆 YOU WIN!"
            else:
                result["msg"] = "You climbed out — but without gold. Game over."
        else:
            result["msg"] = "Can only climb at (0,0)."
        result["percepts"] = self.current_percepts()
        self._log_action(result)
        return result

    # ── helpers ────────────────────────────────
    def _log_action(self, result: dict):
        self.action_log.append(f"[{result['action']}] {result.get('msg','')}")

    # ─────────────────────────────────────────────
    # Display
    # ─────────────────────────────────────────────
    def display(self):
        size = self.size
        ax, ay = self.agent.x, self.agent.y
        dir_arrow = {"EAST": "→", "NORTH": "↑", "WEST": "←", "SOUTH": "↓"}[self.agent.direction]

        print(c("bold", "\n╔═══════════════════════════════════════╗"))
        print(c("bold", "║        G R I D   W O R L D            ║"))
        print(c("bold", "╚═══════════════════════════════════════╝"))
        print()

        # Grid (y from top = size-1 down to 0)
        cell_w = 7
        border = "+" + ("-" * cell_w + "+") * size

        for row_y in range(size - 1, -1, -1):
            print(c("grey", border))
            top_line = "|"
            mid_line = "|"
            bot_line = "|"
            for col_x in range(size):
                cell = self.grid[col_x][row_y]
                is_agent = (col_x == ax and row_y == ay)

                # Top sub-row: sensors
                sens = ""
                if cell.visited or is_agent:
                    if cell.has_stench:  sens += c("magenta", "S")
                    if cell.has_breeze:  sens += c("cyan",    "B")
                    if cell.has_gold and not self.agent.has_gold:
                        sens += c("yellow", "G")
                else:
                    sens = c("grey", "?????")
                top_line += f" {sens:<13}{c('grey','|')}"  # noqa

                # Mid sub-row: content
                if is_agent:
                    content = c("green", f" {dir_arrow}@  ")
                elif not cell.visited:
                    content = c("grey",  "  ???  ")
                else:
                    parts = []
                    if cell.has_wumpus and self.wumpus_alive:
                        parts.append(c("red",    "W"))
                    if cell.has_pit:
                        parts.append(c("blue",   "P"))
                    content = " " + "".join(parts).center(5) + " "
                mid_line += f"{content}{c('grey','|')}"

                # Bot sub-row: coordinates
                coord = c("grey", f"({col_x},{row_y})")
                bot_line += f" {coord}  {c('grey','|')}"

            print(top_line)
            print(mid_line)
            print(bot_line)

        print(c("grey", border))
        print()

        # Status panel
        print(c("bold", "─" * 42))
        arrow_str = c("green","✓ Have arrow") if self.agent.has_arrow else c("red","✗ No arrow")
        gold_str  = c("yellow","✓ Carrying gold") if self.agent.has_gold else "✗ No gold"
        wump_str  = c("red","ALIVE") if self.wumpus_alive else c("green","DEAD")

        print(f"  Score : {c('yellow', str(self.agent.score)):<25} "
              f"Facing: {c('cyan', self.agent.direction)}")
        print(f"  Pos   : ({ax}, {ay})                       "
              f"Wumpus: {wump_str}")
        print(f"  Arrow : {arrow_str}")
        print(f"  Gold  : {gold_str}")
        print(c("bold", "─" * 42))

        # Percepts
        p = self.current_percepts()
        plist = []
        if p["stench"]:  plist.append(c("magenta", "STENCH"))
        if p["breeze"]:  plist.append(c("cyan",    "BREEZE"))
        if p["glitter"]: plist.append(c("yellow",  "GLITTER"))
        if not plist:    plist.append(c("grey",     "none"))
        print(f"  Percepts: {', '.join(plist)}")
        print()

        # Legend
        print(c("grey", "  Legend: @=Agent  W=Wumpus  P=Pit  G=Gold"))
        print(c("grey", "          S=Stench B=Breeze  ?=Unexplored"))
        print()


# ─────────────────────────────────────────────
# Interactive REPL
# ─────────────────────────────────────────────
HELP_TEXT = """
  Commands:
    w / forward    — Move forward
    a / left       — Turn left
    d / right      — Turn right
    s / shoot      — Shoot arrow
    g / grab       — Grab gold
    c / climb      — Climb out (at 0,0)
    r / reveal     — Reveal full map (cheat)
    h / help       — Show this help
    q / quit       — Quit
"""

def play():
    print(c("bold", c("yellow", "\n  ══════════════════════════════════")))
    print(c("bold", c("yellow", "   WUMPUS-STYLE GRID WORLD  v1.0")))
    print(c("bold", c("yellow", "  ══════════════════════════════════")))
    print("\n  Enter seed (or press Enter for random): ", end="")
    seed_in = input().strip()
    seed = int(seed_in) if seed_in.isdigit() else None

    world = GridWorld(size=4, seed=seed)
    reveal = False

    print(HELP_TEXT)

    while not world.game_over:
        if reveal:
            # Temporarily mark all as visited for display
            for row in world.grid:
                for cell in row:
                    cell.visited = True

        world.display()

        if reveal:
            # restore
            for x in range(world.size):
                for y in range(world.size):
                    world.grid[x][y].visited = (
                        x == world.agent.x and y == world.agent.y
                        or world.action_log  # hack: visited cells stay marked
                    )

        print("  > ", end="", flush=True)
        cmd = input().strip().lower()

        result = None
        if cmd in ("w", "forward"):
            result = world.move_forward()
        elif cmd in ("a", "left"):
            result = world.turn_left()
        elif cmd in ("d", "right"):
            result = world.turn_right()
        elif cmd in ("s", "shoot"):
            result = world.shoot()
        elif cmd in ("g", "grab"):
            result = world.grab()
        elif cmd in ("c", "climb"):
            result = world.climb()
        elif cmd in ("r", "reveal"):
            reveal = not reveal
            print(c("yellow", f"  Map reveal: {'ON' if reveal else 'OFF'}"))
            continue
        elif cmd in ("h", "help"):
            print(HELP_TEXT)
            continue
        elif cmd in ("q", "quit"):
            print(c("grey", "  Quit. Goodbye!\n"))
            return
        else:
            print(c("red", "  Unknown command. Type 'h' for help."))
            continue

        if result:
            msg = result.get("msg", "")
            print(c("cyan", f"\n  ➤ {msg}\n"))

    world.display()
    if world.won:
        print(c("bold", c("yellow", "\n  🏆  VICTORY!  You escaped with the gold!")))
    else:
        print(c("bold", c("red", "\n  💀  GAME OVER!")))
    print(c("bold", f"  Final score: {c('yellow', str(world.agent.score))}\n"))


# ─────────────────────────────────────────────
# Demo / non-interactive walkthrough
# ─────────────────────────────────────────────
def demo():
    """Run a scripted walkthrough to demonstrate the API."""
    print(c("bold", c("cyan", "\n══ DEMO MODE ══\n")))
    world = GridWorld(size=4, seed=42)
    world.display()

    script = [
        ("move_forward", world.move_forward),
        ("turn_left",    world.turn_left),
        ("move_forward", world.move_forward),
        ("turn_right",   world.turn_right),
        ("shoot",        world.shoot),
        ("grab",         world.grab),
        ("turn_left",    world.turn_left),
        ("turn_left",    world.turn_left),
        ("move_forward", world.move_forward),
        ("turn_right",   world.turn_right),
        ("move_forward", world.move_forward),
        ("climb",        world.climb),
    ]

    for name, fn in script:
        if world.game_over:
            break
        print(c("bold", f"\n  ▶ ACTION: {name.upper()}"))
        result = fn()
        print(c("cyan", f"  ➤ {result.get('msg','')}"))
        p = result.get("percepts", {})
        active = [k for k, v in p.items() if v]
        print(c("grey", f"  Percepts: {active if active else ['none']}"))
        world.display()

    if world.game_over:
        verdict = "WON 🏆" if world.won else "LOST 💀"
        print(c("bold", f"  Game {verdict} — Final score: {world.agent.score}"))


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        demo()
    else:
        play()
