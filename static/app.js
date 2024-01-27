
// Names of the games
// JavaScript to handle toggle state
const toggleButton = document.getElementById('toggleButton');
const gameNamesDict  = {"Berlin": "Berlin", "Liverpool": "Liverpool", "Paris": "Paris", "Tokyo":"Tokyo", "Rome":"Rome", "France":"France", "Russia":"Russia", 'League Of Legends': 'lol', 'GTA V': 'GTAV', 'Test': 'test', }

// JavaScript to handle slider value
const slider = document.getElementById('slider');
const lastSliderValue = document.getElementById('lastSliderValue');
const displayButton = document.getElementById('displayButton');
let xDiv = [];
let yDiv = [];
let exitPoints = [];


toggleButton.addEventListener('change', function() {
    if (this.checked) {
        fetch('/get_hpa_path', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Update Content-Type to JSON
            },
            body: JSON.stringify({
                'x_divisions': xDiv, 'y_divisions': yDiv, 'exit_points': exitPoints,
            }),
        }).then(response => response.json())
            .then(data => {
                const paths = data.paths;
                clearPath(['line']);
                for(let i = 0; i < paths.length; i++){
                    let path = paths[i].map(coord => {
                        return { x: coord[0], y: coord[1] };
                    });
                    drawLine(path, size=3, color='cyan');
                }
            })
            .catch(error => console.error('Error:', error));
        
    }
});

slider.addEventListener('input', function() {
    const value = this.value;
    clearPath(['gridLine', 'exitPoint'])
    promise = fetchGridAndExitPoints(value); 
        promise.then(result => {
            xDiv = result.x_div;
            yDiv = result.y_div;
            exitPoints = result.exit_points;
            // Draw Grid lines
            for (let i = 0; i < xDiv.length; i++) {
                drawLine([{ x: xDiv[i], y: 0 }, { x: xDiv[i], y: originalImageHeight }], size=3, color='purple', className='gridLine');
                drawLine([{ x: 0, y: yDiv[i] }, { x: originalImageWidth, y: yDiv[i] }], size=3, color='purple', className='gridLine');
            }

            // Draw Exit points
            for (let i = 0; i < exitPoints.length; i++){
                exitPoints[i][1].forEach(coords => {
                    setPoint(imageContainer, 'exitPoint', coords, size=3, color='#FFB534')
                });
            }

        }).catch(error => {
            console.error('Error:', error);
        }); 
    lastSliderValue.textContent = value;
});

displayButton.addEventListener('click', function () {
    const contentToToggle = document.getElementById('contentToToggle');
    const buttonIcon = document.querySelector('#displayButton i');

    if (contentToToggle.style.display === 'none' || contentToToggle.style.display === '') {
      contentToToggle.style.display = 'block';
      buttonIcon.classList.remove('fa-eye-slash');
      buttonIcon.classList.add('fa-eye');
      displayButton.textContent = 'Hide';
    } else {
      contentToToggle.style.display = 'none';
      buttonIcon.classList.remove('fa-eye');
      buttonIcon.classList.add('fa-eye-slash');
      displayButton.textContent = 'Show';
    }
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

async function fetchGridAndExitPoints(gridSize) {
    try {
        const response = await fetch('/load_grid_and_exit_points', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                grid_size : gridSize
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
    if (clickCounter === 0) {
        startPoint = {x, y};
        setPoint(imageContainer, 'startPoint', startPoint, size=7, color='blue');
        clickCounter++;
    } else if (clickCounter === 1){
        endPoint = {x, y};
        setPoint(imageContainer, 'endPoint', endPoint, size=7, color='red');
        clickCounter++;
        promise = fetchOptimalPath(startPoint, endPoint); 
        promise.then(result => {
            const path = result.path;
            drawLine(path);
        }).catch(error => {
            console.error('Error:', error);
        }); 
    } else {
        clearPath(['line', 'startPoint', 'endPoint']);
        clickCounter = 0;
        startPoint = {x, y};
        setPoint(imageContainer, 'startPoint', startPoint,  size=7, color='blue');
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

function drawLine(coords, size=3, color='green', className='line') {
    coords.forEach((coord, i) => {
    
        if (i < coords.length - 1) {
            const start = coord;
            const end = coords[i + 1];
    
            // Calculate distance and angle between points
            const distance = Math.hypot(end.x - start.x, end.y - start.y);
            const angle = Math.atan2(end.y - start.y, end.x - start.x);
    
            // Create a line element
            const newLine = document.createElement('div');
            newLine.className = `${className}`;
            newLine.style.width = `${distance}px`;
            newLine.style.transform = `rotate(${angle}rad)`;
            newLine.style.height = `${size}px`;
            newLine.style.left = `${start.x}px`;
            newLine.style.top = `${start.y}px`;
            newLine.style.backgroundColor = `${color}`;
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


function setPoint(parentElement, className, coords, size=7, color) {
    const pointElement = document.createElement('div');
    pointElement.style.position = 'absolute';
    pointElement.style.left = `${coords.x - Math.floor(size/2)}px`;
    pointElement.style.top = `${coords.y- Math.floor(size/2)}px`;
    pointElement.style.height = `${size}px`;
    pointElement.style.width = `${size}px`;
    pointElement.style.backgroundColor = `${color}`;
    pointElement.className = `point ${className}`;
    pointElement.style.visibility = 'visible';

    parentElement.appendChild(pointElement);
}

function clearPath(classNames) {
    classNames.forEach( className => {
        const existingclass = document.querySelectorAll(`.${className}`);
        existingclass.forEach(obj => obj.remove());
    });
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
                clearPath(['line', 'gridLine', 'point']);
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