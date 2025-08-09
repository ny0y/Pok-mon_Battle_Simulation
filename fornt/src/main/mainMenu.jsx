import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';


// Pokémon data
const pokemonData = {
  charizard: { name: "Charizard", sprite: "🔥", types: ["fire", "flying"], hp: 78, attack: 84, defense: 78, speed: 100, moves: ["ember", "wing attack", "slash", "fire blast"] },
  blastoise: { name: "Blastoise", sprite: "🌊", types: ["water"], hp: 79, attack: 83, defense: 100, speed: 78, moves: ["water gun", "bite", "withdraw", "hydro pump"] },
  venusaur: { name: "Venusaur", sprite: "🌿", types: ["grass", "poison"], hp: 80, attack: 82, defense: 83, speed: 80, moves: ["vine whip", "poison powder", "sleep powder", "solar beam"] },
  pikachu: { name: "Pikachu", sprite: "⚡", types: ["electric"], hp: 35, attack: 55, defense: 40, speed: 90, moves: ["thunder shock", "quick attack", "tail whip", "thunderbolt"] },
  gengar: { name: "Gengar", sprite: "👻", types: ["ghost", "poison"], hp: 60, attack: 65, defense: 60, speed: 110, moves: ["lick", "hypnosis", "shadow ball", "dream eater"] },
  alakazam: { name: "Alakazam", sprite: "🔮", types: ["psychic"], hp: 55, attack: 50, defense: 45, speed: 120, moves: ["confusion", "teleport", "psychic", "recover"] }
};

// Move data
const moveData = {
  // Fire moves
  ember: { power: 40, type: "fire", effect: "burn" },
  "fire blast": { power: 110, type: "fire", effect: "burn" },
  
  // Flying moves
  "wing attack": { power: 60, type: "flying" },
  
  // Normal moves
  slash: { power: 70, type: "normal" },
  "quick attack": { power: 40, type: "normal", priority: 1 },
  "tail whip": { power: 0, type: "normal", effect: "lower_defense" },
  bite: { power: 60, type: "dark", effect: "flinch" },
  
  // Water moves
  "water gun": { power: 40, type: "water" },
  "hydro pump": { power: 110, type: "water" },
  withdraw: { power: 0, type: "water", effect: "raise_defense" },
  
  // Grass moves
  "vine whip": { power: 45, type: "grass" },
  "solar beam": { power: 120, type: "grass" },
  
  // Poison moves
  "poison powder": { power: 0, type: "poison", effect: "poison" },
  "sleep powder": { power: 0, type: "grass", effect: "sleep" },
  
  // Electric moves
  "thunder shock": { power: 40, type: "electric", effect: "paralyze" },
  thunderbolt: { power: 90, type: "electric", effect: "paralyze" },
  
  // Ghost moves
  lick: { power: 30, type: "ghost", effect: "paralyze" },
  "shadow ball": { power: 80, type: "ghost" },
  
  // Psychic moves
  confusion: { power: 50, type: "psychic", effect: "confuse" },
  psychic: { power: 90, type: "psychic" },
  teleport: { power: 0, type: "psychic", effect: "escape" },
  recover: { power: 0, type: "normal", effect: "heal" },
  hypnosis: { power: 0, type: "psychic", effect: "sleep" },
  "dream eater": { power: 100, type: "psychic", effect: "heal_damage" }
};

