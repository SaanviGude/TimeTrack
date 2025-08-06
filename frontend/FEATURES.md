# TimeTrack React + TypeScript App

This is a complete React + TypeScript application built with Next.js that includes:

## Features

### 🔐 Authentication
- **Login Page** (`/login`): Email/password authentication
- **Signup Page** (`/signup`): User registration with email, password, and confirm password
- **Protected Routes**: Dashboard is protected and redirects to login if not authenticated
- **Persistent Sessions**: Uses localStorage to maintain authentication state

### 📊 Dashboard 
- **Project Management**: View, create, edit, and delete projects
- **User-specific Data**: Each user sees only their own projects
- **Inline Editing**: Click "Edit" to modify project names directly
- **Real-time Updates**: Changes are immediately reflected in the UI

### 🛠 Technical Implementation
- **React Hooks**: Uses useState, useEffect, and custom hooks
- **TypeScript**: Fully typed interfaces and components
- **Context API**: Authentication state management
- **Next.js App Router**: File-based routing system
- **Tailwind CSS**: Modern, responsive styling
- **localStorage**: Mock API for data persistence

## Getting Started

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Run Development Server**:
   ```bash
   npm run dev
   ```

3. **Open Browser**: Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/
│   ├── login/page.tsx          # Login page
│   ├── signup/page.tsx         # Signup page
│   ├── dashboard/page.tsx      # Protected dashboard
│   ├── layout.tsx              # Root layout with AuthProvider
│   └── page.tsx                # Home page (redirects)
├── components/
│   ├── ProtectedRoute.tsx      # Route protection HOC
│   ├── ProjectItem.tsx         # Individual project component
│   └── AddProject.tsx          # Add new project form
├── contexts/
│   └── AuthContext.tsx         # Authentication context
├── services/
│   ├── authService.ts          # Authentication logic
│   └── projectService.ts       # Project CRUD operations
└── types/
    ├── auth.ts                 # Authentication types
    └── project.ts              # Project types
```

## How to Use

### Authentication
1. **First Time**: Visit the app and you'll be redirected to login
2. **Create Account**: Click "create a new account" to go to signup
3. **Login**: Use your email and password to access the dashboard

### Project Management
1. **Add Project**: Use the form at the top of the dashboard
2. **Edit Project**: Click "Edit" button, modify the name, press Enter or click outside
3. **Delete Project**: Click "Delete" button and confirm the action

### Data Persistence
- User accounts and projects are stored in localStorage
- Data persists between browser sessions
- Each user's projects are isolated and secure

## Key Features Implemented

✅ **Authentication Pages**: Login and signup with validation  
✅ **React Router**: Navigation between pages using Next.js App Router  
✅ **Dashboard**: Project CRUD operations with real-time updates  
✅ **localStorage**: Mock API for data persistence  
✅ **Auth Guard**: Protected routes with automatic redirects  
✅ **TypeScript**: Clean interfaces and type safety  
✅ **React Hooks**: Modern functional component approach  

The application is fully functional and ready for development or demonstration!
