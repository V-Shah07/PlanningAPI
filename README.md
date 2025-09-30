# PlannerAPI - Backend for Promptly

Backend API for [Promptly](https://github.com/V-Shah07/Promptly), an agentic AI-powered React Native productivity app.

## What it does

Provides intelligent task scheduling and planning for Promptly's AI-powered productivity system. Converts natural language task requests into structured schedules with conflict detection, priority assignment, and smart time allocation.

## Tech Stack

- **FastAPI** - Python web framework
- **OpenAI GPT-4** - AI-powered task scheduling and planning
- **Pydantic** - Data validation and serialization
- **Railway** - Deployment platform

## Endpoints

- `POST /schedule` - Convert natural language tasks into structured schedules with timing, priorities, and conflict detection

## Features

- **Smart Scheduling** - Automatically assigns optimal times based on task type and existing commitments
- **Conflict Detection** - Identifies and reports scheduling conflicts
- **Priority Management** - Assigns priority levels (high/medium/low) with category tagging
- **Long-term Planning** - Breaks down future tasks into actionable subtasks
- **Time Buffer** - Ensures no tasks are scheduled within 30 minutes of current time

## Integration

This API powers Promptly's intelligent scheduling agents, enabling natural language task input and automated calendar optimization for the mobile app.
