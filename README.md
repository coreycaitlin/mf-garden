# mf-garden
Native plant garden in PNW

**View the plant collection:** https://coreycaitlin.github.io/mf-garden/

## Plant Index

<!-- PLANT_INDEX_START -->
| Common Name | Scientific Name | Type |
|-------------|-----------------|------|
| [Baldhip Rose](plants/baldhip-rose.md) | *Rosa gymnocarpa* | Shrub |
| [Big Leaf Lupine](plants/big-leaf-lupine.md) | *Lupinus polyphyllus* | Perennial |
| [Blue Elderberry](plants/blue-elderberry.md) | *Sambucus cerulea* | Shrub |
| [Cascade Penstemon](plants/cascade-penstemon.md) | *Penstemon serrulatus* | Perennial |
| [Common Snowberry](plants/snowberry.md) | *Symphoricarpos albus* | Shrub |
| [Deer Fern](plants/deer-fern.md) | *Blechnum spicant* | Fern |
| [Douglas Fir](plants/douglas-fir.md) | *Pseudotsuga menziesii* | Tree |
| [Douglas Iris](plants/douglas-iris.md) | *Iris douglasiana* | Perennial |
| [Dr. Hurd Manzanita](plants/dr-hurd-manzanita.md) | *Arctostaphylos manzanita 'Dr. Hurd'* | Shrub |
| [Dwarf Snowberry](plants/dwarf-snowberry.md) | *Symphoricarpos mollis* | Shrub |
| [Evergreen Huckleberry](plants/evergreen-huckleberry.md) | *Vaccinium ovatum* | Shrub |
| [False Solomon's Seal](plants/false-solomons-seal.md) | *Maianthemum racemosum* | Perennial |
| [Flowering Currant](plants/flowering-currant.md) | *Ribes sanguineum* | Shrub |
| [Foamflower](plants/foamflower.md) | *Tiarella trifoliata* | Perennial |
| [Foothill Sedge](plants/foothill-sedge.md) | *Carex tumulicola* | Grass |
| [Fringecup](plants/fringecup.md) | *Tellima grandiflora* | Perennial |
| [Heath Aster](plants/heath-aster.md) | *Symphyotrichum ericoides* | Perennial |
| [Idaho Fescue](plants/idaho-fescue.md) | *Festuca idahoensis* | Grass |
| [Inside-out Flower](plants/inside-out-flower.md) | *Vancouveria hexandra* | Perennial |
| [Manzanita](plants/manzanita.md) | *Arctostaphylos columbiana* | Shrub |
| [Meadow Checkermallow](plants/meadow-checkermallow.md) | *Sidalcea campestris* | Perennial |
| [Oak Fern](plants/oak-fern.md) | *Gymnocarpium dryopteris* | Fern |
| [Ocean Spray](plants/ocean-spray.md) | *Holodiscus discolor* | Shrub |
| [Oregon Boxwood](plants/oregon-boxwood.md) | *Paxistima myrsinites* | Shrub |
| [Oregon Checkermallow](plants/oregon-checkermallow.md) | *Sidalcea oregana* | Perennial |
| [Oregon Stonecrop](plants/oregon-stonecrop.md) | *Sedum oreganum* | Perennial |
| [Osoberry](plants/osoberry.md) | *Oemleria cerasiformis* | Shrub |
| [Pacific Madrone](plants/pacific-madrone.md) | *Arbutus menziesii* | Tree |
| [Pacific Wax Myrtle](plants/pacific-wax-myrtle.md) | *Myrica californica* | Shrub |
| [Piggyback Plant](plants/piggyback-plant.md) | *Tolmiea menziesii* | Perennial |
| [Red Elderberry](plants/red-elderberry.md) | *Sambucus racemosa* | Shrub |
| [Red Huckleberry](plants/red-huckleberry.md) | *Vaccinium parvifolium* | Shrub |
| [Redwood Sorrel](plants/redwood-sorrel.md) | *Oxalis oregana* | Perennial |
| [Salal](plants/salal.md) | *Gaultheria shallon* | Shrub |
| [Seaside Daisy](plants/seaside-daisy.md) | *Erigeron glaucus* | Perennial |
| [Stinging Nettle](plants/stinging-nettle.md) | *Urtica dioica* | Perennial |
| [Sword Fern](plants/sword-fern.md) | *Polystichum munitum* | Fern |
| [Tall Oregon Grape](plants/oregon-grape.md) | *Mahonia aquifolium* | Shrub |
| [Tufted Hair Grass](plants/tufted-hair-grass.md) | *Deschampsia cespitosa* | Grass |
| [Vanilla Leaf](plants/vanilla-leaf.md) | *Achlys triphylla* | Perennial |
| [Vine Maple](plants/vine-maple.md) | *Acer circinatum* | Tree |
| [Western Bleeding Heart](plants/western-bleeding-heart.md) | *Dicentra formosa* | Perennial |
| [Western Serviceberry](plants/serviceberry.md) | *Amelanchier alnifolia* | Shrub |
| [Western Trillium](plants/western-trillium.md) | *Trillium ovatum* | Perennial |
| [White Yarrow](plants/white-yarrow.md) | *Achillea millefolium* | Perennial |
| [Wild Ginger](plants/wild-ginger.md) | *Asarum caudatum* | Perennial |
<!-- PLANT_INDEX_END -->

## Adding a New Plant

1. **Create the plant file** using the template:
   ```bash
   cp templates/plant-template.md plants/your-plant-name.md
   ```

2. **Fill in the basics** - at minimum, add the `common_name` and `scientific_name` in the frontmatter, and set the `garden_area` (e.g., `["front"]`, `["back"]`, or `["front", "back"]`).

3. **Fetch a photo** from Wikimedia Commons:
   ```bash
   python scripts/fetch-plant-photo.py your-plant-name
   ```
   This searches by scientific name, shows available CC-licensed images, and lets you pick one. It downloads the image and updates the photo credit automatically.

4. **Regenerate the plant data** for the webapp:
   ```bash
   python scripts/generate-plant-data.py
   ```

### Other Useful Commands

```bash
# List plants that are missing photos
python scripts/fetch-plant-photo.py --missing

# Fetch photos for all plants missing them (interactive)
python scripts/fetch-plant-photo.py --missing --fetch
```
