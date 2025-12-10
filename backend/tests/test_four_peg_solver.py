"""
Unit Tests for Four Peg Solver Algorithms
Tests requirement 4.1.4: Two algorithm approaches for 4 Pegs
"""
import pytest
from algorithms.four_peg_solver import FourPegSolver, AlgorithmResult


class TestFourPegSolver:
    """Test cases for FourPegSolver class"""
    
    def test_solver_initialization_valid_disks(self):
        """Test solver initializes correctly with valid disk counts"""
        for n in range(5, 11):
            solver = FourPegSolver(n)
            assert solver.num_disks == n
    
    def test_solver_initialization_invalid_disks_low(self):
        """Test solver raises error for disk count below 5"""
        with pytest.raises(ValueError) as exc_info:
            FourPegSolver(4)
        assert "between 5 and 10" in str(exc_info.value)
    
    def test_solver_initialization_invalid_disks_high(self):
        """Test solver raises error for disk count above 10"""
        with pytest.raises(ValueError) as exc_info:
            FourPegSolver(11)
        assert "between 5 and 10" in str(exc_info.value)
    
    def test_frame_stewart_returns_result(self):
        """Test Frame-Stewart algorithm returns AlgorithmResult"""
        solver = FourPegSolver(5)
        result = solver.solve_frame_stewart()
        
        assert isinstance(result, AlgorithmResult)
        assert result.algorithm_name == "FrameStewart_4Peg"
        assert result.move_count > 0
        assert result.time_taken_ms >= 0
        assert len(result.moves) == result.move_count
    
    def test_recursive_optimized_returns_result(self):
        """Test optimized recursive algorithm returns AlgorithmResult"""
        solver = FourPegSolver(5)
        result = solver.solve_recursive_optimized()
        
        assert isinstance(result, AlgorithmResult)
        assert result.algorithm_name == "Recursive_4Peg"
        assert result.move_count > 0
        assert result.time_taken_ms >= 0
        assert len(result.moves) == result.move_count
    
    def test_four_peg_fewer_moves_than_three_peg(self):
        """Test 4-peg solution uses fewer moves than 3-peg"""
        from algorithms.three_peg_solver import ThreePegSolver
        
        for n in range(5, 11):
            three_peg = ThreePegSolver(n)
            four_peg = FourPegSolver(n)
            
            three_peg_result = three_peg.solve_recursive()
            four_peg_result = four_peg.solve_frame_stewart()
            
            assert four_peg_result.move_count < three_peg_result.move_count, \
                f"4-peg ({four_peg_result.move_count}) should be less than " \
                f"3-peg ({three_peg_result.move_count}) for {n} disks"
    
    def test_frame_stewart_solution_valid(self):
        """Test Frame-Stewart algorithm produces valid solution"""
        solver = FourPegSolver(5)
        result = solver.solve_frame_stewart()
        assert solver.verify_solution(result.moves) == True
    
    def test_recursive_optimized_solution_valid(self):
        """Test optimized recursive algorithm produces valid solution"""
        solver = FourPegSolver(5)
        result = solver.solve_recursive_optimized()
        assert solver.verify_solution(result.moves) == True
    
    def test_both_algorithms_produce_valid_solutions(self):
        """Test both algorithms produce valid solutions for all disk counts"""
        for n in range(5, 11):
            solver = FourPegSolver(n)
            
            fs_result = solver.solve_frame_stewart()
            assert solver.verify_solution(fs_result.moves), \
                f"Frame-Stewart invalid for {n} disks"
            
            ro_result = solver.solve_recursive_optimized()
            assert solver.verify_solution(ro_result.moves), \
                f"Recursive Optimized invalid for {n} disks"
    
    def test_get_minimum_moves_estimate(self):
        """Test minimum moves estimation"""
        solver = FourPegSolver(5)
        min_moves = solver.get_minimum_moves_estimate()
        assert min_moves > 0
        assert min_moves < (2 ** 5 - 1)  # Should be less than 3-peg minimum
    
    def test_moves_format(self):
        """Test moves are in correct format (disk, from_peg, to_peg)"""
        solver = FourPegSolver(5)
        result = solver.solve_frame_stewart()
        
        for move in result.moves:
            assert isinstance(move, tuple)
            assert len(move) == 3
            disk, from_peg, to_peg = move
            assert 1 <= disk <= 5  # Valid disk number
            assert 0 <= from_peg <= 3  # Valid peg index for 4 pegs
            assert 0 <= to_peg <= 3  # Valid peg index for 4 pegs
            assert from_peg != to_peg  # Different pegs
    
    def test_time_taken_recorded(self):
        """Test that time taken is recorded for each algorithm (requirement 4.1.6)"""
        solver = FourPegSolver(5)
        
        result = solver.solve_frame_stewart()
        assert result.time_taken_ms >= 0
        
        result = solver.solve_recursive_optimized()
        assert result.time_taken_ms >= 0
    
    def test_verify_invalid_solution(self):
        """Test verify_solution returns False for invalid moves"""
        solver = FourPegSolver(5)
        
        # Invalid: moving to wrong destination peg sequence
        invalid_moves = [(1, 0, 3), (2, 0, 3)]  # Move disk 2 onto disk 1
        assert solver.verify_solution(invalid_moves) == False
    
    def test_solver_reusable(self):
        """Test solver can be used multiple times"""
        solver = FourPegSolver(5)
        
        result1 = solver.solve_frame_stewart()
        result2 = solver.solve_frame_stewart()
        
        assert result1.move_count == result2.move_count


class TestFourPegEdgeCases:
    """Edge case tests for FourPegSolver"""
    
    def test_minimum_valid_disks(self):
        """Test with minimum valid disk count (5)"""
        solver = FourPegSolver(5)
        result = solver.solve_frame_stewart()
        assert result.move_count > 0
        assert solver.verify_solution(result.moves)
    
    def test_maximum_valid_disks(self):
        """Test with maximum valid disk count (10)"""
        solver = FourPegSolver(10)
        result = solver.solve_frame_stewart()
        assert result.move_count > 0
        assert solver.verify_solution(result.moves)
    
    def test_both_algorithms_complete(self):
        """Test both algorithms complete for all valid disk counts"""
        for n in range(5, 11):
            solver = FourPegSolver(n)
            
            frame_stewart = solver.solve_frame_stewart()
            assert frame_stewart is not None
            assert solver.verify_solution(frame_stewart.moves)
            
            recursive_opt = solver.solve_recursive_optimized()
            assert recursive_opt is not None
            assert solver.verify_solution(recursive_opt.moves)


class TestFourPegPerformance:
    """Performance tests for FourPegSolver"""
    
    def test_frame_stewart_reasonable_time(self):
        """Test Frame-Stewart completes in reasonable time"""
        solver = FourPegSolver(10)
        result = solver.solve_frame_stewart()
        # Should complete in under 1 second
        assert result.time_taken_ms < 1000
    
    def test_recursive_optimized_reasonable_time(self):
        """Test Recursive Optimized completes in reasonable time"""
        solver = FourPegSolver(10)
        result = solver.solve_recursive_optimized()
        # Should complete in under 1 second
        assert result.time_taken_ms < 1000
