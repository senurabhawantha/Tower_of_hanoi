"""
Tower of Hanoi Algorithms - 3 Pegs Implementation
Implements requirement 4.1.3: Two algorithm approaches for 3 Pegs
"""
import time
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class AlgorithmResult:
    """Data class to store algorithm execution results"""
    algorithm_name: str
    move_count: int
    time_taken_ms: float
    moves: List[Tuple[int, int, int]]  # (disk, from_peg, to_peg)
    

class ThreePegSolver:
    """
    Solves Tower of Hanoi problem with 3 pegs
    Implements two different algorithm approaches as per requirement 4.1.3
    """
    
    def __init__(self, num_disks: int):
        """
        Initialize solver with number of disks
        Args:
            num_disks: Number of disks (5-10 as per requirement 4.1.1)
        """
        if not 5 <= num_disks <= 10:
            raise ValueError("Number of disks must be between 5 and 10")
        self.num_disks = num_disks
        self.moves = []
    
    def _record_move(self, disk: int, from_peg: int, to_peg: int):
        """Record a single move"""
        self.moves.append((disk, from_peg, to_peg))
    
    # ========================================================================
    # ALGORITHM 1: Classic Recursive Approach (3 Pegs)
    # ========================================================================
    def solve_recursive(self) -> AlgorithmResult:
        """
        Algorithm 1: Classic Recursive Solution for 3 Pegs
        
        The classic recursive algorithm solves Tower of Hanoi by:
        1. Move n-1 disks from source to auxiliary peg
        2. Move the largest disk from source to destination
        3. Move n-1 disks from auxiliary to destination
        
        Time Complexity: O(2^n)
        Space Complexity: O(n) due to recursion stack
        
        Returns:
            AlgorithmResult with moves and timing
        """
        self.moves = []
        
        # Record start time for requirement 4.1.6
        start_time = time.perf_counter()
        
        def recursive_solve(n: int, source: int, auxiliary: int, destination: int):
            """
            Recursive helper function
            Args:
                n: Number of disks to move
                source: Source peg (0, 1, or 2)
                auxiliary: Auxiliary peg
                destination: Destination peg
            """
            if n == 1:
                # Base case: move single disk directly
                self._record_move(n, source, destination)
                return
            
            # Step 1: Move n-1 disks from source to auxiliary
            recursive_solve(n - 1, source, destination, auxiliary)
            
            # Step 2: Move largest disk from source to destination
            self._record_move(n, source, destination)
            
            # Step 3: Move n-1 disks from auxiliary to destination
            recursive_solve(n - 1, auxiliary, source, destination)
        
        # Execute algorithm: Move all disks from peg 0 to peg 2
        recursive_solve(self.num_disks, 0, 1, 2)
        
        # Record end time
        end_time = time.perf_counter()
        time_taken_ms = (end_time - start_time) * 1000
        
        return AlgorithmResult(
            algorithm_name="Recursive_3Peg",
            move_count=len(self.moves),
            time_taken_ms=time_taken_ms,
            moves=self.moves.copy()
        )
    
    # ========================================================================
    # ALGORITHM 2: Iterative Approach using Stack Simulation (3 Pegs)
    # ========================================================================
    def solve_iterative(self) -> AlgorithmResult:
        """
        Algorithm 2: Iterative Solution using Stack Simulation for 3 Pegs
        
        This approach uses an explicit stack to simulate recursion.
        It avoids the overhead of function calls and is more memory efficient.
        
        The algorithm works by:
        1. Creating a stack with initial problem state
        2. Processing each state and pushing sub-problems onto stack
        3. Recording moves when processing single disk moves
        
        Time Complexity: O(2^n)
        Space Complexity: O(n) for explicit stack
        
        Returns:
            AlgorithmResult with moves and timing
        """
        self.moves = []
        
        # Record start time for requirement 4.1.6
        start_time = time.perf_counter()
        
        # Stack stores: (n, source, auxiliary, destination, phase)
        # phase: 0 = initial, 1 = after first recursive call, 2 = after move
        stack = [(self.num_disks, 0, 1, 2, 0)]
        
        while stack:
            n, source, auxiliary, destination, phase = stack.pop()
            
            if n == 1:
                # Base case: move single disk
                self._record_move(n, source, destination)
                continue
            
            if phase == 0:
                # First visit: push continuation and first sub-problem
                # Push in reverse order (LIFO)
                stack.append((n, source, auxiliary, destination, 1))
                stack.append((n - 1, source, destination, auxiliary, 0))
            
            elif phase == 1:
                # After first sub-problem: move disk n and push second sub-problem
                self._record_move(n, source, destination)
                stack.append((n - 1, auxiliary, source, destination, 0))
        
        # Record end time
        end_time = time.perf_counter()
        time_taken_ms = (end_time - start_time) * 1000
        
        return AlgorithmResult(
            algorithm_name="Iterative_3Peg",
            move_count=len(self.moves),
            time_taken_ms=time_taken_ms,
            moves=self.moves.copy()
        )
    
    def get_minimum_moves(self) -> int:
        """
        Calculate minimum number of moves required
        For 3 pegs: 2^n - 1 moves
        """
        return (2 ** self.num_disks) - 1
    
    def verify_solution(self, moves: List[Tuple[int, int, int]]) -> bool:
        """
        Verify if a solution is valid
        Args:
            moves: List of (disk, from_peg, to_peg) tuples
        Returns:
            True if solution is valid
        """
        # Initialize pegs with all disks on peg 0
        pegs = [list(range(self.num_disks, 0, -1)), [], []]
        
        for disk, from_peg, to_peg in moves:
            # Check if move is valid
            if not pegs[from_peg] or pegs[from_peg][-1] != disk:
                return False
            
            # Check if we can place disk on destination
            if pegs[to_peg] and pegs[to_peg][-1] < disk:
                return False
            
            # Execute move
            pegs[from_peg].pop()
            pegs[to_peg].append(disk)
        
        # Verify all disks are on destination peg (peg 2)
        expected = list(range(self.num_disks, 0, -1))
        return pegs[2] == expected and not pegs[0] and not pegs[1]
