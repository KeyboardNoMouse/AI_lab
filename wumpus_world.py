class SimpleWumpusWorld:
    def __init__(self, size=4):
        """Initializes a square grid of the given size."""
        self.size = size
        # Create a 2D grid where each cell is a set to hold multiple items (e.g., Agent and Gold)
        self.grid = [[set() for _ in range(size)] for _ in range(size)]
        self.agent_pos = [0, 0]  # Agent starts at bottom-left (0, 0)
        self.game_over = False
        
        # Place the agent on the grid
        self.grid[0][0].add('A')

    def place_item(self, item, pos):
        """Places an item (Wumpus 'W', Pit 'P', Gold 'G') at a specific (x, y) coordinate."""
        x, y = pos
        if 0 <= x < self.size and 0 <= y < self.size:
            self.grid[x][y].add(item)
        else:
            print(f"Cannot place {item}: Position {pos} is out of bounds.")

    def display(self):
        """Prints the current state of the grid world visually."""
        print("\n--- Grid World ---")
        # Print from top to bottom (y = size-1 down to 0) so (0,0) is visually at the bottom left
        for y in range(self.size - 1, -1, -1):
            row_str = ""
            for x in range(self.size):
                cell = self.grid[x][y]
                if not cell:
                    row_str += "[   ] "
                else:
                    # Join items with a comma (e.g., A,P)
                    row_str += f"[{','.join(cell):^3}] "
            print(row_str)
        print("------------------")

    def move_agent(self, direction):
        """Moves the agent UP, DOWN, LEFT, or RIGHT."""
        if self.game_over:
            print("Game is over. Please restart.")
            return

        x, y = self.agent_pos
        self.grid[x][y].remove('A')  # Remove agent from current cell

        # Calculate new position
        if direction == 'UP' and y < self.size - 1:
            y += 1
        elif direction == 'DOWN' and y > 0:
            y -= 1
        elif direction == 'RIGHT' and x < self.size - 1:
            x += 1
        elif direction == 'LEFT' and x > 0:
            x -= 1
        else:
            print("Bump! You hit a wall.")

        # Update position
        self.agent_pos = [x, y]
        self.grid[x][y].add('A')
        
        # Check what happened after moving
        self.evaluate_state()

    def get_percepts(self):
        """Generates percepts based on the agent's current location."""
        x, y = self.agent_pos
        percepts = set()

        # Check current cell for Glitter
        if 'G' in self.grid[x][y]:
            percepts.add('Glitter')

        # Check adjacent cells for Wumpus (Stench) or Pits (Breeze)
        adjacents = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        for ax, ay in adjacents:
            if 0 <= ax < self.size and 0 <= ay < self.size:
                adj_cell = self.grid[ax][ay]
                if 'W' in adj_cell:
                    percepts.add('Stench')
                if 'P' in adj_cell:
                    percepts.add('Breeze')

        return list(percepts)

    def evaluate_state(self):
        """Checks if the agent has died, won, or is safe."""
        x, y = self.agent_pos
        cell = self.grid[x][y]

        if 'W' in cell:
            print("💀 Oh no! You were eaten by the Wumpus! Game Over.")
            self.game_over = True
        elif 'P' in cell:
            print("🕳️ Ahhhhh! You fell into a Pit! Game Over.")
            self.game_over = True
        elif 'G' in cell:
            print("🏆 You found the Gold! You win!")
            self.game_over = True
        else:
            # If safe, print current percepts
            percepts = self.get_percepts()
            if percepts:
                print(f"Current Percepts: {', '.join(percepts)}")
            else:
                print("Current Percepts: None (Looks safe here)")


# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    # 1. Initialize a 4x4 world
    world = SimpleWumpusWorld(size=4)

    # 2. Setup the environment
    world.place_item('P', (2, 0))  # Pit at x=2, y=0
    world.place_item('P', (2, 2))  # Pit at x=2, y=2
    world.place_item('W', (0, 2))  # Wumpus at x=0, y=2
    world.place_item('G', (1, 2))  # Gold at x=1, y=2

    print("Initial State:")
    world.display()

    # 3. Perform a sequence of operations
    # In this scenario, moving RIGHT, UP, UP, RIGHT will hit the gold safely
    commands = ['RIGHT', 'UP', 'UP', 'RIGHT'] 
    
    for cmd in commands:
        print(f"\n>>> Action: Move {cmd}")
        world.move_agent(cmd)
        world.display()
        if world.game_over:
            break
