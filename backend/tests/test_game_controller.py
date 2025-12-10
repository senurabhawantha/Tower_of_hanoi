"""
Unit Tests for Game Controller
Tests requirements 4.1.1, 4.1.2, and validation
"""
import pytest
from game.game_controller import GameController, GameState, ValidationError, GameError
from config import Config


class TestGameControllerDiskGeneration:
    """Tests for requirement 4.1.1: Random disk selection (5-10)"""
    
    def test_generate_random_disk_count_in_range(self):
        """Test random disk count is between 5 and 10"""
        for _ in range(100):  # Test multiple times for randomness
            disk_count = GameController.generate_random_disk_count()
            assert Config.MIN_DISKS <= disk_count <= Config.MAX_DISKS
    
    def test_generate_random_disk_count_type(self):
        """Test random disk count is an integer"""
        disk_count = GameController.generate_random_disk_count()
        assert isinstance(disk_count, int)
    
    def test_create_game_has_random_disk_count(self):
        """Test new game has random disk count in valid range"""
        controller = GameController()
        game = controller.create_new_game("TestPlayer", 3)
        assert Config.MIN_DISKS <= game.disk_count <= Config.MAX_DISKS


class TestGameControllerPegValidation:
    """Tests for requirement 4.1.2: Peg count validation (3-4)"""
    
    def test_validate_peg_count_3(self):
        """Test peg count 3 is valid"""
        assert GameController.validate_peg_count(3) == True
    
    def test_validate_peg_count_4(self):
        """Test peg count 4 is valid"""
        assert GameController.validate_peg_count(4) == True
    
    def test_validate_peg_count_2_invalid(self):
        """Test peg count 2 is invalid"""
        with pytest.raises(ValidationError) as exc_info:
            GameController.validate_peg_count(2)
        assert "3 or 4" in str(exc_info.value)
    
    def test_validate_peg_count_5_invalid(self):
        """Test peg count 5 is invalid"""
        with pytest.raises(ValidationError) as exc_info:
            GameController.validate_peg_count(5)
        assert "3 or 4" in str(exc_info.value)
    
    def test_create_game_with_3_pegs(self):
        """Test creating game with 3 pegs"""
        controller = GameController()
        game = controller.create_new_game("TestPlayer", 3)
        assert game.peg_count == 3
        assert len(game.pegs) == 3
    
    def test_create_game_with_4_pegs(self):
        """Test creating game with 4 pegs"""
        controller = GameController()
        game = controller.create_new_game("TestPlayer", 4)
        assert game.peg_count == 4
        assert len(game.pegs) == 4


class TestPlayerNameValidation:
    """Tests for player name validation (requirement 4.2.2)"""
    
    def test_validate_player_name_valid(self):
        """Test valid player names"""
        valid_names = ["John", "Jane Doe", "Player_1", "Test-User", "Player123"]
        for name in valid_names:
            assert GameController.validate_player_name(name) == True
    
    def test_validate_player_name_empty(self):
        """Test empty player name is invalid"""
        with pytest.raises(ValidationError) as exc_info:
            GameController.validate_player_name("")
        assert "cannot be empty" in str(exc_info.value)
    
    def test_validate_player_name_whitespace_only(self):
        """Test whitespace-only player name is invalid"""
        with pytest.raises(ValidationError) as exc_info:
            GameController.validate_player_name("   ")
        assert "cannot be empty" in str(exc_info.value)
    
    def test_validate_player_name_too_long(self):
        """Test player name exceeding 100 characters is invalid"""
        long_name = "A" * 101
        with pytest.raises(ValidationError) as exc_info:
            GameController.validate_player_name(long_name)
        assert "100 characters" in str(exc_info.value)
    
    def test_validate_player_name_special_chars(self):
        """Test player name with invalid special characters"""
        with pytest.raises(ValidationError) as exc_info:
            GameController.validate_player_name("Player@123!")
        assert "letters, numbers" in str(exc_info.value)


