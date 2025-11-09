'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import axios from 'axios'
import Header from '@/components/Header'
import { GameEngine } from '@/components/GameEngine'
import type { GameBlueprint } from '@/types/gameBlueprint'

interface GameState {
  currentQuestion: number
  totalQuestions: number
  score: number
  answers: Array<{
    questionNumber: number
    selectedAnswer: string
    isCorrect: boolean
  }>
}

export default function GamePage() {
  const router = useRouter()
  const [blueprint, setBlueprint] = useState<GameBlueprint | null>(null)
  const [visualizationHtml, setVisualizationHtml] = useState<string>('')
  const [visualizationType, setVisualizationType] = useState<'blueprint' | 'html'>('html')
  const [loading, setLoading] = useState(true)
  const [gameState, setGameState] = useState<GameState>({
    currentQuestion: 0,
    totalQuestions: 0,
    score: 0,
    answers: [],
  })
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)

  useEffect(() => {
    const visualizationId = localStorage.getItem('visualizationId')
    if (!visualizationId) {
      router.push('/app')
      return
    }

    const fetchVisualization = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await axios.get(`${apiUrl}/api/visualization/${visualizationId}`)
        
        if (response.data.type === 'blueprint' && response.data.blueprint) {
          // New blueprint-based visualization
          setBlueprint(response.data.blueprint.blueprint as GameBlueprint)
          setVisualizationType('blueprint')
        } else if (response.data.html) {
          // Legacy HTML visualization
          setVisualizationHtml(response.data.html)
          setVisualizationType('html')
          
          // Extract question data from the visualization
          const questionData = response.data.question_data
          setGameState({
            currentQuestion: 0,
            totalQuestions: questionData?.question_flow?.length || 1,
            score: 0,
            answers: [],
          })
        }
      } catch (error) {
        console.error('Failed to fetch visualization:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchVisualization()
  }, [router])

  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswer(answer)
  }

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer) return

    // Get correct answer from visualization data
    const visualizationId = localStorage.getItem('visualizationId')
    try {
      const response = await axios.post(`/api/check-answer/${visualizationId}`, {
        questionNumber: gameState.currentQuestion + 1,
        selectedAnswer,
      })

      const correct = response.data.is_correct
      setIsCorrect(correct)

      const newScore = correct ? gameState.score + 1 : gameState.score
      const newAnswers = [
        ...gameState.answers,
        {
          questionNumber: gameState.currentQuestion + 1,
          selectedAnswer,
          isCorrect: correct,
        },
      ]

      setGameState({
        ...gameState,
        score: newScore,
        answers: newAnswers,
      })

      setShowFeedback(true)

      // Auto-advance after 2 seconds
      setTimeout(() => {
        if (gameState.currentQuestion + 1 < gameState.totalQuestions) {
          setGameState({
            ...gameState,
            currentQuestion: gameState.currentQuestion + 1,
            score: newScore,
            answers: newAnswers,
          })
          setSelectedAnswer(null)
          setShowFeedback(false)
        } else {
          // Game complete, navigate to score page
          localStorage.setItem('finalScore', newScore.toString())
          localStorage.setItem('totalQuestions', gameState.totalQuestions.toString())
          router.push('/app/score')
        }
      }, 2000)
    } catch (error) {
      console.error('Failed to check answer:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white to-[#FFFEF9] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-brilliant-green" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-[#FFFEF9]">
      <Header />
      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-black">
                Question {gameState.currentQuestion + 1} of {gameState.totalQuestions}
              </span>
              <span className="text-sm font-semibold text-brilliant-green">
                Score: {gameState.score}/{gameState.totalQuestions}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-brilliant-green h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{
                  width: `${((gameState.currentQuestion + 1) / gameState.totalQuestions) * 100}%`,
                }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          {/* Visualization Container */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-8"
          >
            {visualizationType === 'blueprint' && blueprint ? (
              <GameEngine blueprint={blueprint} />
            ) : (
              <div
                className="visualization-container w-full"
                dangerouslySetInnerHTML={{ __html: visualizationHtml }}
              />
            )}
          </motion.div>

          {/* Feedback */}
          {showFeedback && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`mb-8 p-6 rounded-2xl ${
                isCorrect ? 'bg-mint-green' : 'bg-red-50'
              } flex items-center gap-4`}
            >
              {isCorrect ? (
                <CheckCircle2 className="w-8 h-8 text-brilliant-green" />
              ) : (
                <XCircle className="w-8 h-8 text-red-500" />
              )}
              <div>
                <p className={`font-semibold text-lg ${isCorrect ? 'text-brilliant-green' : 'text-red-700'}`}>
                  {isCorrect ? 'Correct!' : 'Incorrect'}
                </p>
                <p className={`text-sm ${isCorrect ? 'text-green-700' : 'text-red-600'}`}>
                  {isCorrect
                    ? 'Great job! Moving to next question...'
                    : "Don't worry, let's continue..."}
                </p>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}

