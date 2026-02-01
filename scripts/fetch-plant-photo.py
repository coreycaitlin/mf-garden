#!/usr/bin/env python3
"""
Fetch plant photos from Wikimedia Commons.

Usage:
    python scripts/fetch-plant-photo.py <plant-slug>
    python scripts/fetch-plant-photo.py sword-fern
    python scripts/fetch-plant-photo.py --missing   # Show plants without photos

Searches Wikimedia Commons using the plant's scientific name,
displays available images, and lets you pick one to download.
"""

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
PLANTS_DIR = REPO_ROOT / 'plants'
IMAGES_DIR = REPO_ROOT / 'images'
DOCS_IMAGES_DIR = REPO_ROOT / 'docs' / 'images'

# Wikimedia API endpoints
COMMONS_API = 'https://commons.wikimedia.org/w/api.php'


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).strip().split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            frontmatter[key] = value
    return frontmatter


def curl_get_json(url: str) -> dict | None:
    """Use curl to fetch JSON from a URL. Returns None on error."""
    result = subprocess.run(
        ['curl', '-sL', '-A', 'MF-Garden-PhotoFetcher/1.0 (https://github.com/example/mf-garden)', url],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        return None
    if not result.stdout:
        return None
    # Check for HTML error page
    if result.stdout.strip().startswith('<!'):
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def curl_download(url: str, dest_path: Path) -> bool:
    """Use curl to download a file."""
    result = subprocess.run(
        ['curl', '-sL', url, '-o', str(dest_path)],
        capture_output=True,
        timeout=60
    )
    return result.returncode == 0


def api_request(params: dict) -> dict | None:
    """Make a request to the Wikimedia Commons API."""
    params['format'] = 'json'
    # Use quote_via to handle pipe characters properly
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = f"{COMMONS_API}?{query_string}"
    # Small delay to be nice to the API
    time.sleep(0.2)
    return curl_get_json(url)


def search_commons_images(scientific_name: str, limit: int = 10) -> list:
    """Search Wikimedia Commons for images of a plant."""
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': scientific_name,
        'srnamespace': '6',  # File namespace
        'srlimit': str(limit)
    }

    data = api_request(params)
    if not data:
        return []

    results = []
    for item in data.get('query', {}).get('search', []):
        title = item['title']
        # Only include image files
        if any(title.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
            results.append(title)

    return results


def get_image_info(file_title: str) -> dict | None:
    """Get detailed info about a Wikimedia Commons image."""
    params = {
        'action': 'query',
        'titles': file_title,
        'prop': 'imageinfo',
        'iiprop': 'url|extmetadata|size',
        'iiurlwidth': '300'  # Get thumbnail
    }

    data = api_request(params)
    if not data:
        return None

    pages = data.get('query', {}).get('pages', {})

    for page in pages.values():
        if 'imageinfo' not in page:
            continue

        info = page['imageinfo'][0]
        meta = info.get('extmetadata', {})

        # Extract artist name from HTML
        artist_html = meta.get('Artist', {}).get('value', '')
        # Try to get plain text from HTML
        artist_match = re.search(r'>([^<]+)</a>', artist_html)
        if artist_match:
            artist = artist_match.group(1)
        else:
            artist = re.sub(r'<[^>]+>', '', artist_html).strip()

        license_name = meta.get('LicenseShortName', {}).get('value', 'Unknown')

        # Skip non-free licenses
        if 'CC' not in license_name and 'Public domain' not in license_name.lower():
            return None

        return {
            'title': file_title,
            'url': info.get('url'),
            'thumb_url': info.get('thumburl'),
            'width': info.get('width', 0),
            'height': info.get('height', 0),
            'artist': artist or 'Unknown',
            'license': license_name,
            'commons_url': f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(file_title)}"
        }

    return None


def update_plant_file(plant_path: Path, commons_url: str, artist: str, license_name: str) -> bool:
    """Update the plant markdown file with photo credit."""
    content = plant_path.read_text(encoding='utf-8')

    # Pattern to match the photo credit line
    old_pattern = r'\*Photo: \[.*?\]\(.*?\) \| .*?\*'
    new_credit = f'*Photo: [{artist}]({commons_url}) | {license_name}*'

    if re.search(old_pattern, content):
        new_content = re.sub(old_pattern, new_credit, content)
    else:
        # Try to find placeholder
        placeholder = '*Photo: [Author Name](wikimedia-source-url) | License*'
        if placeholder in content:
            new_content = content.replace(placeholder, new_credit)
        else:
            print("Warning: Could not find photo credit line to update")
            return False

    plant_path.write_text(new_content, encoding='utf-8')
    return True


