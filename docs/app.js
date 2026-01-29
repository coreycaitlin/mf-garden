/**
 * MF Garden - Plant Collection Webapp
 * Displays plant data in a filterable, sortable table
 */

// State
let plants = [];
let filteredPlants = [];
let sortColumn = 'common_name';
let sortDirection = 'asc';

// DOM Elements
const plantTbody = document.getElementById('plant-tbody');
const statusFilter = document.getElementById('status-filter');
const areaFilter = document.getElementById('area-filter');
const plantCount = document.getElementById('plant-count');
const tableHeaders = document.querySelectorAll('#plant-table th[data-sort]');

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
        sortAndRender();
    } catch (error) {
        console.error('Error fetching plants:', error);
        plantTbody.innerHTML = `
            <tr>
                <td colspan="6" class="no-results">
                    Error loading plant data. Make sure to run the generate script first.
                </td>
            </tr>
        `;
    }
}

/**
 * Create HTML for a single table row
 */
function createPlantRow(plant) {
    return `
        <tr data-slug="${plant.slug}">
            <td>${plant.common_name}</td>
            <td>${plant.scientific_name}</td>
            <td>${plant.plant_type || ''}</td>
            <td>${plant.sun_requirements || ''}</td>
            <td>${plant.water_needs || ''}</td>
            <td>${plant.soil_type || ''}</td>
        </tr>
    `;
}

/**
 * Get plant by slug
 */
function getPlantBySlug(slug) {
    return plants.find(p => p.slug === slug);
}

/**
 * Render plant rows to the table
 */
function renderPlants() {
    if (filteredPlants.length === 0) {
        plantTbody.innerHTML = `
            <tr>
                <td colspan="6" class="no-results">No plants match the selected filters.</td>
            </tr>
        `;
        plantCount.textContent = '0 plants';
        return;
    }

    plantTbody.innerHTML = filteredPlants.map(createPlantRow).join('');

    // Add click handlers to rows
    plantTbody.querySelectorAll('tr[data-slug]').forEach(row => {
        row.addEventListener('click', () => {
            const plant = getPlantBySlug(row.dataset.slug);
            if (plant) {
                showLightbox(plant);
            }
        });
    });

    const count = filteredPlants.length;
    plantCount.textContent = `${count} plant${count !== 1 ? 's' : ''}`;
}

/**
 * Sort plants by the current sort column and direction
 */
function sortPlants() {
    filteredPlants.sort((a, b) => {
        let valA = (a[sortColumn] || '').toLowerCase();
        let valB = (b[sortColumn] || '').toLowerCase();

        if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
        if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
        return 0;
    });
}

/**
 * Update sort header visual indicators
 */
function updateSortHeaders() {
    tableHeaders.forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
        if (th.dataset.sort === sortColumn) {
            th.classList.add(sortDirection === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }
    });
}

/**
 * Sort and render plants
 */
function sortAndRender() {
    sortPlants();
    updateSortHeaders();
    renderPlants();
}

/**
 * Handle sort header click
 */
function handleSort(e) {
    const column = e.currentTarget.dataset.sort;

    if (column === sortColumn) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }

    sortAndRender();
}

/**
 * Apply filters to plant data
 */
function applyFilters() {
    const statusValue = statusFilter.value;
    const areaValue = areaFilter.value;

    filteredPlants = plants.filter(plant => {
        if (statusValue !== 'all') {
            if (statusValue === 'none') {
                if (plant.status && plant.status !== 'none') {
                    return false;
                }
            } else if (plant.status?.toLowerCase() !== statusValue.toLowerCase()) {
                return false;
            }
        }

        if (areaValue !== 'all') {
            if (areaValue === 'unassigned') {
                if (plant.garden_area && plant.garden_area !== '') {
                    return false;
                }
            } else if (plant.garden_area?.toLowerCase() !== areaValue.toLowerCase()) {
                return false;
            }
        }

        return true;
    });

    sortAndRender();
}

/**
 * Initialize the app
 */
function init() {
    statusFilter.addEventListener('change', applyFilters);
    areaFilter.addEventListener('change', applyFilters);

    tableHeaders.forEach(th => {
        th.addEventListener('click', handleSort);
    });

    fetchPlants();
}

/**
 * Show plant image in lightbox
 */
function showLightbox(plant) {
    const lightbox = document.getElementById('lightbox');
    const title = document.getElementById('lightbox-title');
    const image = document.getElementById('lightbox-image');
    const caption = document.getElementById('lightbox-caption');

    title.textContent = plant.common_name;
    image.src = plant.image || '';
    image.alt = plant.common_name;
    caption.textContent = plant.photo_credit || '';

    lightbox.classList.add('active');
}

/**
 * Hide lightbox
 */
function hideLightbox() {
    document.getElementById('lightbox').classList.remove('active');
}

/**
 * Set up lightbox event listeners
 */
function initLightbox() {
    const lightbox = document.getElementById('lightbox');
    const closeBtn = document.querySelector('.lightbox-close');

    closeBtn.addEventListener('click', hideLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            hideLightbox();
        }
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hideLightbox();
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    init();
    initLightbox();
});
