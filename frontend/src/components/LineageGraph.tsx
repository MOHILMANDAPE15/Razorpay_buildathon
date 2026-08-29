'use client';

import React, { useState, useMemo, useRef } from 'react';
import { LineageNode, LineageEdge } from '@/lib/api';
import { Sparkles, Trophy, GitBranch, ArrowRight, Eye, ShieldAlert, CheckCircle2, XCircle } from 'lucide-react';
import clsx from 'clsx';

interface LineageGraphProps {
  nodes: LineageNode[];
  edges: LineageEdge[];
  rounds: number[];
  selectedNodeId: string | null;
  onSelectNode: (node: LineageNode) => void;
}

interface NodePosition {
  x: number;
  y: number;
  width: number;
  height: number;
}

export function LineageGraph({
  nodes,
  edges,
  rounds,
  selectedNodeId,
  onSelectNode,
}: LineageGraphProps) {
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [zoom, setZoom] = useState<number>(1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Group nodes by generation round
  const nodesByRound = useMemo(() => {
    const map: { [round: number]: LineageNode[] } = {};
    rounds.forEach((r) => {
      map[r] = [];
    });
    nodes.forEach((n) => {
      const r = n.generation_round || 1;
      if (!map[r]) map[r] = [];
      if (filterStatus === 'all' || n.status === filterStatus || (filterStatus === 'champion' && n.is_champion)) {
        map[r].push(n);
      }
    });
    return map;
  }, [nodes, rounds, filterStatus]);

  // Layout calculations
  const COLUMN_WIDTH = 340;
  const COLUMN_GAP = 90;
  const NODE_HEIGHT = 165;
  const NODE_GAP = 30;
  const TOP_PADDING = 80;
  const LEFT_PADDING = 50;

  const nodePositions = useMemo(() => {
    const posMap: { [id: string]: NodePosition } = {};

    rounds.forEach((round, colIdx) => {
      const roundNodes = nodesByRound[round] || [];
      const colX = LEFT_PADDING + colIdx * (COLUMN_WIDTH + COLUMN_GAP);

      roundNodes.forEach((node, rowIdx) => {
        const nodeY = TOP_PADDING + rowIdx * (NODE_HEIGHT + NODE_GAP);
        posMap[node.id] = {
          x: colX,
          y: nodeY,
          width: COLUMN_WIDTH,
          height: NODE_HEIGHT,
        };
      });
    });

    return posMap;
  }, [nodesByRound, rounds]);

  // Calculate canvas dimensions
  const canvasWidth = useMemo(() => {
    return LEFT_PADDING * 2 + rounds.length * COLUMN_WIDTH + (rounds.length - 1) * COLUMN_GAP;
  }, [rounds]);

  const canvasHeight = useMemo(() => {
    let maxNodesInRound = 0;
    rounds.forEach((r) => {
      const count = (nodesByRound[r] || []).length;
      if (count > maxNodesInRound) maxNodesInRound = count;
    });
    return Math.max(650, TOP_PADDING + maxNodesInRound * (NODE_HEIGHT + NODE_GAP) + 100);
  }, [nodesByRound, rounds]);

  // Active lineage set for highlight
  const activeLineageNodeIds = useMemo(() => {
    const targetId = hoveredNodeId || selectedNodeId;
    if (!targetId) return null;

    const ids = new Set<string>([targetId]);
    // Find parents
    edges.forEach((e) => {
      if (e.target === targetId) ids.add(e.source);
    });
    // Find children
    edges.forEach((e) => {
      if (e.source === targetId) ids.add(e.target);
    });
    return ids;
  }, [hoveredNodeId, selectedNodeId, edges]);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden flex flex-col">
      {/* Control & Filter Toolbar */}
      <div className="p-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 bg-slate-50/70">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <span>Filter Nodes:</span>
            <div className="inline-flex rounded-lg bg-white border border-slate-200 p-0.5 shadow-xs">
              {['all', 'champion', 'alive', 'pruned'].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilterStatus(status)}
                  className={clsx(
                    'px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wider transition capitalize',
                    filterStatus === status
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  )}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Zoom & View Controls */}
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-slate-500 font-mono bg-white px-2.5 py-1 rounded-lg border border-slate-200 shadow-xs">
            <button
              onClick={() => setZoom((z) => Math.max(0.7, z - 0.1))}
              className="px-1.5 py-0.5 hover:bg-slate-100 rounded font-bold"
            >
              −
            </button>
            <span>{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom((z) => Math.min(1.3, z + 0.1))}
              className="px-1.5 py-0.5 hover:bg-slate-100 rounded font-bold"
            >
              +
            </button>
            <button
              onClick={() => setZoom(1)}
              className="text-[11px] text-indigo-600 font-semibold hover:underline ml-1"
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* DAG Interactive Canvas Viewport */}
      <div
        ref={containerRef}
        className="w-full overflow-auto relative p-4 custom-scrollbar bg-[#FAFAFA]"
        style={{ minHeight: '620px' }}
      >
        <div
          style={{
            width: `${canvasWidth * zoom}px`,
            height: `${canvasHeight * zoom}px`,
            transform: `scale(${zoom})`,
            transformOrigin: 'top left',
            position: 'relative',
          }}
          className="transition-transform duration-100 ease-out"
        >
          {/* Column Stage Headers (Round 1 to Round 5) */}
          {rounds.map((round, idx) => {
            const colX = LEFT_PADDING + idx * (COLUMN_WIDTH + COLUMN_GAP);
            return (
              <div
                key={`col_header_${round}`}
                style={{
                  position: 'absolute',
                  left: `${colX}px`,
                  top: '20px',
                  width: `${COLUMN_WIDTH}px`,
                }}
                className="flex items-center justify-between pb-2 border-b border-slate-200"
              >
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-indigo-50 border border-indigo-200 flex items-center justify-center text-xs font-bold text-indigo-700">
                    R{round}
                  </div>
                  <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Generation Round {round}
                  </span>
                </div>
                <span className="text-[11px] font-mono text-slate-500 font-medium">
                  {(nodesByRound[round] || []).length} Rules
                </span>
              </div>
            );
          })}

          {/* SVG Connection Edges */}
          <svg
            className="absolute inset-0 pointer-events-none"
            width={canvasWidth}
            height={canvasHeight}
          >
            <defs>
              {/* Arrowhead markers */}
              <marker
                id="arrowhead-default"
                viewBox="0 0 10 10"
                refX="9"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto"
              >
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#6366F1" opacity="0.6" />
              </marker>
              <marker
                id="arrowhead-active"
                viewBox="0 0 10 10"
                refX="9"
                refY="5"
                markerWidth="7"
                markerHeight="7"
                orient="auto"
              >
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669" />
              </marker>
            </defs>

            {edges.map((edge) => {
              const srcPos = nodePositions[edge.source];
              const tgtPos = nodePositions[edge.target];
              if (!srcPos || !tgtPos) return null;

              const isEdgeActive =
                activeLineageNodeIds &&
                activeLineageNodeIds.has(edge.source) &&
                activeLineageNodeIds.has(edge.target);

              // Calculate start and end coordinates
              const startX = srcPos.x + srcPos.width;
              const startY = srcPos.y + srcPos.height / 2;
              const endX = tgtPos.x;
              const endY = tgtPos.y + tgtPos.height / 2;

              // Cubic bezier control points
              const dx = endX - startX;
              const cp1X = startX + dx * 0.5;
              const cp1Y = startY;
              const cp2X = startX + dx * 0.5;
              const cp2Y = endY;

              const pathD = `M ${startX} ${startY} C ${cp1X} ${cp1Y}, ${cp2X} ${cp2Y}, ${endX} ${endY}`;

              return (
                <g key={edge.id}>
                  <path
                    d={pathD}
                    fill="none"
                    stroke={isEdgeActive ? '#059669' : '#6366F1'}
                    strokeWidth={isEdgeActive ? 3 : 1.5}
                    strokeDasharray={isEdgeActive ? 'none' : '4 4'}
                    opacity={isEdgeActive ? 1 : 0.4}
                    markerEnd={isEdgeActive ? 'url(#arrowhead-active)' : 'url(#arrowhead-default)'}
                    className={isEdgeActive ? 'transition-all duration-200' : ''}
                  />
                  {/* Subtle edge label for mutation strategy on active */}
                  {isEdgeActive && edge.mutation_strategy && (
                    <text
                      x={(startX + endX) / 2}
                      y={(startY + endY) / 2 - 8}
                      fill="#059669"
                      fontSize="10"
                      fontFamily="monospace"
                      fontWeight="bold"
                      textAnchor="middle"
                    >
                      🧬 {edge.mutation_strategy}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>

          {/* Node Cards */}
          {nodes.map((node) => {
            const pos = nodePositions[node.id];
            if (!pos) return null;

            const isSelected = selectedNodeId === node.id;
            const isHovered = hoveredNodeId === node.id;
            const isInActiveLineage = activeLineageNodeIds?.has(node.id);
            const isChampion = node.status === 'champion' || node.is_champion;
            const isPruned = node.status === 'pruned';
            const isAutonomous = node.discovery_type === 'autonomous_discovery';
            const hasParents = node.parent_ids.length > 0;

            return (
              <div
                key={node.id}
                style={{
                  position: 'absolute',
                  left: `${pos.x}px`,
                  top: `${pos.y}px`,
                  width: `${pos.width}px`,
                  height: `${pos.height}px`,
                }}
                onMouseEnter={() => setHoveredNodeId(node.id)}
                onMouseLeave={() => setHoveredNodeId(null)}
                onClick={() => onSelectNode(node)}
                className={clsx(
                  'rounded-2xl p-4 cursor-pointer transition-all duration-200 flex flex-col justify-between select-none relative group border',
                  isChampion
                    ? 'bg-emerald-50/40 border-emerald-300 shadow-sm hover:shadow-md'
                    : isAutonomous
                    ? 'bg-purple-50/40 border-purple-300 hover:border-purple-400 shadow-sm hover:shadow-md'
                    : isPruned
                    ? 'bg-rose-50/30 border-rose-200 hover:border-rose-300'
                    : hasParents
                    ? 'bg-white border-indigo-200 hover:border-indigo-400 shadow-sm hover:shadow-md'
                    : 'bg-white border-slate-200 hover:border-slate-300 shadow-xs hover:shadow-sm',
                  isSelected && 'ring-2 ring-indigo-500 ring-offset-2 ring-offset-white shadow-md',
                  isInActiveLineage && !isSelected && 'border-indigo-500 shadow-md'
                )}
              >
                {/* Node Header */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      {isChampion ? (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-100 border border-emerald-200 px-2 py-0.5 rounded-full">
                          <Trophy className="w-3 h-3 text-emerald-600" />
                          Champion
                        </span>
                      ) : isAutonomous ? (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-purple-700 bg-purple-100 border border-purple-200 px-2 py-0.5 rounded-full">
                          <Sparkles className="w-3 h-3 text-purple-600" />
                          Autonomous Discovery
                        </span>
                      ) : isPruned ? (
                        <span className="flex items-center gap-1 text-[10px] font-semibold text-rose-700 bg-rose-100 border border-rose-200 px-2 py-0.5 rounded-full">
                          <XCircle className="w-3 h-3 text-rose-600" />
                          Pruned
                        </span>
                      ) : hasParents ? (
                        <span className="flex items-center gap-1 text-[10px] font-semibold text-indigo-700 bg-indigo-100 border border-indigo-200 px-2 py-0.5 rounded-full">
                          <Sparkles className="w-3 h-3 text-indigo-600" />
                          Mutated
                        </span>
                      ) : (
                        <span className="text-[10px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
                          R{node.generation_round} Candidate
                        </span>
                      )}

                      <span className="text-[10px] font-mono text-slate-500 truncate">{node.id}</span>
                    </div>

                    <h4 className="text-xs font-bold text-slate-900 truncate group-hover:text-indigo-600 transition">
                      {node.name}
                    </h4>
                  </div>
                </div>


                {/* Target Signal & Strategy preview */}
                <div className="text-[11px] text-slate-600 line-clamp-2 my-1 leading-snug font-normal">
                  {node.description || node.rationale || 'Vectorized Python fraud rule hypothesis.'}
                </div>

                {/* Bottom Metric Pill */}
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-mono">
                  {node.metrics ? (
                    <>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-500">
                          P: <strong className="text-slate-800">{(node.metrics.precision * 100).toFixed(0)}%</strong>
                        </span>
                        <span className="text-slate-500">
                          R: <strong className="text-slate-800">{(node.metrics.recall * 100).toFixed(1)}%</strong>
                        </span>
                      </div>
                      <div
                        className={clsx(
                          'font-bold',
                          node.metrics.net_financial_savings_inr >= 0 ? 'text-emerald-600' : 'text-rose-600'
                        )}
                      >
                        ₹{node.metrics.net_financial_savings_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                      </div>
                    </>
                  ) : (
                    <span className="text-slate-400 text-[10px] italic">Awaiting evaluation report</span>
                  )}
                </div>

                {/* Inspect Action Hint on Hover */}
                <div className="absolute right-3 bottom-3 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-[10px] font-semibold text-indigo-700 bg-white px-2 py-0.5 rounded-md border border-indigo-200 shadow-xs">
                  <Eye className="w-3 h-3 text-indigo-600" />
                  Inspect
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
