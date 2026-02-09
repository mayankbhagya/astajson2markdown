# astajson2markdown

![Screenshot](ss.png)

Convert Asta JSON output to a markdown file.

[AllenAI's Asta](https://asta.allen.ai/) report generation tool allows downloads in JSON format. This repository contains two tools:
- a webpage 
- a python script

Each of them can be used independently to convert Asta JSONs to Markdown. The webpage doubles up as a browser-based reader for the report.

## Usage 
### HTML
Simply open `index.html` in your browser.
### Python
`python3 convert_report_to_md.py input.json [output.md]`

## Features
- Title + Text from all sections
- Converts tables
- Preserves citations
- Sorted list of references
- Download button