const BattleSimulator = () => {
  const navigate = useNavigate();
  const logRef = useRef(null);
  
  // Game state
  const [gamePhase, setGamePhase] = useState('selection'); // 'selection' or 'battle'
  const [selectedPokemon, setSelectedPokemon] = useState(null);
  const [battleState, setBattleState] = useState({
    player: null,
    ai: null,
    turn: 0,
    gameOver: false,
    playerTurn: true
  });
  const [logMessages, setLogMessages] = useState([]);
  const [status, setStatus] = useState({ 
    message: "Choose your Pokémon to start battling!", 
    className: "info" 
  });

  // Scroll log to bottom when new messages are added
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

  const getRandomPokemon = () => {
    const names = Object.keys(pokemonData);
    const randomName = names[Math.floor(Math.random() * names.length)];
    return JSON.parse(JSON.stringify(pokemonData[randomName])); // Deep clone
  };

  const initializePokemon = (pokemon) => {
    const clone = { ...pokemon };
    clone.maxHp = pokemon.hp;
    clone.currentAttack = pokemon.attack;
    clone.currentDefense = pokemon.defense;
    clone.statusEffects = {};
    return clone;
  };

  // Pokémon selection
  const handleSelectPokemon = (pokemonName) => {
    setSelectedPokemon(pokemonName);
    updateStatus(`You selected ${pokemonData[pokemonName].name}! Starting battle...`, "success");
    startNewBattle(pokemonName);
  };

  const startNewBattle = (pokemonName) => {
    const player = initializePokemon(pokemonData[pokemonName]);
    let ai = initializePokemon(getRandomPokemon());
    
    // Ensure AI doesn't pick the same as player
    while (ai.name.toLowerCase() === pokemonName.toLowerCase()) {
      ai = initializePokemon(getRandomPokemon());
    }

    setBattleState({
      player,
      ai,
      turn: 0,
      gameOver: false,
      playerTurn: true
    });
    
    setGamePhase('battle');
    
    // Initial log messages
    setLogMessages([]);
    logMessage(`⚔️ A wild ${ai.name} appeared!`);
    logMessage(`🎮 Go, ${player.name}!`);
    updateStatus("Battle started! Your turn - choose a move!", "success");
  };

  // Battle logic
  const calculateDamage = (attacker, defender, move) => {
    if (move.power === 0) return 0;
    
    const level = 50;
    const critical = Math.random() < 0.0625 ? 2 : 1;
    const random = Math.random() * (1 - 0.85) + 0.85;
    
    // Simplified type effectiveness
    let effectiveness = 1;
    const typeChart = {
      fire: { grass: 2, water: 0.5 },
      water: { fire: 2, grass: 0.5 },
      grass: { water: 2, fire: 0.5 },
      electric: { water: 2, grass: 0.5 },
      psychic: { poison: 2 },
      ghost: { normal: 0 }
    };
    
    if (typeChart[move.type]) {
      defender.types.forEach(defType => {
        if (typeChart[move.type][defType]) {
          effectiveness *= typeChart[move.type][defType];
        }
      });
    }
    
    const damage = Math.floor(
      ((((2 * level / 5 + 2) * move.power * attacker.currentAttack / defender.currentDefense) / 50) + 2) 
      * critical * random * effectiveness
    );
    
    return Math.max(1, damage);
  };

  const applyMoveEffect = (move, target, attacker) => {
    if (!move.effect) return;
    
    switch (move.effect) {
      case "burn":
        if (Math.random() < 0.1 && !target.statusEffects.burn) {
          target.statusEffects.burn = 5;
          logMessage(`🔥 ${target.name} was burned!`, "status");
        }
        break;
      case "poison":
        if (Math.random() < 0.75 && !target.statusEffects.poison) {
          target.statusEffects.poison = 5;
          logMessage(`☠️ ${target.name} was poisoned!`, "status");
        }
        break;
      case "paralyze":
        if (Math.random() < 0.3 && !target.statusEffects.paralyze) {
          target.statusEffects.paralyze = 5;
          logMessage(`⚡ ${target.name} was paralyzed!`, "status");
        }
        break;
      case "sleep":
        if (Math.random() < 0.75 && !target.statusEffects.sleep) {
          target.statusEffects.sleep = Math.floor(Math.random() * 3) + 1;
          logMessage(`😴 ${target.name} fell asleep!`, "status");
        }
        break;
      case "heal":
        const healAmount = Math.floor(attacker.maxHp / 2);
        attacker.hp = Math.min(attacker.maxHp, attacker.hp + healAmount);
        logMessage(`💚 ${attacker.name} healed ${healAmount} HP!`, "heal");
        break;
      case "raise_defense":
        attacker.currentDefense = Math.floor(attacker.currentDefense * 1.5);
        logMessage(`🛡️ ${attacker.name}'s defense rose!`, "status");
        break;
      case "lower_defense":
        target.currentDefense = Math.floor(target.currentDefense * 0.67);
        logMessage(`📉 ${target.name}'s defense fell!`, "status");
        break;
    }
  };

  const processStatusEffects = (pokemon) => {
    Object.keys(pokemon.statusEffects).forEach(effect => {
      if (pokemon.statusEffects[effect] <= 0) {
        delete pokemon.statusEffects[effect];
        logMessage(`${pokemon.name} recovered from ${effect}!`, "heal");
        return;
      }
      
      switch (effect) {
        case "burn":
        case "poison":
          const damage = Math.floor(pokemon.maxHp / 8);
          pokemon.hp = Math.max(0, pokemon.hp - damage);
          logMessage(`${pokemon.name} took ${damage} damage from ${effect}!`, "damage");
          pokemon.statusEffects[effect]--;
          break;
        case "paralyze":
        case "sleep":
          pokemon.statusEffects[effect]--;
          break;
      }
    });
  };

  const canAct = (pokemon) => {
    if (pokemon.statusEffects.sleep > 0) {
      logMessage(`${pokemon.name} is fast asleep!`, "status");
      return false;
    }
    if (pokemon.statusEffects.paralyze > 0 && Math.random() < 0.25) {
      logMessage(`${pokemon.name} is paralyzed and can't move!`, "status");
      return false;
    }
    return true;
  };

  const handlePlayerMove = (moveName) => {
    if (battleState.gameOver || !battleState.playerTurn) return;
    
    const move = moveData[moveName];
    const player = { ...battleState.player };
    const ai = { ...battleState.ai };
    
    if (!canAct(player)) {
      setBattleState(prev => ({ ...prev, playerTurn: false }));
      setTimeout(handleAiMove, 1000);
      return;
    }
    
    logMessage(`🎮 ${player.name} used ${moveName}!`);
    
    const damage = calculateDamage(player, ai, move);
    if (damage > 0) {
      ai.hp = Math.max(0, ai.hp - damage);
      logMessage(`💥 Dealt ${damage} damage!`, "damage");
    }
    
    applyMoveEffect(move, ai, player);
    
    if (ai.hp <= 0) {
      endBattle("Player");
      return;
    }
    
    setBattleState(prev => ({
      ...prev,
      player,
      ai,
      playerTurn: false
    }));
    
    setTimeout(handleAiMove, 1500);
  };

  const handleAiMove = () => {
    if (battleState.gameOver) return;
    
    const player = { ...battleState.player };
    const ai = { ...battleState.ai };
    
    if (!canAct(ai)) {
      setBattleState(prev => ({ ...prev, playerTurn: true }));
      return;
    }
    
    const moveName = ai.moves[Math.floor(Math.random() * ai.moves.length)];
    const move = moveData[moveName];
    
    logMessage(`🤖 ${ai.name} used ${moveName}!`);
    
    const damage = calculateDamage(ai, player, move);
    if (damage > 0) {
      player.hp = Math.max(0, player.hp - damage);
      logMessage(`💥 You took ${damage} damage!`, "damage");
    }
    
    applyMoveEffect(move, player, ai);
    
    // Process status effects
    processStatusEffects(player);
    processStatusEffects(ai);
    
    if (player.hp <= 0) {
      endBattle("AI");
      return;
    }
    if (ai.hp <= 0) {
      endBattle("Player");
      return;
    }
    
    setBattleState(prev => ({
      ...prev,
      player,
      ai,
      playerTurn: true,
      turn: prev.turn + 1
    }));
    
    updateStatus(`Turn ${battleState.turn + 2} - Your turn! Choose a move.`, "info");
  };

  const endBattle = (winner) => {
    const emoji = winner === "Player" ? "🎉" : "💀";
    updateStatus(`${emoji} Battle Over! Winner: ${winner}`, winner === "Player" ? "success" : "error");
    logMessage(`🏆 ${winner} wins the battle!`);
    
    setBattleState(prev => ({ ...prev, gameOver: true }));
  };

  // UI Helpers
  const renderPokemonCard = (pokemon, isPlayer) => {
    if (!pokemon) return null;
    
    const hpPercentage = (pokemon.hp / pokemon.maxHp) * 100;
    let hpClass = "hp-fill";
    if (hpPercentage <= 25) hpClass += " critical";
    else if (hpPercentage <= 50) hpClass += " low";
    
    return (
      <div className={`pokemon-card ${isPlayer ? 'player' : 'ai'}`}>
        <div className="pokemon-name">{pokemon.name}</div>
        <div className="pokemon-sprite">{pokemon.sprite}</div>
        <div className="types">
          {pokemon.types.map(type => (
            <span key={type} className="type-badge">{type}</span>
          ))}
        </div>
        <div className="hp-bar">
          <div 
            className={hpClass} 
            style={{ width: `${hpPercentage}%` }}
          >
            {pokemon.hp}/{pokemon.maxHp}
          </div>
        </div>
        <div className="stats">
          <div className="stat">ATK: {pokemon.currentAttack}</div>
          <div className="stat">DEF: {pokemon.currentDefense}</div>
          <div className="stat">SPD: {pokemon.speed}</div>
          <div className="stat">Status: {Object.keys(pokemon.statusEffects).join(", ") || "Normal"}</div>
        </div>
      </div>
    );
  };

  // Navigation handlers
  const handleGoToLogin = () => {
    navigate('/login');
  };

  const handleGoToRegister = () => {
    navigate('/register');
  };

  const handleGoToMainMenu = () => {
    navigate('/main');
  };

  return (
    <div className="container">
      <h1>🔥 Pokémon Battle Simulator ⚡</h1>
      
      {/* Status Bar */}
      <div className={`status-bar ${status.className}`}>
        {status.message}
      </div>
      
      {/* Pokémon Selection Screen */}
      {gamePhase === 'selection' && (
        <div className="pokemon-selection">
          <h3>Choose Your Pokémon:</h3>
          <div className="pokemon-grid">
            {Object.entries(pokemonData).map(([key, pokemon]) => (
              <div 
                key={key} 
                className="pokemon-option"
                onClick={() => handleSelectPokemon(key)}
              >
                <div className="pokemon-sprite">{pokemon.sprite}</div>
                <div className="pokemon-name">{pokemon.name}</div>
                <div className="types">
                  {pokemon.types.map(type => (
                    <span key={type} className="type-badge">{type}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Battle Controls */}
      {gamePhase === 'battle' && (
        <div className="control-buttons">
          <button 
            className="control-btn"
            onClick={() => setGamePhase('selection')}
          >
            🔄 Choose Different Pokémon
          </button>
          <button 
            className="control-btn"
            onClick={() => setLogMessages([])}
          >
            🧹 Clear Log
          </button>
          <button 
            className="control-btn"
            onClick={handleGoToMainMenu}
          >
            🏠 Back to Main Menu
          </button>
        </div>
      )}
      
      {/* Battle Arena */}
      {gamePhase === 'battle' && (
        <div className="battle-arena">
          {renderPokemonCard(battleState.player, true)}
          {renderPokemonCard(battleState.ai, false)}
        </div>
      )}
      
      {/* Moves Section */}
      {gamePhase === 'battle' && battleState.playerTurn && !battleState.gameOver && (
        <div className="moves-section">
          <h3>Choose Your Move:</h3>
          <div className="moves-grid">
            {battleState.player?.moves.map(move => (
              <button
                key={move}
                className="move-btn"
                onClick={() => handlePlayerMove(move)}
                disabled={!battleState.playerTurn || battleState.gameOver}
              >
                {move}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Battle Log */}
      <div ref={logRef} className="log">
        {logMessages.map((entry, index) => (
          <p key={index} className={entry.className}>{entry.message}</p>
        ))}
      </div>
      
      {/* Navigation Footer */}
      <div className="navigation-footer">
        <button onClick={handleGoToLogin}>Login</button>
        <button onClick={handleGoToRegister}>Register</button>
        <button onClick={handleGoToMainMenu}>Main Menu</button>
      </div>
    </div>
  );
};

export default BattleSimulator;