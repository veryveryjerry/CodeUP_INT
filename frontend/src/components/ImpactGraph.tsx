import React, { useCallback, useMemo } from 'react';
import ReactFlow, { 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  MarkerType,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';

// Custom Node to support tailwind classes
const CustomNode = ({ data }: any) => {
  const getColors = () => {
    switch (data.impactLevel) {
      case 'direct': return 'bg-red-950 border-red-500 text-red-100';
      case 'indirect': return 'bg-orange-950 border-orange-500 text-orange-100';
      case 'safe': return 'bg-green-950 border-green-500 text-green-100';
      default: return 'bg-gray-800 border-gray-600 text-gray-200';
    }
  };

  return (
    <div className={`px-4 py-2 shadow-md rounded-md border-2 text-xs font-mono min-w-[150px] text-center ${getColors()}`}>
      <Handle type="target" position={Position.Top} className="!bg-gray-500 w-2 h-2" />
      <div>{data.label}</div>
      {data.impactLevel && (
        <div className="text-[10px] mt-1 opacity-80 uppercase font-sans">
          {data.impactLevel} Impact
        </div>
      )}
      <Handle type="source" position={Position.Bottom} className="!bg-gray-500 w-2 h-2" />
    </div>
  );
};

const nodeTypes = {
  custom: CustomNode,
};

const initialNodes = [
  { id: '1', type: 'custom', position: { x: 250, y: 50 }, data: { label: 'AuthService.ts', impactLevel: 'safe' } },
  { id: '2', type: 'custom', position: { x: 100, y: 150 }, data: { label: 'UserController.ts', impactLevel: 'indirect' } },
  { id: '3', type: 'custom', position: { x: 400, y: 150 }, data: { label: 'SessionManager.ts', impactLevel: 'direct' } },
  { id: '4', type: 'custom', position: { x: 250, y: 250 }, data: { label: 'TokenUtils.ts', impactLevel: 'direct' } },
  { id: '5', type: 'custom', position: { x: 400, y: 350 }, data: { label: 'CryptoHelper.ts', impactLevel: 'safe' } },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#9ca3af' } },
  { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#ef4444', strokeWidth: 2 } },
  { id: 'e3-4', source: '3', target: '4', animated: true, style: { stroke: '#ef4444', strokeWidth: 2 } },
  { id: 'e4-5', source: '4', target: '5', style: { stroke: '#9ca3af' } },
];

export default function ImpactGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="w-full h-full bg-gray-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        className="dark-theme-flow"
      >
        <Background color="#374151" gap={16} />
        <Controls className="!bg-gray-900 !border-gray-700 !fill-gray-300" />
      </ReactFlow>
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-gray-900/80 p-3 rounded-lg border border-gray-700 text-xs flex flex-col gap-2 backdrop-blur-sm z-10">
        <div className="font-semibold text-gray-300 mb-1">Impact Legend</div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-red-500 border border-red-400"></div>
          <span className="text-gray-300">Direct Change</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-orange-500 border border-orange-400"></div>
          <span className="text-gray-300">Affected Dependency</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-green-500 border border-green-400"></div>
          <span className="text-gray-300">Safe / Unaffected</span>
        </div>
      </div>
    </div>
  );
}