def get_plant_info(slug: str) -> dict | None:
    """Get plant info from its markdown file."""
    plant_path = PLANTS_DIR / f"{slug}.md"
    if not plant_path.exists():
        return None

    content = plant_path.read_text(encoding='utf-8')
    frontmatter = extract_frontmatter(content)

    return {
        'path': plant_path,
        'slug': slug,
        'common_name': frontmatter.get('common_name', slug),
        'scientific_name': frontmatter.get('scientific_name', ''),
        'has_image': (IMAGES_DIR / f"{slug}.jpg").exists()
    }


def list_plants_missing_photos() -> list:
    """List all plants that don't have photos yet."""
    missing = []
    for plant_file in sorted(PLANTS_DIR.glob('*.md')):
        slug = plant_file.stem
        image_path = IMAGES_DIR / f"{slug}.jpg"
        if not image_path.exists():
            info = get_plant_info(slug)
            if info:
                missing.append(info)
    return missing


def interactive_select(images: list) -> dict | None:
    """Let user interactively select an image."""
    print(f"\nFound {len(images)} images:\n")

    for i, img in enumerate(images, 1):
        print(f"  [{i}] {img['title'].replace('File:', '')}")
        print(f"      Size: {img['width']}x{img['height']} | By: {img['artist']} | {img['license']}")
        print(f"      Preview: {img['thumb_url']}")
        print()

    print("  [0] Skip - don't download any image")
    print()

    while True:
        try:
            choice = input("Select image number: ").strip()
            if choice == '0':
                return None
            num = int(choice)
            if 1 <= num <= len(images):
                return images[num - 1]
            print(f"Please enter a number between 0 and {len(images)}")
        except ValueError:
            print("Please enter a valid number")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled")
            return None


def fetch_photo_for_plant(slug: str) -> bool:
    """Main function to fetch a photo for a plant."""
    plant = get_plant_info(slug)
    if not plant:
        print(f"Error: Plant '{slug}' not found in {PLANTS_DIR}")
        return False

    if not plant['scientific_name']:
        print(f"Error: No scientific name found for '{slug}'")
        return False

    print(f"\nSearching for: {plant['common_name']} ({plant['scientific_name']})")

    # Search for images
    file_titles = search_commons_images(plant['scientific_name'])
    if not file_titles:
        print("No images found on Wikimedia Commons")
        return False

    # Get detailed info for each image
    images = []
    print("Fetching image details...")
    for title in file_titles:
        info = get_image_info(title)
        if info:
            images.append(info)

    if not images:
        print("No suitable Creative Commons images found")
        return False

    # Let user select
    selected = interactive_select(images)
    if not selected:
        print("No image selected")
        return False

    # Download image
    image_filename = f"{slug}.jpg"
    main_dest = IMAGES_DIR / image_filename
    docs_dest = DOCS_IMAGES_DIR / image_filename

    print(f"\nDownloading {selected['title']}...")

    if not curl_download(selected['url'], main_dest):
        print("Error: Download failed")
        return False

    # Copy to docs/images
    docs_dest.write_bytes(main_dest.read_bytes())

    # Update plant file
    if update_plant_file(plant['path'], selected['commons_url'], selected['artist'], selected['license']):
        print(f"\n✓ Downloaded: {main_dest}")
        print(f"✓ Copied to:  {docs_dest}")
        print(f"✓ Updated:    {plant['path']}")
        print(f"\nPhoto credit: {selected['artist']} | {selected['license']}")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(
        description='Fetch plant photos from Wikimedia Commons',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sword-fern          Fetch photo for sword fern
  %(prog)s --missing           List plants without photos
  %(prog)s --missing --fetch   Fetch photos for all plants missing them
"""
    )
    parser.add_argument('slug', nargs='?', help='Plant slug (filename without .md)')
    parser.add_argument('--missing', action='store_true', help='List plants missing photos')
    parser.add_argument('--fetch', action='store_true', help='With --missing, fetch photos interactively')

    args = parser.parse_args()

    if args.missing:
        missing = list_plants_missing_photos()
        if not missing:
            print("All plants have photos!")
            return 0

        print(f"\nPlants missing photos ({len(missing)}):\n")
        for plant in missing:
            print(f"  {plant['slug']}: {plant['common_name']} ({plant['scientific_name']})")

        if args.fetch:
            print("\n" + "="*60)
            for plant in missing:
                print(f"\n{'='*60}")
                fetch_photo_for_plant(plant['slug'])
        else:
            print(f"\nRun with --fetch to download photos interactively")
            print(f"Or: python {sys.argv[0]} <plant-slug>")

        return 0

    if not args.slug:
        parser.print_help()
        return 1

    success = fetch_photo_for_plant(args.slug)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
