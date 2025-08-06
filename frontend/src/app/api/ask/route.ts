// src/app/api/ask/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

// Helper function to fetch user data from backend
async function fetchUserData(userId: string = 'demo') {
  try {
    console.log(`Fetching user data from backend for user: ${userId}`);
    const response = await fetch(`http://localhost:8000/analytics/productivity-insights/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Successfully fetched user data from backend:', data);
    return data;

  } catch (error) {
    console.error('Error fetching user data from backend:', error);
    console.log('Falling back to demo data...');
    
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
    console.log(`Fetching recent activity from backend for user: ${userId}`);
    const response = await fetch(`http://localhost:8000/analytics/recent-activity/${userId}?days=30`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Successfully fetched recent activity from backend:', data);
    return data;

  } catch (error) {
    console.error('Error fetching recent activity from backend:', error);
    console.log('Falling back to demo data...');
    
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

    // Try Gemini API with multiple model fallbacks
    const modelNames = [
      "gemini-1.5-flash-latest",
      "gemini-1.5-flash", 
      "gemini-pro"
    ];
    
    for (const modelName of modelNames) {
      try {
        console.log(`Trying Gemini model: ${modelName}`);
        const model = genAI.getGenerativeModel({ model: modelName });
        
        const prompt = `You are an intelligent productivity assistant for a time tracking application called TimeTrack. 
You help users analyze their work patterns and productivity based on their actual time tracking data.

CURRENT USER DATA:
${JSON.stringify(userData, null, 2)}

RECENT ACTIVITY:
${JSON.stringify(recentActivity, null, 2)}

USER QUESTION: ${query}

INSTRUCTIONS:
- Provide helpful, data-driven insights based on the actual user data above
- If the user asks about specific projects, refer to their actual project data
- Calculate productivity metrics and trends from the real data
- Give actionable recommendations for improving productivity
- If asking about time spent, use the actual hours from the data
- Format your response in plain text without markdown
- Be conversational and helpful
- If there's insufficient data, mention that and suggest they log more time entries

Please analyze the user's data and answer their question:`;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        let answer = response.text();

        // Format the response to remove markdown and make it systematic
        answer = answer
          .replace(/\*\*/g, '') // Remove bold markdown
          .replace(/\*/g, '') // Remove italic markdown
          .replace(/#{1,6}\s/g, '') // Remove headers
          .replace(/`{1,3}/g, '') // Remove code blocks
          .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links, keep text
          .replace(/^\s*[-•]\s*/gm, '• ') // Standardize bullet points
          .replace(/^\s*\d+\.\s*/gm, '') // Remove numbered lists
          .replace(/\n{3,}/g, '\n\n') // Remove excessive line breaks
          .trim(); // Remove leading/trailing whitespace

        console.log(`Successfully used model: ${modelName}`);
        return NextResponse.json({ answer });
        
      } catch (modelError: any) {
        console.log(`Model ${modelName} failed:`, modelError.message);
        // Continue to next model
        continue;
      }
    }
    
    // If all models fail, use intelligent demo responses based on the question
    console.log('All Gemini models failed, using intelligent demo mode');
    
    const intelligentResponse = generateIntelligentResponse(query, userData, recentActivity);
    return NextResponse.json({ answer: intelligentResponse });
    
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
  
  if (lowerQuery.includes('project a') || lowerQuery.includes('timetrack')) {
    return `Based on your data, you've spent ${userData.project_hours_distribution?.TimeTrack || userData.total_hours} hours on TimeTrack project. This is your most active project with ${userData.entries_count} time entries logged.`;
  }
  
  if (lowerQuery.includes('productive') || lowerQuery.includes('productivity')) {
    return `Your productivity analysis:
• Total time tracked: ${userData.total_hours} hours across ${userData.entries_count} sessions
• Average session length: ${userData.average_session_hours} hours
• Most productive project: ${userData.most_productive_project}
• Recent week activity: ${userData.recent_week_hours} hours

${userData.insights?.join('\n• ') || 'Keep up the consistent tracking to build better insights!'}`;
  }
  
  if (lowerQuery.includes('overdue') || lowerQuery.includes('deadline')) {
    return `Based on your current project data, I can see you're working on ${userData.projects_worked?.length || 3} projects: ${userData.projects_worked?.join(', ') || 'TimeTrack, Portfolio Website, Client Project A'}.

To better track deadlines and overdue tasks, make sure to:
• Set due dates for your tasks in the system
• Log time entries regularly
• Check your task status updates

Currently showing your active time tracking data rather than task deadlines.`;
  }
  
  if (lowerQuery.includes('weekly') || lowerQuery.includes('report')) {
    const recentDays = recentActivity.daily_summaries?.slice(0, 7) || [];
    let weeklyReport = `Weekly Time Report (Last 7 days):\n\n`;
    
    let totalWeekHours = 0;
    recentDays.forEach((day: any) => {
      weeklyReport += `• ${day.date}: ${day.total_hours} hours on ${day.projects?.join(', ') || 'various projects'}\n`;
      totalWeekHours += day.total_hours;
    });
    
    weeklyReport += `\nTotal: ${totalWeekHours || userData.recent_week_hours} hours`;
    weeklyReport += `\nMost active project: ${userData.most_productive_project}`;
    
    return weeklyReport;
  }
  
  if (lowerQuery.includes('average') || lowerQuery.includes('daily')) {
    return `Your daily productivity patterns:
• Average session: ${userData.average_session_hours} hours
• Total sessions: ${userData.entries_count}
• Daily average: ${(userData.total_hours / 30).toFixed(1)} hours (based on 30-day period)
• Recent week: ${userData.recent_week_hours} hours

Your most consistent work is on ${userData.most_productive_project} project.`;
  }
  
  // Default response with actual data
  return `Based on your TimeTrack data:

Current Stats:
• Total hours tracked: ${userData.total_hours}
• Active projects: ${userData.projects_worked?.join(', ') || 'TimeTrack and others'}
• Recent activity: ${userData.recent_week_hours} hours in the last week

To answer "${query}": ${userData.insights?.[0] || 'Your data shows steady progress across your projects. Keep logging your time to build more detailed insights!'}

For more specific insights, try asking about your productivity trends, project time distribution, or weekly summaries.`;
}
