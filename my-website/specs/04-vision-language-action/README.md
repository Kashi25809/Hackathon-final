# Module 04: Vision-Language-Action (VLA)

**Status:** ⏳ Not Started  
**Focus:** LLM Integration & Voice Control

## 🎯 Learning Objectives

- Implement a speech-to-text pipeline using Whisper (OpenAI or local).
- Parse natural language commands into robot actions using LLMs (Groq/Llama 3).
- Implement cognitive reasoning for multi-step task planning.
- Build the final "Autonomous Humanoid" capstone project.

## 📚 Content Structure

The module content is located in `docs/04-vision-language-action/`:

| File | Topic | Description |
|------|-------|-------------|
| `01-voice-pipeline.md` | Input | Whisper ASR integration |
| `02-llm-reasoning.md` | Cognition | Command parsing with LLMs |
| `03-action-execution.md` | Output | Mapping intent to ROS actions |
| `04-capstone.md` | Capstone | Final end-to-end integration |

## 🛠️ Technical Implementation

### Key Components
1. **Whisper**: Speech recognition (ASR).
2. **Groq (Llama 3.3)**: Low-latency inference for command parsing.
3. **Reasoning Loop**: Chain-of-thought prompting for task decomposition.
4. **Action Dispatcher**: Translating JSON plans to ROS 2 Service/Action calls.

### Planned Tasks
- Week 5: Voice pipeline
- Week 6: LLM integration
- Week 7: Capstone project

## ✅ Deliverables

1. **Voice Interface**: Robot responds to spoken "Hey Robot" commands.
2. **Cognitive Parsing**: Natural language -> JSON action list.
3. **Capstone**: Complete demo of a user asking the robot to perform a task (e.g., "Go to the kitchen"), and the robot executing it gracefully.
