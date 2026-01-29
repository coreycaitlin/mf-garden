#!/usr/bin/env python3
"""
Generate plants.json from plant markdown files.
Extracts YAML frontmatter and image paths from markdown files in /plants/
"""

import re
import json
from pathlib import Path


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content (simple parser)."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}

    # Simple YAML parser for key: "value" or key: value lines
    frontmatter = {}
    for line in match.group(1).strip().split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            frontmatter[key] = value
    return frontmatter


def extract_image_path(content: str) -> str | None:
    """Extract the first image path from markdown content."""
    # Look for markdown image syntax: ![alt](path)
    match = re.search(r'!\[.*?\]\((.*?)\)', content)
    if match:
        path = match.group(1)
        # Convert relative path ../images/x.jpg to images/x.jpg
        if path.startswith('../'):
            path = path[3:]
        return path
    return None


def extract_field(content: str, field_name: str) -> str:
    """Extract a field value from markdown content like '- **Field:** Value'."""
    pattern = rf'^\s*-\s*\*\*{re.escape(field_name)}:\*\*\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ''


def extract_photo_credit(content: str) -> str:
    """Extract photo credit from markdown like '*Photo: [Author](url) | License*'."""
    # Match *Photo: [Author](url) | License* pattern
    # Use .+?\) to handle URLs with parentheses in filenames
    match = re.search(r'\*Photo:\s*\[([^\]]+)\]\(.+?\)\s*\|\s*([^*]+)\*', content)
    if match:
        author = match.group(1).strip()
        license = match.group(2).strip()
        return f"Photo: {author} | {license}"
    return ''


def generate_slug(filename: str) -> str:
    """Generate slug from filename (remove .md extension)."""
    return filename.replace('.md', '')


def process_plant_file(filepath: Path) -> dict | None:
    """Process a single plant markdown file and return plant data."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    frontmatter = extract_frontmatter(content)
    if not frontmatter:
        print(f"Warning: No frontmatter found in {filepath}")
        return None

    image = extract_image_path(content)
    slug = generate_slug(filepath.name)
    sun_requirements = extract_field(content, 'Sun requirements')
    water_needs = extract_field(content, 'Water needs')
    soil_type = extract_field(content, 'Soil type')
    photo_credit = extract_photo_credit(content)

    return {
        'common_name': frontmatter.get('common_name', ''),
        'scientific_name': frontmatter.get('scientific_name', ''),
        'plant_type': frontmatter.get('plant_type', ''),
        'status': frontmatter.get('status', ''),
        'garden_area': frontmatter.get('garden_area', ''),
        'sun_requirements': sun_requirements,
        'water_needs': water_needs,
        'soil_type': soil_type,
        'image': image,
        'photo_credit': photo_credit,
        'slug': slug
    }


def main():
    # Determine paths relative to script location
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    plants_dir = repo_root / 'plants'
    output_file = repo_root / 'docs' / 'plants.json'

    if not plants_dir.exists():
        print(f"Error: Plants directory not found at {plants_dir}")
        return 1

    # Process all markdown files
    plants = []
    for filepath in sorted(plants_dir.glob('*.md')):
        plant_data = process_plant_file(filepath)
        if plant_data:
            plants.append(plant_data)

    # Ensure webapp directory exists
    output_file.parent.mkdir(exist_ok=True)

    # Write JSON output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(plants, f, indent=2)

    print(f"Generated {output_file} with {len(plants)} plants")
    return 0


if __name__ == '__main__':
    exit(main())
