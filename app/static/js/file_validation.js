document.addEventListener('DOMContentLoaded', function() {
    // Fetch the status of the links when the page loads to ensure they are enabled if available
    fetch('/get_links_status')
        .then(response => response.json())
        .then(data => {
            if (data.links_enabled) {
                enableReportLinks(data.available_routes);
                document.querySelectorAll('.report-link').forEach(link => {
                    link.style.fontWeight = 'bold';
                    link.style.pointerEvents = 'auto';
                });
            }
        });
});

document.getElementById('file-upload-form').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the default form submission.

    const nfmpMode = document.getElementById('nfmp-select').value;
    const files = document.getElementById('file-upload-input').files;
    if (files.length === 0) {
        displayNotification('Please select the Files.', 'error');
        return;
    }

    // Define the mandatory and optional file bases
    const mandatoryFileBases = ['cards_', , 'flash_memory_', 'media_adaptor_', 'power_supply_', 'shelf_'];
    const optionalFileBases = ['fans_','network_element_', 'port_', 'port_connector_'];
    const allFileBases = [...mandatoryFileBases, ...optionalFileBases];
    
    // Initialize required files count for mandatory files
    const requiredFiles = {};
    mandatoryFileBases.forEach(base => {
        requiredFiles[base + 'nfmp1'] = 0;
        if (nfmpMode === 'two_nfmp') {
            requiredFiles[base + 'nfmp2'] = 0;
        }
    });

    // Validate files
    let allFilesValid = true;
    for (let i = 0; i < files.length; i++) {
        // Validate file names against the required pattern
        const pattern = new RegExp('^(' + allFileBases.join('|') + ')\\d{2}\\d{2}\\d{4}_NFMP(1|2)\\.(csv|xlsx?|xls)$', 'i');
        if (pattern.test(files[i].name)) {
            const match = pattern.exec(files[i].name);
            if (nfmpMode === 'one_nfmp' && match[2] === '2') {
                displayNotification('NFMP2 files are not allowed in one_nfmp mode.', 'error');
                return;
            }
            const fileKey = (match[1] + 'nfmp' + match[2]).toLowerCase();
            if (requiredFiles.hasOwnProperty(fileKey)) {
                requiredFiles[fileKey]++;
            }
        } else {
            allFilesValid = false;
            break;
        }
    }

    // Check for missing mandatory files
    let missingFiles = Object.keys(requiredFiles).filter(key => requiredFiles[key] === 0);
    if (missingFiles.length > 0 || !allFilesValid) {
        displayNotification('Not all required files are selected for uploading. Missing: ' + missingFiles.join(', '), 'error');
        return;
    }

    displayNotification('Uploading Files, Please Wait...', 'info');

    let formData = new FormData(this);
    console.log('Uploading files...');
    
    // Send files to the server for validation
    fetch('/validate', {
        method: 'POST',
        body: formData,
        headers: {
            'NFMP-Mode': nfmpMode // Send the NFMP mode to the server
        }
    })
    .then(response => {
        if (!response.ok) {
            // Extract the error message from the JSON response
            return response.json().then(data => {
                // Redirect to the error page with the error message as a query parameter
                window.location.href = `/error?error_message=${encodeURIComponent(data.message)}`;
                throw new Error(data.message);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('All files have been successfully uploaded.');
            enableReportLinks(data.available_routes); // Enable report links
            
            document.querySelectorAll('.report-link').forEach(link => link.classList.remove('disabled'));
            displayNotification('All files have been successfully uploaded.', 'success');
        } else {
            console.error('One or more files did not upload correctly.');
            displayNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error during the upload process:', error);
        // Already handled in the fetch block above
    });
});

// Display notifications to the user
function displayNotification(message, type) {
    const notificationArea = document.getElementById('notification-area');
    notificationArea.textContent = message;
    notificationArea.className = type;

    // Apply the style based on the type
    if (type === 'success') {
        notificationArea.style.color = 'darkgreen';
        notificationArea.style.fontWeight = 'bold';
    } else if (type === 'error') {
        notificationArea.style.color = 'red';
        notificationArea.style.fontWeight = 'bold';
    } else if (type === 'info') {
        notificationArea.style.color = 'blue';
        notificationArea.style.fontWeight = 'bold';
    }

    notificationArea.style.display = 'block';
    // Only apply a timer for success and error messages
    if (type !== 'info') {
        setTimeout(() => {
            notificationArea.style.display = 'none';
        }, 5000);
    }
}

// Enable report links based on available routes
function enableReportLinks(availableRoutes) {
    const reportRoutes = {
        'sfp-report-link': '/reports/sfp',
        'line-card-report-link': '/reports/card',
        'power-module-report-link': '/reports/power',
        'sc-cards-report-link': '/reports/flash',
        'shelf-fan-report-link': '/reports/shelf_fan',
        'shelf-reports-link': '/reports/shelf',
        'summary-reports-link': '/reports/summary',
    };

    document.querySelectorAll('.report-link').forEach(link => {
        const route = reportRoutes[link.id];
        if (route && availableRoutes.includes(route)) {
            link.href = route;
            link.style.pointerEvents = 'auto';
           // link.style.textDecoration = 'none';
            link.style.fontWeight = 'bold';
        }
    });
}
