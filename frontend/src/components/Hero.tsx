'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { BarChart3, TrendingUp, Code, Brain, Atom } from 'lucide-react'

const categoryIcons = [
  { icon: BarChart3, label: 'Math', color: 'text-vibrant-blue' },
  { icon: TrendingUp, label: 'Data Analysis', color: 'text-warm-orange' },
  { icon: Code, label: 'Computer Science', color: 'text-deep-purple' },
  { icon: Brain, label: 'Programming & AI', color: 'text-deep-purple' },
  { icon: Atom, label: 'Science & Engineering', color: 'text-golden-yellow' },
]

// Bar Chart Component for "Solve"
const BarChart = () => {
  const bars = [
    { height: 12, color: '#A78BFA' }, // purple
    { height: 22, color: '#A78BFA' }, // purple
    { height: 32, color: '#A78BFA' }, // purple - tallest
    { height: 25, color: '#E5E7EB' }, // gray
  ]
  
  const baseY = 50
  const tallestBarIndex = 2
  
  return (
    <svg width="200" height="80" viewBox="0 0 200 80" className="absolute left-0" style={{ top: '-5px' }}>
      {bars.map((bar, i) => (
        <rect
          key={i}
          x={25 + i * 30}
          y={80 - bar.height * 1.5}
          width={18}
          height={bar.height * 1.5}
          fill={bar.color}
          rx={2}
        />
      ))}
      {/* Percentage label on tallest bar */}
      <rect x={25 + tallestBarIndex * 30 - 10} y={80 - 32 * 1.5 - 18} width="32" height="14" fill="#A78BFA" rx="2" />
      <text x={25 + tallestBarIndex * 30 + 9} y={80 - 32 * 1.5 - 6} fontSize="11" fill="white" fontWeight="bold" textAnchor="middle">71%</text>
      {/* Dashed line from tallest bar to scale */}
      <line
        x1={34 + tallestBarIndex * 30}
        y1={80 - 32 * 1.5}
        x2={34 + tallestBarIndex * 30}
        y2={80 + 5}
        stroke="#000"
        strokeWidth="1.5"
        strokeDasharray="3,3"
      />
      {/* Interactive slider circle */}
      <circle
        cx={34 + tallestBarIndex * 30}
        cy={80 - 32 * 1.5 - 12}
        r="10"
        fill="white"
        stroke="#000"
        strokeWidth="1.5"
      />
      <path
        d="M 29 3 L 29 11 M 39 3 L 39 11"
        stroke="#000"
        strokeWidth="2"
        strokeLinecap="round"
        transform={`translate(${tallestBarIndex * 30 + 9}, ${80 - 32 * 1.5 - 12})`}
      />
    </svg>
  )
}

// Scatter Plot Component for "Solve"
const ScatterPlot = () => {
  // Generate points with upward trend (deterministic)
  const points = Array.from({ length: 25 }, (_, i) => {
    const progress = i / 24
    // Use a simple hash function for deterministic "random" variation
    const variation = ((i * 7 + 13) % 16 - 8) * 0.5
    return {
      x: 20 + progress * 100,
      y: 40 - progress * 25 + variation,
    }
  })
  
  // Trend line points
  const trendPoints = points.map(p => `${p.x},${p.y}`).join(' ')
  
  return (
    <svg width="200" height="80" viewBox="0 0 200 80" className="absolute right-0" style={{ top: '-5px' }}>
      {/* Trend line */}
      <polyline
        points={points.map(p => `${p.x * 1.4},${p.y * 1.6}`).join(' ')}
        fill="none"
        stroke="#FB923C"
        strokeWidth="2"
      />
      {/* Scatter points */}
      {points.map((point, i) => (
        <circle
          key={i}
          cx={point.x * 1.4}
          cy={point.y * 1.6}
          r={i === points.length - 1 ? 7 : 3.5}
          fill={i === points.length - 1 ? '#FB923C' : '#FED7AA'}
          stroke={i === points.length - 1 ? 'white' : 'none'}
          strokeWidth={i === points.length - 1 ? 2.5 : 0}
          style={{ filter: i === points.length - 1 ? 'drop-shadow(0 0 5px rgba(251, 146, 60, 0.7))' : 'none' }}
        />
      ))}
    </svg>
  )
}

