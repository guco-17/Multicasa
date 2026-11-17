const houseSearch = document.querySelector('[data-house-search]');

if (houseSearch) {
    const form = houseSearch.closest('form');
    const input = houseSearch.querySelector('input[type="search"]');
    const selectedHouse = houseSearch.querySelector('input[type="hidden"]');
    const results = houseSearch.querySelector('[data-house-search-results]');
    const status = houseSearch.querySelector('[data-house-search-status]');
    let debounceTimer;
    let searchRequest;

    const closeResults = () => {
        results.hidden = true;
        results.replaceChildren();
        input.setAttribute('aria-expanded', 'false');
    };

    const selectHouse = (house) => {
        selectedHouse.value = house.id;
        input.value = house.label;
        input.setCustomValidity('');
        status.textContent = `Propiedad seleccionada: ${house.label}`;
        closeResults();
    };

    const showResults = (houses) => {
        results.replaceChildren();
        if (houses.length === 0) {
            closeResults();
            status.textContent = 'No encontramos propiedades con ese nombre o dirección.';
            return;
        }

        houses.forEach((house) => {
            const option = document.createElement('button');
            const title = document.createElement('strong');
            const address = document.createElement('span');

            option.type = 'button';
            option.className = 'house-search-option';
            option.setAttribute('role', 'option');
            title.textContent = house.title;
            address.textContent = `${house.address}, ${house.city}`;
            option.append(title, address);
            option.addEventListener('click', () => selectHouse(house));
            results.append(option);
        });

        results.hidden = false;
        input.setAttribute('aria-expanded', 'true');
        status.textContent = `${houses.length} propiedades encontradas.`;
    };

    input.addEventListener('input', () => {
        selectedHouse.value = '';
        input.setCustomValidity('');
        status.textContent = '';
        window.clearTimeout(debounceTimer);
        if (searchRequest) {
            searchRequest.abort();
        }

        const query = input.value.trim();
        if (query.length < 2) {
            closeResults();
            if (query.length > 0) {
                status.textContent = 'Escribe al menos dos caracteres para buscar.';
            }
            return;
        }

        debounceTimer = window.setTimeout(async () => {
            searchRequest = new AbortController();
            const request = searchRequest;
            const url = new URL(houseSearch.dataset.searchUrl, window.location.origin);
            url.searchParams.set('q', query);

            try {
                const response = await fetch(url, {
                    headers: {'Accept': 'application/json'},
                    signal: request.signal,
                });
                if (!response.ok) {
                    throw new Error(`Property search failed with status ${response.status}`);
                }
                const data = await response.json();
                if (searchRequest === request) {
                    showResults(data.results);
                }
            } catch (error) {
                if (error.name === 'AbortError') {
                    return;
                }
                closeResults();
                status.textContent = 'No se pudo buscar. Intenta de nuevo.';
            }
        }, 250);
    });

    input.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowDown') {
            const firstOption = results.querySelector('[role="option"]');
            if (firstOption) {
                event.preventDefault();
                firstOption.focus();
            }
        } else if (event.key === 'Escape') {
            closeResults();
        }
    });

    form.addEventListener('submit', (event) => {
        if (input.value.trim() && !selectedHouse.value) {
            input.setCustomValidity('Selecciona una propiedad de los resultados de búsqueda.');
            input.reportValidity();
            event.preventDefault();
        } else {
            input.setCustomValidity('');
        }
    });

    document.addEventListener('click', (event) => {
        if (!houseSearch.contains(event.target)) {
            closeResults();
        }
    });
}
