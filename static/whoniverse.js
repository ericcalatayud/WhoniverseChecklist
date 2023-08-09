document.getElementById("column1").addEventListener("click", function(e) {
    handleButtonClick('column2', e, id => `whoniverse-checklist.onrender.com/api/options/${id}`);
});

document.getElementById("column2").addEventListener("click", function(e) {
    handleButtonClick('column3', e, id => `whoniverse-checklist.onrender.com/api/seasons/${id}`);
});

document.getElementById("column3").addEventListener("click", function(e) {
    handleButtonClick('column4', e, id => `whoniverse-checklist.onrender.com/api/episodes/${id}`);
});

document.getElementById("column4").addEventListener("click", async function(e) {
    if (e.target.tagName.toLowerCase() === "button") {
        const id_episode = e.target.dataset.id;
        let url = 'whoniverse-checklist.onrender.com/api/episode_watched';
        if (e.target.classList.contains('episode-seen')) {
            e.target.classList.remove('episode-seen');
            url = 'whoniverse-checklist.onrender.com/api/episode_unwatched';
        } else {
            e.target.classList.add('episode-seen');
        }
        try {
            await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({ id_episode })
            });
        } catch (error) {
            console.error('Error in marking/unmarking episode as watched:', error);
        }
    }
});

document.querySelectorAll('.column button').forEach(button => {
    button.addEventListener('click', function() {
        // Eliminar la clase 'selected' de todos los botones en la misma columna
        this.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('selected'));

        // Agregar la clase 'selected' al botón actual
        this.classList.add('selected');
    });
});

function handleButtonClick(columnId, e, nextUrl) {
    if (e.target.tagName.toLowerCase() === "button") {
        // Verificar si el usuario está autenticado
        checkLoginStatus().then(status => {
            if (status === 'authenticated') {
                // El usuario está autenticado, cargar las opciones
                loadOptions(columnId, nextUrl(e.target.dataset.id));
                // Clear next columns
                for (let i = parseInt(columnId.slice(-1)) + 1; i <= 4; i++) {
                    document.getElementById(`column${i}`).innerHTML = '';
                }
            } else {
                // El usuario no está autenticado, redirigir a la página de inicio de sesión
                window.location.href = 'whoniverse-checklist.onrender.com/login';
            }
        }).catch(error => {
            console.error('Error in checking login status:', error);
        });
    }
}

async function checkLoginStatus() {
    const response = await fetch('whoniverse-checklist.onrender.com/check_login', {
        credentials: 'include'
    });
    const data = await response.json();
    return data.status;
}

async function getWatchedEpisodes() {
    try {
        const response = await fetch('https://whoniverse-checklist.onrender.com/api/episodes_watched', {
            credentials: 'include'
        });
        return await response.json();
    } catch (error) {
        console.error('Error in getting watched episodes:', error);
        return [];
    }
}

async function loadOptions(columnId, url) {
    var column = document.getElementById(columnId);
    column.innerHTML = "";

    try {
        var response = await fetch(url);
        var data = await response.json();

        if (columnId === 'column4') {
            const watchedEpisodes = await getWatchedEpisodes();
            data.forEach(function(item) {
                var button = document.createElement("button");
                button.textContent = item.episode;
                button.dataset.id = item.id_episode;
                if (watchedEpisodes.includes(item.id_episode)) {
                    button.classList.add('episode-seen');
                }
                column.appendChild(button);
            });
        } else {
            data.forEach(function(item) {
                var button = document.createElement("button");
                if (columnId === 'column2') {
                    button.textContent = item.option;
                    button.dataset.id = item.id_option;
                } else if (columnId === 'column3') {
                    button.textContent = item.season;
                    button.dataset.id = item.id_season;
                } else if (columnId === 'column4') {
                    button.textContent = item.episode;
                    button.dataset.id = item.id_episode;
                }
                column.appendChild(button);
                addSelectedHandler(button); // Agrega el controlador de eventos aquí
            });
        }
    } catch (error) {
        console.error(`There was an error in loadOptions for ${columnId}: `, error);
    }
}

function addSelectedHandler(button) {
    button.addEventListener('click', function() {
        // Eliminar la clase 'selected' de todos los botones en la misma columna
        this.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('selected'));

        // Agregar la clase 'selected' al botón actual
        this.classList.add('selected');
    });
}
