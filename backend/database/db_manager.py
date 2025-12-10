"""
Database connection and operations for Tower of Hanoi
"""
import mysql.connector
from mysql.connector import Error
from config import Config
from typing import Optional, List, Dict, Any
from datetime import datetime
import os


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.connection = None
        
    def connect(self) -> bool:
        """
        Establish database connection
        Returns: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
            return self.connection.is_connected()
        except Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """
        Initialize database and create tables if they don't exist
        Returns: True if successful, False otherwise
        """
        try:
            # First connect without database to create it if needed
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            cursor = conn.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
            cursor.execute(f"USE {Config.DB_NAME}")
            
            # Create tables
            tables = self._get_table_definitions()
            for table_name, table_sql in tables.items():
                cursor.execute(table_sql)
                print(f"Table '{table_name}' checked/created.")
            
            # Insert default algorithms if not exist
            cursor.execute("""
                INSERT IGNORE INTO algorithms (algorithm_id, algorithm_name, description, peg_count) VALUES
                (1, 'Recursive', 'Classic recursive Tower of Hanoi solution', 3),
                (2, 'Iterative', 'Iterative solution using stack simulation', 3),
                (3, 'Frame-Stewart', 'Optimal solution for 4 pegs using Frame-Stewart algorithm', 4),
                (4, 'Recursive Optimized', 'Dynamic programming optimized recursive solution for 4 pegs', 4)
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("Database initialized successfully!")
            return True
            
        except Error as e:
            print(f"Database initialization error: {e}")
            return False
    
    def _get_table_definitions(self) -> Dict[str, str]:
        """Return SQL definitions for all tables"""
        return {
            'players': """
                CREATE TABLE IF NOT EXISTS players (
                    player_id INT AUTO_INCREMENT PRIMARY KEY,
                    player_name VARCHAR(100) NOT NULL,
                    email VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_player_name (player_name)
                )
            """,
            'algorithms': """
                CREATE TABLE IF NOT EXISTS algorithms (
                    algorithm_id INT AUTO_INCREMENT PRIMARY KEY,
                    algorithm_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    peg_count INT DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_algorithm_name (algorithm_name)
                )
            """,
            'game_sessions': """
                CREATE TABLE IF NOT EXISTS game_sessions (
                    session_id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT,
                    num_disks INT NOT NULL,
                    num_pegs INT NOT NULL,
                    algorithm_id INT,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NULL,
                    is_completed BOOLEAN DEFAULT FALSE,
                    total_moves INT DEFAULT 0,
                    optimal_moves INT,
                    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE SET NULL,
                    FOREIGN KEY (algorithm_id) REFERENCES algorithms(algorithm_id) ON DELETE SET NULL,
                    INDEX idx_player_id (player_id),
                    INDEX idx_algorithm_id (algorithm_id),
                    INDEX idx_start_time (start_time)
                )
            """,
            'algorithm_results': """
                CREATE TABLE IF NOT EXISTS algorithm_results (
                    result_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    algorithm_id INT NOT NULL,
                    time_taken_ms DECIMAL(15, 6) NOT NULL,
                    moves_count INT NOT NULL,
                    memory_used_bytes BIGINT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id) ON DELETE CASCADE,
                    FOREIGN KEY (algorithm_id) REFERENCES algorithms(algorithm_id) ON DELETE CASCADE,
                    INDEX idx_session_id (session_id),
                    INDEX idx_algorithm_id (algorithm_id)
                )
            """,
            'user_responses': """
                CREATE TABLE IF NOT EXISTS user_responses (
                    response_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    question_type VARCHAR(50) NOT NULL,
                    user_answer TEXT NOT NULL,
                    correct_answer TEXT,
                    is_correct BOOLEAN,
                    response_time_ms INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id) ON DELETE CASCADE,
                    INDEX idx_session_id (session_id),
                    INDEX idx_question_type (question_type)
                )
            """,
            'move_history': """
                CREATE TABLE IF NOT EXISTS move_history (
                    move_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    move_number INT NOT NULL,
                    disk_number INT NOT NULL,
                    from_peg INT NOT NULL,
                    to_peg INT NOT NULL,
                    is_user_move BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id) ON DELETE CASCADE,
                    INDEX idx_session_id (session_id),
                    INDEX idx_move_number (move_number)
                )
            """
        }
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[int]:
        """
        Execute INSERT/UPDATE/DELETE query
        Returns: Last inserted ID or affected rows count
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            print(f"Query execution error: {e}")
            return None
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Fetch single record from database"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Fetch error: {e}")
            return None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """Fetch all records from database"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Fetch error: {e}")
            return []


class PlayerRepository:
    """Repository for player-related database operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_player(self, name: str, email: str = None) -> Optional[int]:
        """
        Create a new player and save to database
        Returns: player_id if successful, None otherwise
        """
        query = "INSERT INTO players (player_name, email) VALUES (%s, %s)"
        return self.db.execute_query(query, (name, email))
    
    def get_player_by_id(self, player_id: int) -> Optional[Dict]:
        """Get player by ID"""
        query = "SELECT * FROM players WHERE player_id = %s"
        return self.db.fetch_one(query, (player_id,))
    
    def get_player_by_name(self, name: str) -> Optional[Dict]:
        """Get player by name"""
        query = "SELECT * FROM players WHERE player_name = %s"
        return self.db.fetch_one(query, (name,))
    
    def get_or_create_player(self, name: str, email: str = None) -> int:
        """Get existing player or create new one"""
        player = self.get_player_by_name(name)
        if player:
            return player['player_id']
        return self.create_player(name, email)


class GameSessionRepository:
    """Repository for game session operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_session(self, player_id: int, disk_count: int, peg_count: int) -> Optional[int]:
        """Create a new game session"""
        query = """
            INSERT INTO game_sessions (player_id, disk_count, peg_count) 
            VALUES (%s, %s, %s)
        """
        return self.db.execute_query(query, (player_id, disk_count, peg_count))
    
    def complete_session(self, session_id: int, total_moves: int = 0) -> bool:
        """Mark session as completed"""
        query = """
            UPDATE game_sessions 
            SET is_completed = TRUE, session_end = NOW()
            WHERE session_id = %s
        """
        return self.db.execute_query(query, (session_id,)) is not None
    
    def get_session(self, session_id: int) -> Optional[Dict]:
        """Get session details"""
        query = "SELECT * FROM game_sessions WHERE session_id = %s"
        return self.db.fetch_one(query, (session_id,))


