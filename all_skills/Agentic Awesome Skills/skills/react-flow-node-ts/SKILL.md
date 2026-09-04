---
name: react-flow-node-ts
description: "Build custom, type-safe node and edge components for React Flow (@xyflow/react). Use when designing node handles, reactive connection logic, drag-and-drop workflow canvases, and custom node data interfaces in TypeScript."
risk: safe
source: community
---
# React Flow Custom Node Architecture (TypeScript)

## When to Use
- Creating custom node types with typed data contracts in React Flow / `@xyflow/react`.
- Configuring source and target `<Handle>` connections with validation rules.
- Building interactive graph and workflow canvases in React/Next.js.

## Custom Node Implementation Pattern

```tsx
import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';

export interface CustomNodeData {
  label: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  value?: number;
}

export type CustomNodeType = Node<CustomNodeData, 'customStep'>;

export const CustomStepNode = memo(({ data, isConnectable }: NodeProps<CustomNodeType>) => {
  return (
    <div className={`flow-node status-${data.status}`}>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="handle-target"
      />

      <div className="node-content">
        <span className="node-title">{data.label}</span>
        <span className="node-badge">{data.status}</span>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        className="handle-source"
      />
    </div>
  );
});

CustomStepNode.displayName = 'CustomStepNode';
```

## Node Registration
```tsx
import { ReactFlow } from '@xyflow/react';
import { CustomStepNode } from './CustomStepNode';

const nodeTypes = {
  customStep: CustomStepNode,
};

export function WorkflowCanvas() {
  return <ReactFlow nodes={initialNodes} edges={initialEdges} nodeTypes={nodeTypes} />;
}
```
