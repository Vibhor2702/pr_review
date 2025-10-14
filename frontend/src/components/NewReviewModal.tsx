import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface NewReviewModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: { owner: string, repo: string, prNumber: number, provider: string }) => void
  backendStatus: 'online' | 'offline' | 'checking'
}

export function NewReviewModal({ isOpen, onClose, onSubmit, backendStatus }: NewReviewModalProps) {
  const [formData, setFormData] = useState({
    provider: 'github',
    owner: 'microsoft',
    repo: 'vscode',
    prNumber: '12345'
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<any>(null)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.owner && formData.repo && formData.prNumber) {
      setIsSubmitting(true)
      try {
        // Fetch real PR data from GitHub API
        const prNumber = parseInt(formData.prNumber)
        const ghResponse = await fetch(
          `https://api.github.com/repos/${formData.owner}/${formData.repo}/pulls/${prNumber}`
        )
        
        if (!ghResponse.ok) {
          const errorData = await ghResponse.json().catch(() => ({}))
          throw new Error(`Failed to fetch PR (${ghResponse.status}): ${errorData.message || ghResponse.statusText}. Check if the PR exists and is accessible.`)
        }
        
        const prData = await ghResponse.json()
        
        // Fetch PR diff
        const diffResponse = await fetch(prData.diff_url)
        if (!diffResponse.ok) {
          throw new Error(`Failed to fetch PR diff: ${diffResponse.statusText}`)
        }
        
        const diffText = await diffResponse.text()
        
        // Get API URL from environment
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8787'
        
        // Call real Cloudflare Workers API for AI review
        const reviewResponse = await fetch(`${apiUrl}/api/review`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            diff: diffText,
            repo: `${formData.owner}/${formData.repo}`,
            author: prData.user.login,
            pr_number: prNumber,
            title: prData.title,
            description: prData.body
          })
        })
        
        if (!reviewResponse.ok) {
          throw new Error(`Review API failed: ${reviewResponse.statusText}`)
        }
        
        const reviewData = await reviewResponse.json()
        
        // Transform to UI format
        const result = {
          status: 'success',
          pr_context: {
            provider: formData.provider,
            owner: formData.owner,
            repo: formData.repo,
            pr_number: prNumber,
            title: prData.title,
            files_changed: prData.changed_files,
            head_ref: prData.head.ref,
            base_ref: prData.base.ref
          },
          review: {
            score: reviewData.score,
            grade: reviewData.grade,
            total_findings: reviewData.suggestions.length + 
              (reviewData.severity_breakdown.critical + reviewData.severity_breakdown.high + 
               reviewData.severity_breakdown.medium + reviewData.severity_breakdown.low),
            summary: reviewData.summary,
            comments: reviewData.suggestions.map((suggestion: string, idx: number) => ({
              file: 'various',
              line: idx + 1,
              side: 'right',
              message: suggestion,
              suggestion: suggestion,
              severity: 'info',
              rule: 'code-quality',
              confidence: 0.85
            }))
          },
          metadata: {
            total_findings: reviewData.suggestions.length,
            severity_breakdown: {
              error: reviewData.severity_breakdown.critical,
              warning: reviewData.severity_breakdown.high + reviewData.severity_breakdown.medium,
              info: reviewData.severity_breakdown.low
            },
            timestamp: reviewData.metadata.timestamp
          },
          artifact_path: null
        }
        
        setResult(result)
        onSubmit({
          ...formData,
          prNumber
        })
      } catch (error) {
        console.error('Review failed:', error)
        setResult({ 
          error: `Review failed: ${error instanceof Error ? error.message : 'Please check your inputs and try again.'}` 
        })
      } finally {
        setIsSubmitting(false)
      }
    }
  }

  const resetForm = () => {
    setResult(null)
    setFormData({
      provider: 'github',
      owner: 'microsoft',
      repo: 'vscode',
      prNumber: '12345'
    })
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              {result ? 'Review Results' : 'Start New Review'}
            </CardTitle>
            <Button variant="outline" size="sm" onClick={handleClose}>×</Button>
          </div>
          <CardDescription>
            {result ? 'PR review completed successfully' : 'Enter the PR details to start a new review'}
          </CardDescription>
          <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold w-fit ${backendStatus === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            Backend: {backendStatus}
          </div>
        </CardHeader>
        <CardContent>
          {!result ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Provider</label>
                <select 
                  className="w-full p-2 border rounded-md mt-1 bg-white text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                  value={formData.provider}
                  onChange={(e) => setFormData({...formData, provider: e.target.value})}
                >
                  <option value="github">GitHub</option>
                  <option value="gitlab">GitLab</option>
                  <option value="bitbucket">Bitbucket</option>
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Owner/Organization</label>
                <input 
                  type="text"
                  className="w-full p-2 border rounded-md mt-1 bg-white text-gray-900 placeholder-gray-500 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                  placeholder="e.g., microsoft"
                  value={formData.owner}
                  onChange={(e) => setFormData({...formData, owner: e.target.value})}
                  required
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Repository</label>
                <input 
                  type="text"
                  className="w-full p-2 border rounded-md mt-1 bg-white text-gray-900 placeholder-gray-500 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                  placeholder="e.g., vscode"
                  value={formData.repo}
                  onChange={(e) => setFormData({...formData, repo: e.target.value})}
                  required
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">PR Number</label>
                <input 
                  type="number"
                  className="w-full p-2 border rounded-md mt-1 bg-white text-gray-900 placeholder-gray-500 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                  placeholder="e.g., 12345"
                  value={formData.prNumber}
                  onChange={(e) => setFormData({...formData, prNumber: e.target.value})}
                  required
                />
              </div>
              
              <div className="flex gap-2 pt-4">
                <Button 
                  type="submit" 
                  disabled={backendStatus !== 'online' || isSubmitting} 
                  className="flex-1"
                >
                  {isSubmitting ? 'Analyzing...' : 'Start Review'}
                </Button>
                <Button type="button" variant="outline" onClick={handleClose}>
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              {result.error ? (
                <div className="p-4 border border-red-200 rounded-md bg-red-50">
                  <p className="text-red-800">{result.error}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 border border-green-200 rounded-md bg-green-50">
                    <h3 className="font-semibold text-green-800">Review Completed!</h3>
                    <p className="text-green-700">
                      {result.pr_context.provider}/{result.pr_context.owner}/{result.pr_context.repo}#{result.pr_context.pr_number}
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-blue-50 rounded-md">
                      <p className="text-sm text-blue-600">Score</p>
                      <p className="text-2xl font-bold text-blue-800">{result.review.score}</p>
                    </div>
                    <div className="p-3 bg-purple-50 rounded-md">
                      <p className="text-sm text-purple-600">Grade</p>
                      <p className="text-2xl font-bold text-purple-800">{result.review.grade}</p>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-gray-50 rounded-md">
                    <h4 className="font-medium mb-2">Summary</h4>
                    <p className="text-sm text-gray-700">{result.review.summary}</p>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-2">Key Findings ({result.review.total_findings})</h4>
                    <div className="space-y-2">
                      {result.review.comments.slice(0, 3).map((comment: any, index: number) => (
                        <div key={index} className="p-2 border rounded text-sm">
                          <span className="font-medium">{comment.file}:{comment.line}</span> - {comment.message}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              
              <div className="flex gap-2 pt-4">
                <Button onClick={resetForm} className="flex-1">
                  Start Another Review
                </Button>
                <Button variant="outline" onClick={handleClose}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}