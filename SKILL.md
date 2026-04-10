# AI Creative Agent Skill

## Overview

AI Creative Agent is a multi-tool AI system designed to generate:

* Product Ads
* Product Photoshoots
* Instagram Posts
* Posters
* Motion Ads
* Product Mockups

The agent supports:

* Face swap
* Background swap
* Photorealistic generation
* Editing
* Enhancement
* Motion & transitions

---

# Capabilities

## Image Generation

Generate:

* Product photography
* Lifestyle ads
* Model photoshoots

Models Supported:

* SDXL
* Flux
* Stable Diffusion
* Local models

---

# Face Swap

Features:

* Upload reference face
* Replace model face
* Preserve lighting
* Maintain expressions

Supported Models:

* InsightFace
* FaceFusion

---

# Editing Engine

Capabilities:

* Background swap
* Object replacement
* Image expansion
* Lighting adjustment

---

# Enhancement Engine

Features:

* Upscale images
* Improve detail
* Texture refinement

Models:

* RealESRGAN
* Upscaler models

---

# Motion Engine

Capabilities:

* Animate product
* Camera movement
* Transitions

Models:

* AnimateDiff
* Motion models

---

# Claude Skill Interface

Example Prompt:

Create product ad with female fitness model, swap face, create Instagram version

Workflow:

1. Generate product image
2. Add model
3. Swap face
4. Replace background
5. Enhance image
6. Generate motion

---

# Input Parameters

User Inputs:

* productDescription
* referenceImage
* faceImage
* style
* platform

Example:

{
product: "Protein Powder",
style: "Fitness Instagram Ad",
platform: "Instagram"
}

---

# Output

Returns:

* Generated image
* Enhanced image
* Motion video

Example:

{
image: "...",
enhancedImage: "...",
motionVideo: "..."
}

---

# Automation

Playwright automation:

* Generate images
* Upload references
* Download outputs

---

# Batch Generation

Generate multiple creatives:

Input:

* Multiple products
* Multiple styles

Output:

* Batch creatives

---

# Multi-Model Switching

Agent automatically selects:

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

# Agent Memory

Stores:

* Brand styles
* User preferences
* Previous generations

---

# API Endpoints

POST /generate-ad

Input:

{
product
faceImage
style
}

Output:

{
image
enhancedImage
motionVideo
}

---

# Usage Examples

Example 1

Create protein supplement ad with fitness model

Example 2

Create skincare product poster

Example 3

Create Instagram motion ad

---

# Deployment

Supports:

* Local deployment
* Cloud deployment
* Hybrid deployment

---

# Requirements

Node.js
TypeScript
Playwright
GPU optional

---

# End of Skill
