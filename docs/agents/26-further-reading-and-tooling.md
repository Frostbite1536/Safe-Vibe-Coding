---
layout: default
title: 26. Further Reading & Tooling
nav_order: 26
parent: Agents Guide
grand_parent: Guides
description: "Curated external resources for building safe, reliable agents — model-provider documentation, papers, frameworks, eval harnesses, and community write-ups, organized by topic."
permalink: /agents/further-reading-and-tooling
---

# 26. Further Reading & Tooling

This guide has been deliberately self-contained. Every idea, pattern, and checklist was meant to be usable without chasing external links. But the field around agents moves fast, and much of what a practitioner eventually needs — framework APIs, model provider guidance, research on specific failure modes, community accounts of real incidents — lives outside of any single document.

This chapter is a curated pointer list to the external resources the guide's authors have found most useful. It is intentionally short. A longer list would be a directory, not a reading list; teams that need exhaustive coverage of the agent ecosystem are served better by search engines than by this chapter. What you will find below is the set of resources worth opening when you first encounter a problem, before you start googling.

Two warnings before the list.

First, **external resources age faster than the guide does.** Frameworks change APIs, papers get superseded, blog posts get revised, and URLs move. Every entry below is described by *title, author, and topic* so that you can find it again even if a link breaks. When a URL is given, it is given because the authors are confident the resource is stable; when none is given, search for the title.

Second, **no framework, paper, or dashboard replaces the work in Parts II–V of this guide.** If a tool promises to handle scope, safety, and observability for you automatically, be skeptical. The tools below are useful precisely because they accelerate work you would otherwise do by hand — they do not remove the need to understand what you are doing.

---

## Primary-Source Documentation

The model providers themselves publish the single best first-stop documentation for building agents on their platforms. If you are using a specific provider, read their docs before reading any third-party material.