// Code Blocks Component for "By Seeing"
const CodeBlocks = () => {
  return (
    <div className="absolute left-0 flex flex-col gap-1.5" style={{ top: '-30px' }}>
      {/* while learning block */}
      <div className="flex items-center bg-gray-100 rounded-lg px-3 py-1.5 text-xs shadow-sm">
        <svg width="14" height="14" viewBox="0 0 14 14" className="mr-1.5">
          <circle cx="7" cy="7" r="6" fill="none" stroke="#6366F1" strokeWidth="1.5"/>
          <path d="M7 3 L9 7 L7 11 M9 7 L5 7" stroke="#6366F1" strokeWidth="1.5" fill="none" strokeLinecap="round"/>
        </svg>
        <span className="bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded mr-1.5 font-medium">while</span>
        <span className="text-gray-700">learning</span>
        <svg width="10" height="10" viewBox="0 0 10 10" className="ml-1.5">
          <path d="M2 2 L5 5 L2 8" stroke="#666" strokeWidth="1.2" fill="none"/>
        </svg>
      </div>
      {/* if doing block */}
      <div className="flex items-center bg-gray-100 rounded-lg px-3 py-1.5 text-xs shadow-sm ml-6">
        <span className="bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded mr-1.5 font-medium">if</span>
        <span className="text-gray-700">doing</span>
        <svg width="10" height="10" viewBox="0 0 10 10" className="ml-1.5">
          <path d="M2 2 L5 5 L2 8" stroke="#666" strokeWidth="1.2" fill="none"/>
        </svg>
        {/* Empty slot indicator */}
        <div className="ml-2 border-2 border-dashed border-gray-300 rounded px-2 py-0.5 min-w-[40px]"></div>
      </div>
      {/* keep growing block (active/angled) */}
      <motion.div
        className="flex items-center bg-gradient-to-r from-blue-200 to-purple-200 rounded-lg px-3 py-1.5 text-xs shadow-md ml-12"
        style={{ transform: 'rotate(-3deg)' }}
        animate={{ y: [0, -3, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <span className="bg-blue-400 text-blue-900 px-1.5 py-0.5 rounded mr-1.5 font-medium">keep</span>
        <span className="text-gray-800">growing</span>
        <svg width="10" height="10" viewBox="0 0 10 10" className="ml-1.5">
          <path d="M2 2 L5 5 L2 8" stroke="#666" strokeWidth="1.2" fill="none"/>
        </svg>
      </motion.div>
    </div>
  )
}

// Right side blocks for "By Seeing" scale
const RightBlocks = () => {
  return (
    <div className="flex flex-col gap-1.5 items-end w-full">
      {/* else block */}
      <div className="flex items-center bg-gray-100 rounded-lg px-3 py-1.5 text-xs shadow-sm">
        <span className="text-purple-500">else</span>
      </div>
      {/* bummer block */}
      <div className="flex items-center bg-gray-100 rounded-lg px-3 py-1.5 text-xs shadow-sm">
        <span className="text-purple-500">bummer</span>
      </div>
    </div>
  )
}

// Sine Wave Component for "By Seeing"
const SineWave = () => {
  const width = 140
  const height = 50
  const frequency = 1.5
  const amplitude = 12
  
  const points = Array.from({ length: 120 }, (_, i) => {
    const x = (i / 120) * width
    const y = height / 2 + Math.sin((i / 120) * Math.PI * frequency * 2) * amplitude
    return `${x},${y}`
  }).join(' ')
  
  const peakX = 100
  const peakY = height / 2 - amplitude
  
  return (
    <svg width="140" height="50" viewBox="0 0 140 50" className="absolute right-0" style={{ top: '-25px' }}>
      <polyline
        points={points}
        fill="none"
        stroke="#60A5FA"
        strokeWidth="2"
      />
      {/* Dashed line from peak to scale */}
      <line
        x1={peakX}
        y1={peakY}
        x2={peakX}
        y2={height + 5}
        stroke="#000"
        strokeWidth="1"
        strokeDasharray="3,3"
      />
      {/* Highlighted point on peak */}
      <circle
        cx={peakX}
        cy={peakY}
        r="6"
        fill="#60A5FA"
        stroke="white"
        strokeWidth="2"
        style={{ filter: 'drop-shadow(0 0 4px rgba(96, 165, 250, 0.6))' }}
      />
      {/* Small dot on scale */}
      <circle
        cx={peakX}
        cy={height + 5}
        r="3"
        fill="#000"
      />
    </svg>
  )
}

// Horizontal Scale Component
const HorizontalScale = ({ className }: { className?: string }) => {
  const tickCount = 25
  return (
    <div className={`relative ${className}`}>
      <svg width="100%" height="20" viewBox="0 0 1000 20" preserveAspectRatio="none" className="w-full">
        {/* Main line */}
        <line x1="0" y1="10" x2="1000" y2="10" stroke="#000" strokeWidth="1.5" />
        {/* Tick marks */}
        {Array.from({ length: tickCount }, (_, i) => (
          <line
            key={i}
            x1={(i / (tickCount - 1)) * 1000}
            y1="7"
            x2={(i / (tickCount - 1)) * 1000}
            y2="13"
            stroke="#000"
            strokeWidth="1"
          />
        ))}
      </svg>
    </div>
  )
}

export default function Hero() {
  return (
    <section className="pt-20 md:pt-32 pb-16 md:pb-24 bg-gradient-to-b from-white to-[#FFFEF9]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Hero Typography with Two Scales Design */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative mb-8"
          >
            {/* Upper Scale with "Solve" */}
            <div className="relative mb-8 md:mb-12">
              <div className="relative flex items-end justify-center">
                {/* Bar Chart on Left */}
                <div className="absolute left-0 w-52 h-24" style={{ bottom: '5px' }}>
                  <BarChart />
                </div>
                
                {/* "Solve" Text - positioned exactly on scale */}
                <h1 className="text-8xl md:text-[140px] lg:text-[160px] font-bold text-black leading-none font-serif relative z-10" style={{ letterSpacing: '0.05em', lineHeight: '1', marginBottom: '0px' }}>
                  Solve
                </h1>
                
                {/* Scatter Plot on Right */}
                <div className="absolute right-0 w-52 h-24" style={{ bottom: '5px' }}>
                  <ScatterPlot />
                </div>
              </div>
              <HorizontalScale className="mt-0" />
            </div>

            {/* Lower Scale with "By Seeing" */}
            <div className="relative">
              <div className="relative flex items-center justify-center">
                {/* Code Blocks on Left */}
                <div className="absolute left-0 w-48" style={{ bottom: '0px' }}>
                  <CodeBlocks />
                </div>
                
                {/* "By Seeing" Text - positioned on scale */}
                <h1 className="text-5xl md:text-7xl lg:text-[96px] font-bold text-black leading-[1.1] font-serif relative z-10" style={{ letterSpacing: '0.05em' }}>
                  By Seeing
                </h1>
                
                {/* Right side container with Sine Wave and blocks */}
                <div className="absolute right-0 flex flex-col items-end" style={{ bottom: '0px' }}>
                  {/* Sine Wave */}
                  <div className="w-36 h-20 mb-3" style={{ marginTop: '-30px' }}>
                    <SineWave />
                  </div>
                  {/* Right blocks (else and bummer) */}
                  <div className="w-36" style={{ marginTop: '-30px' }}>
                    <RightBlocks />
                  </div>
                </div>
              </div>
              <HorizontalScale className="mt-0" />
            </div>
          </motion.div>

          {/* Supporting Text */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-body-lg text-body-gray mb-4 max-w-2xl mx-auto"
          >
            Interactive problem solving that&apos;s effective and fun.
          </motion.p>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="text-body-lg text-body-gray mb-8 max-w-2xl mx-auto"
          >
            Get smarter in 15 minutes a day.
          </motion.p>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Link
              href="/app"
              className="inline-block px-8 py-4 rounded-full bg-brilliant-green text-white font-semibold text-lg hover:scale-105 transition-transform shadow-lg"
            >
              Get started
            </Link>
          </motion.div>

          {/* Category Icons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="flex flex-wrap justify-center gap-8 mt-16"
          >
            {categoryIcons.map((category, index) => {
              const Icon = category.icon
              return (
                <motion.div
                  key={category.label}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: 0.6 + index * 0.1 }}
                  className="flex flex-col items-center gap-2"
                >
                  <div className={`w-12 h-12 ${category.color} bg-gray-50 rounded-lg flex items-center justify-center`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="text-sm text-muted-gray">{category.label}</span>
                </motion.div>
              )
            })}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
