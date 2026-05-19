import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Text } from '@react-three/drei';
import { createNoise3D } from 'simplex-noise';
import * as THREE from 'three';
import '../styles/visualizations.css';

/**
 * 3D Football Pitch Visualization
 * Interactive 3D visualization of player positions and movements
 */

const noise3D = createNoise3D(Math.random);

// ━━━━━ FOOTBALL PITCH ━━━━━
function FootballPitch() {
  return (
    <group>
      {/* Field */}
      <mesh position={[0, 0, 0]}>
        <planeGeometry args={[105, 68, 100, 100]} />
        <meshStandardMaterial color="#2d5016" />
      </mesh>

      {/* Halfway line */}
      <lineSegments position={[0, 0.01, 0]}>
        <geometry>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={2}
              array={new Float32Array([0, 0, 0, 0, 68, 0])}
              itemSize={3}
            />
          </bufferGeometry>
        </geometry>
        <lineBasicMaterial color="white" linewidth={2} />
      </lineSegments>

      {/* Center circle */}
      <mesh position={[0, 0.01, 0]}>
        <circleGeometry args={[9.15, 32]} />
        <meshBasicMaterial color="white" />
      </mesh>

      {/* Goals */}
      <mesh position={[-52.5, 0.5, 0]}>
        <boxGeometry args={[1, 2.44, 8]} />
        <meshStandardMaterial color="#ff6b6b" />
      </mesh>
      <mesh position={[52.5, 0.5, 0]}>
        <boxGeometry args={[1, 2.44, 8]} />
        <meshStandardMaterial color="#4ecdc4" />
      </mesh>
    </group>
  );
}

// ━━━━━ PLAYER POSITION ━━━━━
function Player({ position, number, team, name }) {
  const meshRef = useRef();
  const [hovered, setHovered] = useState(false);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.scale.lerp(
        new THREE.Vector3(hovered ? 1.5 : 1, hovered ? 1.5 : 1, hovered ? 1.5 : 1),
        0.1
      );
    }
  });

  return (
    <group position={position}>
      {/* Player sphere */}
      <mesh
        ref={meshRef}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[0.8, 32, 32]} />
        <meshStandardMaterial
          color={team === 'a' ? '#ff6b6b' : '#4ecdc4'}
          emissive={hovered ? '#ffffff' : '#000000'}
          emissiveIntensity={hovered ? 0.5 : 0}
        />
      </mesh>

      {/* Jersey number */}
      <Text position={[0, 0, 1]} fontSize={0.6} color="white">
        {number}
      </Text>

      {/* Player name on hover */}
      {hovered && (
        <Text position={[0, 2, 0]} fontSize={0.5} color="white">
          {name}
        </Text>
      )}
    </group>
  );
}

// ━━━━━ MATCH STATISTICS VISUALIZATION ━━━━━
function StatsBars({ stats }) {
  return (
    <group position={[0, 40, 0]}>
      {/* Possession bar */}
      <mesh position={[-20, 0, 0]}>
        <boxGeometry args={[stats.possession_a / 2, 2, 20]} />
        <meshStandardMaterial color="#ff6b6b" />
      </mesh>
      <mesh position={[20 - stats.possession_b / 2, 0, 0]}>
        <boxGeometry args={[stats.possession_b / 2, 2, 20]} />
        <meshStandardMaterial color="#4ecdc4" />
      </mesh>

      {/* Shots bar */}
      <mesh position={[-20, 3, 0]}>
        <boxGeometry args={[(stats.shots_a / 30) * 20, 2, 20]} />
        <meshStandardMaterial color="#ff6b6b" />
      </mesh>
      <mesh position={[20, 3, 0]}>
        <boxGeometry args={[(stats.shots_b / 30) * 20, 2, 20]} />
        <meshStandardMaterial color="#4ecdc4" />
      </mesh>
    </group>
  );
}

// ━━━━━ INTERACTIVE 3D PITCH VIEWER ━━━━━
function Pitch3DViewer({ matchData, playerPositions }) {
  return (
    <div className="pitch-3d-container">
      <Canvas>
        <PerspectiveCamera makeDefault position={[0, 50, 100]} fov={75} />
        <OrbitControls />
        
        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 20, 5]} intensity={1} />
        <pointLight position={[-52.5, 10, 0]} intensity={0.5} color="#ff6b6b" />
        <pointLight position={[52.5, 10, 0]} intensity={0.5} color="#4ecdc4" />
        
        {/* Scene */}
        <FootballPitch />
        
        {/* Players */}
        {playerPositions?.map((player, idx) => (
          <Player
            key={idx}
            position={player.position}
            number={player.number}
            team={player.team}
            name={player.name}
          />
        ))}
        
        {/* Stats */}
        {matchData && <StatsBars stats={matchData} />}
      </Canvas>
    </div>
  );
}

export default Pitch3DViewer;
