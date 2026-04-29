"""
Grid World Environment - Wumpus World Style
============================================
A simple grid world with:
  - Agent (A): navigates the grid
  - Wumpus (W): deadly monster, agent loses if it steps on it
  - Pit (P): deadly hole, agent loses if it falls in
  - Gold (G): agent wins by collecting it
  - Walls: border the grid
  - Breeze (b): felt in cells adjacent to a Pit
  - Stench (s): smelled in cells adjacent to Wumpus

Actions: move_up, move_down, move_left, move_right, grab, shoot
"""

import random
from enum import Enum
from typing import Optional


# ── Cell Contents ──────────────────────────────────────────────────────────────

class CellContent(Enum):
    EMPTY   = "."
    WUMPUS  = "W"
    PIT     = "P"
    GOLD    = "G"
    AGENT   = "A"
    BREEZE  = "b"
    STENCH  = "s"
    START   = "S"


# ── Directions ─────────────────────────────────────────────────────────────────

DIRECTIONS = {
    "up":    (-1, 0),
    "down":  ( 1, 0),
    "left":  ( 0,-1),
    "right": ( 0, 1),
}


# ── Grid World ─────────────────────────────────────────────────────────────────

class GridWorld:
    """
    A 4×4 (default) Wumpus-style grid world.

    Coordinate convention: (row, col), (0,0) = top-left.
    The agent always starts at (rows-1, 0) — bottom-left corner.
    """

    def __init__(self, rows: int = 4, cols: int = 4,
                 num_pits: int = 2, seed: Optional[int] = None):
        self.rows = rows
        self.cols = cols
        self.num_pits = num_pits

        if seed is not None:
            random.seed(seed)

        # Agent state
        self.start = (rows - 1, 0)
        self.agent_pos = self.start
        self.has_gold   = False
        self.has_arrow  = True          # one arrow to shoot the Wumpus
        self.wumpus_alive = True
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.win = False
        self.message = ""

        # Build the world
        self._place_entities()
        self._compute_percepts()

    # ── Setup ────────────────────────────────────────────────────────────────

    def _safe_cells(self, exclude: set[tuple]) -> list[tuple]:
        """Return all cells except the start cell and those in exclude."""
        all_cells = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in {self.start} | exclude
        ]
        return all_cells

    def _place_entities(self):
        self.grid = [[set() for _ in range(self.cols)] for _ in range(self.rows)]
        self.wumpus_pos = None
        self.pit_positions: set[tuple] = set()
        self.gold_pos = None

        available = self._safe_cells(set())

        # Wumpus
        self.wumpus_pos = random.choice(available)
        available.remove(self.wumpus_pos)
        self.grid[self.wumpus_pos[0]][self.wumpus_pos[1]].add(CellContent.WUMPUS)

        # Pits
        for _ in range(self.num_pits):
            if not available:
                break
            pos = random.choice(available)
            available.remove(pos)
            self.pit_positions.add(pos)
            self.grid[pos[0]][pos[1]].add(CellContent.PIT)

        # Gold (not on a pit/wumpus cell)
        self.gold_pos = random.choice(available)
        self.grid[self.gold_pos[0]][self.gold_pos[1]].add(CellContent.GOLD)

    def _neighbors(self, r: int, c: int) -> list[tuple]:
        result = []
        for dr, dc in DIRECTIONS.values():
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                result.append((nr, nc))
        return result

    def _compute_percepts(self):
        """Add breeze/stench markers adjacent to pits/wumpus."""
        # Clear old percepts
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c].discard(CellContent.BREEZE)
                self.grid[r][c].discard(CellContent.STENCH)

        for pr, pc in self.pit_positions:
            for nr, nc in self._neighbors(pr, pc):
                self.grid[nr][nc].add(CellContent.BREEZE)

        if self.wumpus_alive and self.wumpus_pos:
            wr, wc = self.wumpus_pos
            for nr, nc in self._neighbors(wr, wc):
                self.grid[nr][nc].add(CellContent.STENCH)

    # ── Percepts visible to the agent ───────────────────────────────────────

    def get_percepts(self) -> dict:
        r, c = self.agent_pos
        cell = self.grid[r][c]
        return {
            "breeze":  CellContent.BREEZE  in cell,
            "stench":  CellContent.STENCH  in cell,
            "glitter": CellContent.GOLD    in cell and not self.has_gold,
            "bump":    False,               # set dynamically on failed move
            "scream":  False,               # set dynamically after shoot
        }

    # ── Actions ──────────────────────────────────────────────────────────────

    def _apply_penalty(self, cost: int = -1):
        self.score += cost

    def move(self, direction: str) -> dict:
        """Move the agent in the given direction. Returns result dict."""
        if self.game_over:
            return {"ok": False, "reason": "Game is over."}
        if direction not in DIRECTIONS:
            return {"ok": False, "reason": f"Unknown direction '{direction}'."}

        dr, dc = DIRECTIONS[direction]
        r, c = self.agent_pos
        nr, nc = r + dr, c + dc
        self._apply_penalty()          # -1 per action
        self.moves += 1
        percepts = self.get_percepts()

        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            percepts["bump"] = True
            self.message = f"Bump! Cannot move {direction}."
            return {"ok": True, "bump": True, "percepts": percepts}

        self.agent_pos = (nr, nc)

        # Check hazards
        cell = self.grid[nr][nc]
        if CellContent.WUMPUS in cell and self.wumpus_alive:
            self.score -= 1000
            self.game_over = True
            self.win = False
            self.message = "EATEN BY THE WUMPUS! You lose."
            return {"ok": True, "dead": True, "reason": "wumpus", "percepts": percepts}

        if CellContent.PIT in cell:
            self.score -= 1000
            self.game_over = True
            self.win = False
            self.message = "FELL INTO A PIT! You lose."
            return {"ok": True, "dead": True, "reason": "pit", "percepts": percepts}

        percepts = self.get_percepts()
        self.message = f"Moved {direction} to {self.agent_pos}."
        return {"ok": True, "percepts": percepts}

    def grab(self) -> dict:
        """Pick up gold if on the same cell."""
        if self.game_over:
            return {"ok": False, "reason": "Game is over."}
        self._apply_penalty()
        self.moves += 1
        r, c = self.agent_pos
        if CellContent.GOLD in self.grid[r][c] and not self.has_gold:
            self.grid[r][c].discard(CellContent.GOLD)
            self.has_gold = True
            self.score += 1000
            self.message = "GOLD GRABBED! Head back to the start!"
            return {"ok": True, "grabbed": True}
        self.message = "No gold here."
        return {"ok": True, "grabbed": False}

    def shoot(self, direction: str) -> dict:
        """Shoot the arrow in a direction. Kills Wumpus if in line of sight."""
        if self.game_over:
            return {"ok": False, "reason": "Game is over."}
        if not self.has_arrow:
            self.message = "No arrow left!"
            return {"ok": True, "fired": False}

        self._apply_penalty(10)        # shooting costs 10
        self.moves += 1
        self.has_arrow = False

        if direction not in DIRECTIONS:
            return {"ok": False, "reason": f"Unknown direction '{direction}'."}

        dr, dc = DIRECTIONS[direction]
        r, c = self.agent_pos
        killed = False
        while True:
            r += dr; c += dc
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                break
            if (r, c) == self.wumpus_pos and self.wumpus_alive:
                self.wumpus_alive = False
                self.grid[r][c].discard(CellContent.WUMPUS)
                self._compute_percepts()
                killed = True
                self.message = "WUMPUS KILLED! You hear a scream!"
                break

        if not killed:
            self.message = "Arrow missed."

        return {"ok": True, "fired": True, "killed": killed}

    def climb_out(self) -> dict:
        """Climb out of the cave (only valid at the start cell)."""
        if self.game_over:
            return {"ok": False, "reason": "Game is over."}
        self._apply_penalty()
        self.moves += 1
        if self.agent_pos == self.start:
            self.game_over = True
            if self.has_gold:
                self.score += 500    # bonus for escaping with gold
                self.win = True
                self.message = "Escaped with the GOLD! YOU WIN! 🏆"
            else:
                self.win = False
                self.message = "Escaped alive, but without the gold."
            return {"ok": True, "escaped": True, "win": self.win}
        self.message = "You can only climb out from the start cell."
        return {"ok": True, "escaped": False}

    # ── Display ──────────────────────────────────────────────────────────────

    def render(self, reveal: bool = False) -> str:
        """
        Render the grid.
        If reveal=False, cells not yet visited are shown as '?'.
        If reveal=True, the full world is shown (debug / post-game).
        """
        lines = []
        sep = "+" + ("-----+" * self.cols)
        lines.append(sep)

        for r in range(self.rows):
            row_parts = ["|"]
            for c in range(self.cols):
                symbols = []
                cell = self.grid[r][c]

                if (r, c) == self.agent_pos:
                    symbols.append("A")
                if CellContent.WUMPUS in cell and (reveal or not self.wumpus_alive):
                    symbols.append("W" if self.wumpus_alive else "X")
                elif CellContent.WUMPUS in cell and reveal:
                    symbols.append("W")
                if CellContent.PIT in cell and reveal:
                    symbols.append("P")
                if CellContent.GOLD in cell and (reveal or (r, c) == self.agent_pos):
                    symbols.append("G")
                if CellContent.BREEZE in cell and (reveal or (r, c) == self.agent_pos):
                    symbols.append("b")
                if CellContent.STENCH in cell and (reveal or (r, c) == self.agent_pos):
                    symbols.append("s")
                if (r, c) == self.start and not symbols:
                    symbols.append("S")

                if not symbols:
                    display = " . " if reveal else " ? "
                else:
                    display = "".join(symbols).center(3)

                row_parts.append(f" {display} |")
            lines.append("".join(row_parts))
            lines.append(sep)

        return "\n".join(lines)

    def status(self) -> str:
        return (
            f"  Position : {self.agent_pos}  |  "
            f"Score: {self.score:+d}  |  "
            f"Moves: {self.moves}  |  "
            f"Gold: {'✓' if self.has_gold else '✗'}  |  "
            f"Arrow: {'✓' if self.has_arrow else '✗'}  |  "
            f"Wumpus: {'alive' if self.wumpus_alive else 'dead'}"
        )