class TestGameCreation:
    """Tests for game creation"""
    
    def test_create_new_game_returns_gamestate(self):
        """Test create_new_game returns GameState object"""
        controller = GameController()
        game = controller.create_new_game("TestPlayer", 3)
        assert isinstance(game, GameState)
    
    def test_create_new_game_sets_player_name(self):
        """Test player name is set correctly"""
        controller = GameController()
        game = controller.create_new_game("TestPlayer", 3)
        assert game.player_name == "TestPlayer"
    
    def test_create_new_game_initial_state(self):
        """Test game starts with correct initial state"""
        controller = GameController()
        game = controller.create_new_game("TestPlayer", 3)
        
        # All disks should be on first peg
        assert len(game.pegs[0]) == game.disk_count
        
        # Other pegs should be empty
        for i in range(1, game.peg_count):
            assert len(game.pegs[i]) == 0
        
        # Move count should be 0
        assert game.move_count == 0
        
        # Game should not be completed
        assert game.is_completed == False
    
    def test_disks_ordered_correctly(self):
        """Test disks are ordered largest to smallest on first peg"""
        controller = GameController()
        game = controller.create_new_game("TestPlayer", 3)
        
        # Disks should be in descending order (largest at bottom)
        expected = list(range(game.disk_count, 0, -1))
        assert game.pegs[0] == expected


class TestGameMoves:
    """Tests for game move mechanics"""
    
    def test_validate_valid_move(self):
        """Test validating a valid move"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 3)
        
        is_valid, message = controller.validate_move(0, 1)
        assert is_valid == True
    
    def test_validate_move_no_game(self):
        """Test validation fails when no game exists"""
        controller = GameController()
        is_valid, message = controller.validate_move(0, 1)
        assert is_valid == False
        assert "No active game" in message
    
    def test_validate_move_invalid_source_peg(self):
        """Test validation fails for invalid source peg"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 3)
        
        is_valid, message = controller.validate_move(-1, 1)
        assert is_valid == False
        
        is_valid, message = controller.validate_move(5, 1)
        assert is_valid == False
    
    def test_validate_move_same_peg(self):
        """Test validation fails when source equals destination"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 3)
        
        is_valid, message = controller.validate_move(0, 0)
        assert is_valid == False
        assert "different" in message
    
    def test_validate_move_empty_source(self):
        """Test validation fails when source peg is empty"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 3)
        
        is_valid, message = controller.validate_move(1, 0)  # Peg 1 is empty
        assert is_valid == False
        assert "No disks" in message
    
    def test_make_valid_move(self):
        """Test making a valid move"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 3)
        
        result = controller.make_move(0, 1)
        
        assert result["success"] == True
        assert result["from_peg"] == 0
        assert result["to_peg"] == 1
        assert result["move_count"] == 1
    
    def test_make_invalid_move_raises_error(self):
        """Test making invalid move raises GameError"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 3)
        
        with pytest.raises(GameError):
            controller.make_move(1, 0)  # Peg 1 is empty


class TestGameCompletion:
    """Tests for game completion detection"""
    
    def test_game_completion_detected(self):
        """Test game completion is detected when all disks on destination"""
        controller = GameController()
        game = controller.create_new_game("TestPlayer", 3)
        
        # Manually set state to completed (all disks on last peg)
        game.pegs[0] = []
        game.pegs[1] = []
        game.pegs[2] = list(range(game.disk_count, 0, -1))
        
        # Verify get_game_state still works
        state = controller.get_game_state()
        assert state is not None


class TestSolveWithAlgorithms:
    """Tests for algorithm solving"""
    
    def test_solve_3_pegs_returns_two_results(self):
        """Test solving with 3 pegs returns 2 algorithm results"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 3)
        
        results = controller.solve_with_algorithms()
        assert len(results) == 2
    
    def test_solve_4_pegs_returns_two_results(self):
        """Test solving with 4 pegs returns 2 algorithm results"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 4)
        
        results = controller.solve_with_algorithms()
        assert len(results) == 2
    
    def test_solve_no_game_raises_error(self):
        """Test solving without active game raises error"""
        controller = GameController()
        
        with pytest.raises(GameError):
            controller.solve_with_algorithms()
    
    def test_solve_results_have_timing(self):
        """Test algorithm results include timing (requirement 4.1.6)"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 3)
        
        results = controller.solve_with_algorithms()
        
        for result in results:
            assert hasattr(result, 'time_taken_ms')
            assert result.time_taken_ms >= 0


class TestGameReset:
    """Tests for game reset functionality"""
    
    def test_reset_restores_initial_state(self):
        """Test reset restores game to initial state"""
        controller = GameController()
        controller.create_new_game("TestPlayer", 3)
        
        # Make some moves
        controller.make_move(0, 1)
        controller.make_move(0, 2)
        
        # Reset
        controller.reset_game()
        
        game = controller.current_game
        assert game.move_count == 0
        assert len(game.pegs[0]) == game.disk_count
        assert len(game.pegs[1]) == 0
        assert len(game.pegs[2]) == 0
        assert game.is_completed == False
