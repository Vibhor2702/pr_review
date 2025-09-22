import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

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
    head_ref: string
    base_ref: string
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
  artifact_path: string
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
  timestamp: string
  dependencies: {
    gemini: boolean
    git_providers: {
      github: boolean
      gitlab: boolean
      bitbucket: boolean
    }
  }
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

// API functions
export const reviewAPI = {
  // Review a pull request
  reviewPR: async (request: PRReviewRequest): Promise<PRReviewResponse> => {
    const response = await api.post('/review_pr', request)
    return response.data
  },

  // Get health status
  getHealth: async (): Promise<HealthResponse> => {
    const response = await api.get('/health')
    return response.data
  },

  // Get configuration
  getConfig: async (): Promise<ConfigResponse> => {
    const response = await api.get('/config')
    return response.data
  },

  // Get providers status
  getProviders: async () => {
    const response = await api.get('/providers')
    return response.data
  },
}