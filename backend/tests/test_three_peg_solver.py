"""
Unit Tests for Three Peg Solver Algorithms
Tests requirement 4.1.3: Two algorithm approaches for 3 Pegs
"""
import pytest
from algorithms.three_peg_solver import ThreePegSolver, AlgorithmResult


class TestThreePegSolver:
    """Test cases for ThreePegSolver class"""
    
    def test_solver_initialization_valid_disks(self):
        """Test solver initializes correctly with valid disk counts"""
        for n in range(5, 11):
            solver = ThreePegSolver(n)
            assert solver.num_disks == n
    
    def test_solver_initialization_invalid_disks_low(self):
        """Test solver raises error for disk count below 5"""
        with pytest.raises(ValueError) as exc_info:
            ThreePegSolver(4)
        assert "between 5 and 10" in str(exc_info.value)
    
    def test_solver_initialization_invalid_disks_high(self):
        """Test solver raises error for disk count above 10"""
        with pytest.raises(ValueError) as exc_info:
            ThreePegSolver(11)
        assert "between 5 and 10" in str(exc_info.value)
    
    def test_recursive_algorithm_returns_result(self):
        """Test recursive algorithm returns AlgorithmResult"""
        solver = ThreePegSolver(5)
        result = solver.solve_recursive()
        
        assert isinstance(result, AlgorithmResult)
        assert result.algorithm_name == "Recursive_3Peg"
        assert result.move_count > 0
        assert result.time_taken_ms >= 0
        assert len(result.moves) == result.move_count
    
    def test_iterative_algorithm_returns_result(self):
        """Test iterative algorithm returns AlgorithmResult"""
        solver = ThreePegSolver(5)
        result = solver.solve_iterative()
        
        assert isinstance(result, AlgorithmResult)
        assert result.algorithm_name == "Iterative_3Peg"
        assert result.move_count > 0
        assert result.time_taken_ms >= 0
        assert len(result.moves) == result.move_count
    
    def test_recursive_correct_move_count(self):
        """Test recursive algorithm produces correct number of moves (2^n - 1)"""
        for n in range(5, 11):
            solver = ThreePegSolver(n)
            result = solver.solve_recursive()
            expected_moves = (2 ** n) - 1
            assert result.move_count == expected_moves, \
                f"Expected {expected_moves} moves for {n} disks, got {result.move_count}"
    
    def test_iterative_correct_move_count(self):
        """Test iterative algorithm produces correct number of moves (2^n - 1)"""
        for n in range(5, 11):
            solver = ThreePegSolver(n)
            result = solver.solve_iterative()
            expected_moves = (2 ** n) - 1
            assert result.move_count == expected_moves, \
                f"Expected {expected_moves} moves for {n} disks, got {result.move_count}"
    
    def test_recursive_solution_valid(self):
        """Test recursive algorithm produces valid solution"""
        solver = ThreePegSolver(5)
        result = solver.solve_recursive()
        assert solver.verify_solution(result.moves) == True
    
    def test_iterative_solution_valid(self):
        """Test iterative algorithm produces valid solution"""
        solver = ThreePegSolver(5)
        result = solver.solve_iterative()
        assert solver.verify_solution(result.moves) == True
    
    def test_both_algorithms_produce_same_move_count(self):
        """Test both algorithms produce same number of moves"""
        for n in range(5, 11):
            solver = ThreePegSolver(n)
            recursive_result = solver.solve_recursive()
            iterative_result = solver.solve_iterative()
            assert recursive_result.move_count == iterative_result.move_count
    
    def test_get_minimum_moves(self):
        """Test minimum moves calculation"""
        solver = ThreePegSolver(5)
        assert solver.get_minimum_moves() == 31  # 2^5 - 1
        
        solver = ThreePegSolver(10)
        assert solver.get_minimum_moves() == 1023  # 2^10 - 1
    
    def test_moves_format(self):
        """Test moves are in correct format (disk, from_peg, to_peg)"""
        solver = ThreePegSolver(5)
        result = solver.solve_recursive()
        
        for move in result.moves:
            assert isinstance(move, tuple)
            assert len(move) == 3
            disk, from_peg, to_peg = move
            assert 1 <= disk <= 5  # Valid disk number
            assert 0 <= from_peg <= 2  # Valid peg index
            assert 0 <= to_peg <= 2  # Valid peg index
            assert from_peg != to_peg  # Different pegs
    
    def test_time_taken_recorded(self):
        """Test that time taken is recorded for each algorithm (requirement 4.1.6)"""
        solver = ThreePegSolver(5)
        
        result = solver.solve_recursive()
        assert result.time_taken_ms >= 0
        
        result = solver.solve_iterative()
        assert result.time_taken_ms >= 0
    
    def test_verify_invalid_solution(self):
        """Test verify_solution returns False for invalid moves"""
        solver = ThreePegSolver(5)
        
        # Invalid: larger disk on smaller disk
        invalid_moves = [(1, 0, 2), (2, 0, 2)]  # Move disk 2 onto disk 1
        assert solver.verify_solution(invalid_moves) == False
    
    def test_solver_reusable(self):
        """Test solver can be used multiple times"""
        solver = ThreePegSolver(5)
        
        result1 = solver.solve_recursive()
        result2 = solver.solve_recursive()
        
        assert result1.move_count == result2.move_count
        assert result1.moves == result2.moves


class TestThreePegEdgeCases:
    """Edge case tests for ThreePegSolver"""
    
    def test_minimum_valid_disks(self):
        """Test with minimum valid disk count (5)"""
        solver = ThreePegSolver(5)
        result = solver.solve_recursive()
        assert result.move_count == 31
    
    def test_maximum_valid_disks(self):
        """Test with maximum valid disk count (10)"""
        solver = ThreePegSolver(10)
        result = solver.solve_recursive()
        assert result.move_count == 1023
    
    def test_both_algorithms_complete(self):
        """Test both algorithms complete for all valid disk counts"""
        for n in range(5, 11):
            solver = ThreePegSolver(n)
            
            recursive = solver.solve_recursive()
            assert recursive is not None
            assert solver.verify_solution(recursive.moves)
            
            iterative = solver.solve_iterative()
            assert iterative is not None
            assert solver.verify_solution(iterative.moves)
