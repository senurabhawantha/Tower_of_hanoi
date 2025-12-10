import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Confetti from 'react-confetti';
import axios from 'axios';



const API_BASE = 'http://localhost:5000/api';

// Disk colors - vibrant gaming palette
const DISK_COLORS = [
  'linear-gradient(135deg, #e94560, #ff6b6b)',
  'linear-gradient(135deg, #00d4ff, #0099cc)',
  'linear-gradient(135deg, #ffd93d, #ffcc00)',
  'linear-gradient(135deg, #44ff88, #22cc66)',
  'linear-gradient(135deg, #ff6b9d, #ff4777)',
  'linear-gradient(135deg, #9b59b6, #8e44ad)',
  'linear-gradient(135deg, #e67e22, #d35400)',
  'linear-gradient(135deg, #1abc9c, #16a085)',
  'linear-gradient(135deg, #3498db, #2980b9)',
  'linear-gradient(135deg, #e74c3c, #c0392b)',
];

// Disk component with animation
const Disk = ({ size, totalDisks, onClick, isTopDisk }) => {
  const width = 40 + (size * 15);
  const colorIndex = (size - 1) % DISK_COLORS.length;
  
  return (
    <motion.div
      className={`disk ${isTopDisk ? 'top-disk' : ''}`}
      initial={{ scale: 0, y: -50 }}
      animate={{ scale: 1, y: 0 }}
      exit={{ scale: 0, y: -50 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      style={{
        width: `${width}px`,
        background: DISK_COLORS[colorIndex],
      }}
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <span style={{ 
        color: '#fff', 
        fontFamily: 'Orbitron', 
        fontSize: '0.8rem',
        fontWeight: 'bold',
        textShadow: '0 1px 2px rgba(0,0,0,0.5)'
      }}>
        {size}
      </span>
    </motion.div>
  );
};

// Peg component
const Peg = ({ pegs, pegIndex, onPegClick, selectedPeg, pegCount }) => {
  const disks = pegs[pegIndex] || [];
  const isSelected = selectedPeg === pegIndex;
  
  const pegLabels = pegCount === 3 
    ? ['SOURCE', 'AUXILIARY', 'DESTINATION']
    : ['SOURCE', 'AUX 1', 'AUX 2', 'DESTINATION'];
  
  return (
    <motion.div 
      className={`peg-container ${isSelected ? 'selected' : ''}`}
      onClick={() => onPegClick(pegIndex)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="peg-label">{pegLabels[pegIndex]}</div>
      <div className="peg-rod">
        <AnimatePresence>
          {disks.map((disk, index) => (
            <Disk 
              key={`disk-${disk}`}
              size={disk}
              totalDisks={Math.max(...pegs.flat(), 1)}
              isTopDisk={index === disks.length - 1}
            />
          ))}
        </AnimatePresence>
      </div>
      <div className="peg-base"></div>
    </motion.div>
  );
};

// Welcome Screen Component
const WelcomeScreen = ({ onStartGame }) => {
  const [playerName, setPlayerName] = useState('');
  const [pegCount, setPegCount] = useState(null);
  const [error, setError] = useState('');

  const handleStart = () => {
    if (!playerName.trim()) {
      setError('Please enter your name');
      return;
    }
    if (!pegCount) {
      setError('Please select number of pegs');
      return;
    }
    setError('');
    onStartGame(playerName.trim(), pegCount);
  };

  return (
    <div className="welcome-screen">
      <motion.div 
        className="welcome-card"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="form-group">
          <label className="form-label">Enter Your Name</label>
          <input
            type="text"
            className="form-input"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            placeholder="Your gaming name..."
            maxLength={50}
          />
        </div>
        
        <div className="form-group">
          <label className="form-label">Select Number of Pegs</label>
          <div className="peg-selection">
            <motion.button
              className={`peg-option ${pegCount === 3 ? 'selected' : ''}`}
              onClick={() => setPegCount(3)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              3 Pegs
            </motion.button>
            <motion.button
              className={`peg-option ${pegCount === 4 ? 'selected' : ''}`}
              onClick={() => setPegCount(4)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              4 Pegs
            </motion.button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <motion.button
          className="start-button"
          onClick={handleStart}
          disabled={!playerName.trim() || !pegCount}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          🎮 Start Game 🎮
        </motion.button>
      </motion.div>
    </div>
  );
};

// Algorithm Results Modal
const AlgorithmResultsModal = ({ results, onClose }) => {
  return (
    <motion.div 
      className="modal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div 
        className="modal-content"
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.5, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="modal-title">⚡ Algorithm Results ⚡</h2>
        
        {results.map((result, index) => (
          <div key={index} className="algorithm-result">
            <h3 className="algorithm-name">{result.algorithm_name}</h3>
            <div className="result-stats">
              <div className="stat-item">
                <div className="stat-label">Moves Required</div>
                <div className="stat-value">{result.move_count}</div>
              </div>
              <div className="stat-item">
                <div className="stat-label">Time Taken</div>
                <div className="stat-value">{result.time_taken_ms.toFixed(4)} ms</div>
              </div>
            </div>
          </div>
        ))}
        
        <button className="close-button" onClick={onClose}>
          Close
        </button>
      </motion.div>
    </motion.div>
  );
};

// Question Modal
const QuestionModal = ({ gameState, onClose, onSubmit }) => {
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!answer.trim()) return;
    
    try {
      const response = await axios.post(`${API_BASE}/game/answer`, {
        question_type: 'minimum_moves',
        user_answer: answer.trim()
      });
      
      setFeedback(response.data);
      setSubmitted(true);
      onSubmit(response.data);
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  };

  return (
    <motion.div 
      className="modal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <motion.div 
        className="modal-content"
        initial={{ scale: 0.5 }}
        animate={{ scale: 1 }}
      >
        <h2 className="modal-title">🎯 Challenge Question 🎯</h2>
        
        <p style={{ fontSize: '1.3rem', color: '#00d4ff', textAlign: 'center', marginBottom: '20px' }}>
          You completed the puzzle with <span style={{ color: '#ffd93d' }}>{gameState.disk_count}</span> disks 
          and <span style={{ color: '#ffd93d' }}>{gameState.peg_count}</span> pegs!
        </p>
        
        <p style={{ fontSize: '1.2rem', color: '#fff', textAlign: 'center' }}>
          What is the minimum number of moves required to solve this puzzle optimally?
        </p>
        
        <input
          type="number"
          className="question-input"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Enter your answer..."
          disabled={submitted}
        />
        
        {feedback && (
          <div className={`answer-feedback ${feedback.is_correct ? 'correct' : 'incorrect'}`}>
            {feedback.is_correct 
              ? '🎉 Correct! Well done!' 
              : `❌ Incorrect. The correct answer is ${feedback.correct_answer}`
            }
          </div>
        )}
        
        {!submitted ? (
          <motion.button
            className="start-button"
            onClick={handleSubmit}
            whileHover={{ scale: 1.02 }}
          >
            Submit Answer
          </motion.button>
        ) : (
          <motion.button
            className="close-button"
            onClick={onClose}
            whileHover={{ scale: 1.02 }}
          >
            Continue
          </motion.button>
        )}
      </motion.div>
    </motion.div>
  );
};

// Main App Component
function App() {
  const [gameState, setGameState] = useState(null);
  const [selectedPeg, setSelectedPeg] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [algorithmResults, setAlgorithmResults] = useState([]);
  const [showWinner, setShowWinner] = useState(false);
  const [showQuestion, setShowQuestion] = useState(false);

  const startGame = useCallback(async (playerName, pegCount) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE}/game/new`, {
        player_name: playerName,
        peg_count: pegCount
      });
      
      setGameState(response.data.game);
      setShowWinner(false);
      setShowQuestion(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start game');
    } finally {
      setLoading(false);
    }
  }, []);

  const handlePegClick = useCallback(async (pegIndex) => {
    if (!gameState || gameState.is_completed) return;
    
    if (selectedPeg === null) {
      // Select source peg (must have disks)
      if (gameState.pegs[pegIndex] && gameState.pegs[pegIndex].length > 0) {
        setSelectedPeg(pegIndex);
      }
    } else {
      // Make move
      if (selectedPeg !== pegIndex) {
        try {
          const response = await axios.post(`${API_BASE}/game/move`, {
            from_peg: selectedPeg,
            to_peg: pegIndex
          });
          
          setGameState(prev => ({
            ...prev,
            pegs: response.data.pegs,
            move_count: response.data.move_count,
            is_completed: response.data.is_completed
          }));
          
          if (response.data.is_completed) {
            setShowWinner(true);
            setTimeout(() => setShowQuestion(true), 2000);
          }
        } catch (err) {
          setError(err.response?.data?.error || 'Invalid move');
          setTimeout(() => setError(''), 2000);
        }
      }
      setSelectedPeg(null);
    }
  }, [gameState, selectedPeg]);

  const handleSolve = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/game/solve`);
      setAlgorithmResults(response.data.results);
      setShowResults(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to solve');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      const response = await axios.post(`${API_BASE}/game/reset`);
      setGameState(response.data.game);
      setSelectedPeg(null);
      setShowWinner(false);
      setShowQuestion(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to reset');
    }
  };

  const handleNewGame = () => {
    setGameState(null);
    setSelectedPeg(null);
    setShowWinner(false);
    setShowQuestion(false);
    setAlgorithmResults([]);
  };

  const handleHint = async () => {
    try {
      const response = await axios.get(`${API_BASE}/game/hint`);
      if (response.data.hint) {
        const { from_peg, to_peg } = response.data.hint;
        // Highlight hint pegs
        setSelectedPeg(from_peg);
        setTimeout(() => {
          handlePegClick(to_peg);
        }, 500);
      }
    } catch (err) {
      setError('Could not get hint');
    }
  };

  return (
    <div className="app-container">
      {showWinner && <Confetti recycle={false} numberOfPieces={500} />}
      
      <header className="game-header">
        <h1 className="game-title">TOWER OF HANOI</h1>
        <p className="game-subtitle">The Classic Puzzle Challenge</p>
      </header>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {!gameState ? (
        <WelcomeScreen onStartGame={startGame} />
      ) : (
        <div className="game-screen">
          <div className="game-info-bar">
            <div className="info-item">
              <div className="info-label">Player</div>
              <div className="info-value">{gameState.player_name}</div>
            </div>
            <div className="info-item">
              <div className="info-label">Disks</div>
              <div className="info-value">{gameState.disk_count}</div>
            </div>
            <div className="info-item">
              <div className="info-label">Pegs</div>
              <div className="info-value">{gameState.peg_count}</div>
            </div>
            <div className="info-item">
              <div className="info-label">Moves</div>
              <div className="info-value">{gameState.move_count}</div>
            </div>
            <div className="info-item">
              <div className="info-label">Minimum</div>
              <div className="info-value">{gameState.minimum_moves}</div>
            </div>
          </div>

          {showWinner && (
            <motion.div 
              className="winner-screen"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
            >
              <h2 className="winner-title">🏆 CONGRATULATIONS! 🏆</h2>
              <div className="winner-stats">
                You solved the puzzle in {gameState.move_count} moves!
                {gameState.move_count === gameState.minimum_moves && (
                  <div style={{ color: '#44ff88', marginTop: '10px' }}>
                    ⭐ PERFECT SCORE! ⭐
                  </div>
                )}
              </div>
            </motion.div>
          )}

          <div className="game-board">
            {Array.from({ length: gameState.peg_count }, (_, i) => (
              <Peg
                key={i}
                pegs={gameState.pegs}
                pegIndex={i}
                onPegClick={handlePegClick}
                selectedPeg={selectedPeg}
                pegCount={gameState.peg_count}
              />
            ))}
          </div>

          <div className="control-panel">
            <motion.button
              className="control-button btn-solve"
              onClick={handleSolve}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              🔬 Solve & Compare
            </motion.button>
            <motion.button
              className="control-button btn-hint"
              onClick={handleHint}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              💡 Get Hint
            </motion.button>
            <motion.button
              className="control-button btn-reset"
              onClick={handleReset}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              🔄 Reset Puzzle
            </motion.button>
            <motion.button
              className="control-button btn-new-game"
              onClick={handleNewGame}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              🎮 New Game
            </motion.button>
          </div>
        </div>
      )}

      <AnimatePresence>
        {showResults && (
          <AlgorithmResultsModal 
            results={algorithmResults} 
            onClose={() => setShowResults(false)} 
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showQuestion && (
          <QuestionModal 
            gameState={gameState}
            onClose={() => setShowQuestion(false)}
            onSubmit={() => {}}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
