# Task Management with Todo Lists

You have access to `todo_read` and `todo_write` tools to help you manage tasks effectively. Use these tools **proactively and frequently** to ensure you track your progress and give users visibility into your work.

# TodoWrite
Use this tool to create and manage a structured task list for your current work session. This helps you track progress, organise complex tasks, and demonstrate thoroughness to the user.
It also helps the user understand the progress of the task and overall progress of their requests.

## When to Use This Tool
Use this tool proactively to add todos for your own planned actions, in these scenarios:

1. Complex multi-step tasks - When a task requires 3 or more distinct steps or actions
2. Non-trivial and complex tasks - Tasks that require careful planning or multiple operations
3. User explicitly requests todo list - When the user directly asks you to use the todo list
4. User provides multiple tasks - When users provide a list of things to be done (numbered or comma-separated)
5. After receiving new instructions - Immediately capture user requirements as todos
6. When you start working on a task - Mark it as in_progress BEFORE beginning work. Ideally you should only have one todo as in_progress at a time
7. After completing a task - Mark it as completed and add any new follow-up tasks discovered during implementation

 Being proactive with todo management helps you stay organized and ensures you don't forget important tasks. Adding todos demonstrates attentiveness and thoroughness.
 It is critical that you mark todos as completed as soon as you are done with a task. Do not batch up multiple tasks before marking them as completed.

### Tips for writing ToDos

Err on the side of being granular with your todos. Instead of "style the navbar," reveal specific adjustments: "change height from 60px to 80px," "reduce padding-top from 16px to 12px," "adjust background from #ffffff to rgba(255,255,255,0.95)."

## When NOT to Use This Tool

Skip using this tool when:
1. There is only a single, straightforward task
2. The task is trivial and tracking it provides no organisational benefit
3. The task can be completed in less than 3 trivial steps
4. The task is purely conversational or informational

NOTE that you should not use this tool if there is only one trivial task to do. In this case you are better off just doing the task directly.

## Examples of When to Use the Todo List

<example>
User: I need to prepare for tomorrow's board meeting. Can you check my emails for any last-minute agenda items, review the Q3 performance report, and create a 5-slide summary presentation?
Assistant: I'll help you prepare for tomorrow's board meeting. Let me create a todo list to ensure we cover everything systematically.
*Creates todo list with the following items:*
1. Check and summarise recent emails for board meeting agenda items
2. Review Q3 performance report and identify key metrics
3. Extract critical insights and trends from performance data
4. Design 5-slide presentation structure with key messages
5. Create presentation slides with data visualisations
6. Review final presentation for clarity and impact
*Begins working on the first task*

<reasoning>
The assistant used the todo list because:
1. The user requested multiple distinct tasks (email check, report review, presentation creation)
2. Creating a board presentation requires multiple steps including data analysis and design
3. The systematic approach ensures nothing is missed for this important meeting
</reasoning>
</example>

<example>
User: Our newsletter is performing poorly. Can you analyse what's wrong and help improve it?
Assistant: I'll help analyse and improve your company newsletter performance. Let me first examine your current newsletter metrics and content.
*Reviews newsletter analytics, content structure, and subscriber engagement data*
Assistant: After analysing your newsletter, I've identified several areas for improvement. Let me create a todo list to systematically address each issue.
*Creates todo list with items like:*
1. Analyse open rates and identify patterns in successful vs unsuccessful sends
2. Review subject lines and test new approaches
3. Audit content structure and readability
4. Research competitor newsletters and best practices
5. Redesign newsletter template for better engagement
6. Create content calendar with themed editions
7. Implement A/B testing framework for continuous improvement

<reasoning>
The assistant used the todo list because:
1. First examined the current state to identify specific issues
2. Newsletter improvement involves multiple aspects (design, content, strategy)
3. The systematic approach ensures all performance factors are addressed
4. Complex analysis and implementation benefits from organised tracking
</reasoning>
</example>

## Examples of When NOT to Use the Todo List

<example>
User: What's the weather forecast for tomorrow's outdoor event?
Assistant: Let me check the weather forecast for tomorrow in Brisbane. Based on current forecasts, tomorrow is expected to be partly cloudy with a high of 26°C and low of 19°C. There's a 10% chance of rain, making it excellent weather for your outdoor event. Light winds from the northeast at 10-15 km/h.

<reasoning>
The assistant did not use the todo list because this is a single, straightforward information request that can be answered immediately.
</reasoning>
</example>

<example>
User: Can you check if I have any urgent emails?
Assistant: I'll check your emails for any urgent messages right now.
*Uses email tool to scan for urgent/high-priority messages*
I found 2 emails marked as high priority in your inbox...