- **Anthropic — Developer Documentation.** The Claude API reference, tool-use guide, prompt-engineering notes, and agent-building guidance. Start at [docs.anthropic.com](https://docs.anthropic.com). Anthropic's engineering blog at [anthropic.com/engineering](https://www.anthropic.com/engineering) has published several long-form posts on agent design and long-running agent harnesses that are worth reading end-to-end.
- **Anthropic — Courses and Cookbooks.** Hands-on examples for API usage, tool design, and prompt engineering, maintained at [github.com/anthropics/courses](https://github.com/anthropics/courses) and [github.com/anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook).
- **OpenAI — API Reference and Cookbook.** The OpenAI API documentation and the companion [github.com/openai/openai-cookbook](https://github.com/openai/openai-cookbook) are essential reading for teams on that platform and useful context even for teams that are not.
- **Google — Gemini API Documentation.** For teams using Gemini, the Google AI for Developers documentation is the primary source.

In every case, the provider documentation is closer to the truth than any third-party summary. Third-party posts move slower than API changes; the official docs are the first to reflect new capabilities and deprecations.

---

## Foundational Reading on Agents and LLMs

A short reading list for practitioners who want to understand the terrain the guide sits inside.

- **"ReAct: Synergizing Reasoning and Acting in Language Models"** (Yao et al.). The paper that gave the agent community a working vocabulary for the reason-act-observe loop. Worth reading once, even if you have already internalized the pattern.
- **"Toolformer: Language Models Can Teach Themselves to Use Tools"** (Schick et al.). Useful historical context for why "tools" are the interface they are today.
- **"Reflexion: Language Agents with Verbal Reinforcement Learning"** (Shinn et al.). A good entry point for thinking about in-loop self-correction in agents.
- **"Constitutional AI: Harmlessness from AI Feedback"** (Anthropic). Not strictly an agent paper, but it is the clearest published exposition of how to specify and enforce behavior at the policy level, which is exactly the problem every agent team eventually runs into.
- **Anthropic's published research on agent evaluations and long-horizon tasks.** Anthropic periodically publishes research notes on how frontier models behave on multi-step agent tasks, including failure modes. These are worth subscribing to through the Anthropic research page.

These are starting points, not the full literature. The papers above were selected because each one establishes a concept this guide takes for granted; the citation trails forward from each will take you deeper than any curated list could.

---

## Safety, Injection, and Adversarial Testing

The most active external research in the agent space is on safety and adversarial robustness. If you are responsible for an agent that touches real users or real systems, you should keep up with it.

- **OWASP Top 10 for LLM Applications.** The closest thing the field has to an industry-consensus list of LLM application risks, maintained by the OWASP Foundation. Covers prompt injection, insecure output handling, model denial of service, supply chain risks, and more. Find it on the OWASP website under "Top 10 for LLM Applications" (the URL has moved more than once; search for the title).
- **NIST AI Risk Management Framework (AI RMF).** The U.S. National Institute of Standards and Technology's framework for managing AI risk. Useful as a vocabulary for risk reporting to stakeholders outside engineering, even for teams that are not in regulated industries.
- **Simon Willison's blog.** Willison has been writing about prompt injection and LLM security since before most practitioners knew the problem existed, and his posts remain among the most practical on the topic. Search for "Simon Willison prompt injection" to find the running series.
- **Academic literature on prompt injection and jailbreaking.** Papers on direct and indirect injection, scope escape, and jailbreak robustness are now appearing frequently. Track new work through arXiv's cs.CR and cs.CL listings; search for "prompt injection" and "jailbreak" periodically.

When reading adversarial research, pay attention to the threat model each paper assumes. A technique that works against a chatbot with no external content may not be relevant to an agent that reads user-submitted documents, and vice versa.

---

## Evaluation and Testing

Building a good eval set is a distinct discipline, and the ecosystem around it has matured faster than most other parts of the agent space.

- **Inspect AI** (UK AI Security Institute, AISI — formerly the UK AI Safety Institute). An open-source evaluation framework designed for LLMs and LLM agents, maintained at [github.com/UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai). Probably the most serious open-source eval harness currently available, with good support for scorers, multi-turn evaluations, and agent tasks.
- **OpenAI Evals** ([github.com/openai/evals](https://github.com/openai/evals)). The original open-source eval framework from OpenAI. Less actively developed than Inspect but still a useful reference for how to structure eval cases.
- **Promptfoo** ([promptfoo.dev](https://www.promptfoo.dev/)). A CLI and framework oriented toward prompt and agent evaluation with good support for regression testing and side-by-side comparisons across models.
- **LangSmith** (the evaluation product associated with LangChain). A hosted service for tracing, eval, and regression testing of LLM and agent applications. Useful if your team is already building on LangChain; worth understanding conceptually either way.
- **"Anthropic Economic Index" and Anthropic's published eval work.** Anthropic periodically publishes evaluations on how Claude models handle agent tasks and multi-step workflows. These are primary-source data on real-world agent performance and worth tracking.

A rule that applies to every eval framework: the framework is the cheap part; the golden dataset is the expensive and valuable part. Do not confuse installing an eval tool with having an eval.

---

## Agent Frameworks

A practical reality is that most teams do not build agent loops from scratch. Several frameworks now offer varying degrees of scaffolding — tool-calling, state management, multi-agent coordination. A partial list, with notes on what each emphasizes:

- **Anthropic Agent SDK.** Anthropic's SDK for building agents on the Claude API, with tool-use primitives and support for long-running agent patterns. Start at the Anthropic developer documentation.
- **LangChain and LangGraph.** The most widely-used open-source framework ecosystem for LLM applications. LangChain is the higher-level framework; LangGraph is the lower-level graph-based orchestration library under it. Both are documented at [langchain.com](https://www.langchain.com/). LangGraph in particular is worth understanding because its graph model maps cleanly onto the orchestrator/worker patterns from [Chapter 20](./20-multi-agent-coordination.md).
- **LlamaIndex** ([llamaindex.ai](https://www.llamaindex.ai/)). Originally a retrieval-focused framework, now with agent and workflow support. Worth knowing if your agent is heavy on retrieval-augmented generation.
- **AutoGen** (Microsoft). A multi-agent framework with an emphasis on agent-to-agent conversation patterns. Useful for exploring multi-agent designs, though the framework itself encourages patterns that the reliability math in [Chapter 20](./20-multi-agent-coordination.md) would suggest treating with caution.
- **CrewAI** ([crewai.com](https://www.crewai.com/)). A higher-level framework oriented around "crews" of role-specialized agents. Same caution applies.
- **Pydantic AI** ([ai.pydantic.dev](https://ai.pydantic.dev/)). A relatively new framework from the Pydantic maintainers, focused on type-safe tool definitions and structured outputs. Worth looking at if the typed-tool-interface arguments in [Chapter 5](./05-tool-interface-design.md) resonated with your team.

Choosing a framework is a significant decision and often not reversible cheaply. Four questions help:

1. **Does the framework make the four pillars (Scope, Tool Contracts, Escalation, Observability) easier or harder to implement well?** A framework that hides observability is a framework that makes [Observability Theater](./22-anti-patterns.md#observability-theater) more likely.
2. **Does the framework encourage a structure that matches your problem?** Orchestrator/worker, single-agent with many tools, workflow-with-embedded-agent — each has a natural framework fit.
3. **Is the framework's error surface inspectable?** When something breaks, can you see why without trusting the framework's own explanation?
4. **What is the upgrade story?** Frameworks churn; the question is not whether you will need to adapt, but how painful each adaptation will be.

The honest answer for many teams is that *no framework is simpler than the alternative of writing a thin orchestration layer yourself*. The framework's value comes from the patterns it encodes, not the code it saves.

---

## Observability and Tracing

- **OpenTelemetry.** The open standard for distributed tracing, and the right long-term target for agent observability because it integrates with whatever your existing systems already use. Search for "OpenTelemetry GenAI semantic conventions" for the emerging LLM-specific conventions.
- **Langfuse** ([langfuse.com](https://langfuse.com/)). An open-source LLM observability platform with strong agent-trace support. Useful if you do not already have a tracing pipeline.
- **LangSmith** (again, from LangChain). Closed-source but mature. Sensible choice if your team is already on LangChain.
- **Arize Phoenix** ([phoenix.arize.com](https://phoenix.arize.com/)). Open-source observability and eval tooling from Arize. Good support for trace inspection and LLM-as-judge workflows.
- **Your existing observability stack.** Datadog, Honeycomb, Grafana, and the rest can all be adapted to capture LLM and tool-call traces. The integration is work, but the payoff is that agent traces live in the same system as the rest of your infrastructure, which is what you ultimately want.

The thing to optimize for is *queryability* at incident time. A trace system that stores everything but cannot answer "what did the agent decide at step 7" in under a minute is not an asset during an incident.

---

## Incident Write-Ups and Community Accounts

Some of the most educational material in the agent space is not papers or docs — it is accounts of real incidents, often posted by the teams that experienced them. These are harder to index because they surface unpredictably, but two patterns help:

- **Track the personal blogs and Twitter/X feeds of practitioners who write honestly about failures.** Simon Willison, Hamel Husain, Chip Huyen, and others in this loosely-defined community regularly publish post-mortems and critique of agent designs. Follow a few; the signal is high.
- **Read the "what went wrong" posts more than the "what we built" posts.** Marketing posts about new agent products rarely teach you anything that was not also in the product's landing page. Incident accounts — even informal ones on forums like Hacker News, r/LocalLLaMA, or r/ClaudeAI — often describe failure modes you can learn from without paying for.
- **Watch conference talks.** Conferences like AI Engineer Summit publish their talks on YouTube. Talks from practitioners running agents in production are often the best summary of lessons the speaker paid for in real incidents.

The bar for useful reading in this category is honesty, not production value. A paragraph on a forum from an engineer who just watched their agent delete a customer database teaches more than a forty-minute keynote on "the future of agentic AI."

---

## Related Reading Inside This Repository

This guide is one of several in the broader Safe Vibe Coding project. Several of its other chapters are useful companions to the agents guide:

- **Context Management** — the memory and state chapter ([Chapter 8](./08-memory-and-state.md)) in this guide is the agent-specific view; the project's [Context Management guide](../CONTEXT_MANAGEMENT.md) covers the underlying principles for LLM applications more broadly.
- **Prompt Engineering and Emotional Prompt Engineering** — the [Emotional Prompt Engineering guide](../EMOTIONAL_PROMPT_ENGINEERING.md) and related prompt-craft material in this repository are good background for the system prompts covered in [Chapter 6](./06-system-prompts-as-contracts.md).
- **Plan-Driven Development** — the [Plan-Driven Development guide](../PLAN_DRIVEN_DEVELOPMENT.md) in this repository covers the discipline of writing plans before acting, which is the pre-agent-loop version of the scope brief discipline from [Chapter 4](./04-defining-purpose-and-scope.md).
- **AI Audit Failures** — the [AI Audit Failures guide](../AI_AUDIT_FAILURES.md) in this repository catalogs failure modes in AI-assisted workflows more broadly; many of its cases rhyme with the anti-patterns in [Chapter 22](./22-anti-patterns.md).
- **The repository-level anti-patterns document** — [`ANTI_PATTERNS.md`](../ANTI_PATTERNS.md) in the top-level docs directory is the non-agent version of this guide's anti-pattern chapter and a useful cross-reference.

The agents guide is meant to stand alone, but readers who want to ground agent work in the broader practice of working safely with AI-assisted development will find most of what they need in the adjacent documents above.

---

## How to Keep Up Without Drowning

The volume of agent-adjacent content published every week is more than any practitioner can reasonably read. A defensible strategy:

1. **Subscribe to three sources, not thirty.** A provider's engineering blog, one serious practitioner's feed, and one research aggregator is enough. Adding more produces noise, not signal.
2. **Read the long-form post, not the tweet thread.** A three-paragraph thread and a three-thousand-word post that says the same thing do not contain the same information — the long form almost always does. Save the tweets for discovery; read the posts for substance.
3. **Follow incidents across providers, not just your own.** Failure modes often translate across platforms. An incident on a different framework or a different model family is still an incident your team could have had.
4. **Prefer primary sources to summaries.** If a post references a paper, read the paper. If a post references provider documentation, read the documentation. Summaries drift faster than the things they summarize.
5. **Re-read the guide.** This sounds self-serving, but it is the most useful single recommendation. Most of the value of a long-form guide is lost on the first read; the second pass — done months later, with a specific problem in mind — is where the principles become usable. Chapters in Parts II and III in particular reward a re-read once the agent has been running in production for a while.

---

## Anti-Pattern: Reading Instead of Building

**Symptom**: The team has read every recent paper, subscribed to every blog, and can discuss the relative merits of five different frameworks. Their agent is still in the design phase. Every conversation about shipping produces a new reading recommendation that gets added to the backlog. The reading substitutes for the work.

**Why it hurts**: Reading is necessary, but it is not the thing that produces a working agent. Most agent failures are caused by not doing the boring parts — scope briefs, observability, test suites, kill switches — and most of that boring work is not blocked by a knowledge gap. Teams that are continuously reading without building are usually doing so because reading feels productive and building feels risky. The cost is obvious in retrospect and invisible at the time.

**Fix**: Set a reading budget — one paper or long-form post a week is plenty for most teams — and spend the rest of the time building, testing, and documenting. When a specific problem arises, read *targeted* material on that specific problem, not the full backlog. Trust that the fundamentals of this guide and the resources in this chapter are enough to start; the marginal paper is almost never the thing standing between your team and a working agent. Ship first, refine with the reading later.

---

## Checklist

- [ ] The team subscribes to the provider engineering blog for whichever model provider it is using.
- [ ] At least one person on the team is tracking the OWASP Top 10 for LLM Applications and the periodic updates to it.
- [ ] The eval framework the team has adopted is actively maintained and has been used to run at least one full eval in the last month.
- [ ] The observability stack can answer "what did the agent decide at step N of run X" in under a minute.
- [ ] The framework (if any) in use does not hide observability, escalation, or authorization behind abstractions the team does not understand.
- [ ] The team has read at least one incident write-up from outside their own organization in the last quarter.
- [ ] A reading budget exists and is not being used as a backlog for work that should be getting done.
- [ ] New external resources worth adopting are written up in the team's internal documentation, not just bookmarked.

---

## What to Read Next

- [Chapter 1 — What Is an Agent?](./01-what-is-an-agent.md): if you have reached this chapter as the end of a first read, the first chapter is now worth revisiting with the full context of the guide in mind.
- [Chapter 25 — Quick-Reference Checklists](./25-quick-reference-checklists.md): the consolidated lists that turn everything in this guide into day-to-day practice.
- [Chapter 22 — Anti-Patterns & Failure Modes](./22-anti-patterns.md): the failure modes you now have the vocabulary to recognize and the resources to avoid.
- And then — close the guide, open your editor, and write the scope brief.
