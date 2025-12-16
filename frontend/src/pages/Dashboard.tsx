import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { NewReviewModal } from "@/components/NewReviewModal";
import { GitPullRequest, Sparkles, Zap, Shield, Clock, CheckCircle2, TrendingUp } from "lucide-react";

export function Dashboard() {
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  
  useEffect(() => {
    // Check backend status
    const checkBackend = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8787';
        const response = await fetch(`${apiUrl}/api/status`, { 
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        });
        setBackendStatus(response.ok ? 'online' : 'offline');
      } catch (error) {
        setBackendStatus('offline');
      }
    };
    checkBackend();
  }, []);
  
  return (
    <div className="space-y-10">
      {/* Hero & Definition */}
      <div className="relative overflow-hidden rounded-3xl border border-blue-200 bg-gradient-to-r from-blue-50 via-white to-purple-50">
        <div className="absolute -left-10 -top-10 h-40 w-40 rounded-full bg-blue-200/50 blur-3xl" aria-hidden />
        <div className="absolute -bottom-12 -right-12 h-48 w-48 rounded-full bg-purple-200/40 blur-3xl" aria-hidden />
        <div className="relative grid gap-8 p-8 lg:grid-cols-[3fr,2fr]">
          <div className="space-y-5">
            <div className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-widest text-blue-700">
              <Sparkles className="h-4 w-4" />
              Meet your AI reviewer
            </div>
            <div>
              <h1 className="text-4xl font-bold tracking-tight text-slate-900">
                PR Review Agent
              </h1>
              <p className="mt-2 text-lg text-slate-600">
                AI-powered code reviews for your pull requests • Powered by Google Gemini
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {[
                'Understands the PR title, description, and entire diff before giving feedback.',
                'Scores quality across security, performance, testing, and documentation pillars.',
                'Returns copy-ready review comments so you can respond in seconds.',
                'Keeps your repo private—analysis runs through your Cloudflare Worker proxy.',
              ].map((item) => (
                <div key={item} className="flex items-start gap-2 rounded-xl bg-white/70 p-3 text-sm text-slate-600 shadow-sm">
                  <span className="mt-1 inline-block h-2 w-2 rounded-full bg-blue-500" aria-hidden />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-4 rounded-2xl bg-white/90 p-6 shadow-xl backdrop-blur">
            <div>
              <p className="text-sm font-semibold text-blue-700">What does the agent do?</p>
              <p className="text-sm text-slate-600">
                It fetches the GitHub PR metadata, streams the diff through Gemini, and packages the findings into a clean scorecard for your team.
              </p>
            </div>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>• Highlights blockers before humans review.</li>
              <li>• Suggests safer patterns and tests to add.</li>
              <li>• Works 24/7 with consistent standards.</li>
            </ul>
            <Button 
              onClick={() => setIsReviewModalOpen(true)}
              size="lg"
              className="text-lg"
            >
              <GitPullRequest className="mr-2 h-5 w-5" />
              Start New Review
            </Button>
            <p className="text-xs text-slate-500">
              Analyze any GitHub PR in ~8 seconds. No credentials are stored—tokens stay in your browser session.
            </p>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <Zap className="h-8 w-8 text-yellow-500 mb-2" />
            <CardTitle>Lightning Fast</CardTitle>
            <CardDescription>
              Get comprehensive code reviews in under 10 seconds
            </CardDescription>
          </CardHeader>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <Shield className="h-8 w-8 text-green-500 mb-2" />
            <CardTitle>Security Focused</CardTitle>
            <CardDescription>
              Identifies vulnerabilities and security issues automatically
            </CardDescription>
          </CardHeader>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CheckCircle2 className="h-8 w-8 text-blue-500 mb-2" />
            <CardTitle>Best Practices</CardTitle>
            <CardDescription>
              Ensures code follows industry standards and conventions
            </CardDescription>
          </CardHeader>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <TrendingUp className="h-8 w-8 text-purple-500 mb-2" />
            <CardTitle>Quality Scores</CardTitle>
            <CardDescription>
              Get detailed grades and metrics for every review
            </CardDescription>
          </CardHeader>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <Clock className="h-8 w-8 text-orange-500 mb-2" />
            <CardTitle>24/7 Available</CardTitle>
            <CardDescription>
              Review PRs anytime, anywhere with serverless architecture
            </CardDescription>
          </CardHeader>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <Sparkles className="h-8 w-8 text-pink-500 mb-2" />
            <CardTitle>AI Powered</CardTitle>
            <CardDescription>
              Leverages Google Gemini 1.5 Flash for intelligent analysis
            </CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Status Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Backend API</span>
            <div className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
              backendStatus === 'online' ? 'bg-green-100 text-green-800' : 
              backendStatus === 'offline' ? 'bg-red-100 text-red-800' : 
              'bg-yellow-100 text-yellow-800'
            }`}>
              {backendStatus === 'online' ? '🟢 Online' : 
               backendStatus === 'offline' ? '🔴 Offline' : 
               '🟡 Checking...'}
            </div>
          </div>
        </CardContent>
      </Card>
      
      <NewReviewModal 
        isOpen={isReviewModalOpen}
        onClose={() => setIsReviewModalOpen(false)}
        backendStatus={backendStatus}
      />
    </div>
  );
}