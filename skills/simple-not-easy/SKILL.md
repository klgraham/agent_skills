---
name: simple-not-easy
description: >-
  Use when designing or reviewing a module, API, data model, or feature
  plan, when handed a feature list or bug report, or when a change feels
  harder than it should. Decomplect interleaved concerns, take the problem
  apart before composing a solution, and make design decisions instead of
  leaving every option open.
---

# Simple, not easy

Simple means one role, one concept, not intertwined with anything else. Easy means familiar or close at hand. Optimize for simple, even when easy is right there.

Design is taking things apart so they can be put back together. Start by taking apart the requirements and the candidate solutions, not by drawing the big plan. The value of a design is the decisions it makes. Leaving every option open is not design; it hands the design work to the user.

Source: Rich Hickey, "Design, Composition, and Performance" (QCon San Francisco, 2013), for taking apart the problem and design as deciding.

## Decomplect

- Ask of every construct what it's braiding together: state and time, identity and value, what and how, policy and mechanism.
- Prefer plain data over objects that bundle data with behavior; functions over methods; composition over inheritance; queues over direct calls between components.
- Keep the declarative *what* separate from the *how* of execution.
- Judge a tool by what it tangles over the life of the system, not by how fast you can start with it.
- When a fix touches many unrelated places, untangle before patching.

## Take apart the problem

- Break the feature list into the actual problems the user has. Solve problems, not features.
- Split known from unknown, and domain requirements from solution requirements ("must run on AWS, must use X").
- For "it's not working," separate cause from symptom before typing a fix.
- Write down the unstated requirements: don't crash, don't eat memory, don't cost too much to run, don't need manual babysitting, don't make users hate it.
- Take apart order and participants: where can queues, idempotence, or commutative operations remove an ordering dependency?
- List each candidate solution's tradeoffs and costs, and reject one that is bigger than the problem.
- Decompose until each piece is about one thing; extension, reuse, and testability fall out of the seams.

## Design is deciding

- Seek out constraints early. If the problem doesn't supply enough, choose some.
- Think up ten, ship one.
- Don't make it configurable when you can decide.
- Push back on "take my good idea." Every addition may be good; all of them together are unplayable.
- Stay at the layer you're working on. Rewriting the driver for 10% while building the feature is scope creep.
- Quit fidgeting with tooling and build setup; spend the time on the actual problem.
- Build a repertoire (patterns, techniques, what works and what doesn't) so that coding draws on preparation instead of making it up.

## Anti-patterns

- Choosing the familiar framework because it's quick to start, then fighting its coupling for years.
- A class that owns its data, its persistence, and its scheduling.
- Patching a symptom in five places instead of finding the shared cause.
- Shipping a settings page instead of a decision.

When this skill shaped your work, name the principle you applied ("simple-not-easy") and the decision it changed. For example: "split job scheduling out of the job data before adding retries".
