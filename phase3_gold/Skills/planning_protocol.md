# Planning Protocol Skill

## Description
This skill handles the reasoning and planning phase before any task execution in the Silver tier system.

## Decision Steps
1. Analyze the incoming task from the Inbox directory
2. Determine the complexity and requirements of the task
3. Create a detailed plan before executing any action
4. Identify potential risks and mitigation strategies

## Planning Steps
1. **Task Analysis**
   - What: Analysis of what needs to be done
   - Why: Purpose and importance of the task
   - How: Proposed approach to complete the task
   - Constraints: Any limitations or requirements

2. **Step-by-Step Planning**
   - Break down the task into manageable steps
   - Assign priorities to each step
   - Identify dependencies between steps

3. **Resource Assessment**
   - Determine what resources are needed
   - Check availability of required tools
   - Identify potential bottlenecks

4. **Risk Assessment**
   - Identify possible challenges
   - Develop contingency plans
   - Define success criteria

## Execution Requirements
1. Before executing any task, generate a Plan_<task_name>_<timestamp>.md file in the /Plans directory
2. The plan must include all the sections mentioned above
3. The execution process should reference the plan during task completion
4. Log all planning activities to Logs/activity.log

## Example Plan Structure
```markdown
# Reasoning Plan for: [Task Title]

## Original Task
[Content of the original task]

## Task Analysis
- What: [Analysis of what needs to be done]
- Why: [Purpose and importance of the task]
- How: [Proposed approach to complete the task]
- Constraints: [Any limitations or requirements]

## Step-by-Step Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Resources Needed
- [List any required resources]

## Potential Challenges
- [Identify possible issues]
- [Risk mitigation strategies]

## Success Criteria
- [Define what successful completion looks like]

## Decision Log
- [Timestamp]: Plan created for task
- [Timestamp]: [Add decision points as needed]
```

## Logging Requirements
- Log creation of each plan file
- Log reference to plan during task execution
- Log any deviations from the original plan