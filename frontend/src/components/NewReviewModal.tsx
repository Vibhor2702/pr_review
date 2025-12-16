import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface NewReviewModalProps {
  isOpen: boolean
  onClose: () => void
  backendStatus: 'online' | 'offline' | 'checking'
}

export function NewReviewModal({ isOpen, onClose, backendStatus }: NewReviewModalProps) {
  const [formData, setFormData] = useState({
    provider: 'github',
    owner: 'microsoft',
    repo: 'vscode',
    prNumber: '282199', // Recent valid PR
    githubToken: '' // Optional GitHub token for higher rate limits
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [suggestedPRs, setSuggestedPRs] = useState<any[]>([])
  const [isFetchingPRs, setIsFetchingPRs] = useState(false)
  const [repoUrl, setRepoUrl] = useState('')
  const [prFilter, setPrFilter] = useState<'all' | 'open' | 'closed'>('open')

  if (!isOpen) return null

  // Parse GitHub/GitLab/Bitbucket URLs
  const parseRepoUrl = (url: string) => {
    try {
      // Remove trailing slashes and .git
      const cleanUrl = url.trim().replace(/\.git$/, '').replace(/\/+$/, '')
      
      // GitHub: https://github.com/owner/repo or github.com/owner/repo
      const githubMatch = cleanUrl.match(/(?:https?:\/\/)?(?:www\.)?github\.com\/([^\/]+)\/([^\/]+)/)
      if (githubMatch) {
        return { provider: 'github', owner: githubMatch[1], repo: githubMatch[2] }
      }
      
      // GitLab: https://gitlab.com/owner/repo
      const gitlabMatch = cleanUrl.match(/(?:https?:\/\/)?(?:www\.)?gitlab\.com\/([^\/]+)\/([^\/]+)/)
      if (gitlabMatch) {
        return { provider: 'gitlab', owner: gitlabMatch[1], repo: gitlabMatch[2] }
      }
      
      // Bitbucket: https://bitbucket.org/owner/repo
      const bitbucketMatch = cleanUrl.match(/(?:https?:\/\/)?(?:www\.)?bitbucket\.org\/([^\/]+)\/([^\/]+)/)
      if (bitbucketMatch) {
        return { provider: 'bitbucket', owner: bitbucketMatch[1], repo: bitbucketMatch[2] }
      }
      
      return null
    } catch (e) {
      return null
    }
  }

  // Fetch PRs from repository
  const fetchPRsFromRepo = async () => {
    if (!formData.owner || !formData.repo) {
      alert('Please enter owner and repository name first')
      return
    }
    
    setIsFetchingPRs(true)
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8787'
      let githubPath = ''
      
      if (formData.provider === 'github') {
        githubPath = `/repos/${formData.owner}/${formData.repo}/pulls?state=${prFilter}&per_page=20&sort=updated&direction=desc`
      } else if (formData.provider === 'gitlab') {
        // GitLab uses different API - not proxying for now
        alert('GitLab support coming soon. Please use GitHub for now.')
        setIsFetchingPRs(false)
        return
      } else if (formData.provider === 'bitbucket') {
        // Bitbucket uses different API - not proxying for now
        alert('Bitbucket support coming soon. Please use GitHub for now.')
        setIsFetchingPRs(false)
        return
      }
      
      const headers: HeadersInit = {}
      if (formData.githubToken) {
        headers['Authorization'] = `token ${formData.githubToken}`
      }
      
      const response = await fetch(`${apiUrl}/api/github-proxy?path=${encodeURIComponent(githubPath)}`, { headers })
      
      if (!response.ok) {
        // Handle specific error cases
        if (response.status === 403) {
          const errorData = await response.json().catch(() => ({}))
          if (errorData.message?.includes('rate limit')) {
            throw new Error(`GitHub API rate limit exceeded. You can:\n• Wait an hour and try again\n• Enter the PR number manually\n• Use a smaller repository`)
          }
          throw new Error(`Access forbidden (403). The repository might be private or you've hit the rate limit.`)
        }
        if (response.status === 404) {
          throw new Error(`Repository "${formData.owner}/${formData.repo}" not found. Please check the owner and repo name.`)
        }
        throw new Error(`Failed to fetch PRs (${response.status}). Please try again or enter PR number manually.`)
      }
      
      const data = await response.json()
      
      // Check if response has error message (from GitHub)
      if (data.message) {
        if (data.message.includes('rate limit')) {
          throw new Error(`⏰ GitHub API rate limit exceeded.\n\n💡 Tip: You can still enter the PR number manually below!`)
        }
        throw new Error(`GitHub API error: ${data.message}`)
      }
      
      // Normalize data across providers
      let prs: any[] = []
      if (formData.provider === 'github') {
        if (!Array.isArray(data)) {
          throw new Error('Invalid response from GitHub API')
        }
        prs = data.map((pr: any) => ({
          number: pr.number,
          title: pr.title,
          state: pr.state,
          author: pr.user?.login,
          created_at: pr.created_at,
          updated_at: pr.updated_at
        }))
      }
      
      if (prs.length === 0) {
        alert(`No ${prFilter} PRs found in ${formData.owner}/${formData.repo}`)
        return
      }
      
      setSuggestedPRs(prs)
    } catch (error) {
      console.error('Failed to fetch PRs:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      alert(errorMessage)
    } finally {
      setIsFetchingPRs(false)
    }
  }
  
  // Auto-refresh when filter changes
  const handleFilterChange = (newFilter: 'all' | 'open' | 'closed') => {
    setPrFilter(newFilter)
    if (suggestedPRs.length > 0) {
      setTimeout(() => fetchPRsFromRepo(), 100)
    }
  }

  // Handle URL paste
  const handleUrlPaste = () => {
    const parsed = parseRepoUrl(repoUrl)
    if (parsed) {
      setFormData({
        ...formData,
        provider: parsed.provider,
        owner: parsed.owner,
        repo: parsed.repo
      })
      setRepoUrl('')
      // Auto-fetch PRs after parsing URL
      setTimeout(() => fetchPRsFromRepo(), 100)
    } else {
      alert('Invalid repository URL. Supported formats:\n• https://github.com/owner/repo\n• https://gitlab.com/owner/repo\n• https://bitbucket.org/owner/repo')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.owner && formData.repo && formData.prNumber) {
      setIsSubmitting(true)
      setSuggestedPRs([]) // Clear previous suggestions
      try {
        // Fetch real PR data from GitHub API
        const prNumber = parseInt(formData.prNumber)
        
        // Use Cloudflare Worker proxy to avoid CORS issues
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8787'
        
        let ghResponse
        try {
          const headers: HeadersInit = {
            'Accept': 'application/json'
          }
          if (formData.githubToken) {
            headers['Authorization'] = `token ${formData.githubToken}`
          }
          
          ghResponse = await fetch(
            `${apiUrl}/api/github-proxy?path=/repos/${formData.owner}/${formData.repo}/pulls/${prNumber}`,
            { headers }
          )
        } catch (fetchError) {
          throw new Error(`Network error: Unable to reach GitHub API. Please check your internet connection and try again.`)
        }
        
        if (!ghResponse.ok) {
          // Fetch recent PRs to suggest
          if (ghResponse.status === 404) {
            try {
              const suggestedHeaders: HeadersInit = {}
              if (formData.githubToken) {
                suggestedHeaders['Authorization'] = `token ${formData.githubToken}`
              }
              
              const recentPRsResponse = await fetch(
                `${apiUrl}/api/github-proxy?path=/repos/${formData.owner}/${formData.repo}/pulls?state=all&per_page=5&sort=updated&direction=desc`,
                { headers: suggestedHeaders }
              )
              if (recentPRsResponse.ok) {
                const recentPRs = await recentPRsResponse.json()
                setSuggestedPRs(recentPRs.map((pr: any) => ({
                  number: pr.number,
                  title: pr.title,
                  state: pr.state
                })))
              }
            } catch (e) {
              console.error('Failed to fetch suggested PRs:', e)
            }
            
            throw new Error(`PR #${prNumber} not found in ${formData.owner}/${formData.repo}. This PR may not exist or may have been deleted. See suggested PRs below.`)
          }
          
          const errorData = await ghResponse.json().catch(() => ({}))
          
          // Handle rate limiting
          if (ghResponse.status === 403 && errorData.message?.includes('rate limit')) {
            throw new Error(`GitHub API rate limit exceeded. Please try again later or add a GitHub token for higher limits.`)
          }
          
          throw new Error(`Failed to fetch PR (${ghResponse.status}): ${errorData.message || ghResponse.statusText}`)
        }
        
        const prData = await ghResponse.json()
        
        // Check if PR is too large
        if (prData.changed_files > 100) {
          console.warn(`Large PR detected: ${prData.changed_files} files changed`)
        }
        
        // Fetch PR diff through proxy to avoid CORS
        // Use GitHub API with Accept: application/vnd.github.v3.diff header
        const diffHeaders: HeadersInit = {
          'Accept': 'application/vnd.github.v3.diff'
        }
        if (formData.githubToken) {
          diffHeaders['Authorization'] = `token ${formData.githubToken}`
        }
        
        const diffResponse = await fetch(
          `${apiUrl}/api/github-proxy?path=${encodeURIComponent(`/repos/${formData.owner}/${formData.repo}/pulls/${prNumber}`)}`,
          { headers: diffHeaders }
        )
        if (!diffResponse.ok) {
          throw new Error(`Failed to fetch PR diff: ${diffResponse.statusText}`)
        }
        
        const diffText = await diffResponse.text()
        
        // Check diff size
        if (diffText.length > 500000) {
          throw new Error(`PR diff too large (${(diffText.length / 1000).toFixed(1)}KB). Please try a smaller PR.`)
        }
        
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
          const errorText = await reviewResponse.text().catch(() => '')
          throw new Error(`Review API failed (${reviewResponse.status}): ${errorText || reviewResponse.statusText}`)
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
        // Don't call onSubmit here - keep modal open to show results
      } catch (error) {
        console.error('Review failed:', error)
        let errorMessage = 'Unknown error occurred'
        
        if (error instanceof Error) {
          errorMessage = error.message
          
          // Provide helpful context for common errors
          if (error.message.includes('Failed to fetch') || error.message === 'Failed to fetch') {
            errorMessage = `Network error: Unable to connect to GitHub API or review service. Please check:\n• Your internet connection\n• The PR exists and is accessible\n• GitHub API is not blocked by firewall/proxy`
          } else if (error.message.includes('CORS')) {
            errorMessage = `CORS error: Browser blocked the request. This usually means:\n• GitHub API requires authentication for this request\n• Try a public repository instead`
          }
        }
        
        setResult({ 
          error: errorMessage
        })
      } finally {
        setIsSubmitting(false)
      }
    }
  }

  const resetForm = () => {
    setResult(null)
    setSuggestedPRs([])
    setRepoUrl('')
    setFormData({
      provider: 'github',
      owner: 'microsoft',
      repo: 'vscode',
      prNumber: '282199',
      githubToken: ''
    })
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[95vh] flex flex-col shadow-2xl">
        <CardHeader className="flex-shrink-0 border-b">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle className="text-2xl">
                {result ? '✨ Review Results' : '🚀 Start New Review'}
              </CardTitle>
              <CardDescription>
                {result ? 'AI-powered code analysis completed' : 'Enter PR details to analyze with AI'}
              </CardDescription>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleClose}
              className="h-8 w-8 p-0 hover:bg-red-100"
            >
              <span className="text-xl">×</span>
            </Button>
          </div>
          <div className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold w-fit ${backendStatus === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {backendStatus === 'online' ? '🟢' : '🔴'} Backend: {backendStatus}
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto p-6">
          {!result ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Quick URL Import */}
              <div className="p-3 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-md">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">
                  🔗 Quick Import from URL
                </label>
                <div className="flex gap-2">
                  <input 
                    type="text"
                    className="flex-1 p-2 border rounded-md bg-white text-gray-900 placeholder-gray-500 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                    placeholder="Paste GitHub/GitLab/Bitbucket URL (e.g., https://github.com/microsoft/vscode)"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleUrlPaste())}
                  />
                  <Button 
                    type="button" 
                    onClick={handleUrlPaste}
                    disabled={!repoUrl.trim()}
                    variant="outline"
                    size="sm"
                  >
                    Import
                  </Button>
                </div>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-gray-500">Or enter manually</span>
                </div>
              </div>
              
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

              {/* GitHub Token (Optional) */}
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">
                  🔑 GitHub Token (Optional)
                  <span className="ml-2 text-xs text-gray-500">Increases rate limit to 5000/hour</span>
                </label>
                <input 
                  type="password"
                  className="w-full p-2 border rounded-md bg-white text-gray-900 placeholder-gray-500 border-gray-300 focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200"
                  placeholder="ghp_xxxxxxxxxxxx (Leave empty for 60/hour limit)"
                  value={formData.githubToken}
                  onChange={(e) => setFormData({...formData, githubToken: e.target.value})}
                />
                <p className="text-xs text-gray-600 mt-1">
                  💡 Get a token from <a href="https://github.com/settings/tokens" target="_blank" rel="noopener" className="text-blue-600 hover:underline">GitHub Settings</a> (needs 'repo' scope)
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
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
              </div>
              
              {/* Browse PRs Button */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={fetchPRsFromRepo}
                    disabled={!formData.owner || !formData.repo || isFetchingPRs}
                    className="flex-1"
                  >
                    {isFetchingPRs ? '⏳ Loading...' : '📋 Browse Available PRs'}
                  </Button>
                  
                  {suggestedPRs.length > 0 && (
                    <select
                      className="p-2 border rounded-md bg-white text-gray-900 border-gray-300"
                      value={prFilter}
                      onChange={(e) => handleFilterChange(e.target.value as 'all' | 'open' | 'closed')}
                    >
                      <option value="open">Open</option>
                      <option value="closed">Closed</option>
                      <option value="all">All</option>
                    </select>
                  )}
                </div>
                <p className="text-xs text-gray-500 italic">
                  💡 Tip: If rate limited, enter PR number manually below
                </p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">PR Number</label>
                <input 
                  type="number"
                  className="w-full p-2 border rounded-md mt-1 bg-white text-gray-900 placeholder-gray-500 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                  placeholder="e.g., 282199"
                  value={formData.prNumber}
                  onChange={(e) => setFormData({...formData, prNumber: e.target.value})}
                  required
                />
              </div>
              
              {/* Show suggested PRs if available */}
              {suggestedPRs.length > 0 && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-md max-h-80 overflow-y-auto">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-blue-800">
                      {suggestedPRs.length} PRs in {formData.owner}/{formData.repo}
                    </p>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setSuggestedPRs([])}
                      className="h-6 text-xs"
                    >
                      Clear
                    </Button>
                  </div>
                  <div className="space-y-1">
                    {suggestedPRs.map((pr) => (
                      <button
                        key={pr.number}
                        type="button"
                        onClick={() => {
                          setFormData({...formData, prNumber: pr.number.toString()})
                          setSuggestedPRs([]) // Auto-hide list after selection
                        }}
                        className="w-full text-left p-2 text-sm hover:bg-blue-100 rounded transition-colors border border-transparent hover:border-blue-300"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-medium text-blue-700">#{pr.number}</span>
                              <span className={`px-1.5 py-0.5 text-xs rounded ${pr.state === 'open' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                {pr.state}
                              </span>
                              {pr.author && (
                                <span className="text-xs text-gray-500">by {pr.author}</span>
                              )}
                            </div>
                            <p className="text-gray-700 text-sm truncate">{pr.title}</p>
                            {pr.updated_at && (
                              <p className="text-xs text-gray-500 mt-1">
                                Updated: {new Date(pr.updated_at).toLocaleDateString()}
                              </p>
                            )}
                          </div>
                          <div className="text-blue-600">→</div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
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
            <div className="space-y-6">
              {result.error ? (
                <div className="p-6 border-2 border-red-300 rounded-lg bg-red-50">
                  <h3 className="text-lg font-semibold text-red-900 mb-2">⚠️ Review Failed</h3>
                  <p className="text-red-800 whitespace-pre-line">{result.error}</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Success Banner */}
                  <div className="p-6 border-2 border-green-300 rounded-lg bg-gradient-to-r from-green-50 to-emerald-50">
                    <h3 className="text-xl font-bold text-green-900 mb-2">✅ Review Completed!</h3>
                    <p className="text-green-700 font-mono text-sm">
                      {result.pr_context.provider}/{result.pr_context.owner}/{result.pr_context.repo} #{result.pr_context.pr_number}
                    </p>
                    <p className="text-green-600 text-sm mt-2">
                      {result.pr_context.title}
                    </p>
                  </div>
                  
                  {/* Scores */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border-2 border-blue-200 text-center">
                      <p className="text-sm text-blue-600 font-medium mb-1">Overall Score</p>
                      <p className="text-4xl font-bold text-blue-900">{result.review.score}</p>
                      <p className="text-xs text-blue-600 mt-1">out of 100</p>
                    </div>
                    <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border-2 border-purple-200 text-center">
                      <p className="text-sm text-purple-600 font-medium mb-1">Grade</p>
                      <p className="text-4xl font-bold text-purple-900">{result.review.grade}</p>
                      <p className="text-xs text-purple-600 mt-1">quality rating</p>
                    </div>
                  </div>
                  
                  {/* Summary */}
                  <div className="p-6 bg-gradient-to-r from-gray-50 to-slate-50 rounded-lg border border-gray-200">
                    <h4 className="font-bold text-lg mb-3 flex items-center gap-2">
                      📝 AI Summary
                    </h4>
                    <p className="text-gray-700 leading-relaxed">{result.review.summary}</p>
                  </div>
                  
                  {/* Key Findings */}
                  <div>
                    <h4 className="font-bold text-lg mb-3 flex items-center gap-2">
                      🔍 Key Findings 
                      <span className="text-sm font-normal text-gray-500">
                        ({result.review.total_findings} total)
                      </span>
                    </h4>
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {result.review.comments.map((comment: any, index: number) => (
                        <div key={index} className="p-4 border-l-4 border-blue-500 bg-blue-50 rounded-r-lg hover:bg-blue-100 transition-colors">
                          <div className="flex items-start gap-3">
                            <span className="text-2xl">{index === 0 ? '🔴' : index === 1 ? '🟡' : '🟢'}</span>
                            <div className="flex-1">
                              <p className="font-mono text-xs text-gray-600 mb-1">
                                {comment.file}:{comment.line}
                              </p>
                              <p className="text-sm text-gray-800">{comment.message}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Stats Footer */}
                  <div className="grid grid-cols-3 gap-3 pt-4 border-t">
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <p className="text-xs text-orange-600">Files Changed</p>
                      <p className="text-xl font-bold text-orange-900">{result.pr_context.files_changed || 0}</p>
                    </div>
                    <div className="text-center p-3 bg-teal-50 rounded-lg">
                      <p className="text-xs text-teal-600">Findings</p>
                      <p className="text-xl font-bold text-teal-900">{result.review.total_findings}</p>
                    </div>
                    <div className="text-center p-3 bg-indigo-50 rounded-lg">
                      <p className="text-xs text-indigo-600">Severity</p>
                      <p className="text-xl font-bold text-indigo-900">
                        {result.metadata.severity_breakdown.error > 0 ? '🔴 High' : 
                         result.metadata.severity_breakdown.warning > 0 ? '🟡 Med' : '🟢 Low'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="flex gap-3 pt-4 border-t">
                <Button onClick={resetForm} className="flex-1" size="lg">
                  ➕ Start Another Review
                </Button>
                <Button variant="outline" onClick={handleClose} size="lg">
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