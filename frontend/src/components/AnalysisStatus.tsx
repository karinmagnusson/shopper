'use client'

import { useEffect, useRef } from 'react'
import type { AnalysisJob } from '@/types'
import clsx from 'clsx'
import { CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/solid'

interface AnalysisStatusProps {
  job: AnalysisJob
}

export default function AnalysisStatus({ job }: AnalysisStatusProps) {
  const progressPercent = job.totalPins > 0
    ? Math.round((job.processedPins / job.totalPins) * 100)
    : job.progress

  const isRunning = job.status === 'RUNNING' || job.status === 'PENDING'
  const isComplete = job.status === 'COMPLETED'
  const isFailed = job.status === 'FAILED'

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <div className="flex items-start gap-4">
        {/* Status icon */}
        <div
          className={clsx(
            'w-10 h-10 rounded-full flex items-center justify-center shrink-0',
            isRunning && 'bg-blue-100',
            isComplete && 'bg-green-100',
            isFailed && 'bg-red-100'
          )}
        >
          {isRunning && (
            <div className="w-5 h-5 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
          )}
          {isComplete && (
            <CheckCircleIcon className="w-6 h-6 text-green-600" />
          )}
          {isFailed && (
            <ExclamationCircleIcon className="w-6 h-6 text-red-600" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <p className="text-sm font-semibold text-gray-900">
              {isRunning && 'Analyzing your Pinterest boards…'}
              {isComplete && 'Analysis complete!'}
              {isFailed && 'Analysis failed'}
            </p>
            {isRunning && (
              <span className="text-xs font-medium text-blue-600">
                {progressPercent}%
              </span>
            )}
          </div>

          {/* Progress bar */}
          {(isRunning || isComplete) && (
            <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden mb-2">
              <div
                className={clsx(
                  'h-full rounded-full transition-all duration-500',
                  isComplete ? 'bg-green-500' : 'bg-blue-500'
                )}
                style={{ width: `${isComplete ? 100 : progressPercent}%` }}
              />
            </div>
          )}

          {/* Sub-message */}
          <p className="text-xs text-gray-500">
            {job.message ??
              (isRunning
                ? `Processed ${job.processedPins} of ${job.totalPins} pins`
                : isComplete
                ? `Processed ${job.totalPins} pins across ${job.boardIds.length} board${job.boardIds.length !== 1 ? 's' : ''}`
                : 'Please try again or select different boards.')}
          </p>
        </div>
      </div>
    </div>
  )
}
