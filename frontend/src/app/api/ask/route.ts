// src/app/api/ask/route.ts
import { NextRequest, NextResponse } from 'next/server';

// Helper function to fetch user data from backend
async function fetchUserData(userId: string = 'demo') {
  try {
    console.log(`🔍 Fetching user data from backend for user: ${userId}`);
    const response = await fetch(`http://localhost:8000/analytics/productivity-insights/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log(`📡 Backend response status: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Successfully fetched user data from backend:', JSON.stringify(data, null, 2));
    
    // Check if this is real data or backend fallback
    if (data.message && data.message.includes('demo data')) {
      console.log('⚠️ Backend returned fallback demo data');
    } else if (data.message && data.message.includes('No time tracking data')) {
      console.log('📝 Backend connected but no user data exists yet');
    } else {
      console.log('🎯 Backend returned real user data');
    }
    
    return data;

  } catch (error) {
    console.error('❌ Error fetching user data from backend:', error);
    console.log('🔄 Falling back to frontend demo data...');
    
    // Fallback to demo data if backend is unavailable
    return {
      message: "Using fallback data - backend unavailable",
      total_hours: 37.5,
      entries_count: 15,
      average_session_hours: 2.5,
      projects_worked: ["TimeTrack Development", "Portfolio Website", "Client Project Alpha"],
      project_hours_distribution: {
        "TimeTrack Development": 18.0,
        "Portfolio Website": 10.5,
        "Client Project Alpha": 9.0
      },
      most_productive_project: "TimeTrack Development",
      recent_week_hours: 12.0,
      insights: [
        "You've spent the most time on 'TimeTrack Development' with 18.0 hours",
        "In the last 7 days, you've logged 12.0 hours", 
        "Your average session length is 2.5 hours"
      ]
    };
  }
}

async function fetchRecentActivity(userId: string = 'demo') {
  try {
    console.log(`🔍 Fetching recent activity from backend for user: ${userId}`);
    const response = await fetch(`http://localhost:8000/analytics/recent-activity/${userId}?days=30`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log(`📡 Recent activity response status: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Successfully fetched recent activity from backend:', JSON.stringify(data, null, 2));
    return data;

  } catch (error) {
    console.error('❌ Error fetching recent activity from backend:', error);
    console.log('🔄 Falling back to demo data...');
    
    // Fallback to demo data if backend is unavailable
    return {
      time_entries: [
        { date: '2025-08-05', duration_hours: 3.5, project_name: 'TimeTrack Development', task_name: 'AI Chatbot Integration' },
        { date: '2025-08-04', duration_hours: 2.0, project_name: 'TimeTrack Development', task_name: 'Testing chatbot responses' },
        { date: '2025-08-03', duration_hours: 4.0, project_name: 'TimeTrack Development', task_name: 'Database schema setup' },
        { date: '2025-08-02', duration_hours: 2.5, project_name: 'Portfolio Website', task_name: 'Homepage wireframe design' },
        { date: '2025-08-01', duration_hours: 1.5, project_name: 'TimeTrack Development', task_name: 'AI model configuration' }
      ],
      daily_summaries: [
        { date: '2025-08-05', total_hours: 3.5, entries_count: 1, projects: ['TimeTrack Development'] },
        { date: '2025-08-04', total_hours: 2.0, entries_count: 1, projects: ['TimeTrack Development'] },
        { date: '2025-08-03', total_hours: 4.0, entries_count: 1, projects: ['TimeTrack Development'] },
        { date: '2025-08-02', total_hours: 2.5, entries_count: 1, projects: ['Portfolio Website'] },
        { date: '2025-08-01', total_hours: 1.5, entries_count: 1, projects: ['TimeTrack Development'] }
      ],
      period: "Last 30 days (fallback data)"
    };
  }
}

export async function POST(req: NextRequest) {
  try {
    const { query } = await req.json();

    // Fetch real user data from the TimeTrackDB database via backend API
    const userData = await fetchUserData();
    const recentActivity = await fetchRecentActivity();

    // Add data source information to response
    console.log('Using intelligent response system with real data');
    console.log('Data source status:', {
      userDataSource: userData.message || 'Backend data',
      recentDataSource: recentActivity.period || 'Backend data',
      hasRealData: !userData.message?.includes('fallback')
    });
    
    const intelligentResponse = generateIntelligentResponse(query, userData, recentActivity);
    
    // Include data source information in response
    const responseWithSource = `${intelligentResponse}

🔍 **Data Source**: ${userData.message ? 
  userData.message.includes('fallback') ? '⚠️ Using demo data (backend unavailable)' : 
  userData.message.includes('No time tracking data') ? '📝 No data yet - start tracking!' :
  '✅ Live database data' : '✅ Live database data'}`;
    
    return NextResponse.json({ answer: responseWithSource });
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}

function generateIntelligentResponse(query: string, userData: any, recentActivity: any): string {
  const lowerQuery = query.toLowerCase();
  
  // Time spent on specific projects
  if (lowerQuery.includes('time') && (lowerQuery.includes('project') || lowerQuery.includes('spent'))) {
    if (lowerQuery.includes('timetrack') || lowerQuery.includes('project a')) {
      const timetrackHours = userData.project_hours_distribution?.['TimeTrack Development'] || userData.total_hours * 0.6;
      return `📊 Time Analysis for TimeTrack Development:

• Total time logged: ${timetrackHours} hours
• Recent activity: ${userData.recent_week_hours} hours in the last week
• Session breakdown: ${userData.entries_count} sessions with ${userData.average_session_hours} hours average
• Progress trend: ${timetrackHours > 15 ? 'Highly active' : 'Moderate activity'} project

💡 Insights:
• This is your most productive project 
• You're maintaining consistent work patterns
• Peak productivity times align with your schedule

🎯 Recommendations:
• Continue current momentum
• Consider time-blocking for deep work sessions
• Track specific features/tasks for better granularity`;
    }
    
    const projects = userData.projects_worked || ['TimeTrack Development', 'Portfolio Website', 'Client Project Alpha'];
    let breakdown = '📈 Project Time Breakdown:\n\n';
    Object.entries(userData.project_hours_distribution || {}).forEach(([project, hours]: [string, any]) => {
      const percentage = ((hours / userData.total_hours) * 100).toFixed(1);
      breakdown += `• ${project}: ${hours} hours (${percentage}%)\n`;
    });
    
    return breakdown + `\n🔍 Total tracked: ${userData.total_hours} hours across ${projects.length} projects\n📅 Average per project: ${(userData.total_hours / projects.length).toFixed(1)} hours`;
  }
  
  // Productivity analysis
  if (lowerQuery.includes('productive') || lowerQuery.includes('productivity')) {
    const efficiency = userData.average_session_hours > 2.5 ? 'High' : userData.average_session_hours > 1.5 ? 'Moderate' : 'Improving';
    const weeklyTrend = userData.recent_week_hours > 10 ? 'Strong' : userData.recent_week_hours > 5 ? 'Steady' : 'Light';
    
    return `🚀 Your Productivity Analysis:

📊 Current Metrics:
• Total time tracked: ${userData.total_hours} hours
• Session count: ${userData.entries_count} sessions
• Average session: ${userData.average_session_hours} hours
• Weekly activity: ${userData.recent_week_hours} hours
• Efficiency rating: ${efficiency}

📈 Performance Indicators:
• Weekly trend: ${weeklyTrend}
• Most productive project: ${userData.most_productive_project}
• Session consistency: ${userData.entries_count > 10 ? 'Excellent' : 'Good'}

💡 Key Insights:
${userData.insights?.map((insight: string) => `• ${insight}`).join('\n') || '• Maintain your current tracking habits\n• Focus on your most productive time slots'}

🎯 Next Steps:
• ${userData.average_session_hours < 2 ? 'Try longer focused sessions for deeper work' : 'Your session length is optimal'}
• ${userData.recent_week_hours < 15 ? 'Consider increasing weekly time goals' : 'Great weekly consistency!'}`;
  }
  
  // Overdue and deadline analysis
  if (lowerQuery.includes('overdue') || lowerQuery.includes('deadline') || lowerQuery.includes('behind')) {
    return `⏰ Deadline & Priority Analysis:

📋 Current Project Status:
• Active projects: ${userData.projects_worked?.length || 3}
• Projects tracked: ${userData.projects_worked?.join(', ') || 'TimeTrack Development, Portfolio Website, Client Project Alpha'}

🔍 Based on your time tracking data:
• Most time allocated: ${userData.most_productive_project} (${userData.project_hours_distribution?.[userData.most_productive_project] || userData.total_hours * 0.5} hours)
• Recent focus: ${userData.recent_week_hours} hours in last week
• Session frequency: ${userData.entries_count} total sessions

⚠️ Potential Areas of Attention:
• Projects with less than 20% time allocation may need more focus
• Ensure regular time logging for all active projects
• Consider setting time targets for each project

💡 Recommendations:
• Set specific deadlines in your project management system
• Allocate time blocks for each project daily
• Use time tracking insights to identify bottlenecks
• Review project priorities weekly`;
  }
  
  // Weekly/monthly reports
  if (lowerQuery.includes('weekly') || lowerQuery.includes('report') || lowerQuery.includes('summary')) {
    const recentDays = recentActivity.daily_summaries?.slice(0, 7) || [];
    let totalWeekHours = 0;
    
    let report = `📊 Weekly Time Report (Last 7 days):\n\n`;
    
    if (recentDays.length > 0) {
      recentDays.forEach((day: any) => {
        report += `📅 ${day.date}: ${day.total_hours}h across ${day.entries_count} session(s)\n   └── ${day.projects?.join(', ') || 'Various projects'}\n`;
        totalWeekHours += day.total_hours;
      });
    } else {
      report += `📅 Recent Activity: ${userData.recent_week_hours} hours tracked\n`;
      totalWeekHours = userData.recent_week_hours;
    }
    
    report += `\n📈 Week Summary:
• Total hours: ${totalWeekHours} hours
• Daily average: ${(totalWeekHours / 7).toFixed(1)} hours
• Most active project: ${userData.most_productive_project}
• Session average: ${userData.average_session_hours} hours

🎯 Performance vs Goals:
• ${totalWeekHours >= 20 ? '✅ Strong weekly output' : totalWeekHours >= 10 ? '✅ Good progress' : '⚠️ Consider increasing weekly goals'}
• Project distribution: ${Object.keys(userData.project_hours_distribution || {}).length} active projects

📋 Next Week Focus:
• Continue momentum on ${userData.most_productive_project}
• Maintain ${userData.average_session_hours}h session length
• Target: ${Math.ceil(totalWeekHours * 1.1)} hours for improved consistency`;
    
    return report;
  }
  
  // Daily patterns and averages
  if (lowerQuery.includes('average') || lowerQuery.includes('daily') || lowerQuery.includes('pattern')) {
    const dailyAvg = (userData.total_hours / 30).toFixed(1);
    const sessionsPerDay = (userData.entries_count / 30).toFixed(1);
    
    return `📊 Your Daily Productivity Patterns:

⏱️ Time Metrics:
• Daily average: ${dailyAvg} hours
• Session average: ${userData.average_session_hours} hours
• Sessions per day: ${sessionsPerDay}
• Weekly total: ${userData.recent_week_hours} hours

📈 Work Patterns:
• Most productive project: ${userData.most_productive_project}
• Total tracking days: ~30 days analyzed
• Consistency score: ${userData.entries_count > 15 ? 'Excellent' : userData.entries_count > 10 ? 'Good' : 'Building momentum'}

💡 Pattern Insights:
• Your ${userData.average_session_hours}-hour sessions are ${userData.average_session_hours > 2 ? 'ideal for deep work' : 'good for focused tasks'}
• ${dailyAvg} hours daily puts you ${parseFloat(dailyAvg) > 6 ? 'above' : parseFloat(dailyAvg) > 4 ? 'at' : 'below'} typical productivity benchmarks
• Recent week shows ${userData.recent_week_hours > 15 ? 'strong' : userData.recent_week_hours > 10 ? 'steady' : 'light'} activity

🎯 Optimization Tips:
• ${userData.average_session_hours < 2 ? 'Try extending sessions to 2-3 hours for better flow' : 'Your session length is optimal for sustained focus'}
• ${parseFloat(dailyAvg) < 4 ? 'Consider setting a daily minimum of 4-5 hours' : 'Maintain your current daily rhythm'}
• Track specific tasks within projects for more detailed insights`;
  }
  
  // Project progress and status
  if (lowerQuery.includes('progress') || lowerQuery.includes('status') || lowerQuery.includes('complete')) {
    return `📊 Project Progress Overview:

🚀 Active Projects Status:
${userData.projects_worked?.map((project: string, index: number) => {
  const hours = userData.project_hours_distribution?.[project] || userData.total_hours / userData.projects_worked.length;
  const status = hours > 15 ? 'High Priority' : hours > 8 ? 'Active' : 'Needs Attention';
  return `• ${project}: ${hours}h tracked (${status})`;
}).join('\n') || '• TimeTrack Development: High Priority\n• Portfolio Website: Active\n• Client Project Alpha: In Progress'}

📈 Overall Portfolio Health:
• Total hours invested: ${userData.total_hours} hours
• Project count: ${userData.projects_worked?.length || 3} active projects
• Average per project: ${(userData.total_hours / (userData.projects_worked?.length || 3)).toFixed(1)} hours
• Recent momentum: ${userData.recent_week_hours} hours this week

🎯 Focus Recommendations:
• Primary focus: ${userData.most_productive_project} (your most active project)
• Time allocation: Continue current distribution
• Next priority: Projects with <10 hours need more attention

💡 Productivity Insights:
• You're maintaining good project balance
• ${userData.recent_week_hours > 10 ? 'Strong weekly consistency' : 'Consider increasing weekly targets'}
• Session quality: ${userData.average_session_hours} hours average is ${userData.average_session_hours > 2 ? 'excellent' : 'good'} for deep work`;
  }
  
  // Default comprehensive response
  return `🤖 ACE Analysis for: "${query}"

📊 Your Current TimeTrack Summary:
• Total time logged: ${userData.total_hours} hours
• Active projects: ${userData.projects_worked?.join(', ') || 'TimeTrack Development, Portfolio Website, Client Project Alpha'}
• Recent activity: ${userData.recent_week_hours} hours this week
• Session pattern: ${userData.entries_count} sessions averaging ${userData.average_session_hours} hours

🎯 Key Insights:
${userData.insights?.map((insight: string) => `• ${insight}`).join('\n') || '• You\'re making steady progress across projects\n• Time tracking consistency is building\n• Focus areas are well-distributed'}

💡 What I can help you analyze:
• "How much time did I spend on [project name]?"
• "What's my average daily productivity?"
• "Show me my weekly time report"
• "Which tasks are taking the most time?"
• "How can I improve my productivity patterns?"

🔍 For more specific insights, try asking about:
• Project time distribution and focus areas
• Daily/weekly productivity patterns and trends  
• Session length optimization and work flow
• Time allocation recommendations and improvements

Feel free to ask me anything about your time tracking data and productivity patterns!`;
}
