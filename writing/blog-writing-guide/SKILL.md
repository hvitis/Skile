---
name: blog-writing-guide
description: Write, review, and improve blog posts for the Sentry engineering blog following Sentry's specific writing standards, voice, and quality bar. Use this skill whenever someone asks to write a blog post, draft a technical article, review blog content, improve a draft, write a product announcement, create an engineering deep-dive, or produce any written content destined for the Sentry blog or developer audience. Also trigger when the user mentions "blog post," "blog draft," "write-up," "announcement post," "engineering post," "deep dive," "postmortem," or asks for help with technical writing for Sentry. Even if the user just says "help me write about [feature/topic]" — if it sounds like it could become a Sentry blog post, use this skill.
license: MIT
---

# Sentry Blog Writing Skill

This skill enforces Sentry's blog writing standards across every post — whether you're helping an engineer write their first blog post or a marketer draft a product announcement.

**The bar:** Every Sentry blog post should be something a senior engineer would share in their team's Slack, or reference in a technical decision.

What follows are the core principles to internalize and apply to every piece of content.

## Before Drafting: Diagram Preference

Ask the user whether they want a graph or diagram in the post and, if so, what it should contain or explain, such as components, data flow, decision paths, or a comparison. Reuse preferences already provided; ask only for missing details. Continue work on the prose while waiting, but wait for the user's answer before adding a diagram. If they decline, omit it even for system descriptions.

## The Sentry Voice

**We sound like:** A senior developer at a conference afterparty explaining something they're genuinely excited about — smart, specific, a little irreverent, deeply knowledgeable.

**We don't sound like:** A corporate blog, a press release, a sales deck, or an AI-generated summary.

Be technically precise, opinionated, and direct. Humor is welcome but should serve the content, not replace it. Sarcasm works. One good joke per post is plenty.

Use "we" (Sentry) and "you" (the reader). This is a conversation, not a paper.

## Banned Language

Never use these. They are automatic red flags:

- "We're excited/thrilled to announce" — just announce it
- "Best-in-class" / "industry-leading" / "cutting-edge" — show, don't tell
- "Seamless" / "seamlessly" — nothing is seamless
- "Empower" / "leverage" / "unlock" — say what you actually mean
- "Robust" — describe what makes it robust instead
- "At [Company], we believe..." — just state the belief
- "Streamline" — everyone is streamlining, stop
- Filler transitions: "That being said," "It's worth noting that," "At the end of the day," "Without further ado," "As you might know"
- "In this blog post, we will explore..." — be direct, just start

## The Opening (First 2-3 Sentences)

The opening must do one of two things: **state the problem** or **state the conclusion**. Never start with background, company history, or hype.

**Good:** "Two weeks before launch, we killed our entire metrics product. Here's why pre-aggregating time-series metrics breaks down for debugging, and how we rebuilt the system from scratch."

**Bad:** "At Sentry, we're always looking for ways to improve the developer experience. Today, we're thrilled to share some exciting updates to our metrics product that we think you'll love."

## Structure: Follow the Reader's Questions

Structure every post around what the reader is actually wondering, not your internal narrative:

1. **What problem does this solve?** (1-2 paragraphs max)
2. **How does it actually work?** Not buttons-you-click, but underlying technology. (Bulk of the post — be specific)
3. **What were the trade-offs or alternatives?** (This separates good from great)
4. **How do I use/try/implement this?** (Concrete next steps)

For engineering deep-dives, also address:
5. **What did we try that didn't work?** (Builds trust)
6. **What are the known limitations?** (Shows intellectual honesty)

## Formatting for Skimmability

People scroll. Shorter paragraphs are almost always better for keeping people reading.

**Break paragraphs at contrast points.** When a sentence introduces a "but," "however," or shifts perspective, start a new paragraph. Don't bury the turn inside a block of text.

**Bad:**
> Traditional monitoring tracks requests and latency. That works for stateless HTTP services. AI agents are different. A single run might involve multiple LLM calls, tool executions, and handoffs.

**Good:**
> Traditional monitoring tracks requests and latency. That works for stateless HTTP services.
>
> AI agents are different. A single run might involve multiple LLM calls, tool executions, and handoffs.

The line break before the contrasting point creates visual emphasis. This is standard in online writing even though it breaks traditional paragraph rules.

