document.addEventListener('DOMContentLoaded', () => {
    const countryInput = document.getElementById('country-input');
    const stateInput = document.getElementById('state-input');
    const cityInput = document.getElementById('city-input');
    const predictBtn = document.getElementById('predict-btn');
    const resultsSection = document.getElementById('results');

    let currentCountry = "";
    let currentState = "";
    let currentCityId = "";

    function setupCustomSelect(inputEl, containerId, data, textKey, valueKey, onSelect) {
        const container = document.getElementById(containerId);
        
        const renderOptions = (filter = "") => {
            container.innerHTML = "";
            let count = 0;
            for (let item of data) {
                const text = item[textKey] || item[valueKey];
                if (text.toLowerCase().includes(filter.toLowerCase())) {
                    const div = document.createElement('div');
                    div.className = 'option-item';
                    div.textContent = text;
                    div.addEventListener('click', () => {
                        inputEl.value = text;
                        inputEl.dataset.value = item[valueKey];
                        container.classList.remove('active');
                        onSelect(item[valueKey]);
                    });
                    container.appendChild(div);
                    count++;
                    if (count > 200) break;
                }
            }
            if (count === 0) {
                 const div = document.createElement('div');
                 div.className = 'option-item';
                 div.textContent = "No results found";
                 container.appendChild(div);
            }
        };
        
        const newClone = inputEl.cloneNode(true);
        inputEl.parentNode.replaceChild(newClone, inputEl);
        inputEl = newClone;
        
        inputEl.addEventListener('focus', () => {
            if(!inputEl.disabled) {
                renderOptions(inputEl.value);
                container.classList.add('active');
            }
        });
        
        inputEl.addEventListener('input', (e) => {
            renderOptions(e.target.value);
            container.classList.add('active');
            inputEl.dataset.value = ""; 
            if(inputEl.id === 'city-input') predictBtn.disabled = true;
        });
        
        document.addEventListener('click', (e) => {
            if (!inputEl.contains(e.target) && !container.contains(e.target)) {
                container.classList.remove('active');
            }
        });
    }

    // Number counting animation
    function animateValue(id, start, end, duration) {
        const obj = document.getElementById(id);
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            // Ease out quad
            const easeOut = progress * (2 - progress);
            obj.innerHTML = (start + easeOut * (end - start)).toFixed(1);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                obj.innerHTML = end;
            }
        };
        window.requestAnimationFrame(step);
    }

    // Load countries
    fetch('/api/countries')
        .then(res => res.json())
        .then(data => {
            if(data.length === 0) {
                alert("Database is empty. Please run setup_project.py first.");
                return;
            }
            setupCustomSelect(document.getElementById('country-input'), 'country-options', data, 'country_name', 'country_code', (val) => {
                currentCountry = val;
                
                const sInput = document.getElementById('state-input');
                const cInput = document.getElementById('city-input');
                const btn = document.getElementById('predict-btn');
                
                sInput.value = "";
                sInput.disabled = true;
                cInput.value = "";
                cInput.disabled = true;
                btn.disabled = true;

                sInput.placeholder = "Loading states...";
                fetch(`/api/states/${currentCountry}`)
                    .then(res => res.json())
                    .then(stateData => {
                        sInput.placeholder = "Search State/Province...";
                        sInput.disabled = false;
                        setupCustomSelect(sInput, 'state-options', stateData, 'state_name', 'admin1_code', (stateVal) => {
                            currentState = stateVal;
                            
                            cInput.value = "";
                            cInput.disabled = true;
                            btn.disabled = true;
                            
                            cInput.placeholder = "Loading cities...";
                            fetch(`/api/cities/${currentCountry}/${currentState}`)
                                .then(res => res.json())
                                .then(cityData => {
                                    cInput.placeholder = "Search City...";
                                    cInput.disabled = false;
                                    setupCustomSelect(cInput, 'city-options', cityData, 'asciiname', 'geonameid', (cityVal) => {
                                        currentCityId = cityVal;
                                        btn.disabled = false;
                                    });
                                });
                        });
                    });
            });
        });

    document.getElementById('predict-btn').addEventListener('click', (e) => {
        e.preventDefault();
        const btn = document.getElementById('predict-btn');
        const geonameid = currentCityId;
        if(!geonameid) return;

        btn.textContent = "Processing AI...";
        btn.disabled = true;

        fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ geonameid })
        })
        .then(res => res.json())
        .then(data => {
            if(data.error) {
                alert(data.error);
                btn.textContent = "Predict Climate";
                btn.disabled = false;
                return;
            }
            
            const iconContainer = document.getElementById('weather-icon-container');
            const w = data.weather.toLowerCase();
            let svgCode = '';
            if(w.includes('sunny') || w.includes('clear')) {
                svgCode = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
            } else if(w.includes('rain')) {
                svgCode = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16" y1="13" x2="16" y2="21"></line><line x1="8" y1="13" x2="8" y2="21"></line><line x1="12" y1="15" x2="12" y2="23"></line><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"></path></svg>';
            } else if(w.includes('cloud')) {
                svgCode = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path></svg>';
            } else {
                svgCode = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
            }
            iconContainer.innerHTML = svgCode;

            document.getElementById('prediction-date').textContent = `Forecast generated for: ${data.prediction_date}`;
            document.getElementById('location-title').textContent = `${data.city}, ${data.country}`;
            
            animateValue('temperature', 0, parseFloat(data.temperature), 1500);
            
            document.getElementById('weather-desc').textContent = data.weather;
            document.getElementById('feels-like').textContent = `${data.feels_like}°C`;
            document.getElementById('humidity').textContent = `${data.humidity}%`;
            document.getElementById('wind').textContent = `${data.wind_speed} km/h`;
            document.getElementById('pressure').textContent = `${data.pressure} hPa`;

            document.getElementById('uv-index').textContent = data.uv_index;
            document.getElementById('aqi').textContent = data.aqi;


            // Render Hourly Forecast
            const hourlyGrid = document.getElementById('hourly-grid');
            hourlyGrid.innerHTML = '';
            if(data.hourly_forecast && data.hourly_forecast.length > 0) {
                data.hourly_forecast.forEach(f => {
                    const dateObj = new Date(f.prediction_date);
                    const hourStr = dateObj.getHours().toString().padStart(2, '0') + ":00";
                    
                    const w = f.weather.toLowerCase();
                    let svgIcon = '';
                    if(w.includes('sunny') || w.includes('clear')) {
                        svgIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
                    } else if(w.includes('rain')) {
                        svgIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16" y1="13" x2="16" y2="21"></line><line x1="8" y1="13" x2="8" y2="21"></line><line x1="12" y1="15" x2="12" y2="23"></line><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"></path></svg>';
                    } else if(w.includes('cloud')) {
                        svgIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path></svg>';
                    } else {
                        svgIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
                    }
                    
                    const card = document.createElement('div');
                    card.className = 'hourly-card';
                    card.innerHTML = `
                        <div class="hourly-time">${hourStr}</div>
                        <div class="hourly-icon">${svgIcon}</div>
                        <div class="hourly-temp">${f.temperature}°C</div>
                    `;
                    hourlyGrid.appendChild(card);
                });
            }

            // Render forecast
            const forecastGrid = document.getElementById('forecast-grid');
            forecastGrid.innerHTML = '';
            
            if(data.forecast && data.forecast.length > 0) {
                data.forecast.forEach(f => {
                    const dateObj = new Date(f.prediction_date);
                    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                    const dayName = days[dateObj.getDay()];
                    
                    const w = f.weather.toLowerCase();
                    let svgIcon = '';
                    if(w.includes('sunny') || w.includes('clear')) {
                        svgIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
                    } else if(w.includes('rain')) {
                        svgIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16" y1="13" x2="16" y2="21"></line><line x1="8" y1="13" x2="8" y2="21"></line><line x1="12" y1="15" x2="12" y2="23"></line><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"></path></svg>';
                    } else if(w.includes('cloud')) {
                        svgIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path></svg>';
                    } else {
                        svgIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
                    }
                    
                    const card = document.createElement('div');
                    card.className = 'forecast-card';
                    card.innerHTML = `
                        <div class="forecast-date">${dayName}</div>
                        <div class="forecast-icon">${svgIcon}</div>
                        <div class="forecast-temp">${f.temperature}°C</div>
                    `;
                    forecastGrid.appendChild(card);
                });
            }

            document.getElementById('results').classList.remove('hidden');
            btn.textContent = "Predict Climate";
            btn.disabled = false;
        })
        .catch(err => {
            console.error(err);
            alert("Error predicting climate");
            btn.textContent = "Predict Climate";
            btn.disabled = false;
        });
    });
});
