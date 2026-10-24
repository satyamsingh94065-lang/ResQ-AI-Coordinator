# ResQ AI Coordinator

An ACP-compatible emergency readiness planning agent for college event organizers, hosted on Agentverse and intended for direct use through ASI:One.

## Problem
Event organizers need a fast way to gather current weather conditions, locate nearby hospitals and pharmacies, and turn this information into a prioritized preparation checklist.

## Workflow
1. Receive a request and extract the city.
2. Resolve the city using Open-Meteo geocoding.
3. Retrieve current weather from Open-Meteo and nearby mapped resources from OpenStreetMap Overpass.
4. Generate a prioritized readiness plan using ASI:One, identifying missing or failed data rather than inventing it.
5. Reply through Agent Chat Protocol (ACP).

This is a planning assistant, not an emergency dispatch service. Resource listings do not confirm operating hours, capacity, or availability. In an immediate emergency, contact local emergency services directly.

## Setup
1. Create a hosted agent on [Agentverse](https://agentverse.ai/).
2. Add `agent.py` in the Build editor. Ensure the hosted environment has `uagents`, `uagents-core`, `httpx`, and `openai` available.
3. Configure `ASI1_BASE_URL` and `ASI1_API_KEY` securely in the environment if they are not already provided by the hosted platform. Never commit credentials.
4. Start the agent and check logs for registration and runtime errors.
5. Test in Agentverse Testing, then open the agent directly in ASI:One and verify a response from ResQ AI Coordinator.

## Demo prompt
> Prepare a complete emergency readiness plan for a college event in Roorkee, India. Fetch live weather, search nearby hospitals and pharmacies, assess risks and generate a prioritized safety checklist with sources.

## Integrations
- Agentverse / uAgents / ACP
- ASI:One language model API
- Open-Meteo Geocoding and Forecast APIs
- OpenStreetMap Overpass API (two endpoints for fallback)

## Submission links
- Agentverse profile: ADD_YOUR_PUBLIC_AGENTVERSE_PROFILE_URL
- ASI:One agent: https://asi1.ai/ai/blank-agent-781 (verify this still points to your agent)
- ASI:One shared demonstration chat: ADD_SHARED_CHAT_URL
- Demo video: ADD_DEMO_VIDEO_URL

## Limitations
Geocoding can be ambiguous for cities with the same name. OpenStreetMap data can be incomplete or outdated; Overpass endpoints may rate-limit or fail. Verify all listed resources before relying on them. The agent does not book or dispatch emergency services.




## Project Links

### GitHub Repository
https://github.com/satyamsingh94065-lang/ResQ-AI-Coordinator

### Agentverse Profile
https://agentverse.ai/agents/details/agent1qtc4m5jmjjmtna7mef3qaga4m5sk4z3s69zhh6jlwpvtrvqesnhys53k5dx/profile

### ASI:One Agent
https://asi1.ai/ai/blank-agent-781

### ASI:One Shared Chat
PENDING - Add actual shared conversation link

### Demo Video
PENDING - Add public demo video link

## Project Links

### GitHub Repository
https://github.com/satyamsingh94065-lang/ResQ-AI-Coordinator

### Agentverse Profile
https://agentverse.ai/agents/details/agent1qtc4m5jmjjmtna7mef3qaga4m5sk4z3s69zhh6jlwpvtrvqesnhys53k5dx/profile

### ASI:One Agent
https://asi1.ai/ai/blank-agent-781

### ASI:One Shared Chat
PENDING - Add actual shared conversation link

### Demo Video
PENDING - Add public demo video link

