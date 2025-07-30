# 🎯 AI Resume Builder

Generate professional resumes from YAML data using LaTeX templates. Simple, fast, and customizable.

## 🚀 Quick Start

### Docker (Recommended)
```bash
git clone <repository-url>
cd resume-genie
.\start.bat  # Windows or ./start.sh for Linux/Mac
```
Visit http://localhost:8000

### Local Development
```bash
pip install -r requirements.txt
python manage.py runserver
```

### Command Line
```bash
python cli.py --output "resume.pdf"
```

## 📝 How It Works

1. **Edit your data**: Update `data/resume.yaml` with your information
2. **Generate PDF**: Use web interface or CLI to create your resume
3. **Optional AI**: Add OpenAI API key for job-specific customization

### Sample Data Format
```yaml
basic:
  name: "John Doe"
  email: "john.doe@example.com"
  phone: "+1 (555) 123-4567"
  websites:
    - text: "LinkedIn"
      url: "https://linkedin.com/in/johndoe"

experiences:
  - company: "Tech Solutions Inc."
    titles:
      - name: "Senior Software Engineer"
        startdate: "2021"
        enddate: "Present"
    highlights:
      - "Led development of microservices architecture"
      - "Mentored 3 junior developers"

skills:
  - category: "Programming Languages"
    skills: ["Python", "JavaScript", "Java"]
```

## 🔧 Configuration

### AI Features (Optional)
1. Get OpenAI API key from https://platform.openai.com/api-keys
2. Set in `.env` file: `OPENAI_API_KEY=your-key-here`
3. Use web interface to paste job posting for customization

### LaTeX Installation
- **Ubuntu/Debian**: `sudo apt-get install texlive-latex-base texlive-latex-recommended`
- **macOS**: `brew install --cask mactex`
- **Windows**: Download MiKTeX from https://miktex.org/

## 📁 Project Structure
```
resume-genie/
├── data/resume.yaml          # Your resume data
├── templates/resume.tex      # LaTeX template
├── web/                      # Django web interface
├── cli.py                    # Command line tool
└── output/                   # Generated PDFs
```

## 🎯 Features
- ✅ Simple YAML data format
- ✅ Professional LaTeX templates
- ✅ Web interface and CLI
- ✅ Docker support
- ✅ Optional AI customization
- ✅ Error handling and validation

## 🐛 Troubleshooting

**PDF Generation Fails**:
- Check LaTeX installation: `pdflatex --version`
- View logs in `logs/` directory
- Validate YAML syntax

**Docker Issues**:
- Ensure Docker is running
- Try: `docker-compose down && docker-compose up --build`

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## 📄 License

MIT License - see LICENSE file for details.