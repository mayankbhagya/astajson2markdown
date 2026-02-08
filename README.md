# astajson2markdown

Convert Asta JSON output to a markdown file.

[AllenAI's Asta](https://asta.allen.ai/) report generation tool allows JSON file download only. This script converts the JSON file to a readable MD file.

## Usage 
`python convert_report_to_md.py report.json`

## Features
- Title + Text from all sections
- Converts tables
- Sorted list of references
- Ignores TLDR section summaries
