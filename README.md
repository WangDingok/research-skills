# Research Skills

This folder contains modular "skills" for research, trend analysis, and creative inspiration. Each skill is designed to be loaded by an orchestrator agent or used standalone for specific research tasks.

## Skills Overview

### 1. deep-research-custom
**Purpose:**  
Systematic, multi-dimensional web research for any question requiring in-depth exploration and current trend discovery.  
**How to use:**  
- Always load this skill before starting any content creation or research task.
- Works best when combined with `tavily-web-search`, `twitter-trends`, and `google-ai-search` skills.
- Use for: trend analysis, concept explanation, comparison, or any task needing up-to-date, multi-source information.

### 2. design-inspirator
**Purpose:**  
Finds and collects design inspiration, product ideas, color palettes, and real-world examples from the web and e-commerce platforms after a niche/trend is identified.  
**How to use:**  
- Run in parallel with `tavily-web-search`, `google-ai-search`, and `etsy-market-research` for comprehensive inspiration.
- Use for: gathering visual and conceptual references for product design.

### 3. etsy-market-research
**Purpose:**  
Analyzes the T-shirt market on Etsy: market overview, niche analysis, and top-selling product lists.  
**How to use:**  
- Run CLI tool with keywords and parameters for market or niche analysis.
- Use for: evaluating commercial opportunities, competition, price distribution, and identifying top products for a given keyword/niche.

### 4. google-ai-search
**Purpose:**  
Uses Google AI Mode (SGE) to get comprehensive AI-generated summaries on a topic.  
**How to use:**  
- Run CLI tool with a query and optional geo parameter.
- Use for: quick, structured summaries, niche ideas, key points, and product suggestions from Google AI.

### 5. google-trends
**Purpose:**  
Analyzes search trends over time on Google Trends.  
**How to use:**  
- Run CLI tool with keywords, geo, and timeframe.
- Use for: evaluating trend stability, direction, volatility, and peak interest for up to 5 keywords per batch.

### 6. report-writer
**Purpose:**  
Synthesizes all research results from sub-agents into a final, clear, and professional report for the user.  
**How to use:**  
- Use after all research steps are complete.
- Formats the report, cites sources, and presents findings clearly.

### 7. surprise-me
**Purpose:**  
Creates a delightful, unexpected "wow" experience by creatively combining other enabled skills.  
**How to use:**  
- Triggers when the user asks for a surprise, inspiration, or something interesting.
- Dynamically discovers and mashes up 1-3 skills for a unique, polished output.

### 8. tavily-web-search
**Purpose:**  
Performs web search and reads web page content using the Tavily API.  
**How to use:**  
- Run CLI tool with a query and optional fetch_content flag.
- Use for: finding information, news, emerging trends, community discussions, and blog posts.

---

Each skill folder contains a `SKILL.md` with detailed usage and agent guidelines.  