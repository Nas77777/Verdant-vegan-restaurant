const monthYearElement = document.getElementById('monthYear');
const datesElement = document.getElementById('dates');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

let currentDate = new Date();
let selectedDate = null;

const updateCalendar = () => {
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth();

    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const totalDays = lastDay.getDate();
    const firstDayIndex = firstDay.getDay();
    const lastDayIndex = lastDay.getDay();

    const monthYearString = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });
    monthYearElement.innerText = monthYearString;

    let datesHTML = '';

    for (let i = firstDayIndex; i > 0; i--) {
        const prevDate = new Date(currentYear, currentMonth, 0 - i + 1);
        datesHTML += `<div class="date inactive">${prevDate.getDate()}</div>`;
    }

    for (let i = 1; i <= totalDays; i++) {
        const date = new Date(currentYear, currentMonth, i);
        const isSelected = selectedDate && date.toDateString() === selectedDate.toDateString();
        const selectedClass = isSelected ? 'selected' : '';
        datesHTML += `<div class="date ${selectedClass}" data-date="${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}">${i}</div>`;
    }

    for (let i = 1; i <= 7 - lastDayIndex; i++) {
        const nextDate = new Date(currentYear, currentMonth + 1, i);
        datesHTML += `<div class="date inactive">${nextDate.getDate()}</div>`;
    }

    datesElement.innerHTML = datesHTML;

    const dateElements = document.querySelectorAll('.date:not(.inactive)');
    dateElements.forEach(dateElement => {
        dateElement.addEventListener('click', handleDateSelection);
    });
};

const handleDateSelection = (event) => {
    const dateString = event.target.getAttribute('data-date');
    selectedDate = new Date(dateString + 'T00:00:00');

    console.log('Selected Date:', selectedDate);

    updateCalendar();

    const formattedDate = formatDate(selectedDate);
    sendDateToBackend(formattedDate);
    
    // Add this line to fetch available times when a date is selected
    fetchAvailableTimes(formattedDate);
};

const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`; // YYYY-MM-DD format
};

const sendDateToBackend = (formattedDate) => {
    fetch('/select-time', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ date: formattedDate })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

prevBtn.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    updateCalendar();
});

nextBtn.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    updateCalendar();
});

updateCalendar();


function toggleCheckbox(checkedCheckbox) {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        if (checkbox !== checkedCheckbox) {
            checkbox.checked = false; // Uncheck other checkboxes
        }
    });
    console.log("Checked checkbox:", checkedCheckbox.name);
}

document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                toggleCheckbox(this); // Uncheck others only if this is checked
            }
        });
    });
});

function fetchAvailableTimes(selectedDate) {
    console.log("FULL DEBUG - Fetching available times for date:", selectedDate);

    fetch(`/get-available-times?date=${selectedDate}`)
    .then(response => {
        console.log("FULL DEBUG - Response status:", response.status);
        console.log("FULL DEBUG - Response headers:", response.headers);
        return response.json();
    })
    .then(data => {
        console.log("FULL DEBUG - Received Data:", data);
        
        let timesContainer = document.querySelector('.timesContainer');
        if (!timesContainer) {
            console.error("FULL DEBUG - Times container not found");
            return;
        }
        
        // Clear previous times
        timesContainer.innerHTML = "";

        // Check if times exist and is an array
        if (!data.times || !Array.isArray(data.times) || data.times.length === 0) {
            console.warn("FULL DEBUG - No available times for this date");
            timesContainer.innerHTML = "<p>No available times for this date.</p>";
            return;
        }

        // Log and create time buttons
        data.times.forEach((time, index) => {
            console.log(`FULL DEBUG - Time slot ${index + 1}:`, time);
            
            let button = document.createElement("button");
            
            // Extract start_time from the time object if it exists
            let displayTime = typeof time === 'object' && time.start_time 
                ? time.start_time
                : (typeof time === 'object' ? JSON.stringify(time) : time);
            
            button.innerText = displayTime;
            button.classList.add("time-button");
            
            button.onclick = function() { 
                // Remove selected class from all time buttons
                document.querySelectorAll('.time-button').forEach(btn => {
                    btn.classList.remove('selected');
                });
                
                // Add selected class to current button
                button.classList.add('selected');
                
                // Select the time
                selectTime(selectedDate, displayTime);
            };
            
            timesContainer.appendChild(button);
        });
    })
    .catch(error => {
        console.error('FULL DEBUG - Error fetching available times:', error);
        let timesContainer = document.querySelector('.timesContainer');
        if (timesContainer) {
            timesContainer.innerHTML = `<p>Error fetching times: ${error.message}</p>`;
        }
    });
}

function selectTime(date, time) {
    console.log("FULL DEBUG - Selecting time - Date:", date, "Time:", time);
    
    fetch('/select-time', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 
            date: date, 
            time: time 
        })
    })
    .then(response => {
        console.log("FULL DEBUG - Select time response status:", response.status);
        return response.json();
    })
    .then(data => {
        console.log("FULL DEBUG - Select time response:", data);
    })
    .catch(error => console.error('FULL DEBUG - Error selecting time:', error));
}
