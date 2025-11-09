'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { CheckCircle2, ArrowRight, Loader2 } from 'lucide-react'
import axios from 'axios'
import Header from '@/components/Header'

interface Question {
  id: string
  text: string
  options?: string[]
  correct_answer?: string
  story?: {
    story_title: string
    story_context: string
    question_flow: Array<{
      question_number: number
      intuitive_question: string
      answer_structure: {
        options: string[]
        correct_answer: string
      }
    }>
  }
}

export default function PreviewPage() {
  const router = useRouter()
  const [question, setQuestion] = useState<Question | null>(null)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const questionId = localStorage.getItem('questionId')
    if (!questionId) {
      router.push('/app')
      return
    }

    // Fetch question details
    const fetchQuestion = async () => {
      try {
        const response = await axios.get(`/api/questions/${questionId}`)
        setQuestion(response.data)
      } catch (error) {
        console.error('Failed to fetch question:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchQuestion()
  }, [router])

  const handleStartGame = async () => {
    if (!question) {
      console.error('[Start Game] No question available')
      return
    }

    console.log('[Start Game] Button clicked - Starting interactive game generation')
    setProcessing(true)
    const questionId = localStorage.getItem('questionId')
    
    if (!questionId) {
      console.error('[Start Game] No questionId found in localStorage')
      alert('Question ID not found. Please upload a question first.')
      setProcessing(false)
      return
    }

    console.log('[Start Game] Question ID:', questionId)

    try {
      // Start processing pipeline
      console.log('[Start Game] Calling /api/process endpoint...')
      const processResponse = await axios.post(`/api/process/${questionId}`)
      const processId = processResponse.data.process_id
      console.log('[Start Game] Process started with ID:', processId)

      // Poll for progress
      let pollCount = 0
      const maxPolls = 300 // 10 minutes max (300 * 2 seconds)
      const progressInterval = setInterval(async () => {
        pollCount++
        try {
          console.log(`[Start Game] Polling progress (attempt ${pollCount})...`)
          const progressResponse = await axios.get(`/api/progress/${processId}`)
          const progressData = progressResponse.data

          console.log('[Start Game] Progress update:', {
            status: progressData.status,
            progress: progressData.progress,
            step: progressData.current_step,
            error: progressData.error_message
          })

          setProgress(progressData.progress)

          if (progressData.status === 'completed') {
            console.log('[Start Game] Processing completed! Visualization ID:', progressData.visualization_id)
            clearInterval(progressInterval)
            localStorage.setItem('visualizationId', progressData.visualization_id)
            router.push('/app/game')
          } else if (progressData.status === 'error') {
            console.error('[Start Game] Processing failed:', progressData.error_message)
            clearInterval(progressInterval)
            const errorMsg = progressData.error_message || 'Processing failed. Please try again.'
            alert(`Processing failed: ${errorMsg}`)
            setProcessing(false)
          } else if (pollCount >= maxPolls) {
            console.error('[Start Game] Max polling attempts reached')
            clearInterval(progressInterval)
            alert('Processing is taking too long. Please try again.')
            setProcessing(false)
          }
        } catch (error: any) {
          console.error('[Start Game] Progress check failed:', error)
          console.error('[Start Game] Error details:', {
            message: error.message,
            response: error.response?.data,
            status: error.response?.status
          })
          if (pollCount >= 5) {
            clearInterval(progressInterval)
            alert(`Failed to check progress: ${error.response?.data?.detail || error.message}`)
            setProcessing(false)
          }
        }
      }, 2000) // Poll every 2 seconds
    } catch (error: any) {
      console.error('[Start Game] Failed to start processing:', error)
      console.error('[Start Game] Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to start processing'
      alert(`Failed to start processing: ${errorMsg}`)
      setProcessing(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white to-[#FFFEF9] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-brilliant-green" />
      </div>
    )
  }

  if (!question) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white to-[#FFFEF9] flex items-center justify-center">
        <p className="text-body-gray">Question not found</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-[#FFFEF9]">
      <Header />
      <div className="pt-32 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-4xl md:text-5xl font-bold text-black mb-4">
              Question Preview
            </h1>
            <p className="text-body-lg text-body-gray">
              Review your question before we transform it into an interactive game
            </p>
          </motion.div>

          {/* Question Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-8"
          >
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-black mb-4">Question</h2>
                <p className="text-body-lg text-body-gray leading-relaxed">
                  {question.text}
                </p>
              </div>

              {question.options && question.options.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold text-black mb-3">Options</h3>
                  <ul className="space-y-2">
                    {question.options.map((option, index) => (
                      <li
                        key={index}
                        className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
                      >
                        <span className="font-semibold text-vibrant-blue">
                          {String.fromCharCode(65 + index)}.
                        </span>
                        <span className="text-body-gray">{option}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {question.story && (
                <div className="mt-6 p-6 bg-light-lavender rounded-lg">
                  <h3 className="text-xl font-semibold text-black mb-2">
                    {question.story.story_title}
                  </h3>
                  <p className="text-body-gray leading-relaxed mb-4">
                    {question.story.story_context}
                  </p>
                  <div className="space-y-3">
                    {question.story.question_flow.map((q) => (
                      <div key={q.question_number} className="flex items-start gap-3">
                        <CheckCircle2 className="w-5 h-5 text-brilliant-green mt-1 flex-shrink-0" />
                        <div>
                          <p className="font-semibold text-black">{q.intuitive_question}</p>
                          <p className="text-sm text-muted-gray mt-1">
                            {q.answer_structure.options.length} options
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>

          {/* Progress Indicator */}
          {processing && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-8"
            >
              <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-lg font-semibold text-black">
                    Processing your question...
                  </span>
                  <span className="text-sm text-muted-gray">{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    className="bg-brilliant-green h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
                <p className="text-sm text-muted-gray mt-4">
                  {progress < 30 && 'Analyzing question...'}
                  {progress >= 30 && progress < 60 && 'Generating story...'}
                  {progress >= 60 && progress < 90 && 'Creating visualization...'}
                  {progress >= 90 && 'Finalizing...'}
                </p>
              </div>
            </motion.div>
          )}

          {/* Start Game Button */}
          {!processing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-center"
            >
              <button
                onClick={handleStartGame}
                className="px-8 py-4 rounded-full bg-brilliant-green text-white font-semibold text-lg hover:scale-105 transition-transform flex items-center gap-2 mx-auto"
              >
                Start Interactive Game
                <ArrowRight className="w-5 h-5" />
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}

