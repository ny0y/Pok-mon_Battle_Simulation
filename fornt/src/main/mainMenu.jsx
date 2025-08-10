import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const PokemonBattleGame = () => {
  const logRef = useRef(null);
  const navigate = useNavigate();
  
  // Backend configuration
  const API_BASE_URL = 'http://127.0.0.1:8000';
  
  // Game state
  const [gamePhase, setGamePhase] = useState('selection');
  const [battleId, setBattleId] = useState(null);
  const [selectedPokemon, setSelectedPokemon] = useState(null);
  const [battleState, setBattleState] = useState({
    player: null,
    ai: null,
    gameOver: false,
    playerTurn: true
  });
  const [logMessages, setLogMessages] = useState([]);
  const [status, setStatus] = useState({ 
    message: "Choose your Pokémon to start battling!", 
    className: "info" 
  });
  const [loading, setLoading] = useState(false);
  
  // Pokemon data
  const pokemonData = {
    charizard: { name: "Charizard", sprite: "🔥", types: ["fire", "flying"], hp: 78, attack: 84, defense: 78, speed: 100, moves: ["ember", "wing attack", "slash", "fire blast"] },
    blastoise: { name: "Blastoise", sprite: "🌊", types: ["water"], hp: 79, attack: 83, defense: 100, speed: 78, moves: ["water gun", "bite", "withdraw", "hydro pump"] },
    venusaur: { name: "Venusaur", sprite: "🌿", types: ["grass", "poison"], hp: 80, attack: 82, defense: 83, speed: 80, moves: ["vine whip", "poison powder", "sleep powder", "solar beam"] },
    pikachu: { name: "Pikachu", sprite: "⚡", types: ["electric"], hp: 35, attack: 55, defense: 40, speed: 90, moves: ["thunder shock", "quick attack", "tail whip", "thunderbolt"] },
    gengar: { name: "Gengar", sprite: "👻", types: ["ghost", "poison"], hp: 60, attack: 65, defense: 60, speed: 110, moves: ["lick", "hypnosis", "shadow ball", "dream eater"] },
    alakazam: { name: "Alakazam", sprite: "🔮", types: ["psychic"], hp: 55, attack: 50, defense: 45, speed: 120, moves: ["confusion", "teleport", "psychic", "recover"] }
  };

  // CSS styles
  const styles = {
    body: {
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      margin: 0,
      padding: '20px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: '#333',
      minHeight: '100vh'
    },
    container: {
      maxWidth: '1200px',
      margin: '0 auto',
      background: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '20px',
      padding: '30px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.1)'
    },
    h1: {
      textAlign: 'center',
      color: '#2c3e50',
      fontSize: '2.5em',
      marginBottom: '30px',
      textShadow: '2px 2px 4px rgba(0,0,0,0.1)'
    },
    pokemonGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
      gap: '20px',
      margin: '30px 0'
    },
    pokemonOption: {
      background: 'linear-gradient(145deg, #f8f9fa, #e9ecef)',
      border: '3px solid #dee2e6',
      borderRadius: '15px',
      padding: '20px',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      textAlign: 'center',
      boxShadow: '0 5px 15px rgba(0,0,0,0.1)'
    },
    pokemonOptionHover: {
      transform: 'translateY(-5px)',
      borderColor: '#007bff',
      boxShadow: '0 10px 25px rgba(0,123,255,0.2)',
      background: 'linear-gradient(145deg, #cce7ff, #b3d9ff)'
    },
    battleArena: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '30px',
      marginBottom: '30px'
    },
    pokemonCard: {
      background: 'linear-gradient(145deg, #f8f9fa, #e9ecef)',
      borderRadius: '15px',
      padding: '25px',
      textAlign: 'center',
      boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
      border: '3px solid #dee2e6',
      transition: 'all 0.3s ease'
    },
    pokemonCardPlayer: {
      borderColor: '#007bff',
      background: 'linear-gradient(145deg, #cce7ff, #b3d9ff)'
    },
    pokemonCardAi: {
      borderColor: '#dc3545',
      background: 'linear-gradient(145deg, #ffcccc, #ffb3b3)'
    },
    hpBar: {
      background: '#e9ecef',
      borderRadius: '10px',
      height: '25px',
      margin: '15px 0',
      overflow: 'hidden',
      position: 'relative',
      boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)'
    },
    hpFill: {
      height: '100%',
      background: 'linear-gradient(90deg, #28a745, #20c997)',
      transition: 'width 0.5s ease',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontWeight: 'bold',
      textShadow: '1px 1px 2px rgba(0,0,0,0.3)'
    },
    movesGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '15px',
      margin: '20px 0'
    },
    moveBtn: {
      background: 'linear-gradient(145deg, #007bff, #0056b3)',
      color: 'white',
      border: 'none',
      padding: '15px 25px',
      borderRadius: '10px',
      fontSize: '1.1em',
      fontWeight: 'bold',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      textTransform: 'capitalize',
      boxShadow: '0 5px 15px rgba(0,123,255,0.3)'
    },
    log: {
      background: '#f8f9fa',
      padding: '25px',
      margin: '20px 0',
      borderRadius: '15px',
      maxHeight: '400px',
      overflowY: 'auto',
      border: '2px solid #dee2e6',
      fontFamily: "'Courier New', monospace",
      lineHeight: '1.6'
    },
    statusBar: {
      padding: '15px',
      margin: '20px 0',
      borderRadius: '10px',
      textAlign: 'center',
      fontWeight: 'bold',
      fontSize: '1.2em'
    },
    controlBtn: {
      background: 'linear-gradient(145deg, #28a745, #1e7e34)',
      color: 'white',
      border: 'none',
      padding: '12px 25px',
      borderRadius: '8px',
      fontSize: '1em',
      fontWeight: 'bold',
      cursor: 'pointer',
      margin: '0 10px',
      transition: 'all 0.3s ease'
    }
  };

  // Scroll log to bottom
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logMessages]);

  // Helper functions
  const logMessage = (message, className = "") => {
    setLogMessages(prev => [...prev, { message, className }]);
  };

  const updateStatus = (message, className = "info") => {
    setStatus({ message, className });
  };

  // API call function with proper error handling
  const apiCall = async (endpoint, options = {}) => {
    try {
      const token = localStorage.getItem('accessToken');
      
      const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      };

      const config = {
        method: options.method || 'GET',
        headers,
        ...options
      };

      if (options.body) {
        config.body = JSON.stringify(options.body);
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      
      // Handle Unauthorized
      if (response.status === 401) {
        localStorage.removeItem('accessToken');
        navigate('/login');
        throw new Error('Session expired. Please login again.');
      }
      
      // Handle other errors
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API call failed:', error);
      updateStatus(`Error: ${error.message}`, "error");
      throw error;
    }
  };

  // Start battle with API integration
  const startBattle = async (pokemonName) => {
    try {
      setLoading(true);
      updateStatus("Starting battle...", "info");
      
      // Step 1: GET the pokemon by name to get full data
      const normalizedName = pokemonName.toLowerCase();
      const getResponse = await apiCall(
        `/pokemon/index?name=${encodeURIComponent(normalizedName)}&including_evolution=true&page_size=50`
      );
      
      // Find exact match
      const character = getResponse.results.find(
        p => p.name.toLowerCase() === normalizedName
      );
      
      if (!character) {
        throw new Error(`Pokémon "${pokemonName}" not found`);
      }
      
      // Step 2: POST to create battle with detailed data
      const postBody = {
        name: character.name,
        types: character.types,
        hp: character.stats.hp,
        attack: character.stats.attack,
        defense: character.stats.defense,
        speed: character.stats.speed,
        available_moves: character.moves.slice(0, 4),
        status: null
      };
      
      const battleResponse = await apiCall('/play/create', {
        method: 'POST',
        body: postBody
      });
      
      setBattleId(battleResponse.battle_id);
      
      // Get AI moves from local data
      const aiName = battleResponse.ai.name.toLowerCase();
      const aiMoves = pokemonData[aiName]?.moves || ["tackle", "growl", "scratch", "hyper beam"];
      
      // Set battle state from API response
      setBattleState({
        player: {
          ...battleResponse.player,
          moves: postBody.available_moves, // Add moves from our request
          maxHp: battleResponse.player.max_hp,
          sprite: pokemonData[pokemonName]?.sprite || "🔮"
        },
        ai: {
          ...battleResponse.ai,
          moves: aiMoves, // Add moves from local data
          maxHp: battleResponse.ai.max_hp,
          sprite: pokemonData[aiName]?.sprite || "🔮"
        },
        gameOver: false,
        playerTurn: true
      });
      
      setGamePhase('battle');
      setLogMessages([]);
      logMessage(`⚔️ A wild ${battleResponse.ai.name} appeared!`);
      logMessage(`🎮 Go, ${battleResponse.player.name}!`);
      updateStatus("Battle started! Choose your move!", "success");
      
    } catch (error) {
      console.error('Battle creation failed:', error);
      updateStatus("Using offline mode", "error");
      startLocalBattle(pokemonName);
    } finally {
      setLoading(false);
    }
  };

  // Fallback to local battle
  const startLocalBattle = (pokemonName) => {
    const player = { 
      ...pokemonData[pokemonName], 
      maxHp: pokemonData[pokemonName].hp,
      statusEffects: {} 
    };
    
    const aiPokemonNames = Object.keys(pokemonData)
      .filter(name => name !== pokemonName);
    
    const aiName = aiPokemonNames[Math.floor(Math.random() * aiPokemonNames.length)];
    const ai = { 
      ...pokemonData[aiName], 
      maxHp: pokemonData[aiName].hp,
      statusEffects: {} 
    };
    
    setBattleState({ player, ai, gameOver: false, playerTurn: true });
    setGamePhase('battle');
    setLogMessages([]);
    logMessage(`⚔️ A wild ${ai.name} appeared!`);
    logMessage(`🎮 Go, ${player.name}!`);
    updateStatus("Battle started! (Offline mode)", "success");
  };

  // Make a move in the battle
  const makeMove = async (moveName) => {
    if (!battleState.playerTurn || battleState.gameOver || loading) return;
    
    setLoading(true);
    logMessage(`🎮 ${battleState.player.name} used ${moveName}!`);
    
    try {
      if (battleId) {
        // API move
        const response = await apiCall('/play/move', {
          method: 'POST',
          body: {
            battle_id: battleId,
            move: moveName
          }
        });
        
        // Update battle state while preserving moves
        setBattleState(prev => ({
          player: {
            ...response.player,
            moves: prev.player.moves, // Preserve moves from previous state
            maxHp: prev.player.maxHp,
            sprite: prev.player.sprite
          },
          ai: {
            ...response.ai,
            moves: prev.ai.moves, // Preserve moves from previous state
            maxHp: prev.ai.maxHp,
            sprite: prev.ai.sprite
          },
          gameOver: response.game_over,
          playerTurn: response.player_turn
        }));
        
        // Add battle log
        if (response.log) {
          logMessage(response.log.message, response.log.type);
        }
        
        // Handle game over
        if (response.game_over) {
          endBattle(response.winner);
        }
      } else {
        // Local move
        handleLocalMove(moveName);
      }
    } catch (error) {
      console.error('Move failed:', error);
      updateStatus("Using local calculation", "error");
      handleLocalMove(moveName);
    } finally {
      setLoading(false);
    }
  };

  // Local move handling
  const handleLocalMove = (moveName) => {
    const damage = Math.floor(Math.random() * 30) + 10;
    
    setBattleState(prev => {
      const newAi = { 
        ...prev.ai, 
        hp: Math.max(0, prev.ai.hp - damage) 
      };
      
      logMessage(`💥 Dealt ${damage} damage!`, "damage");
      
      // AI move (random)
      const aiMove = prev.ai.moves[Math.floor(Math.random() * prev.ai.moves.length)];
      const aiDamage = Math.floor(Math.random() * 25) + 8;
      const newPlayer = { 
        ...prev.player, 
        hp: Math.max(0, prev.player.hp - aiDamage) 
      };
      
      setTimeout(() => {
        logMessage(`🤖 ${prev.ai.name} used ${aiMove}!`);
        logMessage(`💥 You took ${aiDamage} damage!`, "damage");
      }, 500);
      
      // Check game over
      let gameOver = false;
      if (newPlayer.hp <= 0) {
        setTimeout(() => endBattle("AI"), 1000);
        gameOver = true;
      } else if (newAi.hp <= 0) {
        setTimeout(() => endBattle("Player"), 1000);
        gameOver = true;
      }
      
      return {
        player: newPlayer,
        ai: newAi,
        gameOver,
        playerTurn: !gameOver
      };
    });
  };

  // End battle
  const endBattle = (winner) => {
    const emoji = winner === "Player" ? "🎉" : "💀";
    updateStatus(`${emoji} Battle Over! Winner: ${winner}`, 
                winner === "Player" ? "success" : "error");
    logMessage(`🏆 ${winner} wins the battle!`);
  };

  // Reset game
  const resetGame = () => {
    setGamePhase('selection');
    setBattleId(null);
    setBattleState({ player: null, ai: null, gameOver: false, playerTurn: true });
    setLogMessages([]);
    updateStatus("Choose your Pokémon to start battling!", "info");
  };

  // Render Pokémon card
  const PokemonCard = ({ pokemon, isPlayer }) => {
    if (!pokemon) return null;
    
    const hpPercentage = Math.max(0, (pokemon.hp / pokemon.maxHp) * 100);
    const hpClass = hpPercentage <= 25 ? "critical" : 
                   hpPercentage <= 50 ? "low" : "";
    
    return (
      <div style={{
        ...styles.pokemonCard,
        ...(isPlayer ? styles.pokemonCardPlayer : styles.pokemonCardAi)
      }}>
        <div style={{ fontSize: '1.8em', fontWeight: 'bold', marginBottom: '15px' }}>
          {pokemon.name}
        </div>
        <div style={{ fontSize: '4em', margin: '20px 0' }}>
          {pokemon.sprite || "🔮"}
        </div>
        <div style={{ margin: '10px 0' }}>
          {pokemon.types?.map(type => (
            <span key={type} style={{
              display: 'inline-block',
              background: '#6c757d',
              color: 'white',
              padding: '3px 8px',
              borderRadius: '12px',
              fontSize: '0.8em',
              margin: '2px',
              textTransform: 'uppercase'
            }}>
              {type}
            </span>
          ))}
        </div>
        
        <div style={styles.hpBar}>
          <div style={{
            ...styles.hpFill,
            width: `${hpPercentage}%`,
            ...(hpClass === "critical" ? { 
              background: 'linear-gradient(90deg, #dc3545, #e74c3c)',
              animation: 'pulse 1s infinite'
            } : {}),
            ...(hpClass === "low" ? { 
              background: 'linear-gradient(90deg, #ffc107, #fd7e14)'
            } : {})
          }}>
            {pokemon.hp}/{pokemon.maxHp}
          </div>
        </div>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '10px',
          margin: '15px 0',
          fontSize: '0.9em'
        }}>
          <div style={{ padding: '5px 10px', background: 'rgba(255,255,255,0.7)', borderRadius: '5px' }}>
            ATK: {pokemon.attack}
          </div>
          <div style={{ padding: '5px 10px', background: 'rgba(255,255,255,0.7)', borderRadius: '5px' }}>
            DEF: {pokemon.defense}
          </div>
          <div style={{ padding: '5px 10px', background: 'rgba(255,255,255,0.7)', borderRadius: '5px' }}>
            SPD: {pokemon.speed}
          </div>
          <div style={{ padding: '5px 10px', background: 'rgba(255,255,255,0.7)', borderRadius: '5px' }}>
            Status: Normal
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={styles.body}>
      <div style={styles.container}>
        <h1 style={styles.h1}>🔥 Pokémon Battle Simulator ⚡</h1>
        
        {/* Status Bar */}
        <div style={{
          ...styles.statusBar,
          ...(status.className === "success" ? {
            backgroundColor: '#d1ecf1',
            color: '#0c5460',
            border: '2px solid #bee5eb'
          } : {}),
          ...(status.className === "error" ? {
            backgroundColor: '#f8d7da',
            color: '#721c24',
            border: '2px solid #f5c6cb'
          } : {}),
          ...(status.className === "info" ? {
            backgroundColor: '#d4edda',
            color: '#155724',
            border: '2px solid #c3e6cb'
          } : {})
        }}>
          {loading && "⏳ "}{status.message}
        </div>
        
        {/* Pokémon Selection */}
        {gamePhase === 'selection' && (
          <div style={{ textAlign: 'center', margin: '30px 0' }}>
            <h3>Choose Your Pokémon:</h3>
            <div style={styles.pokemonGrid}>
              {Object.entries(pokemonData).map(([key, pokemon]) => (
                <div
                  key={key}
                  style={styles.pokemonOption}
                  onClick={() => {
                    setSelectedPokemon(key);
                    startBattle(key);
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-5px)';
                    e.target.style.boxShadow = '0 10px 25px rgba(0,123,255,0.2)';
                    e.target.style.background = 'linear-gradient(145deg, #cce7ff, #b3d9ff)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'none';
                    e.target.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                    e.target.style.background = 'linear-gradient(145deg, #f8f9fa, #e9ecef)';
                  }}
                >
                  <div style={{ fontSize: '3em', margin: '10px 0' }}>{pokemon.sprite}</div>
                  <div style={{ fontSize: '1.3em', fontWeight: 'bold', margin: '10px 0' }}>
                    {pokemon.name}
                  </div>
                  <div style={{ margin: '10px 0' }}>
                    {pokemon.types.map(type => (
                      <span key={type} style={{
                        display: 'inline-block',
                        background: '#6c757d',
                        color: 'white',
                        padding: '2px 8px',
                        borderRadius: '10px',
                        fontSize: '0.8em',
                        margin: '2px'
                      }}>
                        {type}
                      </span>
                    ))}
                  </div>
                  <div>HP: {pokemon.hp}</div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Battle Arena */}
        {gamePhase === 'battle' && (
          <>
            {/* Controls */}
            <div style={{ textAlign: 'center', margin: '30px 0' }}>
              <button 
                style={styles.controlBtn}
                onClick={resetGame}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 5px 15px rgba(40,167,69,0.3)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'none';
                  e.target.style.boxShadow = 'none';
                }}
              >
                🔄 New Battle
              </button>
              <button 
                style={styles.controlBtn}
                onClick={() => setLogMessages([])}
              >
                🧹 Clear Log
              </button>
            </div>
            
            {/* Battle Field */}
            <div style={styles.battleArena}>
              <PokemonCard pokemon={battleState.player} isPlayer={true} />
              <PokemonCard pokemon={battleState.ai} isPlayer={false} />
            </div>
            
            {/* Move Selection */}
            {battleState.playerTurn && !battleState.gameOver && (
              <div style={{ textAlign: 'center', margin: '30px 0' }}>
                <h3>Choose Your Move:</h3>
                <div style={styles.movesGrid}>
                  {battleState.player?.moves?.map((move, index) => (  // Fixed with optional chaining
                    <button
                      key={index}
                      style={{
                        ...styles.moveBtn,
                        ...(loading || battleState.gameOver ? { 
                          background: '#6c757d',
                          cursor: 'not-allowed'
                        } : {})
                      }}
                      onClick={() => makeMove(move)}
                      disabled={loading || battleState.gameOver}
                      onMouseEnter={(e) => {
                        if (!e.target.disabled) {
                          e.target.style.transform = 'translateY(-3px)';
                          e.target.style.boxShadow = '0 8px 25px rgba(0,123,255,0.4)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.transform = 'none';
                        e.target.style.boxShadow = '0 5px 15px rgba(0,123,255,0.3)';
                      }}
                    >
                      {move}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Game Over */}
            {battleState.gameOver && (
              <div style={{
                padding: '30px',
                textAlign: 'center',
                margin: '30px 0',
                borderRadius: '15px',
                border: '3px solid #28a745',
                background: 'linear-gradient(145deg, #f8f9fa, #e9ecef)'
              }}>
                <h2 style={{ fontSize: '2em', marginBottom: '20px' }}>Battle Complete!</h2>
                <button
                  style={{
                    ...styles.controlBtn,
                    background: 'linear-gradient(145deg, #007bff, #0056b3)',
                    fontSize: '1.2em',
                    padding: '15px 30px'
                  }}
                  onClick={resetGame}
                >
                  🔄 New Battle
                </button>
              </div>
            )}
          </>
        )}
        
        {/* Battle Log */}
        <div style={styles.log} ref={logRef}>
          <h3 style={{ marginTop: 0 }}>
            Battle Log {battleId && (
              <span style={{
                marginLeft: '10px',
                fontSize: '12px',
                background: '#28a745',
                color: 'white',
                padding: '2px 8px',
                borderRadius: '4px'
              }}>
                ONLINE
              </span>
            )}
          </h3>
          {logMessages.map((log, index) => (
            <p key={index} style={{
              margin: '8px 0',
              padding: '8px',
              borderRadius: '5px',
              background: 'rgba(255,255,255,0.7)',
              color: log.className === 'damage' ? '#dc3545' : 
                     log.className === 'heal' ? '#28a745' :
                     log.className === 'status' ? '#6f42c1' : '#333',
              fontWeight: log.className ? 'bold' : 'normal',
              fontStyle: log.className === 'status' ? 'italic' : 'normal'
            }}>
              {log.message}
            </p>
          ))}
          {logMessages.length === 0 && (
            <div style={{ padding: '40px 0', textAlign: 'center', color: '#6c757d' }}>
              Battle log will appear here...
            </div>
          )}
        </div>

        {/* Navigation */}
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
          <button 
            style={{
              padding: '10px 15px',
              background: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
            onClick={() => navigate('/Auther')}
          >
            Login
          </button>
        </div>
      </div>
      
      {/* Animation styles */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>
    </div>
  );
};

export default PokemonBattleGame;