'use client'

import { motion } from 'framer-motion'
import { Star } from 'lucide-react'

export default function SocialProof() {
  return (
    <section className="py-16 bg-dark-navy relative overflow-hidden">
      {/* Geometric pattern overlay */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, white 1px, transparent 0)`,
          backgroundSize: '40px 40px'
        }} />
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Join over 10 million learners
          </h2>
          <p className="text-2xl md:text-3xl font-bold text-white mb-8">
            worldwide
          </p>

          {/* Star Rating */}
          <div className="flex items-center justify-center gap-2 mb-6">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="w-6 h-6 text-golden-yellow fill-golden-yellow" />
            ))}
            <span className="text-white ml-2 text-lg">100,000 5-star reviews</span>
          </div>

          {/* Logo Grid */}
          <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto mt-12">
            {['NY Times', 'The Atlantic', 'App of Day'].map((logo, index) => (
              <motion.div
                key={logo}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 0.7, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                whileHover={{ opacity: 1 }}
                className="text-white text-center font-serif text-xl"
              >
                {logo}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}

