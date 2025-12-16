/**
 * PR Review Agent - Cloudflare Workers API
 * Serverless backend for AI-powered pull request reviews
 * 
 * Endpoints:
 * - GET  /api/status - Health check
 * - POST /api/review - AI-powered code review
 */

// Environment type definition
interface Env {
  GEMINI_API_KEY: string;
  GEMINI_MODEL?: string;
  GEMINI_API_VERSION?: string;
  GEMINI_FALLBACK_MODELS?: string;
  GITHUB_TOKEN?: string; // Server-side GitHub token for rate limit fallback
  ENVIRONMENT?: string;
  API_VERSION?: string;
  ALLOWED_ORIGINS?: string;
}

// Request types
interface ReviewRequest {
  diff: string;
  repo: string;
  author: string;
  pr_number?: number;
  title?: string;
  description?: string;
}

interface ReviewResponse {
  score: number;
  grade: string;
  summary: string;
  suggestions: string[];
  severity_breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  metadata: {
    timestamp: string;
    repo: string;
    author: string;
    lines_changed: number;
  };
}

/**
 * CORS headers for cross-origin requests
 */
function getCorsHeaders(origin: string, allowedOrigins: string): Headers {
  const headers = new Headers({
    'Content-Type': 'application/json',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  });

  // Check if origin is allowed
  const allowed = allowedOrigins.split(',').map(o => o.trim());
  const isAllowed = allowed.some(pattern => {
    if (pattern.includes('*')) {
      const regex = new RegExp(pattern.replace(/\*/g, '.*'));
      return regex.test(origin);
    }
    return pattern === origin;
  });

  if (isAllowed) {
    headers.set('Access-Control-Allow-Origin', origin);
  }

  return headers;
}

/**
 * Handle CORS preflight requests
 */
function handleOptions(request: Request, env: Env): Response {
  const origin = request.headers.get('Origin') || '';
  const allowedOrigins = env.ALLOWED_ORIGINS || 'https://pr-review.pages.dev';
  const headers = getCorsHeaders(origin, allowedOrigins);
  
  return new Response(null, {
    status: 204,
    headers,
  });
}

/**
 * Health check endpoint
 */
function handleStatus(request: Request, env: Env): Response {
  const origin = request.headers.get('Origin') || '';
  const allowedOrigins = env.ALLOWED_ORIGINS || 'https://pr-review.pages.dev';
  const headers = getCorsHeaders(origin, allowedOrigins);

  const response = {
    ok: true,
    service: 'PR Review API',
    version: env.API_VERSION || '1.0.0',
    environment: env.ENVIRONMENT || 'production',
    timestamp: new Date().toISOString(),
    endpoints: {
      status: '/api/status',
      review: '/api/review',
    },
  };

  return new Response(JSON.stringify(response, null, 2), {
    status: 200,
    headers,
  });
}

/**
 * Analyze code diff using Google Gemini AI
 */
