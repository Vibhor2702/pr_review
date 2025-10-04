/**
 * API Client for Cloudflare Workers Backend
 * Handles communication between frontend and serverless API
 */

// Get API URL from environment (set in Cloudflare Pages)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8787'

console.log('🔗 API Base URL:', API_BASE_URL)

// Types matching Cloudflare Workers responses
export interface WorkersReviewRequest {
  diff: string
  repo: string
  author: string
  pr_number?: number
  title?: string
  description?: string
}

export interface WorkersReviewResponse {
  score: number
  grade: string
  summary: string
  suggestions: string[]
  severity_breakdown: {
    critical: number
    high: number
    medium: number
    low: number
  }
  metadata: {
    timestamp: string
    repo: string
    author: string
    lines_changed: number
  }
}

export interface WorkersStatusResponse {
  ok: boolean
  service: string
  version: string
  environment: string
  timestamp: string
  endpoints: {
    status: string
    review: string
  }
}

export interface WorkersErrorResponse {
  error: string
  message: string
}

/**
 * Make HTTP request with error handling
 */
async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const error: WorkersErrorResponse = await response.json()
      throw new Error(error.message || `HTTP ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('❌ API Error:', error)
    throw error
  }
}

/**
 * Cloudflare Workers API Client
 */
export const workersAPI = {
  /**
   * Health check - verify API is running
   */
  getStatus: async (): Promise<WorkersStatusResponse> => {
    return fetchAPI<WorkersStatusResponse>('/api/status')
  },

  /**
   * Request AI-powered code review
   */
  reviewCode: async (
    request: WorkersReviewRequest
  ): Promise<WorkersReviewResponse> => {
    return fetchAPI<WorkersReviewResponse>('/api/review', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },
}

/**
 * Legacy API compatibility layer
 * Maps old Flask API format to new Workers format
 */
export interface PRReviewRequest {
  provider: 'github' | 'gitlab' | 'bitbucket'
  owner: string
  repo: string
  pr_number: number
  token?: string
  no_llm?: boolean
  post_comments?: boolean
}

export interface PRReviewResponse {
  status: 'success' | 'error'
  pr_context: {
    provider: string
    owner: string
    repo: string
    pr_number: number
    title: string
    files_changed: number
    head_ref?: string
    base_ref?: string
  }
  review: {
    score: number
    grade: string
    total_findings: number
    summary: string
    comments: ReviewComment[]
  }
  metadata: {
    total_findings: number
    severity_breakdown: {
      error: number
      warning: number
      info: number
    }
    timestamp: string
  }
  artifact_path?: string
}

export interface ReviewComment {
  file: string
  line: number
  side: 'left' | 'right'
  message: string
  suggestion?: string
  severity: 'error' | 'warning' | 'info'
  rule: string
  confidence?: number
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy'
  version: string
  timestamp?: string
  ok?: boolean
  service?: string
}

export interface ConfigResponse {
  providers: {
    gemini: boolean
    github: boolean
    gitlab: boolean
    bitbucket: boolean
  }
  features: {
    llm_enabled: boolean
    ci_integration: boolean
    static_analysis: boolean
  }
}

/**
 * Unified API client with automatic backend detection
 * Supports both Railway (Flask) and Cloudflare Workers backends
 */
export const reviewAPI = {
  /**
   * Review a pull request
   * Maps to Workers format if using Cloudflare, or Flask format for Railway
   */
  reviewPR: async (request: PRReviewRequest): Promise<PRReviewResponse> => {
    // Check if using Workers backend
    const isWorkers = API_BASE_URL.includes('workers.dev')
    
    if (isWorkers) {
      // Transform to Workers format and call
      const workersRequest: WorkersReviewRequest = {
        diff: `Mock diff for ${request.owner}/${request.repo}#${request.pr_number}`,
        repo: `${request.owner}/${request.repo}`,
        author: request.owner,
        pr_number: request.pr_number,
        title: `PR #${request.pr_number}`,
      }
      
      const workersResponse = await workersAPI.reviewCode(workersRequest)
      
      // Transform back to legacy format
      return {
        status: 'success',
        pr_context: {
          provider: request.provider,
          owner: request.owner,
          repo: request.repo,
          pr_number: request.pr_number,
          title: workersRequest.title || `PR #${request.pr_number}`,
          files_changed: 0,
        },
        review: {
          score: workersResponse.score,
          grade: workersResponse.grade,
          total_findings: workersResponse.suggestions.length,
          summary: workersResponse.summary,
          comments: workersResponse.suggestions.map((suggestion, idx) => ({
            file: 'unknown',
            line: idx + 1,
            side: 'right' as const,
            message: suggestion,
            severity: workersResponse.severity_breakdown.critical > 0 
              ? 'error' 
              : workersResponse.severity_breakdown.high > 0 
              ? 'warning' 
              : 'info',
            rule: 'ai-suggestion',
          })),
        },
        metadata: {
          total_findings: workersResponse.suggestions.length,
          severity_breakdown: {
            error: workersResponse.severity_breakdown.critical,
            warning: workersResponse.severity_breakdown.high + workersResponse.severity_breakdown.medium,
            info: workersResponse.severity_breakdown.low,
          },
          timestamp: workersResponse.metadata.timestamp,
        },
      }
    } else {
      // Use Flask backend (Railway)
      const response = await fetch(`${API_BASE_URL}/review_pr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      return await response.json()
    }
  },

  /**
   * Demo review with mock data
   */
  demoReview: async (request: Partial<PRReviewRequest>): Promise<PRReviewResponse> => {
    const response = await fetch(`${API_BASE_URL}/demo/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    return await response.json()
  },

  /**
   * Get health status
   */
  getHealth: async (): Promise<HealthResponse> => {
    // Check if using Workers backend
    const isWorkers = API_BASE_URL.includes('workers.dev')
    
    if (isWorkers) {
      const status = await workersAPI.getStatus()
      return {
        status: status.ok ? 'healthy' : 'unhealthy',
        version: status.version,
        timestamp: status.timestamp,
        ok: status.ok,
        service: status.service,
      }
    } else {
      const response = await fetch(`${API_BASE_URL}/health`)
      return await response.json()
    }
  },

  /**
   * Get configuration (Flask backend only)
   */
  getConfig: async (): Promise<ConfigResponse> => {
    const response = await fetch(`${API_BASE_URL}/config`)
    return await response.json()
  },

  /**
   * Get providers status (Flask backend only)
   */
  getProviders: async () => {
    const response = await fetch(`${API_BASE_URL}/providers`)
    return await response.json()
  },
}

// Export convenience functions
export const checkAPIHealth = async (): Promise<boolean> => {
  try {
    const health = await reviewAPI.getHealth()
    return health.status === 'healthy' || health.ok === true
  } catch {
    return false
  }
}

export const getAPIType = (): 'workers' | 'railway' | 'local' => {
  if (API_BASE_URL.includes('workers.dev')) return 'workers'
  if (API_BASE_URL.includes('railway.app')) return 'railway'
  return 'local'
}
