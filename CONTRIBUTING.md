# Contributing to CrackVision AI

Thank you for your interest in contributing to **CrackVision AI**!

## Development Workflow

1. **Fork the Repository** and clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/crackvision-ai.git
   cd crackvision-ai
   ```

2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Install Dependencies**:
   - Backend:
     ```bash
     cd backend
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```
   - Frontend:
     ```bash
     cd frontend
     npm install
     ```

4. **Run Tests Locally**:
   Ensure all automated tests pass before creating a pull request:
   ```bash
   # Backend tests
   pytest backend/tests

   # Frontend build
   cd frontend && npm run build
   ```

5. **Commit Your Changes**:
   Follow conventional commits (e.g., `feat: ...`, `fix: ...`, `docs: ...`).

6. **Open a Pull Request**:
   Push to your fork and submit a PR to `main` with a clear description of your changes and verification steps.
