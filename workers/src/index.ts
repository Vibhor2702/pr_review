/**
 * PR Review Agent - Cloudflare Workers API
 * Serverless backend for AI-powered pull request reviews
 * 
 * Endpoints:
 * - GET  /api/status - Health check
 * - POST /api/review - AI-powered code review
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

// Environment type definition
interface Env {
  GEMINI_API_KEY: string;
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
  apiKey: string
): Promise<ReviewResponse> {
  try {
    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

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

    // Call Gemini API
    const result = await model.generateContent(prompt);
    const response = result.response;
    const text = response.text();

    // Parse JSON from response (handle markdown code blocks)
    let jsonText = text.trim();
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
      },
    };
  } catch (error) {
    console.error('Gemini API error:', error);
    
    // Return fallback response on error
    return {
      score: 70,
      grade: 'C+',
      summary: 'Automated review unavailable. Please review manually.',
      suggestions: [
        'Ensure code follows project conventions',
        'Add appropriate test coverage',
        'Update documentation as needed',
      ],
      severity_breakdown: {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
      metadata: {
        timestamp: new Date().toISOString(),
        repo: request.repo,
        author: request.author,
        lines_changed: 0,
      },
    };
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

    // Perform AI review
    const reviewResult = await analyzeWithGemini(body, env.GEMINI_API_KEY);

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
