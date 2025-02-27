# Define the behavioral analysis prompt template
ANALYZE_AND_SUGGEST_PROMPT = ("""Functional behavioral analysis based on radical behaviorism and intervention technique suggestions [or habits]

BEHAVIORAL DATA:
- Current behavior you want to analyze: "{behavior}"
- Context or environment in which the behavior occurs: "{antecedent}"
- Immediate consequences of the analyzed behavior (what happens right after the behavior): "{consequence}"
- Previous attempts to change the analyzed behavior: "{previous_attempts}"

INSTRUCTIONS:
1. First, perform a functional analysis based on radical behaviorism and show the behavioral pattern considering:
* The context/environment in which the behavior occurs and the immediate consequence of the behavior
- Frequency and intensity of the behavior
- Other contexts/environments where the same behavior occurs
- Short and long-term consequences
- Behavioral excesses and deficits resulting from the established pattern
- Impact on daily functioning
- Potential barriers to change
- Strengths from previous attempts

2. Based on this analysis, suggest 3-4 practical habits. For each habit, provide:
- Habit name: short and clear title
- Description: brief explanation of the habit
- Implementation: detailed step-by-step execution
- Scientific basis: reference or evidence supporting this habit

RESPONSE FORMAT:
[Behavioral analysis, more than 3 paragraphs]

SUGGESTED HABITS:

1. [Habit name]
Description: [brief description]
How to implement: [practical steps]
Scientific basis: [reference or evidence]

[Repeat format for each suggested habit]""") 