---
name: emily-advisor-strategy
description: Pair a strategic advisor with a smaller execution model when users want to improve quality at controlled cost.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, TaskCreate, TaskUpdate, TaskList
metadata:
  author: emily club
  version: 1.2.0
  updated: 2026-04-10
  source: https://claude.com/blog/the-advisor-strategy
  preferred_model: opus
  tags: [skill, ai, claude, agentic, advisor-pattern, cost-optimization, multi-model]
---

# Advisor Strategy — Give Agents an Intelligence Boost

> Pair **Opus as the advisor** with any **smaller model** (gemma, sonnet, haiku, etc.) as the executor to get near-Opus intelligence at executor-level costs.

This skill runs in a Claude environment where **Opus is the advisor** and **any smaller model** can be the executor.

---

## Core Concept

The **advisor strategy** inverts the traditional sub-agent pattern:

| Traditional Pattern | Advisor Strategy |
|---------------------|-----------------|
| Large model = orchestrator | Small model = executor |
| Large model drives work | Small model drives work |
| Small models = workers | Opus = on-demand advisor |

The executor (gemma, sonnet, haiku, or any smaller model) runs tasks end-to-end, calling tools and iterating toward solutions. When it faces a decision it cannot reasonably solve, it consults Opus. Opus accesses shared context and returns a plan, correction, or stop signal, then the executor resumes.

### Model Pairing Examples

| Executor | Advisor | Best For |
|----------|---------|----------|
| gemma | Opus | Maximum cost savings with intelligence boost |
| haiku | Opus | Budget-friendly research and lookup tasks |
| sonnet | Opus | Complex architectural decisions |
| Any smaller model | Opus | Custom trade-offs with top-tier guidance |

---

## Performance Data

> The following benchmarks from Anthropic demonstrate the advisor strategy's effectiveness with Opus as advisor. Results vary based on executor model and task type.

### Sonnet + Opus Advisor
- **+2.7 percentage points** on SWE-bench Multilingual over Sonnet alone
- **11.9% cost reduction** per agentic task

### Haiku + Opus Advisor
- **41.2%** on BrowseComp (more than **double** Haiku solo's 19.7%)
- Still 29% behind Sonnet solo in score
- Costs **85% less** per task than Sonnet solo

### General Guidelines with Opus
- **Any smaller + Opus** typically outperforms smaller model alone
- **Cost savings** depend on how often Opus is invoked
- **Quality gains** are highest on complex reasoning and architectural decisions
- **gemma + Opus** should show similar improvement patterns (not yet benchmarked)

---

## The `advisor_20260301` Tool

A server-side tool that the executor model (gemma, sonnet, haiku, etc.) knows to invoke automatically when it needs guidance from Opus.

### Key Features
- **Pricing:** Advisor tokens billed at Opus rates; executor tokens at executor rates
- **Cost controls:** `max_uses` caps Opus advisor calls per request
- **Token efficiency:** Opus typically generates 400–700 text tokens per call
- **Integration:** Works alongside existing tools (web search, code execution, etc.)

### Usage Example

```python
response = client.messages.create(
    model="gemma-27b",  # or haiku, sonnet - any smaller executor model
    tools=[{
        "type": "advisor_20260301",
        "name": "advisor",
        "model": "claude-opus-4-6",  # Opus as advisor
        "max_uses": 3,  # cost control cap per request
    }],
    messages=[...]
)
```

### Executor Recommendations with Opus

| Executor | Advisor | Benefit |
|----------|---------|---------|
| gemma | Opus | Maximum cost savings with intelligence boost |
| haiku | Opus | Budget-friendly research and lookup tasks |
| sonnet | Opus | Best quality/cost balance for complex tasks |

### When to Use

| Use Case | Recommendation |
|----------|----------------|
| Simple tasks | Executor solo (no Opus advisor needed) |
| Complex architectural decisions | Add Opus advisor |
| Research/lookup heavy tasks | Add Opus advisor |
| Cost-sensitive projects | Use gemma/haiku + Opus |

---

## Customer Quote

> "It makes better architectural decisions on complex tasks while adding no overhead on simple ones. The plans and trajectories are night and day different."
>
> — Eric Simmons, CEO and Founder, Bolt

---

## Best Practices

1. **Start simple** — Use executor solo (gemma, sonnet, haiku) for straightforward tasks
2. **Add Opus for complexity** — When tasks involve architectural decisions or multi-step reasoning
3. **Set reasonable `max_uses`** — Cap Opus advisor calls to control costs (3-5 is a good starting point)
4. **Monitor token usage** — Track Opus vs executor token ratios
5. **No overhead on simple tasks** — Opus is only called when needed
6. **Choose executor based on budget** — gemma/haiku for maximum savings, Sonnet for better balance
7. **Always use Opus as advisor** — Opus provides top-tier reasoning and guidance

---

## Summary

The advisor strategy lets you:
- Get near-Opus intelligence with any smaller executor
- Pay at executor-level costs
- Improve task quality without adding overhead on simple tasks
- Make better architectural decisions on complex tasks
- Use gemma, sonnet, or haiku as executor with Opus as advisor
