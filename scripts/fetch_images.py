#!/usr/bin/env python3
"""Fetch plant images from Wikimedia Commons."""

import json
import os
import re
import urllib.parse
import urllib.request

# Plant to Wikimedia file mapping
PLANTS = {
    "baldhip-rose": "File:Rosa gymnocarpa 15142.JPG",
    "big-leaf-lupine": "File:Lupinus polyphyllus UA 2015 G5.jpg",
    "douglas-iris": "File:Iris douglasiana Salt Point.jpg",
    "dwarf-snowberry": "File:Symphoricarpos mollis kz04.jpg",
    "false-solomons-seal": "File:Maianthemum racemosum RF.jpg",
    "flowering-currant": "File:Ribes sanguineum 5409.JPG",
    "foamflower": "File:Tiarella trifoliata 10954.JPG",
    "fringecup": "File:Tellima grandiflora 11202.JPG",
    "heath-aster": "File:Symphyotrichum ericoides kz01.jpg",
    "inside-out-flower": "File:Vancouveria hexandra 6356.JPG",
    "manzanita": "File:Arctostaphylos columbiana.jpg",
    "oregon-boxwood": "File:Paxistima myrsinites 38584.JPG",
    "pacific-wax-myrtle": "File:Myrica californica.jpg",
    "piggyback-plant": "File:Tolmiea menziesii 6537.JPG",
    "redwood-sorrel": "File:Oxalis oregana 06104.JPG",
    "seaside-daisy": "File:Erigeron glaucus.jpg",
    "sword-fern": "File:Polystichum munitum (Jami Dwyer) 001.jpg",
    "vine-maple": "File:Acer circinatum 10751.JPG",
    "western-bleeding-heart": "File:Dicentra formosa 6897.JPG",
    "western-trillium": "File:Trillium ovatum 1290.JPG",
    "white-yarrow": "File:Achillea millefolium (52354).jpg",
    "wild-ginger": "File:Asarum caudatum RF.jpg",
}

def get_image_info(file_title):
    """Query Wikimedia API for image info."""
    encoded = urllib.parse.quote(file_title)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={encoded}&prop=imageinfo&iiprop=url|user|extmetadata&format=json"

    req = urllib.request.Request(url, headers={'User-Agent': 'PlantGardenBot/1.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())

    pages = data.get('query', {}).get('pages', {})
    if not pages:
        return None

    page = list(pages.values())[0]
    imageinfo = page.get('imageinfo', [{}])[0]

    ext = imageinfo.get('extmetadata', {})
    artist = ext.get('Artist', {}).get('value', '')
    # Strip HTML tags
    artist = re.sub(r'<[^>]+>', '', artist).strip()

    return {
        'url': imageinfo.get('url', ''),
        'author': artist,
        'license': ext.get('LicenseShortName', {}).get('value', ''),
        'source_url': imageinfo.get('descriptionurl', ''),
    }

def download_image(url, dest_path):
    """Download image from URL to destination path."""
    req = urllib.request.Request(url, headers={'User-Agent': 'PlantGardenBot/1.0'})
    with urllib.request.urlopen(req) as response:
        with open(dest_path, 'wb') as f:
            f.write(response.read())

def main():
    # Create images directory
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    os.makedirs(images_dir, exist_ok=True)

    # Store metadata for later use
    metadata = {}

    for plant, file_title in PLANTS.items():
        print(f"Processing {plant}...")
        try:
            info = get_image_info(file_title)
            if not info or not info['url']:
                print(f"  WARNING: Could not get info for {file_title}")
                continue

            # Determine file extension from URL
            ext = os.path.splitext(info['url'])[1].lower()
            if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                ext = '.jpg'

            dest_path = os.path.join(images_dir, f"{plant}{ext}")

            print(f"  Downloading from {info['url'][:60]}...")
            download_image(info['url'], dest_path)

            metadata[plant] = {
                'file': f"{plant}{ext}",
                'author': info['author'],
                'license': info['license'],
                'source_url': info['source_url'],
            }
            print(f"  Saved to {dest_path}")

        except Exception as e:
            print(f"  ERROR: {e}")

    # Save metadata
    metadata_path = os.path.join(images_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"\nMetadata saved to {metadata_path}")

if __name__ == '__main__':
    main()