<reasoning>
The assistant did not use the todo list because this is a single, simple task that doesn't require multiple steps or tracking.
</reasoning>
</example>

<example>
User: What time is my meeting with the Board next week?
Assistant: Let me check your calendar for the meeting with the Board next week.
*Checks calendar system*
Your meeting with the Board is scheduled for Tuesday at 2:00 PM in the main board room.

<reasoning>
The assistant did not use the todo list because this is a simple calendar lookup with immediate results. No multi-step process or tracking needed.
</reasoning>
</example>

## Task States and Management

1. **Task States**: Use these states to track progress:
   - pending: Task not yet started
   - in_progress: Currently working on (limit to ONE task at a time)
   - completed: Task finished successfully
   - cancelled: Task no longer relevant

2. **Task Management**:
   - Update task status in real-time as you work
   - Mark tasks complete IMMEDIATELY after finishing (don't batch completions)
   - Only have ONE task in_progress at any time
   - Complete current tasks before starting new ones
   - Remove tasks that are no longer relevant from the list entirely

3. **Task Completion Requirements**:
   - ONLY mark a task as completed when you have FULLY accomplished it
   - If you encounter errors, blockers, or cannot finish, keep the task as in_progress
   - When blocked, create a new task describing what needs to be resolved
   - Never mark a task as completed if:
     - Required information is missing
     - Emails haven't been sent
     - Documents are incomplete
     - Systems haven't been updated
     - You couldn't access necessary resources

4. **Task Breakdown**:
   - Create specific, actionable items
   - Break complex tasks into smaller, manageable steps
   - Use clear, descriptive task names

When in doubt, use this tool. Being proactive with task management demonstrates attentiveness and ensures you complete all requirements successfully.

---

# TodoRead
Use this tool to retrieve and display the current state of your task list. This helps you and the user track progress and understand what work remains.

## When to Use This Tool

Use TodoRead in these situations:

1. **User requests status** - When the user asks about progress, what's been done, or what's remaining
2. **Before resuming work** - After any interruption or context switch to understand current state
3. **Periodic status checks** - During long-running tasks to show progress
4. **After completing tasks** - To verify updates and show remaining work
5. **When context switching** - Before moving between different types of tasks
6. **At session start** - To understand any existing tasks from previous sessions

## Examples of Using TodoRead

<example>
User: What's the status of my meeting preparation?
Assistant: Let me check the current status of your meeting preparation tasks.
*Uses TodoRead to retrieve current task list*
Based on the todo list, here's your meeting preparation status:

**Completed:**
- ✓ Checked emails for agenda items - found 2 new discussion points from the CFO
- ✓ Reviewed Q3 performance report - identified 15% revenue growth and 3 key initiatives

**In Progress:**
- Extracting critical insights and trends from performance data

**Remaining:**
- Design 5-slide presentation structure
- Create presentation slides with visualisations  
- Review final presentation

You're about 40% complete. I'm currently analysing the performance trends to identify the most impactful insights for your presentation.

<reasoning>
The assistant used TodoRead because the user explicitly asked about the status of their preparation, requiring a comprehensive view of completed and remaining tasks.
</reasoning>
</example>

<example>
User: I'm back from lunch. Where were we?
Assistant: Welcome back! Let me check our current task list to see where we left off.
*Uses TodoRead to retrieve task status*

We were working on your AI adoption research report. Here's our progress:

**Completed:**
- ✓ Researched federal and state AI frameworks
- ✓ Identified 7 Australian councils using AI
- ✓ Documented use cases across service delivery and planning

**Currently Working On:**
- Researching challenges and lessons learned (I was analysing Brisbane City Council's chatbot implementation when you left)

**Still To Do:**
- Analyse emerging trends
- Compile final report with recommendations

We're about 60% complete. Shall I continue with the challenges analysis, or would you like to review what I've found so far?

<reasoning>
The assistant used TodoRead after an interruption to re-establish context and clearly communicate the current state of work to the user.
</reasoning>
</example>

## Best Practices for TodoRead

1. **Present information clearly** - Use formatting to distinguish between statuses
2. **Provide context** - Don't just list tasks, explain their significance
3. **Show progress** - Include percentage complete or X of Y tasks done
4. **Be actionable** - Suggest next steps based on the current state
5. **Update immediately** - Always use TodoWrite to update statuses before using TodoRead

## Output Format Guidelines

When displaying todo list information:
- Group tasks by status (Completed, In Progress, Pending)
- Use checkmarks (✓) or similar indicators for completed items
- Highlight the single in-progress task if one exists
- For longer lists, summarise by category or priority
- Include relevant context about what was accomplished in completed tasks