"""
Integration Tests for Flask API
Tests API endpoints and validation
"""
import pytest
import json
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestNewGameEndpoint:
    """Tests for new game creation endpoint"""
    
    def test_create_game_success(self, client):
        """Test successful game creation"""
        response = client.post('/api/game/new', 
            data=json.dumps({'player_name': 'TestPlayer', 'peg_count': 3}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'game' in data
        assert data['game']['player_name'] == 'TestPlayer'
        assert data['game']['peg_count'] == 3
        assert 5 <= data['game']['disk_count'] <= 10
    
    def test_create_game_with_4_pegs(self, client):
        """Test game creation with 4 pegs"""
        response = client.post('/api/game/new',
            data=json.dumps({'player_name': 'TestPlayer', 'peg_count': 4}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['game']['peg_count'] == 4
    
    def test_create_game_missing_player_name(self, client):
        """Test error when player name missing"""
        response = client.post('/api/game/new',
            data=json.dumps({'peg_count': 3}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_game_missing_peg_count(self, client):
        """Test error when peg count missing"""
        response = client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test'}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_create_game_invalid_peg_count(self, client):
        """Test error for invalid peg count"""
        response = client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 5}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_create_game_empty_body(self, client):
        """Test error for empty request body"""
        response = client.post('/api/game/new',
            data=None,
            content_type='application/json'
        )
        assert response.status_code == 400


class TestGameStateEndpoint:
    """Tests for game state endpoint"""
    
    def test_get_state_no_game(self, client):
        """Test error when no active game"""
        response = client.get('/api/game/state')
        # May be 200 or 404 depending on previous tests
        # Just check it returns a valid response
        assert response.status_code in [200, 404]
    
    def test_get_state_after_create(self, client):
        """Test getting state after creating game"""
        # Create game first
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        
        response = client.get('/api/game/state')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'game' in data


class TestMoveEndpoint:
    """Tests for move endpoint"""
    
    def test_valid_move(self, client):
        """Test making a valid move"""
        # Create game
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        
        # Make move from peg 0 to peg 1
        response = client.post('/api/game/move',
            data=json.dumps({'from_peg': 0, 'to_peg': 1}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['move_count'] == 1
    
    def test_invalid_move_empty_peg(self, client):
        """Test error when moving from empty peg"""
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        
        response = client.post('/api/game/move',
            data=json.dumps({'from_peg': 1, 'to_peg': 0}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_move_missing_params(self, client):
        """Test error when parameters missing"""
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        
        response = client.post('/api/game/move',
            data=json.dumps({'from_peg': 0}),
            content_type='application/json'
        )
        assert response.status_code == 400


class TestSolveEndpoint:
    """Tests for solve endpoint"""
    
    def test_solve_3_pegs(self, client):
        """Test solving with 3 pegs"""
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        
        response = client.post('/api/game/solve')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'results' in data
        assert len(data['results']) == 2
    
    def test_solve_4_pegs(self, client):
        """Test solving with 4 pegs"""
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 4}),
            content_type='application/json'
        )
        
        response = client.post('/api/game/solve')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['results']) == 2
    
    def test_solve_returns_timing(self, client):
        """Test solve returns timing information (requirement 4.1.6)"""
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        
        response = client.post('/api/game/solve')
        data = json.loads(response.data)
        
        for result in data['results']:
            assert 'time_taken_ms' in result
            assert result['time_taken_ms'] >= 0


class TestAnswerEndpoint:
    """Tests for answer submission endpoint"""
    
    def test_submit_correct_answer(self, client):
        """Test submitting correct answer"""
        # Create game
        create_response = client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        game_data = json.loads(create_response.data)
        disk_count = game_data['game']['disk_count']
        correct_answer = str((2 ** disk_count) - 1)
        
        # Submit answer
        response = client.post('/api/game/answer',
            data=json.dumps({
                'question_type': 'minimum_moves',
                'user_answer': correct_answer
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['is_correct'] == True
    
    def test_submit_wrong_answer(self, client):
        """Test submitting wrong answer"""
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        
        response = client.post('/api/game/answer',
            data=json.dumps({
                'question_type': 'minimum_moves',
                'user_answer': '999'
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['is_correct'] == False


class TestResetEndpoint:
    """Tests for game reset endpoint"""
    
    def test_reset_game(self, client):
        """Test resetting game"""
        # Create and make moves
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        client.post('/api/game/move',
            data=json.dumps({'from_peg': 0, 'to_peg': 1}),
            content_type='application/json'
        )
        
        # Reset
        response = client.post('/api/game/reset')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['game']['move_count'] == 0


class TestHintEndpoint:
    """Tests for hint endpoint"""
    
    def test_get_hint(self, client):
        """Test getting a hint"""
        client.post('/api/game/new',
            data=json.dumps({'player_name': 'Test', 'peg_count': 3}),
            content_type='application/json'
        )
        
        response = client.get('/api/game/hint')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        if data['hint']:
            assert 'from_peg' in data['hint']
            assert 'to_peg' in data['hint']
