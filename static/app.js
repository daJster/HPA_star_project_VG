
// Names of the games
// JavaScript to handle toggle state
const toggleButton = document.getElementById('toggleButton');
const gameNamesDict  = {"Berlin": "Berlin", "Liverpool": "Liverpool", "Paris":"Paris", "Tokyo":"Tokyo", "Rome":"Rome", "France":"France", "Russia":"Russia", 'League Of Legends': 'lol', 'GTA V': 'GTAV', 'Test': 'test', }

toggleButton.addEventListener('change', function() {
    if (this.checked) {
        console.log('On');
    } else {
        console.log('Off');
    }
});

// JavaScript to handle slider value
const slider = document.getElementById('slider');
const lastSliderValue = document.getElementById('lastSliderValue');

slider.addEventListener('input', function() {
    const value = this.value;
    // console.log('Slider Value:', value);
    lastSliderValue.textContent = value;
});


let startPoint = null;
let endPoint = null;
let clickCounter = 0;

const imageElement = document.getElementById('image-element');
const imageContainer = document.querySelector('.image-container');
const line = document.getElementById('line');

// Set the initial image width and height // SEND WITH FLASK
var originalImageWidth = imageElement.width; 
var originalImageHeight = imageElement.height;

// Calculate the scaling factor
const getScaleFactor = () => imageElement.width / originalImageWidth;


async function fetchOptimalPath(startPoint, endPoint) {
    try {
        const response = await fetch('/get_optimal_path', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                start_point: startPoint,
                end_point: endPoint,
            }),
        });

        if (!response.ok) {
            const errorMessage = await response.text();
            // Handle the error message, for example, display it on the website
            console.error('Error:', errorMessage);
            return;
        }

        const result = await response.json();
        // Handle the result, for example, update the UI with the optimal path
        return result;
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Add a click event listener to the image container
imageElement.addEventListener('click', function(event) {
    // Get the coordinates relative to the image container
    const x = event.offsetX;
    const y = event.offsetY;

    const scaleFactor = getScaleFactor();
    const scaledX = Math.floor(x / scaleFactor);
    const scaledY = Math.floor(y / scaleFactor);

    // Log or use the scaled coordinates as needed
    // console.log(`Original Coordinates: (${x}, ${y})`);
    // console.log(`Scaled Coordinates: (${scaledX}, ${scaledY})`);

    if (clickCounter === 0) {
        startPoint = {x, y};
        setPoint('startPoint', startPoint, 'blue-point');
        clickCounter++;
    } else if (clickCounter === 1){
        endPoint = {x, y};
        setPoint('endPoint', endPoint, 'red-point');
        clickCounter++;
        promise = fetchOptimalPath(startPoint, endPoint); 
        promise.then(result => {
            const path = result.path;
            drawLine(path);
        }).catch(error => {
            console.error('Error:', error);
        }); 
    } else {
        clearPath();
        clickCounter = 0;
        startPoint = {x, y};
        setPoint('startPoint', startPoint, 'blue-point');
        clickCounter++;
    }
});

// Generate random coords for testing
function generateRandomLine(numPoints, startPoint) {
    const coords = [];

    let currentX = startPoint.x;
    let currentY = startPoint.y;

    for (let i = 0; i < numPoints; i++) {
        coords.push({ x: Math.floor(currentX), y: Math.floor(currentY) });

        // Adjust the current coordinates randomly
        currentX += Math.random() - Math.floor(Math.random());  
        currentY += Math.random() - Math.floor(Math.random());
    }

    return coords;
}

function drawLine(coords, size=3) {
    coords.forEach((coord, i) => {
        // console.log(coord);
    
        if (i < coords.length - 1) {
            const start = coord;
            const end = coords[i + 1];
    
            // Calculate distance and angle between points
            const distance = Math.hypot(end.x - start.x, end.y - start.y);
            const angle = Math.atan2(end.y - start.y, end.x - start.x);
    
            // Create a line element
            const newLine = document.createElement('div');
            newLine.className = 'line';
            newLine.style.width = `${distance}px`;
            newLine.style.transform = `rotate(${angle}rad)`;
            newLine.style.height = `${size}px`;
            newLine.style.left = `${start.x}px`;
            newLine.style.top = `${start.y}px`;
            newLine.style.visibility = 'visible';
            // Append the line to the container
            imageContainer.appendChild(newLine); // Change this to your actual container element
        }
    });
}

// Function to translate website coordinates to original coordinates
function websiteToOriginalCoords(websiteCoords, scaleFactor) {
    const originalCoords = websiteCoords.map(coord => ({
        x: coord.x / scaleFactor,
        y: coord.y / scaleFactor
    }));
    return originalCoords;
}

// Function to translate original coordinates to website coordinates
function originalToWebsiteCoords(originalCoords, scaleFactor) {
    const websiteCoords = originalCoords.map(coord => ({
        x: coord.x * scaleFactor,
        y: coord.y * scaleFactor
    }));
    return websiteCoords;
}


function setPoint(id, coords, pointClass, size=7) {
    const pointElement = document.getElementById(id);
    pointElement.style.left = `${coords.x}px`;
    pointElement.style.top = `${coords.y}px`;
    pointElement.style.height = `${size}px`;
    pointElement.style.width = `${size}px`;
    pointElement.className = `point ${pointClass}`;
    pointElement.style.visibility = 'visible';
}

function clearPath() {
    const existingLines = document.querySelectorAll('.line');
    existingLines.forEach(line => line.style.visibility = 'hidden');

    const existingPoints = document.querySelectorAll('.point');
    existingPoints.forEach(point => point.style.visibility = 'hidden');
    // console.log("cleared")
}


function createButtons() {
    // Get the container where buttons will be added
    var buttonsContainer = document.getElementById('gameButtons');

    // Loop through the game names and create buttons
    Object.keys(gameNamesDict).forEach( key => {
        // Create a button element
        var button = document.createElement('button');

        // Set button properties    
        button.textContent = key;
        button.className = 'btn btn-primary ml-2';
        button.addEventListener('click', function() {
            fetch('/get_image_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'game_name': gameNamesDict[key]+'-map',
                }),
            })
            .then(response => response.json())
            .then(data => {
                clearPath();
                imageElement.src = data.image_path 
                imageContainer.style.width = `${data.original_width}px`;
                imageContainer.style.height = `${data.original_height}px`; 
                originalImageWidth = data.original_width;
                originalImageHeight = data.original_height;
            })
            .catch(error => console.error('Error:', error));
        });

        // Append the button to the container
        buttonsContainer.appendChild(button);        
    })
    
}



// Call the function to create buttons
createButtons();