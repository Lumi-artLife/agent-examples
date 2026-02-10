# Agent Examples

Production-ready agent workflow examples using the Hive framework. This repository demonstrates multi-agent orchestration, Human-in-the-Loop (HITL) systems, and event-driven patterns.

## 🎯 Purpose

This repository complements the [Hive](https://github.com/adenhq/hive) framework by providing practical, production-ready examples that demonstrate:

- **Multi-agent coordination** - Context handoff between nodes
- **Human-in-the-Loop** - Approval workflows and escalation patterns
- **Event-driven agents** - Reactive systems and monitoring
- **Error handling** - Graceful failure modes and recovery

## 📁 Examples

### 1. HITL Approval Workflow

A production-ready email approval system demonstrating all 5 HITL input types.

**Scenario**: Customer support agent drafts responses, pauses for human approval before sending.

**Features**:
- Free text feedback
- Structured field validation
- Selection lists (approve/reject/modify)
- Timeout handling (what happens if no response in 5 minutes)
- Error escalation

**Files**: [`examples/hitl_approval_workflow/`](examples/hitl_approval_workflow/)

### 2. Multi-Turn Research Loop ✅

Autonomous research agent demonstrating the Think → Act → Evaluate → Repeat pattern.

**Scenario**: Agent searches web, evaluates if information is sufficient, decides whether to search again or synthesize results.

**Features**:
- Self-directed research with stopping criteria
- Quality evaluation at each iteration
- Query refinement based on results
- Graceful escalation when stuck

**Pattern**: Think → Act → Evaluate → Repeat

**Files**: [`examples/multi_turn_research_loop/`](examples/multi_turn_research_loop/)

### 3. Context Handoff ✅

Multi-stage pipeline demonstrating structured context passing between nodes.

**Scenario**: Data collection → Validation → Analysis → Report generation

**Features**:
- Structured context object that flows through stages
- Each stage adds its output while preserving history
- Validation and error handling at each step
- Complete audit trail of execution

**Pattern**: Context passing with structured handoff

**Files**: [`examples/context_handoff/`](examples/context_handoff/)

### 4. Goal-Driven Agent ✅

Agent with declarative goals, weighted success criteria, and constraint handling.

**Scenario**: Optimize for multiple objectives (response time, cost, quality) while respecting boundaries (budget limits).

**Features**:
- Weighted success criteria with priorities
- Hard and soft constraints
- Automatic progress tracking
- Action selection based on goal alignment

**Pattern**: Declarative goals + weighted optimization + constraint satisfaction

**Files**: [`examples/goal_driven_agent/`](examples/goal_driven_agent/)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Lumi-artLife/agent-examples.git
cd agent-examples

# Install dependencies
pip install -r requirements.txt

# Run an example
cd examples/hitl_approval_workflow
python agent.py
```

## 🛠️ Requirements

- Python 3.9+
- Hive framework (`pip install hive-framework`)
- See individual examples for specific dependencies

## 📖 Documentation

Each example includes:
- `README.md` - Detailed explanation and usage
- `agent.py` - Main implementation
- `config.yaml` - Agent configuration
- `tests/` - Unit tests and integration tests

## 🤝 Contributing

Contributions welcome! Areas of interest:

- Additional workflow patterns
- Error handling improvements
- Documentation enhancements
- Real-world use cases

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🔗 Related

- [Hive Framework](https://github.com/adenhq/hive) - The underlying agent framework
- [Hive Documentation](https://docs.hive.com) - Official docs

---

**Author**: Lumi ([Lumi-artLife](https://github.com/Lumi-artLife))  
**Status**: ✅ 4 examples complete (2,800+ lines of production code)  
**Created**: February 10, 2026  
**License**: MIT
