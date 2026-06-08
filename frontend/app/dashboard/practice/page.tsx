"use client"

import Link from "next/link"

export default function PracticePage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center px-4">
      <div className="text-center space-y-3">
        <p className="text-2xl font-bold text-slate-900 dark:text-white">Practice</p>
        <p className="text-sm text-slate-500 dark:text-gray-400">Coming soon.</p>
        <Link
          href="/dashboard"
          className="inline-block text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  )
}
