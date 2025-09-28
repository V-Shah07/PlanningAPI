from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

# Load .env file first
load_dotenv()
print("DEBUG OPENAI KEY:", os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI
app = FastAPI()

# Initialize OpenAI client AFTER loading .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request schema
class TaskRequest(BaseModel):
    tasks: str

# System prompt with scheduling rules + tagging
SYSTEM_PROMPT = """
You are a scheduling assistant that converts natural language requests into a structured JSON object.

Always respond **only** with valid JSON in the following format:

{
  "conflicts": [ 
    // list conflicts between tasks if times overlap
  ],
  "scheduled_tasks": [
    {
      "category": "string",
      "title": "string",
      "description": "string",
      "start_time": "YYYY-MM-DDTHH:MM:SS",
      "end_time": "YYYY-MM-DDTHH:MM:SS",
      "priority": number,
      "reasoning": "string",
      "tags": ["priority_tag", "category_tag"]
    }
  ],
  "suggestions": [],
  "summary": "string"
}

Tagging rules:
- Each task must include a `"tags"` list with exactly 2 values:
  1. A **priority tag** that corresponds to the numeric priority:
     - 1 → "high"
     - 2 → "medium"
     - 3 → "low"
  2. A **category tag** chosen from: ["work", "academic", "social", "extracurriculars", "others", "health", "fitness"]

Scheduling rules:
1. Extract **only the new tasks** from the user's request.  
2. If the request mentions **pre-scheduled tasks with fixed times**, treat those as **blocked time slots** but do **not** include them in `"scheduled_tasks"`.  
3. Always assign new tasks to the **current day** using this datetime format: YYYY-MM-DDTHH:MM:SS, unless they are **long-term tasks** (see rule 6).  
4. **Do not schedule any new task within 30 minutes of the current time.**  
5. Schedule new tasks only in **free time slots that do not overlap** with pre-scheduled tasks.  
6. If the request contains a **long-term task with a future date (e.g., "exam next week" or "tryouts on October 7th")**, then:  
   - Treat that task as a **final goal**.  
   - Generate **3-6 smaller subtasks** that logically build up to the final event.  
   - Spread these subtasks evenly across the days leading up to the future date.  
   - Assign each subtask a short description explaining how it helps achieve the final task.  
   - The **final event itself** should also appear on the actual due date.  
7. Assign **reasonable times of day by convention**:  
   - Studying → 10 AM–12 PM or 2–4 PM.  
   - Workouts → 7–10 AM or 4–6 PM.  
   - Cooking dinner → 6–7 PM.  
   - Cleaning/chores → 11 AM or 3 PM.  
8. Default durations: Studying = 2h, Workout = 1h, Cooking = 1h, Cleaning = 30m, unspecified = 1h.  
9. Adjust task durations if the user specifies intensity or quantity.  
10. Assign priorities: academics/work (1), chores (2), personal/leisure (3).  
11. Provide reasoning for each task's placement. Mention when time was adjusted to avoid conflicts or the 30-minute buffer.  
12. Ensure `conflicts` is empty unless two **new** tasks overlap.  
13. Always return valid JSON only — no extra commentary.  
"""

@app.post("/schedule")
async def schedule_tasks(request: TaskRequest):
    today = date.today().strftime("%Y-%m-%d")
    now = datetime.now()
    earliest_start = (now + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%S")

    print(f"DEBUG: Current time: {now.strftime('%Y-%m-%dT%H:%M:%S')}")
    print(f"DEBUG: Earliest start time: {earliest_start}")

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Today is {today}. The current time is {now.strftime('%H:%M')}.\n"
                        f"Do not schedule any new task before {earliest_start}.\n"
                        f"{request.tasks}"
                    )
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        parsed_data = json.loads(content)
        return parsed_data

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )