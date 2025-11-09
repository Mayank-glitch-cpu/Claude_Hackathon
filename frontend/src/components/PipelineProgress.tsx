'use client'

import React, { useEffect, useState } from 'react'
import { usePipelineStore } from '@/stores/pipelineStore'
import axios from 'axios'

interface PipelineProgressProps {
  processId: string
  onComplete?: (visualizationId: string) => void
  onError?: (error: string) => void
}

const PROCESS_STEPS = [
  'Data Extraction',
  'Prompt Selection',
  'Content Analysis',
  'Template Matching',
  'Story Generation',
  'Blueprint Creation',
  'Asset Planning',
  'Final Assembly'
]

export default function PipelineProgress({
  processId,
  onComplete,
  onError,
}: PipelineProgressProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [stepProgress, setStepProgress] = useState(0)
  const [isPaused, setIsPaused] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)
  const [showAnalysis, setShowAnalysis] = useState(false)
  
  // Generate random durations - all steps 10-12 seconds, Final Assembly 14-22 seconds
  const [stepDurations] = useState(() => {
    return PROCESS_STEPS.map((_, index) => {
      if (index === PROCESS_STEPS.length - 1) {
        // Final Assembly: 14-22 seconds (10-12 base + 4-10 extra)
        return 14000 + Math.random() * 8000
      }
      // All other steps: 10-12 seconds
      return 10000 + Math.random() * 2000
    })
  })
  
  // Pause durations between steps (0.5-1.5 seconds)
  const [pauseDurations] = useState(() => 
    PROCESS_STEPS.map(() => 500 + Math.random() * 1000)
  )

  useEffect(() => {
    if (!processId) return

    let progressInterval: NodeJS.Timeout
    let pauseTimeout: NodeJS.Timeout
    let isCancelled = false
    let backendCompleted = false

    // Poll for completion in the background
    const pollForCompletion = async () => {
      try {
        const response = await axios.get(`/api/progress/${processId}`, { timeout: 5000 })
        const data = response.data

        if (data.status === 'completed' && data.visualization_id) {
          backendCompleted = true
          setIsCompleted(true)
          // Complete the animation if not already done
          setCurrentStepIndex(PROCESS_STEPS.length - 1)
          setStepProgress(100)
          if (onComplete) {
            setTimeout(() => onComplete(data.visualization_id), 500)
          }
        } else if (data.status === 'error' && onError) {
          onError(data.error_message || 'Processing failed')
        }
      } catch (error) {
        // Silently handle errors - just continue polling
      }
    }

    const completionInterval = setInterval(pollForCompletion, 2000)

    // Animate through steps with random durations and pauses
    const startStepAnimation = (stepIndex: number) => {
      if (isCancelled || stepIndex >= PROCESS_STEPS.length) {
        return
      }

      // If completed by backend, finish the animation
      if (backendCompleted) {
        setCurrentStepIndex(PROCESS_STEPS.length - 1)
        setStepProgress(100)
        return
      }

      setCurrentStepIndex(stepIndex)
      setStepProgress(0)
      setIsPaused(false)

      // Animate progress within this step
      const duration = stepDurations[stepIndex]
      const startTime = Date.now()
      
      progressInterval = setInterval(() => {
        if (isCancelled || backendCompleted) {
          clearInterval(progressInterval)
          if (backendCompleted) {
            setCurrentStepIndex(PROCESS_STEPS.length - 1)
            setStepProgress(100)
          }
          return
        }

        const elapsed = Date.now() - startTime
        const progress = Math.min(100, (elapsed / duration) * 100)
        setStepProgress(progress)

        if (progress >= 100) {
          clearInterval(progressInterval)
          
          // Check if backend completed while this step was running
          if (backendCompleted) {
            setCurrentStepIndex(PROCESS_STEPS.length - 1)
            setStepProgress(100)
            return
          }
          
          // Add pause before next step
          setIsPaused(true)
          const pauseDuration = pauseDurations[stepIndex]
          
          pauseTimeout = setTimeout(() => {
            if (!isCancelled && !backendCompleted) {
              startStepAnimation(stepIndex + 1)
            } else if (backendCompleted) {
              setCurrentStepIndex(PROCESS_STEPS.length - 1)
              setStepProgress(100)
            }
          }, pauseDuration)
        }
      }, 50)
    }

    // Start animation
    startStepAnimation(0)

    return () => {
      isCancelled = true
      clearInterval(completionInterval)
      clearInterval(progressInterval)
      clearTimeout(pauseTimeout)
    }
  }, [processId, onComplete, onError, stepDurations, pauseDurations])

  // Show Analysis section after Data Extraction completes (when moving to Prompt Selection)
  useEffect(() => {
    if (currentStepIndex >= 1) {
      setShowAnalysis(true)
    }
  }, [currentStepIndex])

  const overallProgress = isCompleted 
    ? 100 
    : ((currentStepIndex + stepProgress / 100) / PROCESS_STEPS.length) * 100

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm p-6">
        {/* Simple horizontal line with progress */}
        <div className="relative w-full h-2 bg-gray-300 rounded-full overflow-hidden">
          <div
            className={`absolute left-0 top-0 h-full bg-gray-600 rounded-full transition-all duration-300 ${
              isPaused ? 'ease-in-out' : 'ease-linear'
            }`}
            style={{ width: `${overallProgress}%` }}
          />
        </div>

        {/* Current step text */}
        {currentStepIndex < PROCESS_STEPS.length && !isCompleted && (
          <p className="mt-4 text-sm text-gray-600 text-center">
            {PROCESS_STEPS[currentStepIndex]}...
          </p>
        )}
        {isCompleted && (
          <p className="mt-4 text-sm text-green-600 text-center font-medium">
            Processing complete!
          </p>
        )}
      </div>

      {/* Analysis Section - Rendered after Data Extraction */}
      {showAnalysis && (
        <div className="bg-blue-50 rounded-lg shadow-sm p-6 mt-4">
          <h2 className="text-xl font-bold text-black mb-4">Analysis</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-700 mb-1">
                <span className="font-medium">Type:</span> coding
              </p>
              <p className="text-sm text-gray-700 mb-1">
                <span className="font-medium">Difficulty:</span> advanced
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-700 mb-1">
                <span className="font-medium">Subject:</span> Computer Science
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-700 mt-2">
            <span className="font-medium">Key Concepts:</span> Array, Indexing, Searching, Target
          </p>
        </div>
      )}
    </div>
  )
}
