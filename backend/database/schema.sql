-- Tower of Hanoi Database Schema
-- Normalized DB Table Structure

-- Drop existing tables if they exist
DROP DATABASE IF EXISTS tower_of_hanoi;
CREATE DATABASE tower_of_hanoi;
USE tower_of_hanoi;

-- Table: players
-- Stores player information (1NF, 2NF, 3NF compliant)
CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Table: algorithms
-- Stores available algorithm types (1NF, 2NF, 3NF compliant)
CREATE TABLE algorithms (
    algorithm_id INT AUTO_INCREMENT PRIMARY KEY,
    algorithm_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    peg_count INT NOT NULL CHECK (peg_count IN (3, 4)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Insert default algorithms
INSERT INTO algorithms (algorithm_name, description, peg_count) VALUES
('Recursive_3Peg', 'Classic recursive solution for 3 pegs Tower of Hanoi', 3),
('Iterative_3Peg', 'Iterative solution using stack simulation for 3 pegs', 3),
('FrameStewart_4Peg', 'Frame-Stewart algorithm for 4 pegs Tower of Hanoi', 4),
('Recursive_4Peg', 'Recursive solution optimized for 4 pegs', 4);

-- Table: game_sessions
-- Stores each game session information (1NF, 2NF, 3NF compliant)
CREATE TABLE game_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    disk_count INT NOT NULL CHECK (disk_count BETWEEN 5 AND 10),
    peg_count INT NOT NULL CHECK (peg_count IN (3, 4)),
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table: algorithm_results
-- Stores algorithm execution results for each session (1NF, 2NF, 3NF compliant)
CREATE TABLE algorithm_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    algorithm_id INT NOT NULL,
    move_count INT NOT NULL,
    time_taken_ms DECIMAL(15, 6) NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (algorithm_id) REFERENCES algorithms(algorithm_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table: user_responses
-- Stores user's answers/responses during the game (1NF, 2NF, 3NF compliant)
CREATE TABLE user_responses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    user_answer VARCHAR(255) NOT NULL,
    correct_answer VARCHAR(255) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    response_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table: move_history
-- Stores the sequence of moves made during solving (1NF, 2NF, 3NF compliant)
-- Supports both algorithm moves (result_id) and user moves (session_id)
CREATE TABLE move_history (
    move_id INT AUTO_INCREMENT PRIMARY KEY,
    result_id INT NULL,
    session_id INT NULL,
    move_number INT NOT NULL,
    from_peg INT NOT NULL,
    to_peg INT NOT NULL,
    disk_number INT NOT NULL,
    is_user_move BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_id) REFERENCES algorithm_results(result_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create indexes for better query performance
CREATE INDEX idx_sessions_player ON game_sessions(player_id);
CREATE INDEX idx_results_session ON algorithm_results(session_id);
CREATE INDEX idx_responses_session ON user_responses(session_id);
CREATE INDEX idx_moves_result ON move_history(result_id);
CREATE INDEX idx_moves_session ON move_history(session_id);

-- View: player_statistics
-- Aggregated view for player performance
CREATE VIEW player_statistics AS
SELECT 
    p.player_id,
    p.player_name,
    COUNT(DISTINCT gs.session_id) as total_games,
    SUM(CASE WHEN ur.is_correct = TRUE THEN 1 ELSE 0 END) as correct_answers,
    COUNT(ur.response_id) as total_questions,
    AVG(ar.time_taken_ms) as avg_algorithm_time_ms
FROM players p
LEFT JOIN game_sessions gs ON p.player_id = gs.player_id
LEFT JOIN user_responses ur ON gs.session_id = ur.session_id
LEFT JOIN algorithm_results ar ON gs.session_id = ar.session_id
GROUP BY p.player_id, p.player_name;
