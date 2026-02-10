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

### 2. Multi-Turn Research Loop (Coming Soon)

Event loop pattern for autonomous research agents.

**Scenario**: Agent searches web, evaluates results, decides whether to search again or summarize.

**Pattern**: Think → Act → Evaluate → Repeat

### 3. Multi-Node Pipeline (Coming Soon)

Context handoff across 3+ nodes with state passing.

**Scenario**: Data collection → Analysis → Report generation

**Challenge**: How context flows between stages without breaking

### 4. Goal-Driven Agent (Coming Soon)

Weighted success criteria and constraint handling.

**Scenario**: Agent with declarative goals containing multiple success criteria and hard constraints.

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
**Status**: 🚧 Active development - First example coming soon
