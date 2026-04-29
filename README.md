# Artificial Intelligence Lab Assignments: Intelligent Agents

This repository contains a collection of Python programs written for my Artificial Intelligence lab assignments. These scripts demonstrate foundational AI concepts, specifically focusing on the design and implementation of different types of intelligent agents (Simple Reflex Agents and Goal-Based/Rational Agents) in simulated environments like the classic Vacuum Cleaner World.

---

## 📁 Repository Structure & Program Descriptions

Here is a breakdown of the 6 programs included in this repository:

### 1. Basic Simple Reflex Agent (`1_basic_reflex_agent.py`)
A fundamental implementation of a Simple Reflex Agent in a two-room Vacuum Cleaner World (Locations A and B).

* **Concept:** The agent determines its action ("Suck", "Right", or "Left") based only on the current percept (location and dirt status), ignoring percept history.
* **Action:** It evaluates a single, hardcoded state and outputs the appropriate action.

---

### 2. Simulated Simple Reflex Agent (`2_simulated_reflex_agent.py`)
An extension of the basic reflex agent that includes a simulation loop.

* **Concept:** Demonstrates how a reflex agent operates over time in a dynamic loop.
* **Action:** The environment updates based on the agent's actions (e.g., if the action is "Suck", the room status becomes "Clean", and the agent moves to the other room). It runs for 5 iterations to show continuous state evaluation.

---

### 3. Goal-Based Agent - Functional (`3_goal_agent_basic.py`)
A script demonstrating a basic Goal-Based Agent moving through a 1D environment.

* **Concept:** Unlike a reflex agent, a goal-based agent acts to achieve a specific target state.
* **Action:** Uses a simple `while` loop function to increment its position until the predefined goal is reached.

---

### 4. Rational/Goal-Based Agent - Object-Oriented (`4_goal_agent_oop.py`)
An Object-Oriented approach to the goal-based agent using Python classes.

* **Concept:** Encapsulates the agent's properties (position, goal) and behaviors (moving) into a `RationalAgent` class.
* **Action:** Creates an instance of the agent and calls its method to autonomously navigate toward its target integer position.

---

### 5. 4x4 Grid Vacuum Cleaner Agent (`5_vacuum_4x4_grid.py`)
A more complex implementation of a vacuum cleaning agent operating in a 4x4 grid (16 distinct locations).

* **Concept:** Introduces randomized environments and performance measurement — key aspects of rational agent design.
* **Action:**
  1. Initializes a 4x4 grid where rooms are randomly marked as clean (`0`) or dirty (`1`).
  2. Scans the grid, detects dirty rooms, and cleans them.
  3. Calculates and prints a final **Performance Score** based on how many rooms required cleaning.

---

### 6. Grid World Environment — Wumpus Style (`6_grid_world.py`)
A fully interactive simulation of a Wumpus-style grid world environment with an intelligent agent navigating under uncertainty.

* **Concept:** Models a classic AI problem environment featuring incomplete information, hazards, and goal-driven decision-making. The agent must reason about its surroundings using local percepts — it cannot see the full world directly.
* **Environment Layout (4×4 grid by default):**

  | Symbol | Entity | Description |
  |--------|--------|-------------|
  | `A` | Agent | The navigating entity controlled by the player |
  | `W` | Wumpus | A deadly monster; stepping on it kills the agent |
  | `P` | Pit | A deadly hole; falling in kills the agent |
  | `G` | Gold | The objective — the agent must grab it and escape |
  | `S` | Start | The agent's starting cell (bottom-left corner) |
  | `b` | Breeze | Perceived in cells adjacent to a Pit |
  | `s` | Stench | Perceived in cells adjacent to the Wumpus |

* **Actions supported:**

  | Command | Effect |
  |---------|--------|
  | `move up/down/left/right` | Move the agent one cell in the given direction |
  | `grab` | Pick up gold if present on the current cell |
  | `shoot <direction>` | Fire the single arrow in a direction; kills the Wumpus if in line of sight |
  | `climb` | Exit the cave from the start cell (wins if carrying gold) |

* **Scoring System:**

  | Event | Points |
  |-------|--------|
  | Each action taken | −1 |
  | Firing the arrow | −10 |
  | Grabbing the gold | +1,000 |
  | Escaping with gold | +500 bonus |
  | Death (Wumpus or Pit) | −1,000 |

* **Key Features:**
  * Randomly generated world on each run (configurable seed for reproducibility)
  * Percept-based partial observability — unvisited cells are hidden (`?`) by default
  * `reveal` command to toggle full world visibility (useful for debugging)
  * `demo` mode with a scripted agent for automated walkthrough
  * Fully modular `GridWorld` class — importable as a module for AI agent experiments

* **How to run:**

  ```bash
  # Interactive mode (play manually via CLI)
  python 6_grid_world.py

  # Scripted demo mode (watch a pre-planned agent)
  python 6_grid_world.py demo
  ```

* **Sample Output:**

  ```
  +-----+-----+-----+-----+
  |  ?  |  ?  |  ?  |  ?  |
  +-----+-----+-----+-----+
  |  ?  |  ?  |  ?  |  ?  |
  +-----+-----+-----+-----+
  |  ?  |  ?  |  ?  |  ?  |
  +-----+-----+-----+-----+
  |  A  |  ?  |  ?  |  ?  |
  +-----+-----+-----+-----+
  Position: (3, 0) | Score: +0 | Moves: 0 | Gold: ✗ | Arrow: ✓ | Wumpus: alive
  ```

---

## 🚀 How to Run

To run any of these scripts, ensure you have **[Python 3.x](https://www.python.org/downloads/)** installed on your machine.

Open your terminal or command prompt, navigate to the directory containing the files, and run the following command:

```bash
python filename.py
```

For the Grid World environment specifically, you can also run the automated demo:

```bash
python 6_grid_world.py demo
```
