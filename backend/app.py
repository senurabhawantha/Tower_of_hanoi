"""
Tower of Hanoi - Flask API Backend
Main application entry point
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from game import GameController, ValidationError, GameError
from database import (
    DatabaseManager,
    PlayerRepository,
    GameSessionRepository,
    AlgorithmResultRepository,
    UserResponseRepository,
    MoveHistoryRepository
)
from config import Config

app = Flask(__name__)
CORS(app)

# Global game controller instance
game_controller = GameController()

# Database manager
db_manager = DatabaseManager()


def get_db_connection():
    """Get database connection (creates new if needed)"""
    if not db_manager.connection or not db_manager.connection.is_connected():
        db_manager.connect()
    return db_manager


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Tower of Hanoi API is running"})


@app.route('/api/game/new', methods=['POST'])
def create_new_game():
    """
    Create a new game session
    Request body: { "player_name": string, "peg_count": int }
    Implements requirements 4.1.1 (random disk) and 4.1.2 (user selects pegs)
    """
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        player_name = data.get('player_name', '').strip()
        peg_count = data.get('peg_count')
        
        # Validate inputs
        if not player_name:
            return jsonify({"error": "Player name is required"}), 400
        
        if peg_count is None:
            return jsonify({"error": "Number of pegs is required"}), 400
        
        try:
            peg_count = int(peg_count)
        except (ValueError, TypeError):
            return jsonify({"error": "Peg count must be a number"}), 400
        
        # Create new game (disk count is randomly generated - requirement 4.1.1)
        game_state = game_controller.create_new_game(player_name, peg_count)
        
        # Try to save to database
        try:
            db = get_db_connection()
            player_repo = PlayerRepository(db)
            session_repo = GameSessionRepository(db)
            
            player_id = player_repo.get_or_create_player(player_name)
            session_id = session_repo.create_session(
                player_id, 
                game_state.disk_count, 
                game_state.peg_count
            )
            
            game_state.player_id = player_id
            game_state.session_id = session_id
        except Exception as db_error:
            print(f"Database error (continuing without DB): {db_error}")
        
        return jsonify({
            "success": True,
            "message": f"New game created with {game_state.disk_count} disks and {game_state.peg_count} pegs",
            "game": game_controller.get_game_state()
        })
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    """Get current game state"""
    state = game_controller.get_game_state()
    if not state:
        return jsonify({"error": "No active game. Please start a new game."}), 404
    return jsonify({"success": True, "game": state})


@app.route('/api/game/move', methods=['POST'])
def make_move():
    """
    Make a move in the game
    Request body: { "from_peg": int, "to_peg": int }
    """
    try:
        # Check if there's an active game first
        if not game_controller.current_game:
            return jsonify({"error": "No active game. Please start a new game first."}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        from_peg = data.get('from_peg')
        to_peg = data.get('to_peg')
        
        print(f"Move request: from_peg={from_peg}, to_peg={to_peg}")  # Debug log
        
        if from_peg is None or to_peg is None:
            return jsonify({"error": "from_peg and to_peg are required"}), 400
        
        try:
            from_peg = int(from_peg)
            to_peg = int(to_peg)
        except (ValueError, TypeError):
            return jsonify({"error": "Peg indices must be numbers"}), 400
        
        # Get the disk being moved before making the move
        game_state = game_controller.current_game
        disk_moved = None
        if game_state and game_state.pegs[from_peg]:
            disk_moved = game_state.pegs[from_peg][-1]
        
        result = game_controller.make_move(from_peg, to_peg)
        
        # Save move to database
        try:
            if game_state and game_state.session_id and disk_moved is not None:
                db = get_db_connection()
                move_repo = MoveHistoryRepository(db)
                move_repo.save_user_move(
                    game_state.session_id,
                    game_state.move_count,
                    disk_moved,
                    from_peg,
                    to_peg
                )
        except Exception as db_error:
            print(f"Database error saving move: {db_error}")
        
        return jsonify({"success": True, **result})
        
    except GameError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/game/solve', methods=['POST'])
def solve_puzzle():
    """
    Solve the puzzle using algorithms
    Implements requirements 4.1.3, 4.1.4, and 4.1.6
    Returns algorithm results with timing information
    """
    try:
        results = game_controller.solve_with_algorithms()
        
        # Save results to database
        try:
            game_state = game_controller.current_game
            if game_state and game_state.session_id:
                db = get_db_connection()
                result_repo = AlgorithmResultRepository(db)
                
                for result in results:
                    algo_id = result_repo.get_algorithm_id(result.algorithm_name)
                    if algo_id:
                        result_repo.save_result(
                            game_state.session_id,
                            algo_id,
                            result.move_count,
                            result.time_taken_ms
                        )
        except Exception as db_error:
            print(f"Database error saving results: {db_error}")
        
        return jsonify({
            "success": True,
            "results": [
                {
                    "algorithm_name": r.algorithm_name,
                    "move_count": r.move_count,
                    "time_taken_ms": round(r.time_taken_ms, 6),
                    "moves": r.moves[:50]  # Limit moves returned for large solutions
                }
                for r in results
            ]
        })
        
    except GameError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/game/answer', methods=['POST'])
def submit_answer():
    """
    Submit user's answer to a question
    Request body: { "question_type": string, "user_answer": string }
    Implements requirement 4.1.5: save person's name along with correct response
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        question_type = data.get('question_type', '').strip()
        user_answer = data.get('user_answer', '').strip()
        
        if not question_type or not user_answer:
            return jsonify({"error": "question_type and user_answer are required"}), 400
        
        result = game_controller.check_user_answer(question_type, user_answer)
        
        # Save response to database (requirement 4.1.5)
        try:
            game_state = game_controller.current_game
            if game_state and game_state.session_id:
                db = get_db_connection()
                response_repo = UserResponseRepository(db)
                response_repo.save_response(
                    game_state.session_id,
                    result['question_type'],
                    result['user_answer'],
                    result['correct_answer'],
                    result['is_correct']
                )
        except Exception as db_error:
            print(f"Database error saving response: {db_error}")
        
        return jsonify({"success": True, **result})
        
    except GameError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    """Reset current game to initial state"""
    try:
        game_controller.reset_game()
        return jsonify({
            "success": True,
            "message": "Game reset to initial state",
            "game": game_controller.get_game_state()
        })
    except GameError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/game/hint', methods=['GET'])
