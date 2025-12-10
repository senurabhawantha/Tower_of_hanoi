"""
Tower of Hanoi Algorithms - 4 Pegs Implementation
Implements requirement 4.1.4: Two algorithm approaches for 4 Pegs
"""
import time
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AlgorithmResult:
    """Data class to store algorithm execution results"""
    algorithm_name: str
    move_count: int
    time_taken_ms: float
    moves: List[Tuple[int, int, int]]  # (disk, from_peg, to_peg)


class FourPegSolver:
    """
    Solves Tower of Hanoi problem with 4 pegs
    Implements two different algorithm approaches as per requirement 4.1.4
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
        # Precompute optimal k values for Frame-Stewart algorithm
        self._k_cache = {}
    
    def _record_move(self, disk: int, from_peg: int, to_peg: int):
        """Record a single move"""
        self.moves.append((disk, from_peg, to_peg))
    
    def _compute_optimal_k(self, n: int) -> int:
        """
        Compute optimal k value for Frame-Stewart algorithm
        k = n - round(sqrt(2n + 1)) + 1
        """
        if n in self._k_cache:
            return self._k_cache[n]
        
        if n <= 1:
            return 0
        
        # Formula derived from Frame-Stewart algorithm optimization
        k = n - round(math.sqrt(2 * n + 1)) + 1
        k = max(1, min(k, n - 1))
        self._k_cache[n] = k
        return k
    
    # ========================================================================
    # ALGORITHM 1: Frame-Stewart Algorithm (4 Pegs)
    # ========================================================================
    def solve_frame_stewart(self) -> AlgorithmResult:
        """
        Algorithm 1: Frame-Stewart Algorithm for 4 Pegs
        
        The Frame-Stewart algorithm is a conjectured optimal solution for
        the Tower of Hanoi problem with 4 or more pegs.
        
        The algorithm works by:
        1. Choose an optimal k (number of disks to move to auxiliary peg)
        2. Move top k disks from source to auxiliary using 4 pegs
        3. Move remaining n-k disks from source to destination using 3 pegs
        4. Move k disks from auxiliary to destination using 4 pegs
        
        Time Complexity: O(2^sqrt(n)) approximately
        Space Complexity: O(n) for recursion
        
        Returns:
            AlgorithmResult with moves and timing
        """
        self.moves = []
        
        # Record start time for requirement 4.1.6
        start_time = time.perf_counter()
        
        def frame_stewart(n: int, source: int, dest: int, aux1: int, aux2: int,
                          disk_offset: int = 0):
            """
            Frame-Stewart recursive algorithm
            Args:
                n: Number of disks to move
                source: Source peg
                dest: Destination peg
                aux1: First auxiliary peg
                aux2: Second auxiliary peg
                disk_offset: Offset for disk numbering (for sub-problems)
            """
            if n == 0:
                return
            
            if n == 1:
                # Base case: move single disk
                self._record_move(disk_offset + 1, source, dest)
                return
            
            if n == 2:
                # Special case for 2 disks
                self._record_move(disk_offset + 1, source, aux1)
                self._record_move(disk_offset + 2, source, dest)
                self._record_move(disk_offset + 1, aux1, dest)
                return
            
            # Compute optimal k
            k = self._compute_optimal_k(n)
            
            # Step 1: Move top k disks from source to aux1 using 4 pegs
            frame_stewart(k, source, aux1, aux2, dest, disk_offset)
            
            # Step 2: Move remaining n-k disks from source to dest using 3 pegs
            # (aux1 is "blocked" by the k smaller disks)
            hanoi_3peg(n - k, source, dest, aux2, disk_offset + k)
            
            # Step 3: Move k disks from aux1 to dest using 4 pegs
            frame_stewart(k, aux1, dest, source, aux2, disk_offset)
        
        def hanoi_3peg(n: int, source: int, dest: int, aux: int, 
                       disk_offset: int = 0):
            """
            Standard 3-peg Hanoi algorithm (used when one peg is blocked)
            """
            if n == 0:
                return
            if n == 1:
                self._record_move(disk_offset + 1, source, dest)
                return
            
            hanoi_3peg(n - 1, source, aux, dest, disk_offset)
            self._record_move(disk_offset + n, source, dest)
            hanoi_3peg(n - 1, aux, dest, source, disk_offset)
        
        # Execute: Move all disks from peg 0 to peg 3
        frame_stewart(self.num_disks, 0, 3, 1, 2)
        
        # Record end time
        end_time = time.perf_counter()
        time_taken_ms = (end_time - start_time) * 1000
        
        return AlgorithmResult(
            algorithm_name="FrameStewart_4Peg",
            move_count=len(self.moves),
            time_taken_ms=time_taken_ms,
            moves=self.moves.copy()
        )
    
    # ========================================================================
    # ALGORITHM 2: Optimized Recursive Algorithm (4 Pegs)
    # ========================================================================
    def solve_recursive_optimized(self) -> AlgorithmResult:
        """
        Algorithm 2: Optimized Recursive Algorithm for 4 Pegs
        
        This algorithm uses dynamic programming with memoization
        to find the optimal number of moves and then executes them.
        
        The approach:
        1. Precompute minimum moves needed for each n using DP
        2. For each n, find the best split point k that minimizes:
           f(k) + 2^(n-k) - 1 + f(k)
           where f(n) is minimum moves with 4 pegs
        3. Execute moves using the optimal split points
        
        Time Complexity: O(n^2) for precomputation, O(moves) for execution
        Space Complexity: O(n) for memoization
        
        Returns:
            AlgorithmResult with moves and timing
        """
        self.moves = []
        
        # Record start time for requirement 4.1.6
        start_time = time.perf_counter()
        
        # Precompute minimum moves with dynamic programming
        # min_moves_4peg[i] = minimum moves needed to move i disks with 4 pegs
        max_n = self.num_disks + 1
        min_moves_4peg = [0] * max_n
        best_k = [0] * max_n
        
        for n in range(1, max_n):
            if n == 1:
                min_moves_4peg[1] = 1
                best_k[1] = 0
                continue
            
            # Try all possible k values
            min_val = float('inf')
            optimal_k = 1
            
            for k in range(1, n):
                # Cost = 2*f4(k) + (2^(n-k) - 1)
                # where f4(k) is moves for k disks with 4 pegs
                # and 2^(n-k) - 1 is moves for n-k disks with 3 pegs
                cost = 2 * min_moves_4peg[k] + (2 ** (n - k)) - 1
                
                if cost < min_val:
                    min_val = cost
                    optimal_k = k
            
            min_moves_4peg[n] = min_val
            best_k[n] = optimal_k
        
        def solve_4peg_optimized(n: int, source: int, dest: int, 
                                  aux1: int, aux2: int, disk_start: int):
            """
            Solve using precomputed optimal k values
            """
            if n == 0:
                return
            
            if n == 1:
                self._record_move(disk_start, source, dest)
                return
            
            k = best_k[n]
            
            # Step 1: Move top k disks to aux1 using 4 pegs
            solve_4peg_optimized(k, source, aux1, dest, aux2, disk_start)
            
            # Step 2: Move remaining n-k disks to dest using 3 pegs
            solve_3peg(n - k, source, dest, aux2, disk_start + k)
            
            # Step 3: Move k disks from aux1 to dest using 4 pegs
            solve_4peg_optimized(k, aux1, dest, source, aux2, disk_start)
        
        def solve_3peg(n: int, source: int, dest: int, aux: int, disk_start: int):
            """Standard 3-peg solution"""
            if n == 0:
                return
            if n == 1:
                self._record_move(disk_start, source, dest)
                return
            
            solve_3peg(n - 1, source, aux, dest, disk_start)
            self._record_move(disk_start + n - 1, source, dest)
            solve_3peg(n - 1, aux, dest, source, disk_start)
        
        # Execute algorithm
        solve_4peg_optimized(self.num_disks, 0, 3, 1, 2, 1)
        
        # Record end time
        end_time = time.perf_counter()
        time_taken_ms = (end_time - start_time) * 1000
        
        return AlgorithmResult(
            algorithm_name="Recursive_4Peg",
            move_count=len(self.moves),
            time_taken_ms=time_taken_ms,
            moves=self.moves.copy()
        )
    
    def get_minimum_moves_estimate(self) -> int:
        """
        Estimate minimum number of moves for 4 pegs using Frame-Stewart formula
        """
        # Use dynamic programming to compute
        min_moves = [0] * (self.num_disks + 1)
        
        for n in range(1, self.num_disks + 1):
            if n == 1:
                min_moves[1] = 1
                continue
            
            min_val = float('inf')
            for k in range(1, n):
                cost = 2 * min_moves[k] + (2 ** (n - k)) - 1
                min_val = min(min_val, cost)
            min_moves[n] = min_val
        
        return min_moves[self.num_disks]
    
    def verify_solution(self, moves: List[Tuple[int, int, int]]) -> bool:
        """
        Verify if a solution is valid for 4 pegs
        Args:
            moves: List of (disk, from_peg, to_peg) tuples
        Returns:
            True if solution is valid
        """
        # Initialize pegs with all disks on peg 0
        pegs = [list(range(self.num_disks, 0, -1)), [], [], []]
        
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
        
        # Verify all disks are on destination peg (peg 3)
        expected = list(range(self.num_disks, 0, -1))
        return pegs[3] == expected and not pegs[0] and not pegs[1] and not pegs[2]