**One idea per paragraph.** If a paragraph covers two distinct points, split it. Three-sentence paragraphs are fine. One-sentence paragraphs are fine for emphasis.

**No em dashes.** Use commas, periods, or line breaks instead. Em dashes are fine in print but create visual clutter in blog formatting.

## SEO for Developer Content

When targeting a competitive search query:

**Lead generic, close specific.** The first 50-60% of the post should be tool-agnostic educational content (definitions, concepts, metrics, best practices). Introduce your product as an implementation example in the second half. Google ranks guides higher than product pages for informational queries.

**Put keywords in H2s.** Generic headings are invisible to search. "Key metrics for AI agent monitoring" beats "What to measure." (See **Section Headings** below for good/bad examples.)

**Include a definitional section.** For any head term ("agent observability", "error monitoring"), top-ranking pages almost always have a "What is X?" section. Include one even if it feels basic.

**Answer likely reader questions in the closing section.** Use relevant theoretical questions and long-tail search queries as planning prompts, then weave their answers into a coherent wrap-up of the post. Follow **The Closing** below rather than appending an FAQ or a series of question-and-answer headings. Include answers only when they help resolve the post's argument; avoid keyword padding.

## AI Writing Patterns to Avoid

LLM-generated prose has tells. Flag and rewrite these:

**Staccato dramatic fragments.**
- Bad: "No errors. No warnings. Everything green."
- Good: "There were no errors, no warnings, everything looked fine."

**Bumper-sticker aphorisms.**
- Bad: "You can't fix what you can't see."
- Good: "Without visibility into the full request lifecycle, you're guessing."

**Three-beat reveals.**
- Bad: "Not a config issue. Not a code bug. The deploy was stale."
- Good: "It wasn't a config issue or a code bug. The deploy was stale."

**Smug simplicity.**
- Bad: [code block] "That's it. That's all you need."
- Good: [code block] then explain what the code does, or just move on.

**Parallel structure ad copy.**
- Bad: "Metrics tell you what's broken. Traces tell you why."
- Good: "Metrics show what's broken, but traces are where you'll actually figure out why."

**Personality only in the bookends.** AI drafts open with a personal anecdote, go impersonal for 80% of the post, then close with a CTA. The author's voice should persist throughout.
- Bad: Personal intro → clinical middle → "Try Sentry for free."
- Good: First-person asides woven through the post: "this is the part that tripped me up" / "I would have blamed the wrong service."

## Section Headings Must Convey Information

**Weak:** "Background," "Architecture," "Results," "Conclusion"

**Strong:** "Why time-series pre-aggregation destroys debugging context," "The scatter-gather approach to distributed GROUP BY," "Where this breaks down: the cardinality wall"

## Technical Quality Standards

**Numbers over adjectives.** If you make a performance claim, include the number.
- Bad: "This significantly reduced our error processing time."
- Good: "This reduced our p99 error processing time from 340ms to 45ms — a 7.5× improvement."

**Code must work.** If a post includes code, test it. Include imports, configuration, and context. Comments should explain *why*, not *what*.

**Diagrams for systems.** A system with more than two interacting components may benefit from a diagram. Follow the user's diagram preference and agreed scope from **Before Drafting: Diagram Preference**. Label components with real service names, not generic boxes.

**Horizontal Mermaid graphs.** When including a Mermaid flowchart, use `flowchart LR` (or `graph LR`) to lay it out from left to right and save vertical post space. Keep subgraphs horizontal too; avoid `TD` or `TB` layouts. Keep labels concise and show only the agreed content so the graph remains readable within the post width.

**Honesty over hype.** Never overstate what a feature does. Acknowledge limitations. If something is in beta, say so. If a competitor does something well, it's okay to note that. Do not claim AI features are more capable than they are — "Seer suggests a likely root cause" ≠ "Seer finds the root cause."

## Title Guidelines

The title is the highest-leverage sentence in the post. It must stop a developer scrolling through their RSS feed or Twitter.

Draft a few catchy title candidates around the post's strongest supported finding, useful payoff, or surprising trade-off, then choose the one that best matches the finished content. Create curiosity through specificity and the real story.

