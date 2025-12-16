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
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          PR Review Agent
        </h1>
        <p className="text-lg text-muted-foreground">
          AI-powered code reviews for your pull requests • Powered by Google Gemini
        </p>
      </div>

      {/* Definition */}
      <Card className="border border-blue-200 bg-gradient-to-br from-blue-50/80 via-white to-purple-50/60">
        <CardHeader>
          <CardTitle>What does the PR Review Agent do?</CardTitle>
          <CardDescription>
            It inspects any GitHub pull request by fetching the diff, running it through Google Gemini, and returning a human-friendly report with scores, findings, and suggested fixes. Think of it as your always-on senior reviewer who never gets tired.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          {[
            'Understands context from titles, descriptions, and the diff itself',
            'Scores quality across security, performance, testing, and documentation',
            'Surfaces actionable remediation notes you can paste directly into review comments',
          ].map((item) => (
            <div key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
              <span className="mt-1 inline-block h-2 w-2 rounded-full bg-blue-500" aria-hidden />
              <span>{item}</span>
            </div>
          ))}
        </CardContent>
      </Card>
      
      {/* Quick Actions */}
      <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            Quick Actions
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button 
            onClick={() => setIsReviewModalOpen(true)} 
            size="lg"
            className="w-full text-lg py-6"
          >
            <GitPullRequest className="mr-2 h-5 w-5" />
            Start New Review
          </Button>
          <p className="text-sm text-muted-foreground text-center">
            Analyze any GitHub PR with AI in seconds
          </p>
        </CardContent>
      </Card>

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