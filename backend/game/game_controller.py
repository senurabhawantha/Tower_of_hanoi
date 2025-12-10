"""
Game Logic and Controller for Tower of Hanoi
Implements requirements 4.1.1 (random disk selection) and 4.1.2 (peg selection)
"""
import random
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from algorithms import ThreePegSolver, FourPegSolver, AlgorithmResult
from config import Config


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class GameError(Exception):
    """Custom exception for game-related errors"""
    pass


@dataclass
class GameState:
    """Represents the current state of a game"""
    session_id: Optional[int] = None
    player_name: str = ""
    player_id: Optional[int] = None
    disk_count: int = 0
    peg_count: int = 0
    pegs: List[List[int]] = field(default_factory=list)
    move_count: int = 0
    is_completed: bool = False
    algorithm_results: List[AlgorithmResult] = field(default_factory=list)


class GameController:
    """
    Main game controller that manages game logic
    Implements requirements 4.1.1, 4.1.2, 4.1.3, 4.1.4, 4.1.6
    """
    
    def __init__(self):
        self.current_game: Optional[GameState] = None
    
    @staticmethod
    def generate_random_disk_count() -> int:
        """
        Requirement 4.1.1: Randomly select number of disks from 5 to 10
        Returns: Random integer between 5 and 10 inclusive
        """
        disk_count = random.randint(Config.MIN_DISKS, Config.MAX_DISKS)
        return disk_count
    
    @staticmethod
    def validate_peg_count(peg_count: int) -> bool:
        """
        Requirement 4.1.2: Validate peg count is 3 or 4
        Args:
            peg_count: User selected number of pegs
        Returns: True if valid
        Raises: ValidationError if invalid
        """
        if peg_count not in [Config.MIN_PEGS, Config.MAX_PEGS]:
            raise ValidationError(
                f"Number of pegs must be {Config.MIN_PEGS} or {Config.MAX_PEGS}. "
                f"Got: {peg_count}"
            )
        return True
    
    @staticmethod
    def validate_player_name(name: str) -> bool:
        """
        Validate player name
        Args:
            name: Player name
        Returns: True if valid
        Raises: ValidationError if invalid
        """
        if not name or not name.strip():
            raise ValidationError("Player name cannot be empty")
        
        if len(name) > 100:
            raise ValidationError("Player name cannot exceed 100 characters")
        
        # Check for valid characters
        if not all(c.isalnum() or c.isspace() or c in '-_' for c in name):
            raise ValidationError(
                "Player name can only contain letters, numbers, spaces, hyphens, and underscores"
            )
        
        return True
    
    def create_new_game(self, player_name: str, peg_count: int) -> GameState:
        """
        Create a new game with random disk count
        Args:
            player_name: Name of the player
            peg_count: Number of pegs (3 or 4)
        Returns: GameState object
        """
        # Validate inputs
        self.validate_player_name(player_name)
        self.validate_peg_count(peg_count)
        
        # Generate random disk count (requirement 4.1.1)
        disk_count = self.generate_random_disk_count()
        
        # Initialize pegs - all disks start on first peg
        pegs = [list(range(disk_count, 0, -1))]  # First peg with all disks
        pegs.extend([[] for _ in range(peg_count - 1)])  # Empty pegs
        
        self.current_game = GameState(
            player_name=player_name,
            disk_count=disk_count,
            peg_count=peg_count,
            pegs=pegs,
            move_count=0,
            is_completed=False
        )
        
        return self.current_game
    
    def validate_move(self, from_peg: int, to_peg: int) -> Tuple[bool, str]:
        """
        Validate if a move is legal
        Args:
            from_peg: Source peg index
            to_peg: Destination peg index
        Returns: (is_valid, message)
        """
        if not self.current_game:
            return False, "No active game"
        
        game = self.current_game
        
        # Validate peg indices
        if from_peg < 0 or from_peg >= game.peg_count:
            return False, f"Invalid source peg: {from_peg}"
        
        if to_peg < 0 or to_peg >= game.peg_count:
            return False, f"Invalid destination peg: {to_peg}"
        
        if from_peg == to_peg:
            return False, "Source and destination pegs must be different"
        
        # Check if source peg has disks
        if not game.pegs[from_peg]:
            return False, f"No disks on peg {from_peg + 1}"
        
        # Check if move follows Tower of Hanoi rules
        disk_to_move = game.pegs[from_peg][-1]
        if game.pegs[to_peg] and game.pegs[to_peg][-1] < disk_to_move:
            return False, "Cannot place larger disk on smaller disk"
        
        return True, "Valid move"
    
    def make_move(self, from_peg: int, to_peg: int) -> Dict[str, Any]:
        """
        Execute a move in the game
        Args:
            from_peg: Source peg index
            to_peg: Destination peg index
        Returns: Dict with move result
        """
        is_valid, message = self.validate_move(from_peg, to_peg)
        
        if not is_valid:
            raise GameError(message)
        
        game = self.current_game
        
        # Execute move
        disk = game.pegs[from_peg].pop()
        game.pegs[to_peg].append(disk)
        game.move_count += 1
        
        # Check if game is completed
        destination_peg = game.peg_count - 1
        expected_disks = list(range(game.disk_count, 0, -1))
        
        if game.pegs[destination_peg] == expected_disks:
            game.is_completed = True
        
        return {
            "success": True,
            "disk_moved": disk,
            "from_peg": from_peg,
            "to_peg": to_peg,
            "move_count": game.move_count,
            "is_completed": game.is_completed,
            "pegs": game.pegs
        }
    
    def solve_with_algorithms(self) -> List[AlgorithmResult]:
        """
        Solve current puzzle using appropriate algorithms
        Implements requirements 4.1.3, 4.1.4, and 4.1.6
        Returns: List of AlgorithmResult objects with timing
        """
        if not self.current_game:
            raise GameError("No active game")
        
        game = self.current_game
        results = []
        
        if game.peg_count == 3:
            # Requirement 4.1.3: Two algorithms for 3 pegs
            solver = ThreePegSolver(game.disk_count)
            
            # Algorithm 1: Recursive
            result1 = solver.solve_recursive()
            results.append(result1)
            
            # Algorithm 2: Iterative
            result2 = solver.solve_iterative()
            results.append(result2)
            
        elif game.peg_count == 4:
            # Requirement 4.1.4: Two algorithms for 4 pegs
            solver = FourPegSolver(game.disk_count)
            
            # Algorithm 1: Frame-Stewart
            result1 = solver.solve_frame_stewart()
            results.append(result1)
            
            # Algorithm 2: Optimized Recursive
            result2 = solver.solve_recursive_optimized()
            results.append(result2)
        
        game.algorithm_results = results
        return results
    
    def get_minimum_moves(self) -> int:
        """
        Get minimum number of moves for current puzzle
        """
        if not self.current_game:
            raise GameError("No active game")
        
        game = self.current_game
        
        if game.peg_count == 3:
            return (2 ** game.disk_count) - 1
        else:
            solver = FourPegSolver(game.disk_count)
            return solver.get_minimum_moves_estimate()
    
    def check_user_answer(self, question_type: str, user_answer: str) -> Dict[str, Any]:
        """
        Check if user's answer is correct
        Args:
            question_type: Type of question (e.g., 'minimum_moves')
            user_answer: User's answer
        Returns: Dict with correctness and correct answer
        """
        if not self.current_game:
            raise GameError("No active game")
        
        correct_answer = ""
        is_correct = False
        
        if question_type == "minimum_moves":
            correct_answer = str(self.get_minimum_moves())
            is_correct = user_answer.strip() == correct_answer
        
        elif question_type == "disk_count":
            correct_answer = str(self.current_game.disk_count)
            is_correct = user_answer.strip() == correct_answer
        
        return {
            "question_type": question_type,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        }
    
    def get_game_state(self) -> Optional[Dict[str, Any]]:
        """
        Get current game state as dictionary
        """
        if not self.current_game:
            return None
        
        game = self.current_game
        return {
            "session_id": game.session_id,
            "player_name": game.player_name,
            "disk_count": game.disk_count,
            "peg_count": game.peg_count,
            "pegs": game.pegs,
            "move_count": game.move_count,
            "is_completed": game.is_completed,
            "minimum_moves": self.get_minimum_moves()
        }
    
    def reset_game(self):
        """Reset game to initial state"""
        if self.current_game:
            game = self.current_game
            game.pegs = [list(range(game.disk_count, 0, -1))]
            game.pegs.extend([[] for _ in range(game.peg_count - 1)])
            game.move_count = 0
            game.is_completed = False