def get_hint():
    """Get next optimal move as a hint"""
    try:
        game_state = game_controller.current_game
        if not game_state:
            return jsonify({"error": "No active game"}), 404
        
        # Solve the puzzle and get the first move
        results = game_controller.solve_with_algorithms()
        
        if results and results[0].moves:
            first_move = results[0].moves[0]
            return jsonify({
                "success": True,
                "hint": {
                    "disk": first_move[0],
                    "from_peg": first_move[1],
                    "to_peg": first_move[2],
                    "message": f"Move disk {first_move[0]} from peg {first_move[1] + 1} to peg {first_move[2] + 1}"
                }
            })
        
        return jsonify({"success": True, "hint": None, "message": "No moves available"})
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get player leaderboard"""
    try:
        db = get_db_connection()
        query = """
            SELECT 
                p.player_name,
                COUNT(DISTINCT gs.session_id) as games_played,
                SUM(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) as correct_answers,
                COUNT(ur.response_id) as total_questions
            FROM players p
            LEFT JOIN game_sessions gs ON p.player_id = gs.player_id
            LEFT JOIN user_responses ur ON gs.session_id = ur.session_id
            GROUP BY p.player_id, p.player_name
            ORDER BY correct_answers DESC, games_played DESC
            LIMIT 10
        """
        results = db.fetch_all(query)
        return jsonify({"success": True, "leaderboard": results})
    except Exception as e:
        return jsonify({"error": f"Could not fetch leaderboard: {str(e)}"}), 500


if __name__ == '__main__':
    # Initialize database tables on startup
    print("Initializing database...")
    db_manager.initialize_database()
    print("Starting Flask server...")
    app.run(debug=True, port=5000)
