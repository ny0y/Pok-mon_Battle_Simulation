import React, { useState, useEffect, useRef } from 'react';
import { Zap, Shield, Moon, Droplet, Heart, Swords, ArrowLeft, RotateCcw, Home } from 'lucide-react';

const PokemonBattleGame = () => {
  const logRef = useRef(null);
  
  // Backend configuration
  const API_BASE_URL = 'http://127.0.0.1:8000'; // Your FastAPI server URL
  
  // Game state
  const [gamePhase, setGamePhase] = useState('selection'); // 'selection', 'battle', 'connecting'
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

  // Pokemon data from your backend structure
  const pokemonData = {
    charizard: { name: "Charizard", sprite: "🔥", types: ["fire", "flying"], hp: 78, attack: 84, defense: 78, speed: 100, moves: ["ember", "wing attack", "slash", "fire blast"] },
    blastoise: { name: "Blastoise", sprite: "🌊", types: ["water"], hp: 79, attack: 83, defense: 100, speed: 78, moves: ["water gun", "bite", "withdraw", "hydro pump"] },
    venusaur: { name: "Venusaur", sprite: "🌿", types: ["grass", "poison"], hp: 80, attack: 82, defense: 83, speed: 80, moves: ["vine whip", "poison powder", "sleep powder", "solar beam"] },
    pikachu: { name: "Pikachu", sprite: "⚡", types: ["electric"], hp: 35, attack: 55, defense: 40, speed: 90, moves: ["thunder shock", "quick attack", "tail whip", "thunderbolt"] },
    gengar: { name: "Gengar", sprite: "👻", types: ["ghost", "poison"], hp: 60, attack: 65, defense: 60, speed: 110, moves: ["lick", "hypnosis", "shadow ball", "dream eater"] },
    alakazam: { name: "Alakazam", sprite: "🔮", types: ["psychic"], hp: 55, attack: 50, defense: 45, speed: 120, moves: ["confusion", "teleport", "psychic", "recover"] }
  };

  // Move icons mapping
  const moveIcons = {
    ember: { icon: Zap, color: "text-red-400" },
    "fire blast": { icon: Zap, color: "text-red-500" },
    "wing attack": { icon: Swords, color: "text-gray-400" },
    slash: { icon: Swords, color: "text-gray-500" },
    "water gun": { icon: Droplet, color: "text-blue-400" },
    "hydro pump": { icon: Droplet, color: "text-blue-500" },
    bite: { icon: Swords, color: "text-gray-600" },
    withdraw: { icon: Shield, color: "text-blue-300" },
    "vine whip": { icon: Swords, color: "text-green-400" },
    "solar beam": { icon: Zap, color: "text-yellow-400" },
    "poison powder": { icon: Droplet, color: "text-purple-400" },
    "sleep powder": { icon: Moon, color: "text-purple-300" },
    "thunder shock": { icon: Zap, color: "text-yellow-400" },
    thunderbolt: { icon: Zap, color: "text-yellow-500" },
    "quick attack": { icon: Swords, color: "text-gray-400" },
    "tail whip": { icon: Shield, color: "text-orange-400" },
    lick: { icon: Swords, color: "text-purple-400" },
    hypnosis: { icon: Moon, color: "text-purple-500" },
    "shadow ball": { icon: Droplet, color: "text-purple-600" },
    "dream eater": { icon: Heart, color: "text-purple-400" },
    confusion: { icon: Zap, color: "text-pink-400" },
    psychic: { icon: Zap, color: "text-pink-500" },
    teleport: { icon: Shield, color: "text-pink-300" },
    recover: { icon: Heart, color: "text-green-400" }
  };

  // Scroll log to bottom when new messages are added
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logMessages]);

  // Helper functions
  const logMessage = (message, className = "") => {
    setLogMessages(prev => [...prev, { message, className, timestamp: Date.now() }]);
  };

  const updateStatus = (message, className = "info") => {
    setStatus({ message, className });
  };

  // API calls to your FastAPI backend
  const apiCall = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
        },
        ...options,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API call failed:', error);
      updateStatus(`Connection error: ${error.message}`, "error");
      throw error;
    }
  };

  const fetchPokemonData = async (pokemonName) => {
    try {
      const data = await apiCall(`/pokemon/${pokemonName}`);
      return {
        name: data.name,
        hp: data.stats.hp,
        maxHp: data.stats.hp,
        attack: data.stats.attack,
        defense: data.stats.defense,
        speed: data.stats.speed,
        types: data.types,
        moves: data.moves.slice(0, 4), // Limit to 4 moves
        statusEffects: {},
        sprite: pokemonData[pokemonName]?.sprite || "🔮"
      };
    } catch (error) {
      // Fallback to local data if API fails
      const localData = pokemonData[pokemonName];
      return {
        ...localData,
        maxHp: localData.hp,
        statusEffects: {}
      };
    }
  };

  const startBattle = async (pokemonName) => {
    try {
      setLoading(true);
      updateStatus("Starting battle with AI...", "info");
      
      const battleResponse = await apiCall('/play/start', { method: 'POST' });
      setBattleId(battleResponse.battle_id);
      
      // Fetch player pokemon data
      const playerPokemon = await fetchPokemonData(pokemonName);
      
      // For now, we'll simulate the AI pokemon selection
      const aiPokemonNames = Object.keys(pokemonData).filter(name => name !== pokemonName);
      const aiPokemonName = aiPokemonNames[Math.floor(Math.random() * aiPokemonNames.length)];
      const aiPokemon = await fetchPokemonData(aiPokemonName);
      
      setBattleState({
        player: playerPokemon,
        ai: aiPokemon,
        gameOver: false,
        playerTurn: true
      });
      
      setGamePhase('battle');
      setLogMessages([]);
      logMessage(`⚔️ A wild ${aiPokemon.name} appeared!`);
      logMessage(`🎮 Go, ${playerPokemon.name}!`);
      updateStatus("Battle started! Choose your move!", "success");
      
    } catch (error) {
      updateStatus("Failed to start battle. Using offline mode.", "error");
      // Fallback to local battle
      startLocalBattle(pokemonName);
    } finally {
      setLoading(false);
    }
  };

  const startLocalBattle = (pokemonName) => {
    const player = { ...pokemonData[pokemonName], maxHp: pokemonData[pokemonName].hp, statusEffects: {} };
    const aiPokemonNames = Object.keys(pokemonData).filter(name => name !== pokemonName);
    const aiPokemonName = aiPokemonNames[Math.floor(Math.random() * aiPokemonNames.length)];
    const ai = { ...pokemonData[aiPokemonName], maxHp: pokemonData[aiPokemonName].hp, statusEffects: {} };
    
    setBattleState({ player, ai, gameOver: false, playerTurn: true });
    setGamePhase('battle');
    setLogMessages([]);
    logMessage(`⚔️ A wild ${ai.name} appeared!`);
    logMessage(`🎮 Go, ${player.name}!`);
    updateStatus("Battle started! (Offline mode)", "success");
  };

  const makeMove = async (moveName) => {
    if (!battleState.playerTurn || battleState.gameOver || loading) return;
    
    setLoading(true);
    logMessage(`🎮 ${battleState.player.name} used ${moveName}!`);
    
    try {
      if (battleId) {
        // Use backend API
        const response = await apiCall(`/play/${battleId}/move?player_move=${moveName}`);
        
        // Process the response and update battle state
        if (response.turn_log && response.turn_log.length > 0) {
          response.turn_log.forEach(log => {
            if (log.damage > 0) {
              logMessage(`💥 ${log.attacker} dealt ${log.damage} damage with ${log.move}!`, "damage");
            } else {
              logMessage(`🎯 ${log.attacker} used ${log.move}!`);
            }
          });
        }
        
        // Update battle state with response data
        if (response.player && response.ai) {
          setBattleState(prev => ({
            ...prev,
            player: { ...prev.player, hp: response.player.hp || prev.player.hp },
            ai: { ...prev.ai, hp: response.ai.hp || prev.ai.hp },
            playerTurn: true
          }));
          
          // Check for game over
          if (response.player.hp <= 0) {
            endBattle("AI");
          } else if (response.ai.hp <= 0) {
            endBattle("Player");
          }
        }
      } else {
        // Fallback to local battle logic
        handleLocalMove(moveName);
      }
    } catch (error) {
      updateStatus("Move failed, using local calculation", "error");
      handleLocalMove(moveName);
    } finally {
      setLoading(false);
    }
  };

  const handleLocalMove = (moveName) => {
    // Simple local battle logic
    const damage = Math.floor(Math.random() * 30) + 10;
    const aiDamage = Math.floor(Math.random() * 25) + 8;
    
    setBattleState(prev => {
      const newAi = { ...prev.ai, hp: Math.max(0, prev.ai.hp - damage) };
      const newPlayer = { ...prev.player, hp: Math.max(0, prev.player.hp - aiDamage) };
      
      logMessage(`💥 Dealt ${damage} damage!`, "damage");
      
      // AI move
      const aiMove = newAi.moves[Math.floor(Math.random() * newAi.moves.length)];
      setTimeout(() => {
        logMessage(`🤖 ${newAi.name} used ${aiMove}!`);
        logMessage(`💥 You took ${aiDamage} damage!`, "damage");
      }, 1000);
      
      // Check game over
      if (newPlayer.hp <= 0) {
        setTimeout(() => endBattle("AI"), 1500);
      } else if (newAi.hp <= 0) {
        setTimeout(() => endBattle("Player"), 1500);
      }
      
      return { ...prev, player: newPlayer, ai: newAi };
    });
  };

  const endBattle = (winner) => {
    const emoji = winner === "Player" ? "🎉" : "💀";
    updateStatus(`${emoji} Battle Over! Winner: ${winner}`, winner === "Player" ? "success" : "error");
    logMessage(`🏆 ${winner} wins the battle!`);
    setBattleState(prev => ({ ...prev, gameOver: true }));
  };

  const resetGame = () => {
    setGamePhase('selection');
    setBattleId(null);
    setBattleState({ player: null, ai: null, gameOver: false, playerTurn: true });
    setLogMessages([]);
    updateStatus("Choose your Pokémon to start battling!", "info");
  };

  // UI Components
  const PokemonCard = ({ pokemon, isPlayer }) => {
    if (!pokemon) return null;
    
    const hpPercentage = (pokemon.hp / pokemon.maxHp) * 100;
    
    return (
      <div className={`relative p-6 rounded-xl bg-gradient-to-br ${isPlayer ? 'from-blue-500 to-blue-700' : 'from-red-500 to-red-700'} text-white shadow-2xl transform ${loading && ((isPlayer && battleState.playerTurn) || (!isPlayer && !battleState.playerTurn)) ? 'scale-105' : 'scale-100'} transition-transform duration-300`}>
        <div className="text-center mb-4">
          <div className="text-6xl mb-2">{pokemon.sprite}</div>
          <h3 className="text-xl font-bold">{pokemon.name}</h3>
          <div className="flex justify-center space-x-2 mt-2">
            {pokemon.types?.map(type => (
              <span key={type} className="px-2 py-1 bg-black bg-opacity-30 rounded text-xs uppercase">
                {type}
              </span>
            ))}
          </div>
          {Object.keys(pokemon.statusEffects || {}).length > 0 && (
            <div className="text-sm text-yellow-300 font-semibold mt-1">
              {Object.keys(pokemon.statusEffects).join(", ").toUpperCase()}
            </div>
          )}
        </div>
        
        <div className="space-y-2">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>HP</span>
              <span>{pokemon.hp}/{pokemon.maxHp}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3">
              <div 
                className={`h-3 rounded-full transition-all duration-500 ${hpPercentage > 50 ? 'bg-green-400' : hpPercentage > 25 ? 'bg-yellow-400' : 'bg-red-400'}`}
                style={{ width: `${hpPercentage}%` }}
              ></div>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div>ATK: {pokemon.attack}</div>
            <div>DEF: {pokemon.defense}</div>
            <div>SPD: {pokemon.speed}</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-900 via-blue-900 to-indigo-900 p-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-white text-center mb-8">🔥 Pokémon Battle Arena ⚡</h1>
        
        {/* Status Bar */}
        <div className={`text-center mb-6 p-4 rounded-lg font-semibold ${
          status.className === 'success' ? 'bg-green-600 text-white' :
          status.className === 'error' ? 'bg-red-600 text-white' :
          'bg-blue-600 text-white'
        }`}>
          {loading && "⏳ "}{status.message}
        </div>
        
        {/* Pokemon Selection */}
        {gamePhase === 'selection' && (
          <div className="bg-white rounded-xl p-8 shadow-2xl">
            <h2 className="text-2xl font-bold text-center mb-6">Choose Your Pokémon</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(pokemonData).map(([key, pokemon]) => (
                <button
                  key={key}
                  onClick={() => {
                    setSelectedPokemon(key);
                    startBattle(key);
                  }}
                  disabled={loading}
                  className="p-6 rounded-lg bg-gradient-to-br from-purple-400 to-blue-500 text-white hover:from-purple-500 hover:to-blue-600 transition-all duration-200 transform hover:scale-105 shadow-lg disabled:opacity-50"
                >
                  <div className="text-4xl mb-2">{pokemon.sprite}</div>
                  <div className="font-bold">{pokemon.name}</div>
                  <div className="text-sm opacity-75">
                    {pokemon.types.join(", ")}
                  </div>
                  <div className="text-xs mt-2">HP: {pokemon.hp}</div>
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Battle Arena */}
        {gamePhase === 'battle' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div>
                <h2 className="text-xl text-white mb-4 text-center">Your Pokémon</h2>
                <PokemonCard pokemon={battleState.player} isPlayer={true} />
              </div>
              <div>
                <h2 className="text-xl text-white mb-4 text-center">Enemy Pokémon</h2>
                <PokemonCard pokemon={battleState.ai} isPlayer={false} />
              </div>
            </div>
            
            {/* Battle Controls */}
            <div className="flex justify-center space-x-4 mb-6">
              <button 
                onClick={resetGame}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Choose Different Pokémon</span>
              </button>
              <button 
                onClick={() => setLogMessages([])}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Clear Log</span>
              </button>
            </div>
            
            {/* Move Selection */}
            {battleState.playerTurn && !battleState.gameOver && (
              <div className="bg-white rounded-xl p-6 mb-6 shadow-2xl">
                <h3 className="text-lg font-semibold mb-4 text-center">Choose Your Move</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {battleState.player?.moves.map((move, index) => {
                    const moveIcon = moveIcons[move] || { icon: Swords, color: "text-gray-400" };
                    const Icon = moveIcon.icon;
                    
                    return (
                      <button
                        key={index}
                        onClick={() => makeMove(move)}
                        disabled={!battleState.playerTurn || loading || battleState.gameOver}
                        className="p-4 rounded-lg font-semibold transition-all duration-200 flex flex-col items-center space-y-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Icon className={`w-6 h-6 ${moveIcon.color}`} />
                        <span className="text-sm capitalize">{move.replace(/[\-_]/g, ' ')}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
            
            {/* Game Over */}
            {battleState.gameOver && (
              <div className="bg-white rounded-xl p-8 text-center shadow-2xl mb-6">
                <h2 className="text-3xl font-bold mb-4">Battle Complete!</h2>
                <button
                  onClick={resetGame}
                  className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg"
                >
                  🔄 New Battle
                </button>
              </div>
            )}
          </>
        )}
        
        {/* Battle Log */}
        <div className="bg-black bg-opacity-50 rounded-xl p-6 text-white">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <span>Battle Log</span>
            {battleId && <span className="ml-2 text-xs bg-green-600 px-2 py-1 rounded">ONLINE</span>}
          </h3>
          <div ref={logRef} className="space-y-2 h-40 overflow-y-auto">
            {logMessages.map((log, index) => (
              <div key={index} className={`text-sm p-2 rounded ${
                log.className === 'damage' ? 'bg-red-600 bg-opacity-50' :
                log.className === 'heal' ? 'bg-green-600 bg-opacity-50' :
                log.className === 'status' ? 'bg-yellow-600 bg-opacity-50' :
                'bg-gray-800 bg-opacity-50'
              }`}>
                {log.message}
              </div>
            ))}
            {logMessages.length === 0 && (
              <div className="text-gray-400 text-sm text-center py-8">
                Battle log will appear here...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PokemonBattleGame;