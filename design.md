# AI Creative Agent — System Design

## Overview

AI Creative Agent is a multi-model AI pipeline designed for:

* Product Ads
* Product Photoshoots
* Instagram Posts
* Motion Ads
* Posters
* Product Mockups

The system integrates multiple AI models and automation tools.

---

# System Architecture

User Input
↓
Claude Skill Agent
↓
Model Selector
↓
Workflow Engine
↓
Execution Engines
↓
Output

---

# Core Components

## 1. Claude Skill Agent

Responsible for:

* Parsing user prompt
* Understanding intent
* Routing to workflow

Files:

agents/
claudeAgent.ts
promptParser.ts

---

# 2. Model Selector

Selects best model for:

* Image generation
* Face swap
* Enhancement
* Motion

Files:

models/
modelSelector.ts
modelRegistry.ts

---

# 3. Workflow Engine

Controls:

* Multi-step generation
* Automation flow

Files:

workflow/
workflow.ts
pipeline.ts

---

# 4. Image Generation Engine

Responsible for:

* Product images
* Model photoshoots

Models:

* SDXL
* Flux
* Stable Diffusion

Files:

models/
imageGenerator.ts

---

# 5. Face Swap Engine

Features:

* Replace face
* Match lighting

Models:

* InsightFace
* FaceFusion

Files:

models/
faceSwap.ts

---

# 6. Editing Engine

Features:

* Background swap
* Object replacement

Files:

models/
editingEngine.ts

---

# 7. Enhancement Engine

Features:

* Upscale
* Improve detail

Models:

* RealESRGAN

Files:

models/
enhancement.ts

---

# 8. Motion Engine

Features:

* Animate images
* Camera motion

Files:

models/
motionEngine.ts

---

# 9. Playwright Automation

Automates:

* External AI tools
* Uploads
* Downloads

Files:

automation/
playwrightRunner.ts

---

# 10. Agent Memory

Stores:

* User preferences
* Brand style
* Previous generations

Files:

memory/
memoryStore.ts

---

# 11. GPU Manager

Handles:

* Local GPU
* CPU fallback

Files:

gpu/
gpuManager.ts

---

# 12. Batch Generation

Generates:

* Multiple creatives

Files:

batch/
batchGenerator.ts

---

# 13. API Layer

Endpoints:

POST /generate-ad

Files:

api/
routes.ts
controller.ts

---

# 14. UI Dashboard

Frontend:

* Upload images
* Generate creatives

Tech:

* Next.js
* Tailwind

Files:

frontend/
dashboard/

---

# Data Flow

User Input
↓
Prompt Parser
↓
Model Selector
↓
Workflow Engine
↓
Execution Engines
↓
Output

---

# Multi-Model Switching

Agent selects:

* Best image model
* Best face swap model
* Best motion model

---

# GPU Support

Supports:

* Local GPU
* Cloud GPU
* CPU fallback

---

# Error Handling

Fallback logic:

Model failure
↓
Switch model
↓
Retry generation

---

# Scalability

Supports:

* Multi-user
* Batch generation
* Cloud deployment

---

# Deployment

Supports:

* Local
* Cloud
* Hybrid

---

# Performance Optimization

* Async pipeline
* Parallel execution
* Model caching

---

# Security

* API keys stored in env
* Secure uploads

---

# End of Design