class AlgorithmResultRepository:
    """Repository for algorithm results"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def save_result(self, session_id: int, algorithm_id: int, 
                    move_count: int, time_taken_ms: float) -> Optional[int]:
        """
        Save algorithm execution result with time taken
        This implements requirement 4.1.6: record the time taken for each algorithm
        """
        query = """
            INSERT INTO algorithm_results 
            (session_id, algorithm_id, move_count, time_taken_ms) 
            VALUES (%s, %s, %s, %s)
        """
        return self.db.execute_query(query, (session_id, algorithm_id, move_count, time_taken_ms))
    
    def get_algorithm_id(self, algorithm_name: str) -> Optional[int]:
        """Get algorithm ID by name"""
        query = "SELECT algorithm_id FROM algorithms WHERE algorithm_name = %s"
        result = self.db.fetch_one(query, (algorithm_name,))
        return result['algorithm_id'] if result else None
    
    def get_session_results(self, session_id: int) -> List[Dict]:
        """Get all algorithm results for a session"""
        query = """
            SELECT ar.*, a.algorithm_name, a.description 
            FROM algorithm_results ar
            JOIN algorithms a ON ar.algorithm_id = a.algorithm_id
            WHERE ar.session_id = %s
            ORDER BY ar.executed_at
        """
        return self.db.fetch_all(query, (session_id,))


class UserResponseRepository:
    """Repository for user responses"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def save_response(self, session_id: int, question_type: str,
                      user_answer: str, correct_answer: str, 
                      is_correct: bool) -> Optional[int]:
        """
        Save user's response to database
        This implements requirement 4.1.5: save person's name along with correct response
        """
        query = """
            INSERT INTO user_responses 
            (session_id, question_type, user_answer, correct_answer, is_correct) 
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (session_id, question_type, 
                                              user_answer, correct_answer, is_correct))
    
    def get_session_responses(self, session_id: int) -> List[Dict]:
        """Get all responses for a session"""
        query = "SELECT * FROM user_responses WHERE session_id = %s"
        return self.db.fetch_all(query, (session_id,))
    
    def get_player_correct_responses(self, player_id: int) -> List[Dict]:
        """Get all correct responses for a player"""
        query = """
            SELECT ur.*, gs.disk_count, gs.peg_count, p.player_name
            FROM user_responses ur
            JOIN game_sessions gs ON ur.session_id = gs.session_id
            JOIN players p ON gs.player_id = p.player_id
            WHERE gs.player_id = %s AND ur.is_correct = TRUE
        """
        return self.db.fetch_all(query, (player_id,))


class MoveHistoryRepository:
    """Repository for move history operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def save_algorithm_move(self, result_id: int, move_number: int, 
                            disk_number: int, from_peg: int, to_peg: int) -> Optional[int]:
        """Save an algorithm move to history"""
        query = """
            INSERT INTO move_history 
            (result_id, move_number, disk_number, from_peg, to_peg, is_user_move) 
            VALUES (%s, %s, %s, %s, %s, FALSE)
        """
        return self.db.execute_query(query, (result_id, move_number, 
                                              disk_number, from_peg, to_peg))
    
    def save_user_move(self, session_id: int, move_number: int, 
                       disk_number: int, from_peg: int, to_peg: int) -> Optional[int]:
        """Save a user move to history"""
        query = """
            INSERT INTO move_history 
            (session_id, move_number, disk_number, from_peg, to_peg, is_user_move) 
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """
        return self.db.execute_query(query, (session_id, move_number, 
                                              disk_number, from_peg, to_peg))
    
    def get_result_moves(self, result_id: int) -> List[Dict]:
        """Get all moves for an algorithm result"""
        query = """
            SELECT * FROM move_history 
            WHERE result_id = %s 
            ORDER BY move_number
        """
        return self.db.fetch_all(query, (result_id,))
    
    def get_session_moves(self, session_id: int) -> List[Dict]:
        """Get all user moves for a session"""
        query = """
            SELECT * FROM move_history 
            WHERE session_id = %s AND is_user_move = TRUE
            ORDER BY move_number
        """
        return self.db.fetch_all(query, (session_id,))
    
    def get_last_move(self, session_id: int) -> Optional[Dict]:
        """Get the last user move for a session"""
        query = """
            SELECT * FROM move_history 
            WHERE session_id = %s AND is_user_move = TRUE
            ORDER BY move_number DESC 
            LIMIT 1
        """
        return self.db.fetch_one(query, (session_id,))
    
    def get_move_count(self, session_id: int) -> int:
        """Get total number of user moves for a session"""
        query = "SELECT COUNT(*) as count FROM move_history WHERE session_id = %s AND is_user_move = TRUE"
        result = self.db.fetch_one(query, (session_id,))
        return result['count'] if result else 0
