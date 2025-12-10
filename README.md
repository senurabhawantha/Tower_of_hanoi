# Tower of Hanoi - Comprehensive Game System

A full-stack implementation of the classic Tower of Hanoi puzzle game with multiple solving algorithms, a modern React gaming UI, and MySQL database integration.

## 📋 Requirements Implementation

This project implements all requirements from the PDSA coursework specification:


## 🎮 Features

### Gaming UI
- **Cyberpunk/Gaming Theme**: Dark gradient backgrounds, neon colors, glow effects
- **Animated Disks**: Smooth animations using Framer Motion
- **Interactive Gameplay**: Click pegs to move disks
- **Victory Celebration**: Confetti animation on puzzle completion
- **Algorithm Comparison**: View performance of different algorithms
- **Hint System**: Get optimal move suggestions
- **Question Challenge**: Test your knowledge after winning

### Algorithms

#### 3-Peg Algorithms (Requirement 4.1.3)
1. **Classic Recursive**: Standard divide-and-conquer approach
   - Time Complexity: O(2^n)
   - Moves: 2^n - 1

2. **Iterative with Stack**: Non-recursive using explicit stack
   - Time Complexity: O(2^n)
   - Moves: 2^n - 1

#### 4-Peg Algorithms (Requirement 4.1.4)
1. **Frame-Stewart Algorithm**: Conjectured optimal solution
   - Time Complexity: O(2^√n) approximately
   - Uses dynamic k-value optimization

2. **Optimized Recursive**: DP-based approach
   - Precomputes optimal split points
   - Minimizes total move count

## 🗄️ Database Schema (Normalized - 4.1.7)

The database follows 1NF, 2NF, and 3NF normalization:

```sql
-- Core tables
players(player_id PK, player_name, email, created_at)
algorithms(algorithm_id PK, algorithm_name, description, peg_count)
game_sessions(session_id PK, player_id FK, disk_count, peg_count, ...)
algorithm_results(result_id PK, session_id FK, algorithm_id FK, move_count, time_taken_ms)
user_responses(response_id PK, session_id FK, question_type, user_answer, correct_answer, is_correct)
move_history(move_id PK, result_id FK, move_number, from_peg, to_peg, disk_number)
```

## ✅ Validation & Exception Handling (4.2.2)

### Input Validations
- **Player Name**: 
  - Cannot be empty
  - Max 100 characters
  - Only alphanumeric, spaces, hyphens, underscores
- **Peg Count**: Must be 3 or 4
- **Disk Count**: Automatically 5-10 (randomly selected)
- **Move Validation**: 
  - Valid peg indices
  - Source peg has disks
  - Cannot place larger disk on smaller

### Exception Handling
- `ValidationError`: For input validation failures
- `GameError`: For game logic errors
- Database errors: Gracefully handled, game continues without DB
- API errors: Proper HTTP status codes and error messages

## 🚀 Setup Instructions

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup database (optional - game works without DB)
# 1. Create MySQL database
# 2. Run schema.sql
# 3. Copy .env.example to .env and configure

# Run server
python app.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Database Setup (MySQL)

```sql
-- Run the schema file
source backend/database/schema.sql;
```

## 🧪 Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_three_peg_solver.py -v

# Run specific test
pytest tests/test_game_controller.py::TestGameControllerDiskGeneration -v
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check |
| POST | /api/game/new | Create new game |
| GET | /api/game/state | Get current game state |
| POST | /api/game/move | Make a move |
| POST | /api/game/solve | Solve with algorithms |
| POST | /api/game/answer | Submit answer |
| POST | /api/game/reset | Reset game |
| GET | /api/game/hint | Get next optimal move |
| GET | /api/leaderboard | Get top players |


## 🎯 How to Play

1. Enter your name on the welcome screen
2. Select number of pegs (3 or 4)
3. Game starts with random 5-10 disks on the first peg
4. Click a peg with disks to select it
5. Click another peg to move the top disk
6. Move all disks to the destination peg
7. Answer the challenge question to save your score!

