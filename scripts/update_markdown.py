#!/usr/bin/env python3
"""Update plant markdown files with image embeds."""

import json
import os
import re

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    plants_dir = os.path.join(base_dir, 'plants')
    metadata_path = os.path.join(base_dir, 'images', 'metadata.json')

    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # Process each plant file
    for plant_slug, info in metadata.items():
        md_path = os.path.join(plants_dir, f'{plant_slug}.md')

        if not os.path.exists(md_path):
            print(f"WARNING: {md_path} not found")
            continue

        with open(md_path, 'r') as f:
            content = f.read()

        # Check if image already added
        if f'![' in content and f'](../images/' in content:
            print(f"SKIPPED: {plant_slug} (image already present)")
            continue

        # Get plant common name from the H1 heading
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if not h1_match:
            print(f"WARNING: No H1 heading found in {plant_slug}")
            continue

        common_name = h1_match.group(1)

        # Create image embed with attribution
        image_file = info['file']
        author = info['author']
        license_name = info['license']
        source_url = info['source_url']

        image_embed = f'\n![{common_name}](../images/{image_file})\n*Photo: [{author}]({source_url}) | {license_name}*\n'

        # Insert after the H1 heading
        h1_end = h1_match.end()
        new_content = content[:h1_end] + image_embed + content[h1_end:]

        # Write updated content
        with open(md_path, 'w') as f:
            f.write(new_content)

        print(f"UPDATED: {plant_slug}")

if __name__ == '__main__':
    main()
