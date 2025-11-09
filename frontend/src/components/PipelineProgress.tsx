'use client'

import React, { useEffect } from 'react'
import { usePipelineStore } from '@/stores/pipelineStore'
import StepStatus from './StepStatus'
import axios from 'axios'

interface PipelineProgressProps {
  processId: string
  onComplete?: (visualizationId: string) => void
  onError?: (error: string) => void
}

export default function PipelineProgress({
  processId,
  onComplete,
  onError,
}: PipelineProgressProps) {
  const {
    status,
    progress,
    currentStep,
    steps,
    visualizationId,
    errorMessage,
    setStatus,
    setProgress,
    setCurrentStep,
    setSteps,
    setVisualizationId,
    setErrorMessage,
  } = usePipelineStore()

  useEffect(() => {
    if (!processId) {
      console.log('[PipelineProgress] No processId provided, skipping polling')
      return
    }

    console.log('[PipelineProgress] Starting to poll progress for process:', processId)

    const pollProgress = async () => {
      try {
        console.log('[PipelineProgress] Polling progress for process:', processId)
        const response = await axios.get(`/api/progress/${processId}`)
        const data = response.data

        console.log('[PipelineProgress] Progress update:', {
          status: data.status,
          progress: data.progress,
          current_step: data.current_step,
          visualization_id: data.visualization_id,
          steps_count: data.steps?.length || 0
        })

        setStatus(data.status as any)
        setProgress(data.progress)
        setCurrentStep(data.current_step)
        setSteps(data.steps || [])
        
        if (data.visualization_id) {
          console.log('[PipelineProgress] Visualization ID received:', data.visualization_id)
          setVisualizationId(data.visualization_id)
        }
        
        if (data.error_message) {
          console.error('[PipelineProgress] Error message:', data.error_message)
          setErrorMessage(data.error_message)
        }

        // Handle completion
        if (data.status === 'completed') {
          console.log('[PipelineProgress] Process completed!', {
            visualization_id: data.visualization_id,
            has_onComplete: !!onComplete
          })
          if (data.visualization_id && onComplete) {
            console.log('[PipelineProgress] Calling onComplete with visualization_id:', data.visualization_id)
            onComplete(data.visualization_id)
          } else if (!data.visualization_id) {
            console.warn('[PipelineProgress] Process completed but no visualization_id!')
          }
        }

        // Handle error
        if (data.status === 'error' || data.status === 'failed') {
          console.error('[PipelineProgress] Process failed:', data.error_message)
          if (onError) {
            onError(data.error_message || 'Processing failed')
          }
        }
      } catch (error: any) {
        // Handle socket hang up errors (backend restarting) gracefully
        if (error.code === 'ECONNRESET' || error.message?.includes('socket hang up')) {
          console.warn('[PipelineProgress] Backend connection reset (likely restarting), will retry on next poll')
          return // Don't call onError for connection resets, just retry
        }
        
        console.error('[PipelineProgress] Failed to fetch progress:', error)
        if (error.response) {
          console.error('[PipelineProgress] Error response:', error.response.status, error.response.data)
          // Only call onError for actual errors, not connection issues
          if (error.response.status >= 500 && onError) {
            onError(`Server error: ${error.response.status}`)
          }
        } else if (onError && !error.code) {
          // Only call onError if it's not a connection error
          onError(error.message || 'Failed to fetch progress')
        }
      }
    }

    // Poll immediately, then every 2 seconds
    pollProgress()
    const interval = setInterval(pollProgress, 2000)

    return () => clearInterval(interval)
  }, [processId, onComplete, onError, setStatus, setProgress, setCurrentStep, setSteps, setVisualizationId, setErrorMessage])

  const handleRetry = async (stepId: string) => {
    try {
      await axios.post(`/api/pipeline/retry/${stepId}`)
      // Progress will update on next poll
    } catch (error: any) {
      console.error('Failed to retry step:', error)
    }
  }

  const getLayerName = (stepNumber: number) => {
    if (stepNumber <= 2) return 'Layer 1: Input & Document Processing'
    if (stepNumber === 3) return 'Layer 2: Intent Recognition & Classification'
    if (stepNumber === 4) return 'Layer 3: Gamification Strategy Engine'
    if (stepNumber >= 5) return 'Layer 4: Multi-Modal Content Generation'
    return 'Pipeline'
  }

  // Group steps by layer
  const stepsByLayer = steps.reduce((acc, step) => {
    const layer = getLayerName(step.step_number)
    if (!acc[layer]) acc[layer] = []
    acc[layer].push(step)
    return acc
  }, {} as Record<string, typeof steps>)

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Overall Progress */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Processing Pipeline</h2>
          <span className="text-sm font-medium text-gray-600">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-[#00A67E] h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        {currentStep && (
          <p className="mt-2 text-sm text-gray-600">Current: {currentStep}</p>
        )}
        {errorMessage && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            {errorMessage}
          </div>
        )}
      </div>

      {/* Steps by Layer */}
      <div className="space-y-6">
        {Object.entries(stepsByLayer).map(([layerName, layerSteps]) => (
          <div key={layerName} className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{layerName}</h3>
            <div className="space-y-3">
              {layerSteps.map((step) => (
                <StepStatus
                  key={step.id}
                  stepName={step.step_name}
                  stepNumber={step.step_number}
                  status={step.status}
                  errorMessage={step.error_message}
                  retryCount={step.retry_count}
                  startedAt={step.started_at}
                  completedAt={step.completed_at}
                  validationResult={step.validation_result}
                  onRetry={() => handleRetry(step.id)}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Empty state */}
      {steps.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>Waiting for pipeline to start...</p>
        </div>
      )}
    </div>
  )
}

