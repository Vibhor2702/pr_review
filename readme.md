# PR Review Agent

[![Frontend Live](https://img.shields.io/badge/Live-Production-success?style=for-the-badge)](https://pr-review.pages.dev)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-F38020?style=for-the-badge&logo=cloudflare)](https://workers.cloudflare.com)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini_1.5-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **AI-powered code review automation platform** providing instant, comprehensive feedback on pull requests with enterprise-grade analysis and scoring.

## Overview

PR Review Agent is a serverless application that leverages Google Gemini AI to automatically review code changes in pull requests. Built on Cloudflare's edge network, it delivers sub-50ms global response times while maintaining zero infrastructure costs.

**Key Capabilities:**
- Automated code quality assessment with 0-100 scoring
- Security vulnerability detection and analysis
- Best practices validation across multiple languages
- Real-time feedback through modern web interface
- GitHub API integration with intelligent rate limit management

## 🚀 Live Production Environment

The application is deployed on Cloudflare's global edge network with enterprise reliability:

| Component | URL | Technology |
|-----------|-----|------------|
| **Frontend** | [pr-review.pages.dev](https://pr-review.pages.dev) | Cloudflare Pages + React + TypeScript |
| **API** | [pr-review-worker.kenshifan3000.workers.dev](https://pr-review-worker.kenshifan3000.workers.dev) | Cloudflare Workers + Node.js |
| **AI Engine** | Google Gemini 1.5 Flash | Generative AI |

**Infrastructure Metrics:**
- Global CDN with 300+ edge locations
- < 50ms average response time worldwide
- 5,000 GitHub API requests/hour capacity
- Zero infrastructure maintenance required
- 100% serverless architecture

## Architecture

### Technology Stack

**Frontend**
- React 18 with TypeScript
- Tailwind CSS for styling
- Vite for build tooling
- PWA capabilities with offline support

**Backend**
- Cloudflare Workers (serverless)
- Google Gemini 1.5 Flash AI model
- GitHub API proxy with rate limit optimization

**Infrastructure**
- Cloudflare Pages for static hosting
- Cloudflare Workers for API endpoints
- Edge computing for global distribution
- Zero-downtime deployments

### Deployment Architecture

```
User Request
    ↓
Cloudflare Edge (300+ locations)
    ↓
├─→ Pages (Static Assets)
└─→ Workers (API + AI Processing)
        ↓
    ├─→ GitHub API
    └─→ Google Gemini API
```

## Features

### Core Capabilities

**Code Analysis**
- Automated pull request review using Google Gemini 1.5 Flash
- Security vulnerability detection
- Code complexity analysis
- Best practices validation
- 0-100 quality scoring with letter grades (A+ to F)

**Integration**
- Direct GitHub repository integration
- GitHub API proxy to bypass CORS restrictions
- Rate limit management (5,000 requests/hour with token)
- Optional user token override for priority access

**User Interface**
- Modern React-based web dashboard
- Real-time backend status monitoring
- Interactive PR browsing and selection
- Comprehensive results visualization
- Mobile-responsive design

### Web Dashboard

The production application features a professional web interface with:

- **PR Discovery**: Browse and filter available pull requests
- **Instant Analysis**: Submit PRs for AI-powered review
- **Rich Results**: Color-coded findings with severity indicators
- **Score Breakdown**: Overall score, grade, and detailed metrics
- **Token Management**: Optional GitHub token input for rate limits

Access the live dashboard at [pr-review.pages.dev](https://pr-review.pages.dev)

## Getting Started

### Prerequisites

**Required:**
- Node.js 18+ and npm
- Cloudflare account (free tier)
- Google Gemini API key ([Get one here](https://ai.google.dev))

**Optional:**
- GitHub personal access token (for higher rate limits)

### Local Development

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```
Access at `http://localhost:5173`

**Worker Setup:**
```bash
cd workers
npm install
npx wrangler dev
```
API available at `http://localhost:8787`

### Environment Configuration

**Workers Environment Variables:**
```bash
# Set via Wrangler CLI (encrypted)
npx wrangler secret put GEMINI_API_KEY
npx wrangler secret put GITHUB_TOKEN  # Optional but recommended
```

**Frontend Environment Variables:**
```bash
# Create .env in frontend/
VITE_API_URL=https://pr-review-worker.kenshifan3000.workers.dev
```

### Deployment

**Workers Deployment:**
```bash
cd workers
npx wrangler login
npx wrangler deploy
```

**Pages Deployment:**
```bash
cd frontend
npm run build
npx wrangler pages deploy dist --project-name=pr-review
```

**Setting Secrets:**
```bash
# Workers secrets (encrypted)
cd workers
npx wrangler secret put GEMINI_API_KEY
npx wrangler secret put GITHUB_TOKEN
```

## Usage

### Web Interface

1. Visit [pr-review.pages.dev](https://pr-review.pages.dev)
2. Click "🚀 Start New Review"
3. Enter repository details (owner, repo, PR number)
4. Optionally paste GitHub token for higher rate limits
5. Click "Start Review"
6. View comprehensive analysis results

### API Endpoints

**Health Check:**
```bash
GET https://pr-review-worker.kenshifan3000.workers.dev/api/status
```

**Submit PR Review:**
```bash
POST https://pr-review-worker.kenshifan3000.workers.dev/api/review
Content-Type: application/json

{
  "diff": "...",
  "repo": "microsoft/vscode",
  "author": "username",
  "pr_number": 123,
  "title": "PR Title",
  "description": "PR Description"
}
```

**GitHub API Proxy** (CORS bypass):
```bash
GET https://pr-review-worker.kenshifan3000.workers.dev/api/github-proxy?path=/repos/microsoft/vscode/pulls/123
```

### API Response Format

```json
{
  "score": 85,
  "grade": "B+",
  "summary": "Code demonstrates good practices with minor improvements needed...",
  "suggestions": [
    "Consider adding input validation for user data",
    "Error handling could be more specific",
    "Add unit tests for edge cases"
  ],
  "severity_breakdown": {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3
  },
  "metadata": {
    "timestamp": "2025-12-16T12:00:00Z",
    "repo": "microsoft/vscode",
    "author": "username",
    "lines_changed": 247
  }
}
```

## Configuration

### Environment Variables

**Cloudflare Workers (Backend):**

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI reviews |
| `GITHUB_TOKEN` | Recommended | Server-side GitHub token (5000 req/hour) |
| `ENVIRONMENT` | No | Runtime environment (default: production) |
| `API_VERSION` | No | API version identifier |
| `ALLOWED_ORIGINS` | No | CORS allowed origins (default: *.pages.dev) |

**Frontend (Pages):**

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Worker API endpoint URL |

### GitHub Token Management

The application supports two token modes:

1. **Server-side token** (recommended): Set via `wrangler secret put GITHUB_TOKEN`
   - Provides 5,000 req/hour for all users
   - No user friction
   - Centrally managed

2. **User-provided token**: Optional field in web interface
   - Takes priority over server token
   - User's personal rate limit
   - More secure for sensitive repos

## Understanding Results

### Quality Scoring System

Reviews are scored on a 0-100 scale with corresponding letter grades:

| Score | Grade | Quality Level |
|-------|-------|---------------|
| 95-100 | A+ | Exceptional |
| 90-94 | A | Excellent |
| 85-89 | B+ | Very Good |
| 80-84 | B | Good |
| 75-79 | C+ | Above Average |
| 70-74 | C | Average |
| 60-69 | D | Below Average |
| 0-59 | F | Needs Improvement |

### Severity Levels

**Critical**: Security vulnerabilities, data loss risks
**High**: Major bugs, performance issues
**Medium**: Code quality concerns, maintainability
**Low**: Style suggestions, minor optimizations

### Review Criteria

The AI evaluates code across multiple dimensions:

1. **Code Quality**: Readability, maintainability, and adherence to best practices
2. **Security**: Vulnerability detection and safe coding patterns
3. **Performance**: Efficiency and optimization opportunities
4. **Testing**: Test coverage and edge case handling
5. **Documentation**: Code comments and clarity



## Project Structure

```
pr_review_agent/
├── frontend/                 # React TypeScript web interface
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page components
│   │   └── lib/             # Utilities and API clients
│   ├── public/              # Static assets
│   └── package.json
│
├── workers/                  # Cloudflare Workers backend
│   ├── src/
│   │   └── index.ts         # Worker entry point and API handlers
│   ├── wrangler.toml        # Worker configuration
│   └── package.json
│
└── README.md                 # This file
```

## Security & Privacy

### Data Handling

- GitHub tokens are encrypted via Cloudflare Secrets
- User-provided tokens exist only in browser memory (session-only)
- No PR data is stored persistently
- All processing happens in real-time
- Zero data retention after review completion

### API Security

- CORS protection with allowed origins whitelist
- Rate limiting via GitHub API quotas
- Input validation on all endpoints
- Secure HTTPS-only communication

## Development

### Local Development Workflow

1. **Start Worker locally:**
```bash
cd workers
npm install
npx wrangler dev
```

2. **Start Frontend with local API:**
```bash
cd frontend
# Edit .env to point to local worker
echo "VITE_API_URL=http://localhost:8787" > .env
npm install
npm run dev
```

3. **Test the integration:**
- Frontend: `http://localhost:5173`
- Worker API: `http://localhost:8787`

### Making Changes

**Frontend modifications:**
- Edit files in `frontend/src/`
- Hot reload enabled automatically
- Build for production: `npm run build`

**Worker modifications:**
- Edit `workers/src/index.ts`
- Restart wrangler dev to see changes
- Deploy: `npx wrangler deploy`

### Testing

**Frontend:**
```bash
cd frontend
npm run build  # Check for TypeScript errors
```

**Worker:**
```bash
cd workers
npx wrangler dev
# Test endpoints with curl or Postman
```

## Troubleshooting

### Common Issues

**Rate Limit Errors (403)**
- **Symptom**: "GitHub API rate limit exceeded"
- **Solution**: 
  1. Add server-side GitHub token: `npx wrangler secret put GITHUB_TOKEN`
  2. Or paste personal token in web interface
  3. Wait 1 hour for rate limit reset

**Worker Not Responding**
- **Symptom**: Network errors, timeouts
- **Solution**: 
  1. Check worker status: `npx wrangler tail`
  2. Verify environment variables are set
  3. Check Cloudflare dashboard for errors

**CORS Errors**
- **Symptom**: "Cross-origin request blocked"
- **Solution**: 
  1. Verify `ALLOWED_ORIGINS` includes your domain
  2. Check frontend uses correct `VITE_API_URL`
  3. GitHub requests should use `/api/github-proxy`

**Build Failures**
- **Symptom**: TypeScript compilation errors
- **Solution**:
  1. Delete `node_modules` and reinstall: `npm install`
  2. Clear build cache: `rm -rf dist`
  3. Check Node.js version: `node -v` (need 18+)

### Getting Help

1. Check browser console for error messages
2. Review worker logs: `npx wrangler tail`
3. Verify all environment variables are set correctly
4. Test API endpoints directly with curl

## Performance

### Benchmarks

- **Average Response Time**: < 3 seconds for typical PRs
- **AI Processing**: 1-2 seconds (Google Gemini 1.5 Flash)
- **GitHub API Latency**: < 500ms (via Cloudflare proxy)
- **Global Edge Latency**: < 50ms to nearest Cloudflare POP

### Scalability

- Handles concurrent requests via Cloudflare Workers
- No cold starts (always warm on edge)
- Auto-scales to handle traffic spikes
- Rate limited by GitHub API (5000 req/hour with token)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Guidelines

1. Follow TypeScript best practices for frontend code
2. Use proper error handling in all API endpoints
3. Add comments for complex logic
4. Test changes locally before deploying
5. Update documentation for new features

## Acknowledgments

**Technologies:**
- [Cloudflare Workers](https://workers.cloudflare.com) - Serverless compute platform
- [Cloudflare Pages](https://pages.cloudflare.com) - Static site hosting
- [Google Gemini](https://ai.google.dev) - AI language model
- [React](https://react.dev) - Frontend framework
- [Tailwind CSS](https://tailwindcss.com) - Styling framework

---

**Built with Cloudflare Workers and Google Gemini AI**