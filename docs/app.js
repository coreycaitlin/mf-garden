/**
 * MF Garden - Plant Collection Webapp
 * Displays plant data in filterable cards
 */

// State
let plants = [];
let filteredPlants = [];

// DOM Elements
const plantGrid = document.getElementById('plant-grid');
const statusFilter = document.getElementById('status-filter');
const areaFilter = document.getElementById('area-filter');
const plantCount = document.getElementById('plant-count');

/**
 * Fetch plant data from JSON file
 */
async function fetchPlants() {
    try {
        const response = await fetch('plants.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        plants = await response.json();
        filteredPlants = [...plants];
        renderPlants();
    } catch (error) {
        console.error('Error fetching plants:', error);
        plantGrid.innerHTML = `
            <div class="no-results">
                <p>Error loading plant data.</p>
                <p>Make sure to run the generate script first.</p>
            </div>
        `;
    }
}

/**
 * Create HTML for a single plant card
 */
function createPlantCard(plant) {
    const card = document.createElement('article');
    card.className = 'plant-card';

    // Build image path - images are in parent directory from webapp
    const imagePath = plant.image ? `../${plant.image}` : '';

    // Determine badge classes
    const statusClass = plant.status ? plant.status.toLowerCase() : '';
    const areaClass = plant.garden_area ? plant.garden_area.toLowerCase() : '';

    card.innerHTML = `
        ${imagePath ? `<img src="${imagePath}" alt="${plant.common_name}" class="plant-card-image" loading="lazy">` : '<div class="plant-card-image"></div>'}
        <div class="plant-card-content">
            <h2 class="plant-card-name">${plant.common_name}</h2>
            <p class="plant-card-scientific">${plant.scientific_name}</p>
            <div class="plant-card-badges">
                ${plant.plant_type ? `<span class="badge badge-type">${plant.plant_type}</span>` : ''}
                ${plant.status ? `<span class="badge badge-status ${statusClass}">${plant.status}</span>` : ''}
                ${plant.garden_area ? `<span class="badge badge-area ${areaClass}">${plant.garden_area}</span>` : ''}
            </div>
        </div>
    `;

    return card;
}

/**
 * Render plant cards to the grid
 */
function renderPlants() {
    plantGrid.innerHTML = '';

    if (filteredPlants.length === 0) {
        plantGrid.innerHTML = '<div class="no-results">No plants match the selected filters.</div>';
        plantCount.textContent = '0 plants';
        return;
    }

    filteredPlants.forEach(plant => {
        plantGrid.appendChild(createPlantCard(plant));
    });

    // Update count
    const count = filteredPlants.length;
    plantCount.textContent = `${count} plant${count !== 1 ? 's' : ''}`;
}

/**
 * Apply filters to plant data
 */
function applyFilters() {
    const statusValue = statusFilter.value;
    const areaValue = areaFilter.value;

    filteredPlants = plants.filter(plant => {
        // Status filter
        if (statusValue !== 'all') {
            if (statusValue === 'none') {
                // Show plants with no status or empty status
                if (plant.status && plant.status !== 'none') {
                    return false;
                }
            } else if (plant.status?.toLowerCase() !== statusValue.toLowerCase()) {
                return false;
            }
        }

        // Area filter
        if (areaValue !== 'all') {
            if (areaValue === 'unassigned') {
                // Show plants with no garden_area
                if (plant.garden_area && plant.garden_area !== '') {
                    return false;
                }
            } else if (plant.garden_area?.toLowerCase() !== areaValue.toLowerCase()) {
                return false;
            }
        }

        return true;
    });

    renderPlants();
}

/**
 * Initialize the app
 */
function init() {
    // Set up event listeners
    statusFilter.addEventListener('change', applyFilters);
    areaFilter.addEventListener('change', applyFilters);

    // Fetch and display plants
    fetchPlants();
}

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', init);
