'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Upload, FileText, Loader2 } from 'lucide-react'
import axios from 'axios'
import Header from '@/components/Header'

export default function UploadPage() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Store the question ID for preview
      localStorage.setItem('questionId', response.data.question_id)
      router.push('/app/preview')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-[#FFFEF9]">
      <Header />
      <div className="pt-32 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl md:text-5xl font-bold text-black mb-4">
              Upload Your Question
            </h1>
            <p className="text-body-lg text-body-gray max-w-2xl mx-auto">
              Upload a PDF, DOCX, or text file containing your question. We&apos;ll transform it into an interactive learning experience.
            </p>
          </motion.div>

          {/* Upload Zone */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
              file
                ? 'border-brilliant-green bg-mint-green/20'
                : 'border-gray-300 hover:border-vibrant-blue'
            }`}
          >
            {file ? (
              <div className="space-y-4">
                <FileText className="w-16 h-16 text-brilliant-green mx-auto" />
                <p className="text-lg font-semibold text-black">{file.name}</p>
                <p className="text-sm text-muted-gray">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
                <button
                  onClick={() => setFile(null)}
                  className="text-sm text-muted-gray hover:text-black"
                >
                  Choose different file
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="w-16 h-16 text-gray-400 mx-auto" />
                <div>
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer inline-block px-6 py-3 rounded-full bg-brilliant-green text-white font-semibold hover:scale-105 transition-transform"
                  >
                    Choose File
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".pdf,.docx,.txt,.md"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>
                <p className="text-sm text-muted-gray">
                  or drag and drop your file here
                </p>
                <p className="text-xs text-muted-gray">
                  Supports PDF, DOCX, TXT, and Markdown files
                </p>
              </div>
            )}
          </motion.div>

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-center"
            >
              {error}
            </motion.div>
          )}

          {/* Upload Button */}
          {file && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 text-center"
            >
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="px-8 py-4 rounded-full bg-brilliant-green text-white font-semibold text-lg hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Processing...
                  </>
                ) : (
                  'Upload & Process'
                )}
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}

