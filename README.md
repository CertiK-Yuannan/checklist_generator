# Checklist Generator

A tool to generate checklists from externally collected findings.

## Components

1. **Finding Retriever**: Retrieves findings from external sources
2. **Checklist Generator**: Generates checklists based on collected findings

## Setup

\`\`\`bash
# Install dependencies
poetry install

# Run the application
poetry run python main.py --source solodit_tidb --category xxx