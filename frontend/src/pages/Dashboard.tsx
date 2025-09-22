import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  GitPullRequest, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  Clock,
  Users,
  Target,
  Zap,
  BarChart3
} from 'lucide-react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { reviewAPI } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

interface DashboardStats {
  totalReviews: number
  avgScore: number
  activeReviews: number
  weeklyReviews: number
  topIssues: string[]
  recentActivity: RecentActivity[]
  scoreDistribution: { grade: string; count: number }[]
}

interface RecentActivity {
  id: string
  type: 'review_completed' | 'review_started' | 'issue_found'
  pr: string
  repo: string
  score?: number
  timestamp: string
}

export function Dashboard() {
  const [selectedTimeframe, setSelectedTimeframe] = useState<'7d' | '30d' | '90d'>('7d')

  // Fetch dashboard data
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard', selectedTimeframe],
    queryFn: () => fetchDashboardStats(selectedTimeframe),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Mock data fetch function (replace with real API call)
  const fetchDashboardStats = async (timeframe: string): Promise<DashboardStats> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    return {
      totalReviews: 247,
      avgScore: 78.5,
      activeReviews: 3,
      weeklyReviews: 15,
      topIssues: ['Security Issues', 'Code Complexity', 'Style Violations', 'Missing Tests'],
      recentActivity: [
        {
          id: '1',
          type: 'review_completed',
          pr: 'feat: add authentication',
          repo: 'myorg/backend',
          score: 85,
          timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString()
        },
        {
          id: '2',
          type: 'issue_found',
          pr: 'fix: memory leak in parser',
          repo: 'myorg/frontend',
          timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString()
        },
        {
          id: '3',
          type: 'review_started',
          pr: 'refactor: optimize database queries',
          repo: 'myorg/api',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString()
        }
      ],
      scoreDistribution: [
        { grade: 'A+', count: 12 },
        { grade: 'A', count: 28 },
        { grade: 'B+', count: 35 },
        { grade: 'B', count: 22 },
        { grade: 'C+', count: 8 },
        { grade: 'C', count: 3 }
      ]
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-500'
    if (score >= 80) return 'text-blue-500'
    if (score >= 70) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'bg-green-100 text-green-800'
    if (grade.startsWith('B')) return 'bg-blue-100 text-blue-800'
    if (grade.startsWith('C')) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-muted rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor your pull request review performance and insights
          </p>
        </div>
        
        <div className="flex gap-2">
          {(['7d', '30d', '90d'] as const).map((timeframe) => (
            <Button
              key={timeframe}
              variant={selectedTimeframe === timeframe ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedTimeframe(timeframe)}
            >
              {timeframe === '7d' ? '7 Days' : timeframe === '30d' ? '30 Days' : '90 Days'}
            </Button>
          ))}
        </div>
      </motion.div>

      {/* Stats Cards */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        <Card className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Reviews</p>
                <p className="text-2xl font-bold">{stats?.totalReviews.toLocaleString()}</p>
              </div>
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <GitPullRequest className="h-4 w-4 text-blue-600" />
              </div>
            </div>
            <div className="flex items-center mt-2 text-sm">
              <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
              <span className="text-green-500">+12%</span>
              <span className="text-muted-foreground ml-1">from last period</span>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Average Score</p>
                <p className={`text-2xl font-bold ${getScoreColor(stats?.avgScore || 0)}`}>
                  {stats?.avgScore}
                </p>
              </div>
              <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                <Target className="h-4 w-4 text-green-600" />
              </div>
            </div>
            <Progress value={stats?.avgScore} className="mt-2" />
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Reviews</p>
                <p className="text-2xl font-bold">{stats?.activeReviews}</p>
              </div>
              <div className="h-8 w-8 bg-orange-100 rounded-full flex items-center justify-center">
                <Clock className="h-4 w-4 text-orange-600" />
              </div>
            </div>
            <div className="flex items-center mt-2 text-sm">
              <Activity className="h-3 w-3 text-orange-500 mr-1" />
              <span className="text-muted-foreground">In progress</span>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Weekly Reviews</p>
                <p className="text-2xl font-bold">{stats?.weeklyReviews}</p>
              </div>
              <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                <Zap className="h-4 w-4 text-purple-600" />
              </div>
            </div>
            <div className="flex items-center mt-2 text-sm">
              <span className="text-muted-foreground">This week</span>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Recent Activity
              </CardTitle>
              <CardDescription>
                Latest pull request reviews and findings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats?.recentActivity.map((activity, index) => (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 + index * 0.1 }}
                    className="flex items-center gap-4 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex-shrink-0">
                      {activity.type === 'review_completed' && (
                        <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        </div>
                      )}
                      {activity.type === 'issue_found' && (
                        <div className="h-8 w-8 bg-red-100 rounded-full flex items-center justify-center">
                          <AlertCircle className="h-4 w-4 text-red-600" />
                        </div>
                      )}
                      {activity.type === 'review_started' && (
                        <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <Clock className="h-4 w-4 text-blue-600" />
                        </div>
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{activity.pr}</p>
                      <p className="text-sm text-muted-foreground">{activity.repo}</p>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {activity.score && (
                        <Badge variant="outline" className={getScoreColor(activity.score)}>
                          {activity.score}
                        </Badge>
                      )}
                      <span className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Score Distribution */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Score Distribution
              </CardTitle>
              <CardDescription>
                Grade breakdown for recent reviews
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stats?.scoreDistribution.map((item, index) => (
                  <motion.div
                    key={item.grade}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2">
                      <Badge className={getGradeColor(item.grade)}>
                        {item.grade}
                      </Badge>
                      <span className="text-sm">{item.count} reviews</span>
                    </div>
                    <div className="w-20">
                      <Progress 
                        value={(item.count / Math.max(...stats.scoreDistribution.map(s => s.count))) * 100} 
                        className="h-2"
                      />
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Button className="h-auto p-4 flex flex-col items-center gap-2" variant="outline">
                <GitPullRequest className="h-6 w-6" />
                <div className="text-center">
                  <div className="font-medium">New Review</div>
                  <div className="text-xs text-muted-foreground">Start a PR review</div>
                </div>
              </Button>
              
              <Button className="h-auto p-4 flex flex-col items-center gap-2" variant="outline">
                <BarChart3 className="h-6 w-6" />
                <div className="text-center">
                  <div className="font-medium">Analytics</div>
                  <div className="text-xs text-muted-foreground">View detailed stats</div>
                </div>
              </Button>
              
              <Button className="h-auto p-4 flex flex-col items-center gap-2" variant="outline">
                <Users className="h-6 w-6" />
                <div className="text-center">
                  <div className="font-medium">Team Reviews</div>
                  <div className="text-xs text-muted-foreground">Manage team activity</div>
                </div>
              </Button>
              
              <Button className="h-auto p-4 flex flex-col items-center gap-2" variant="outline">
                <Activity className="h-6 w-6" />
                <div className="text-center">
                  <div className="font-medium">Live Monitor</div>
                  <div className="text-xs text-muted-foreground">Real-time updates</div>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}