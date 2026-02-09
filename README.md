# astajson2markdown

Convert Asta JSON output to a markdown file.

[AllenAI's Asta](https://asta.allen.ai/) report generation tool allows JSON file download only. This repository contains two tools:
- a webpage 
- a python script

Both can convert the Asta JSON file to a readable MD file.

## Usage 
### Python
`python3 convert_report_to_md.py input.json [output.md]`
### HTML
Simply open the page in your browser.

## Features
- Title + Text from all sections
- Converts tables
- Preserves citations
- Sorted list of references
- Ignores TLDR section summaries