# ── Interactive CLI ────────────────────────────────────────────────────────────

HELP_TEXT = """
Commands
────────
  move up / move down / move left / move right   — move the agent
  grab                                           — pick up gold
  shoot up / shoot down / shoot left / shoot right — fire arrow
  climb                                          — exit cave (start cell only)
  reveal                                         — toggle full map reveal
  status                                         — show score & state
  reset                                          — start a new game
  quit / exit                                    — quit
  help                                           — show this message
"""


def play():
    print("=" * 60)
    print("       GRID WORLD — Wumpus Style  (4×4)")
    print("=" * 60)
    print(HELP_TEXT)

    world = GridWorld(rows=4, cols=4, num_pits=2)
    reveal = False

    while True:
        print("\n" + world.render(reveal=reveal))
        print(world.status())
        if world.message:
            print(f"  ➤  {world.message}")
            world.message = ""

        if world.game_over:
            print("\n  Game Over. Type 'reset' to play again or 'quit' to exit.")

        try:
            raw = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not raw:
            continue

        tokens = raw.split()
        cmd = tokens[0]

        if cmd in ("quit", "exit"):
            print("Thanks for playing!")
            break

        elif cmd == "reset":
            world = GridWorld(rows=4, cols=4, num_pits=2)
            reveal = False
            print("New game started.")

        elif cmd == "help":
            print(HELP_TEXT)

        elif cmd == "reveal":
            reveal = not reveal
            print(f"Reveal mode: {'ON' if reveal else 'OFF'}")

        elif cmd == "status":
            pass   # already printed above

        elif cmd == "move" and len(tokens) >= 2:
            result = world.move(tokens[1])
            if not result["ok"]:
                print(f"  Error: {result.get('reason')}")

        elif cmd == "grab":
            world.grab()

        elif cmd == "shoot" and len(tokens) >= 2:
            world.shoot(tokens[1])

        elif cmd == "climb":
            world.climb_out()

        else:
            print("  Unknown command. Type 'help' for a list of commands.")


