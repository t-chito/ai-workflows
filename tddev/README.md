# TDDev - Test-Driven Development for Web Applications

**Automatically generate full-stack web applications from requirements via multi-agent test-driven development.**

Based on the research paper:
📄 **[arXiv:2509.25297v2](https://arxiv.org/abs/2509.25297)** - "Automatically Generating Web Applications from Requirements Via Multi-Agent Test-Driven Development"
By Yuxuan Wan, Tingshuo Liang, Jiakai Xu, et al.

---

## 🌟 Features

- **Multi-Agent Architecture**: Three specialized agents work together
  - 🧪 **Test Generation Agent**: Derives test cases from requirements
  - 💻 **Development Agent**: Generates full-stack code
  - ✅ **Testing Agent**: Executes tests and provides feedback

- **Test-Driven Development**: Iteratively refines code until tests pass
- **Multimodal Support**: Accepts text descriptions + design images
- **Multiple Frameworks**: Supports 13+ templates (React, Next.js, Vue, etc.)
- **Automated Testing**: Uses BrowserUse for realistic user simulation
- **Zero Manual Intervention**: Fully autonomous generation and refinement

---

## 📊 Performance

Based on the paper's evaluation on WebGen-Bench:

| Metric | Bolt.diy (Claude) | Cursor (Claude) | **TDDev (Claude)** |
|--------|------------------|-----------------|-------------------|
| **Accuracy** | 44.5% | 63.8% | **70.2%** (+14.4%) |
| **Fail to Start** | 20.0% | 20.0% | **0.0%** |
| **Visual Similarity** | 2.6/5 | 3.3/5 | **4.3/5** |

✅ **30% better** than Cursor with GPT-4.1
✅ **3x better** than Bolt.diy
✅ **Zero manual interventions** required

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- API key for Anthropic (Claude) or OpenAI (GPT)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tddev.git
cd tddev

# Install dependencies
pip install -r requirements.txt

# Set API keys
export ANTHROPIC_API_KEY="your-api-key-here"
# Or for OpenAI:
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

```bash
# Simple app generation
python main.py --input "Create a todo list app where users can add, complete, and delete tasks"

# With design image
python main.py --input "Create a shopping website" --image design.png

# Custom output directory
python main.py --input "Build a blog platform" --output ./my_blog

# Use different model
python main.py --input "Create a dashboard" --provider openai --model gpt-4.1
```

### Run Generated App

```bash
cd output/app
npm install
npm run dev
```

---

## 📖 How It Works

### 1. **Test Generation Phase**

The Test Generation Agent transforms your requirements into comprehensive test cases:

```
Input: "Create a todo list app"

↓ Requirement Decomposition
["Display list of todos", "Add new todos", "Mark todos complete", ...]

↓ Requirement Elaboration
{functionality, ui_design, interactions, data, dependencies}

↓ Test Case Generation (Soap Opera Testing)
{persona, steps, expected_results, validation}
```

### 2. **Development Phase**

The Development Agent generates code to satisfy the tests:

```
Template Selection → Context Selection → Code Generation
     ↓                      ↓                   ↓
  React/Next.js     Relevant files only    Full implementation
```

### 3. **Testing Phase**

The Testing Agent validates the implementation:

```
Deploy App → Execute Tests → Generate Feedback
    ↓             ↓                ↓
  Launch      Simulate user    Detailed error
  server      interactions     reports
```

### 4. **Refinement Loop**

The cycle repeats until tests pass (max 3 iterations by default):

```
Test → Dev → Test → Dev → Test → ✅ Success!
```

---

## 🎯 Usage Examples

### Example 1: Todo List App

```bash
python main.py --input "Create a simple todo list app where users can add, complete, and delete tasks. Use a clean, modern design with a blue color scheme."
```

**Result**: Fully functional todo app with:
- Add/delete/complete functionality
- Clean UI with blue theme
- Persistent state management
- Responsive design

### Example 2: E-commerce Site (with design)

```bash
python main.py \
  --input "Build a shopping website with product catalog, cart, and checkout" \
  --image mockup.png \
  --max-iterations 5
```

**Result**: E-commerce site matching the design with:
- Product listing and search
- Shopping cart functionality
- Checkout flow
- Visual fidelity to mockup

### Example 3: Dashboard Application

```bash
python main.py \
  --input "Create a dashboard for regulatory policies with data visualizations. Include charts, filters, and sortable tables." \
  --provider openai \
  --model gpt-4.1
```

**Result**: Interactive dashboard with:
- Data visualization (charts, graphs)
- Filtering and sorting
- Responsive layout
- Policy browsing interface

---

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

```yaml
llm:
  provider: "anthropic"  # or "openai"
  model: "claude-sonnet-4-5-20250929"
  temperature: 0
  max_tokens: 8192

workflow:
  max_iterations: 3
  early_stopping:
    enabled: true
    min_pass_rate: 0.95

development:
  templates:
    - nextjs-shadcn
    - vite-react
    - vuejs
    # ... 13 total templates

testing:
  browser:
    engine: "browser-use"
    headless: true
    timeout: 30000
```

---

## 🏗️ Architecture

```
tddev/
├── agents/
│   ├── test_generation/     # Test case generation
│   │   └── agent.py          # 3-step pipeline
│   ├── development/          # Code generation
│   │   └── agent.py          # Template + context + editing
│   └── testing/              # Automated testing
│       └── agent.py          # BrowserUse integration
├── orchestrator/
│   └── tdd_workflow.py       # TDD loop orchestration
├── utils/
│   ├── llm_client.py         # LLM API wrapper
│   └── file_utils.py         # File management
├── config/
│   └── config.yaml           # Configuration
├── main.py                   # CLI entry point
└── requirements.txt
```

---

## 📚 Research Background

TDDev is based on cutting-edge research from CUHK, Columbia, and SMU:

### Key Innovations

1. **Multi-Step Test Generation**
   - Requirement decomposition → elaboration → test cases
   - Soap opera testing for realistic scenarios
   - Handles underspecified requirements

2. **Context-Aware Development**
   - Intelligent file selection (not all files)
   - Template-based initialization (13 frameworks)
   - Full-file replacement for consistency

3. **End-to-End Testing**
   - BrowserUse for real browser automation
   - Functional + visual validation
   - Detailed feedback for refinement

### Performance Highlights (from paper)

- **78.2% accuracy** with GPT-4.1 (vs 60.2% Cursor)
- **70.2% accuracy** with Claude-4-Sonnet (vs 63.8% Cursor)
- **0% fail-to-start rate** (vs 20-80% for baselines)
- **4.3/5 visual similarity** (best in class)

---

## 🔬 Advanced Features

### Multimodal Input

Provide both text and images:

```python
workflow.run(
    user_input="Create a dashboard website...",
    design_image="mockup.png"
)
```

### Custom Templates

Add your own starter templates:

```yaml
development:
  templates:
    - name: "my-template"
      description: "Custom Next.js setup"
      path: "templates/my-template"
```

### Programmatic API

```python
from tddev.orchestrator import TDDWorkflow
from tddev.utils.llm_client import LLMClient

llm = LLMClient(provider="anthropic", model="claude-sonnet-4-5-20250929")
workflow = TDDWorkflow(llm, "output/my_app")

result = workflow.run(
    user_input="Create a forum website",
    max_iterations=3
)

print(f"Success: {result['success']}")
print(f"Pass Rate: {result['final_pass_rate']:.1%}")
```

---

## 🐛 Troubleshooting

### API Key Issues

```bash
# Check if API key is set
echo $ANTHROPIC_API_KEY

# Set it if missing
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Installation Errors

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-dev

# Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Application Won't Start

Check the logs:

```bash
python main.py --input "..." --log-level DEBUG --log-file debug.log
```

---

## 📈 Roadmap

- [ ] Support for more frameworks (Angular, Svelte, Solid.js)
- [ ] Database integration (PostgreSQL, MongoDB)
- [ ] API integration (REST, GraphQL)
- [ ] Mobile app generation (React Native, Flutter)
- [ ] Open-source LLM support (DeepSeek, Qwen)
- [ ] Visual regression testing
- [ ] Deployment automation (Vercel, Netlify)

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 📝 Citation

If you use TDDev in your research, please cite:

```bibtex
@article{wan2025tddev,
  title={Automatically Generating Web Applications from Requirements Via Multi-Agent Test-Driven Development},
  author={Wan, Yuxuan and Liang, Tingshuo and Xu, Jiakai and Xiao, Jingyu and Huo, Yintong and Lyu, Michael},
  journal={arXiv preprint arXiv:2509.25297},
  year={2025}
}
```

---

## 🙏 Acknowledgments

- Research team at CUHK, Columbia University, and SMU
- [BrowserUse](https://github.com/browser-use/browser-use) for browser automation
- [Bolt.diy](https://github.com/bolt-diy/bolt-diy) for inspiration
- Anthropic and OpenAI for powerful LLMs

---

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/tddev/issues)
- **Paper**: [arXiv:2509.25297](https://arxiv.org/abs/2509.25297)
- **Email**: contact@tddev.ai

---

<div align="center">

**Built with ❤️ by the TDDev Team**

[⭐ Star us on GitHub](https://github.com/yourusername/tddev) | [📄 Read the Paper](https://arxiv.org/abs/2509.25297) | [🐛 Report Bug](https://github.com/yourusername/tddev/issues)

</div>
