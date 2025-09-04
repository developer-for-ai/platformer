# Contributing to Crystal Quest

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Set up the development environment:
   ```bash
   python3 -m venv game_env
   source game_env/bin/activate  # On Windows: game_env\Scripts\activate
   pip install -r requirements.txt
   ```

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test your changes: `./build.sh test` (or `python build.py test`)
4. Commit your changes: `git commit -m "Clear description of changes"`
5. Push to your fork: `git push origin feature/your-feature-name`
6. Create a Pull Request

## Code Style

- Follow PEP 8 for Python code
- Use clear, descriptive variable and function names
- Add comments for complex logic
- Keep functions focused and small

## Testing

- Run tests before submitting: `./build.sh test`
- Add tests for new features
- Ensure all existing tests pass

## Reporting Issues

- Use the GitHub issue tracker
- Include steps to reproduce
- Provide system information (OS, Python version)
- Include error messages and logs
