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

export default function Hero() {
  return (
    <section className="pt-20 md:pt-32 pb-16 md:pb-24 bg-gradient-to-b from-white to-[#FFFEF9]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Hero Typography with Animations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative mb-8"
          >
            <h1 className="text-5xl md:text-7xl lg:text-[96px] font-bold text-black mb-6 leading-[1.1]">
              <span className="inline-block relative">
                Learn
                <motion.div
                  className="absolute -top-8 -left-4"
                  animate={{ y: [0, -5, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <BarChart3 className="w-12 h-12 text-vibrant-blue" />
                </motion.div>
              </span>
              {' '}
              <span className="inline-block relative">
                by
                <motion.div
                  className="absolute top-0 left-full ml-2 text-sm text-muted-gray"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  while learning
                </motion.div>
              </span>
              {' '}
              <span className="inline-block relative">
                doing
                <motion.div
                  className="absolute -top-4 -right-4"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <div className="w-3 h-3 bg-vibrant-blue rounded-full" />
                </motion.div>
              </span>
            </h1>
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