Check both the literal claim and the likely implication against the post. A title must preserve the direction of the findings, their scope, and any qualification that changes their meaning. Do not imply the opposite of what happened, invent a result, turn a limited observation into a universal claim, or promise an answer the post does not deliver. Use numbers only when supported by the post's evidence. Revise the title if the draft's conclusion changes.

**Strong titles** make a specific claim, tell a story, or promise a specific payoff:
- "The metrics product we built worked. But we killed it and started over anyway"
- "How we reduced release delays by 5% by fixing Salt"
- "How we found 47% dead code in our JavaScript bundle"

For a post where caching improved throughput but left latency unchanged, "Caching improved throughput, but latency stayed flat" is accurate and intriguing. "How caching fixed our latency problem" contradicts the findings.

**Weak titles** are vague announcements:
- "Introducing our new metrics product"
- "Performance improvements in Sentry"
- "AI-powered debugging with Seer"

## The Closing

Close with a section whose heading expresses the post's takeaway. Bring the main argument to a resolution, connect it to the opening problem, and explain what the reader can now conclude or do. Naturally weave in answers to the remaining theoretical questions a reader might have, such as when the approach applies, why the trade-off is acceptable, or where its limits matter. Use connected prose rather than an FAQ, a list of questions, or separate Q&A headings.

Synthesize the implications instead of repeating a section-by-section recap. End with something useful where appropriate: a link to docs, source code, a way to try it, or a call to give feedback. Avoid generic hype ("We can't wait to see what you build!") and product-page CTAs ("Try Sentry for free. Included on all plans.").

## Post Types

Here's the quick map by post type:

| Type | Goal | Byline |
|------|------|--------|
| Engineering Deep Dive | Explain a technical system/decision so other engineers learn | The engineer(s) who built it. Always. |
| Product Launch | Explain what shipped, why it matters, how to use it | PM, engineer, or DevEx. Not PMM unless marketing built it. |
| Postmortem | Transparent failure analysis with timeline and fixes | Engineering leadership |
| Data / Research | Original insights from Sentry's unique data position | Data team, engineering, or research |
| Tutorial / Guide | Help a developer accomplish something specific | DevEx, engineer, or community contributor |

## The "Would I Share This?" Test

Before publishing, ask: Would a developer share this post? Does it have a shot at getting on Hacker News? If the answer is no, the post either needs more depth, more original insight, or it belongs in the changelog instead.

Posts worth sharing contain at least one of:
- A technical decision explained with trade-offs
- Original data or research not found elsewhere
- A real-world debugging story with specific details
- An honest accounting of something that went wrong
- A how-to that saves the reader real time

## Non-Negotiables (Quick Reference)

1. Never publish without a real person's name on it. No "The Sentry Team" bylines.
2. Never publish code that doesn't work.
3. Never say "we're excited to announce." Just announce it.
4. Ask whether the user wants a diagram and what it should show; include one only if wanted, and use a horizontal layout for Mermaid flowcharts.
5. If you make a performance claim, include the number.
6. If you discuss a decision, explain what you didn't choose and why.
7. Every post must have a clear "who is this for" in the author's mind before writing.
8. Changelogs belong in the changelog. Blog posts should offer something more.
9. When in doubt, go deeper. The risk of being too shallow is far greater than being too detailed.
10. Write the post you wish existed when you were trying to solve this problem.

## When Reviewing or Editing a Draft

Run through both checklists:

**Technical Review:**
- All technical claims accurate
- Code samples work
- Architecture descriptions match reality
- Numbers and benchmarks correct
- No oversimplifications that would make an expert cringe

**Editorial Review:**
- Opening hooks reader within 2 sentences
- Passes the "would I share this?" test
- No corporate language, filler, or fluff
- Headings convey information
- Right length (not padded, not too thin)
- Title is catchy, specific, and supported by the post; its implications match the findings and preserve essential qualifications
- Closing resolves the argument and naturally answers relevant reader questions without an FAQ-style ending
- Diagram preference and scope were confirmed; any Mermaid flowchart uses a horizontal layout

**Final Check:**
- Author byline is correct (real person's name)
- Links to docs/getting-started included
- Post doesn't duplicate what's in the changelog

When providing feedback, be specific and constructive. Quote the weak passage, explain why it's weak, and rewrite it to show the standard.