# ── Simple Demo (non-interactive) ──────────────────────────────────────────────

def demo():
    """Run a scripted demo to show the environment programmatically."""
    print("=" * 60)
    print("  GRID WORLD DEMO  (scripted agent)")
    print("=" * 60)

    world = GridWorld(rows=4, cols=4, num_pits=2, seed=42)
    print("\n[Full world revealed for demo]\n")
    print(world.render(reveal=True))
    print(world.status())

    actions = [
        ("move", "up"),
        ("move", "up"),
        ("move", "right"),
        ("shoot", "up"),
        ("move", "right"),
        ("grab", None),
        ("move", "left"),
        ("move", "left"),
        ("move", "down"),
        ("move", "down"),
        ("climb", None),
    ]

    print("\n─── Executing scripted actions ───")
    for action, arg in actions:
        if world.game_over:
            break

        if action == "move":
            result = world.move(arg)
        elif action == "grab":
            result = world.grab()
        elif action == "shoot":
            result = world.shoot(arg)
        elif action == "climb":
            result = world.climb_out()

        label = f"{action} {arg}" if arg else action
        print(f"\n  Action : {label}")
        print(world.render(reveal=True))
        print(world.status())
        if world.message:
            print(f"  ➤  {world.message}")
            world.message = ""

    print("\n" + "=" * 60)
    outcome = "WIN 🏆" if world.win else "LOSS 💀"
    print(f"  Final outcome : {outcome}  |  Final score : {world.score:+d}")
    print("=" * 60)


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        play()
