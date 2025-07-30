# AI Resume Builder

Generate professional resumes from YAML data using LaTeX templates. Simple, fast, and customizable.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
git clone <repository-url>
cd resume-builder
docker-compose up --build
```

Visit `http://localhost:8000`

### Local Development

```bash
pip install -r requirements.txt
python manage.py runserver
```

### Command Line

```bash
python cli.py --output "resume.pdf"
# Or with custom data file
python cli.py --data "my_resume.yaml" --output "my_resume.pdf"
```

## 📝 How It Works

1. **Edit your data**: Update `data/resume.yaml` with your information
2. **Choose template**: Modify `templates/resume.tex` for custom styling
3. **Generate PDF**: Use web interface or CLI to create your resume

### Sample Data Format

```yaml
name: "John Doe"
email: "john.doe@example.com"
phone: "+1-555-0123"
education_school: "University of Technology"
education_degree: "Bachelor of Science - Computer Science"
skills_languages: "Python, JavaScript, Java"
# ... more fields
```

## 🔧 Debugging

### Common Issues

**LaTeX not found**

```bash
# Ubuntu/Debian
sudo apt-get install texlive-full

# macOS
brew install --cask mactex

# Windows
# Download MiKTeX from https://miktex.org/
```

**Template errors**

- Check `{{VARIABLE}}` placeholders match YAML keys
- Ensure LaTeX syntax is valid
- View generated `.tex` file in `output/` folder

**YAML errors**

- Validate YAML syntax at yamllint.com
- Check indentation and quotes
- Ensure required fields are present

### Debug Mode

```bash
# Enable debug output
DEBUG=True python manage.py runserver

# Check generated files
ls output/  # View generated PDFs and LaTeX files
```

## 📁 Project Structure

```
resume-builder/
├── data/resume.yaml          # Your resume data
├── templates/resume.tex      # LaTeX template
├── web/                      # Django web interface
├── cli.py                    # Command line tool
└── output/                   # Generated files
```

## 🎯 Features

- ✅ Simple YAML data format
- ✅ Professional LaTeX templates
- ✅ Web interface and CLI
- ✅ Docker support
- ✅ Variable replacement system
- ✅ Error handling and validation

## 🤝 Contributing

Want to contribute? We'd love your help!

[![Contribute](https://img.shields.io/badge/📖-Contributing%20Guide-blue?style=for-the-badge)](CONTRIBUTING.md)

See our [Contributing Guide](CONTRIBUTING.md) for:

- Development setup
- Code style guidelines
- How to submit pull requests
- System architecture details

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need help?** Open an issue or check our [Contributing Guide](CONTRIBUTING.md) for detailed documentation.