async function analyzeWithGemini(
  request: ReviewRequest,
  env: Env
): Promise<ReviewResponse> {
  try {
    const apiKey = env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error('Gemini API key not configured');
    }

    // Construct the prompt for code review
    const prompt = `You are an expert code reviewer. Analyze the following pull request and provide a detailed review.

**Repository:** ${request.repo}
**Author:** ${request.author}
${request.title ? `**PR Title:** ${request.title}` : ''}
${request.description ? `**Description:** ${request.description}` : ''}

**Code Diff:**
\`\`\`diff
${request.diff}
\`\`\`

Please provide a comprehensive code review in the following JSON format:
{
  "score": <number 0-100>,
  "grade": "<letter grade A+, A, B+, B, C+, C, D, F>",
  "summary": "<2-3 sentence overall assessment>",
  "suggestions": [
    "<specific actionable suggestion 1>",
    "<specific actionable suggestion 2>",
    "<specific actionable suggestion 3>"
  ],
  "severity_breakdown": {
    "critical": <count>,
    "high": <count>,
    "medium": <count>,
    "low": <count>
  }
}

Evaluate based on:
1. Code Quality - readability, maintainability, best practices
2. Security - potential vulnerabilities, input validation
3. Performance - efficiency, optimization opportunities  
4. Testing - test coverage, edge cases
5. Documentation - comments, docstrings, clarity

Be constructive, specific, and actionable. Return ONLY valid JSON.`;

    const sanitizeModel = (name: string) => (name || '').replace(/^models\//, '').trim();
    const apiVersion = env.GEMINI_API_VERSION || 'v1beta';
    const preferredModel = sanitizeModel(env.GEMINI_MODEL || 'gemini-flash-latest');
    const configuredFallbacks = (env.GEMINI_FALLBACK_MODELS || '')
      .split(',')
      .map(sanitizeModel)
      .filter(Boolean);
    const fallbackDefaults = [
      'gemini-flash-latest',
      'gemini-2.5-flash',
      'gemini-2.0-flash',
      'gemini-flash-lite-latest',
      'gemini-pro-latest', // keep pro last to avoid extra spend unless necessary
    ];
    const fallbackPreferenceList = configuredFallbacks.length ? configuredFallbacks : fallbackDefaults;

    const listAvailableModels = async (): Promise<string[]> => {
      try {
        const listResponse = await fetch(
          `https://generativelanguage.googleapis.com/${apiVersion}/models?key=${apiKey}`
        );
        const listJson = await listResponse.json();
        const names = listJson?.models?.map((m: { name: string }) => m.name) || [];
        console.warn('Available Gemini models:', names);
        return names.map(sanitizeModel);
      } catch (listError) {
        console.error('Failed to list Gemini models:', listError);
        return [];
      }
    };

    const runInference = async (modelName: string) => {
      const endpoint = `https://generativelanguage.googleapis.com/${apiVersion}/models/${modelName}:generateContent`;
      const payload = {
        contents: [
          {
            role: 'user',
            parts: [{ text: prompt }],
          },
        ],
      };

      const aiResponse = await fetch(`${endpoint}?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!aiResponse.ok) {
        const errorBody = await aiResponse.text();
        const errorObj = new Error(`Gemini API request failed (${aiResponse.status}): ${errorBody}`);
        (errorObj as Error & { status?: number }).status = aiResponse.status;
        throw errorObj;
      }

      const aiData = await aiResponse.json();
      const text = aiData?.candidates?.[0]?.content?.parts
        ?.map((part: { text: string }) => part.text)
        .join('\n')
        .trim();

      if (!text) {
        throw new Error('Gemini API returned no content');
      }

      return { text, usedModel: modelName };
    };

    const fallbackPreferences = Array.from(
      new Set([preferredModel, ...fallbackPreferenceList])
    ).filter(Boolean);

    const pickFallbackModel = async (): Promise<string | null> => {
      const available = await listAvailableModels();
      if (!available.length) return null;

      for (const candidate of fallbackPreferences) {
        if (candidate && available.includes(candidate) && candidate !== preferredModel) {
          return candidate;
        }
      }

      // As a last resort, pick the first available model different from the preferred one
      const fallback = available.find((name) => name !== preferredModel);
      return fallback || null;
    };

    let reviewText: string;
    let modelUsed = preferredModel;

    try {
      const result = await runInference(preferredModel);
      reviewText = result.text;
      modelUsed = result.usedModel;
    } catch (primaryError) {
      if ((primaryError as { status?: number }).status === 404) {
        const fallbackModel = await pickFallbackModel();
        if (fallbackModel) {
          console.warn(`Gemini fallback triggered: ${preferredModel} -> ${fallbackModel}`);
          const fallbackResult = await runInference(fallbackModel);
          reviewText = fallbackResult.text;
          modelUsed = fallbackResult.usedModel;
        } else {
          throw primaryError;
        }
      } else {
        throw primaryError;
      }
    }

    // Parse JSON from response (handle markdown code blocks)
    let jsonText = reviewText.trim();
    if (jsonText.startsWith('```json')) {
      jsonText = jsonText.replace(/```json\n?/, '').replace(/\n?```$/, '');
    } else if (jsonText.startsWith('```')) {
      jsonText = jsonText.replace(/```\n?/, '').replace(/\n?```$/, '');
    }

    const reviewData = JSON.parse(jsonText);

    // Count lines changed in diff
    const linesChanged = request.diff.split('\n').filter(
      line => line.startsWith('+') || line.startsWith('-')
    ).length;

    // Return structured response
    return {
      score: reviewData.score || 75,
      grade: reviewData.grade || 'B',
      summary: reviewData.summary || 'Code review completed.',
      suggestions: reviewData.suggestions || [],
      severity_breakdown: reviewData.severity_breakdown || {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
      metadata: {
        timestamp: new Date().toISOString(),
        repo: request.repo,
        author: request.author,
        lines_changed: linesChanged,
        model_used: modelUsed,
      },
    };
  } catch (error) {
    console.error('Gemini API error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Gemini error details:', errorMessage);
    
    // Throw error instead of returning fallback - let caller handle it
    throw new Error(`AI review failed: ${errorMessage}`);
  }
}

/**
 * Proxy GitHub API requests to avoid CORS issues
 */
async function handleGitHubProxy(request: Request, env: Env): Promise<Response> {
  const origin = request.headers.get('Origin') || '';
  const allowedOrigins = env.ALLOWED_ORIGINS || 'https://pr-review.pages.dev';
  const headers = getCorsHeaders(origin, allowedOrigins);

  try {
    const url = new URL(request.url);
    const githubPath = url.searchParams.get('path');
    
    if (!githubPath) {
      return new Response(
        JSON.stringify({ error: 'Missing path parameter' }),
        { status: 400, headers }
      );
    }

    // Get Accept header from request (for diff format)
    const acceptHeader = request.headers.get('Accept') || 'application/vnd.github.v3+json';
    
    // Get Authorization header from request (user-provided GitHub token)
    const authHeader = request.headers.get('Authorization');
    
    // Build headers for GitHub API
    const githubHeaders: HeadersInit = {
      'Accept': acceptHeader,
      'User-Agent': 'PR-Review-Agent-Cloudflare-Worker',
    };
    
    // Priority: Use user token if provided, otherwise fall back to server token
    if (authHeader) {
      // User provided their own token - use it
      githubHeaders['Authorization'] = authHeader;
    } else if (env.GITHUB_TOKEN) {
      // Fall back to server-side token for better rate limits
      githubHeaders['Authorization'] = `token ${env.GITHUB_TOKEN}`;
    }
    // If neither exists, request will be unauthenticated (60 req/hour limit)
    
    // Fetch from GitHub API
    const githubResponse = await fetch(`https://api.github.com${githubPath}`, {
      headers: githubHeaders,
    });

    // Check if response is JSON or plain text (diff)
    const contentType = githubResponse.headers.get('Content-Type') || '';
    
    let responseData;
    let responseHeaders = new Headers(headers);
    
    if (contentType.includes('application/json')) {
      responseData = JSON.stringify(await githubResponse.json());
      responseHeaders.set('Content-Type', 'application/json');
    } else {
      // Plain text response (like diff)
      responseData = await githubResponse.text();
      responseHeaders.set('Content-Type', 'text/plain');
    }
    
    return new Response(responseData, {
      status: githubResponse.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('GitHub proxy error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Failed to fetch from GitHub',
        message: error instanceof Error ? error.message : 'Unknown error'
      }),
      { status: 500, headers }
    );
  }
}

/**
 * Handle review request
 */
async function handleReview(request: Request, env: Env): Promise<Response> {
  const origin = request.headers.get('Origin') || '';
  const allowedOrigins = env.ALLOWED_ORIGINS || 'https://pr-review.pages.dev';
  const headers = getCorsHeaders(origin, allowedOrigins);

  try {
    // Validate API key
    if (!env.GEMINI_API_KEY) {
      return new Response(
        JSON.stringify({
          error: 'Configuration error',
          message: 'GEMINI_API_KEY not configured',
        }),
        { status: 500, headers }
      );
    }

    // Parse request body
    const body = await request.json() as ReviewRequest;

    // Validate required fields
    if (!body.diff || !body.repo || !body.author) {
      return new Response(
        JSON.stringify({
          error: 'Validation error',
          message: 'Missing required fields: diff, repo, author',
        }),
        { status: 400, headers }
      );
    }

    // Log request details
    console.log(`Review request: ${body.repo} by ${body.author}, diff size: ${body.diff.length} chars`);
    
    // Perform AI review
    const reviewResult = await analyzeWithGemini(body, env);
    
    // Log successful review
    console.log(`Review completed: score=${reviewResult.score}, grade=${reviewResult.grade}`);

    return new Response(JSON.stringify(reviewResult, null, 2), {
      status: 200,
      headers,
    });
  } catch (error) {
    console.error('Review error:', error);
    
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    return new Response(
      JSON.stringify({
        error: 'Internal server error',
        message: errorMessage,
      }),
      { status: 500, headers }
    );
  }
}

/**
 * Main Worker handler
 */
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return handleOptions(request, env);
    }

    // Route requests
    if (path === '/api/status' || path === '/') {
      return handleStatus(request, env);
    }

    if (path === '/api/review' && request.method === 'POST') {
      return handleReview(request, env);
    }

    if (path === '/api/github-proxy' && request.method === 'GET') {
      return handleGitHubProxy(request, env);
    }

    // 404 Not Found
    const origin = request.headers.get('Origin') || '';
    const allowedOrigins = env.ALLOWED_ORIGINS || 'https://pr-review.pages.dev';
    const headers = getCorsHeaders(origin, allowedOrigins);

    return new Response(
      JSON.stringify({
        error: 'Not found',
        message: `Endpoint ${path} not found`,
        available_endpoints: ['/api/status', '/api/review'],
      }),
      { status: 404, headers }
    );
  },
};
