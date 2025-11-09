'use client'

import type { ParameterPlaygroundBlueprint } from '@/types/gameBlueprint'

export function ParameterPlaygroundGame({ blueprint }: { blueprint: ParameterPlaygroundBlueprint }) {
  return (
    <div id="gameRoot" className="flex flex-col gap-4 p-6">
      <h2 className="text-xl font-bold">{blueprint.title}</h2>
      <p className="text-gray-600">{blueprint.narrativeIntro}</p>
      <div className="flex gap-4">
        <div id="parametersPanel" className="w-64 space-y-4">
          {blueprint.parameters.map(param => (
            <div key={param.id}>
              <label className="block mb-1">{param.label}</label>
              {param.type === 'slider' && (
                <input
                  type="range"
                  min={param.min}
                  max={param.max}
                  defaultValue={param.defaultValue as number}
                  className="w-full"
                />
              )}
            </div>
          ))}
        </div>
        <div id="visualizationArea" className="flex-1 border rounded p-4">
          {blueprint.visualization.assetUrl && (
            <img src={blueprint.visualization.assetUrl} alt="Visualization" />
          )}
        </div>
      </div>
    </div>
  )
}

