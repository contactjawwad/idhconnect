// static/js/SFP_report.js
document.addEventListener('DOMContentLoaded', function () {
    
    let mainGridApi;
    let summaryGridApi;

    let currentStart = 0;
    const chunkSize = 10000;

    const gridOptions = {
        columnDefs: [
            { headerName: "Site Name", field: "Site Name", filter: true },
            { headerName: "Connector Type", field: "Connector Type", filter: true },
            { headerName: "Part Number", field: "Part Number", filter: true },
            { headerName: "Vendor Serial Number", field: "Vendor Serial Number", filter: true },
            { headerName: "Description", field: "Description", filter: true },
            // ← Add this line:
            { headerName: "Shelf Type",             field: "Shelf Type",             filter: true }

        ],
        defaultColDef: {
            flex: 1,
            minWidth: 100,
            resizable: true,
            sortable: true,
        },
        onGridReady: function (params) {
            mainGridApi = params.api;
            params.api.setGridOption('loading', true); // Replaced showLoadingOverlay
            setTimeout(() => {
                loadNextChunk();
            }, 100);
        },
        onFirstDataRendered: function (params) {
            params.api.autoSizeColumns(['Site Name', 'Connector Type', 'Part Number', 'Vendor Serial Number','Description','Shelf Type']);
        }
    };

    const summaryGridOptions = {
        //enableRangeSelection: true,
        clipboardDelimiter: '\t',
        columnDefs: [
            { headerName: "Part Number", field: "Part Number", filter: true },
            { headerName: "QTY", field: "QTY", filter: 'agNumberColumnFilter' },
            { headerName: "Description", field: "Description", filter: true }
        ],
        defaultColDef: {
            flex: 1,
            minWidth: 100,
            resizable: true,
        },
        ensureDomOrder: true,
        onGridReady: function (params) {
            summaryGridApi = params.api;
            params.api.setGridOption('loading', true); // Replaced showLoadingOverlay
        },
        onFirstDataRendered: function (params) {
            params.api.autoSizeColumns(['Part Number', 'QTY']);
        }
    };

    const gridDiv = document.querySelector('#myGrid');
    const summaryGridDiv = document.querySelector('#summaryGrid');
    const notification = document.getElementById('notification');
    const exportButton = document.getElementById('exportFullReport');

    exportButton.disabled = true;  // Initially disable the export button

    agGrid.createGrid(gridDiv, gridOptions);
    agGrid.createGrid(summaryGridDiv, summaryGridOptions);

    // Function to display notifications
    function displayNotification(message, success = false) {
        notification.textContent = message;
        notification.style.display = 'inline'; // Adjusted to show inline with the Summary text
        if (success) {
            notification.classList.add('success');
            notification.classList.remove('error');
        } else {
            notification.classList.add('error');
            notification.classList.remove('success');
        }
    }

    function hideNotification() {
        notification.style.display = 'none';
    }

    function clearGridData() {
        mainGridApi.setRowData([]);
        summaryGridApi.setRowData([]);
        currentStart = 0;
    }

    function loadNextChunk() {
        console.log(`Requesting data starting from index ${currentStart} for ${chunkSize} rows...`);
        fetch(`/reports/sfp/data?start=${currentStart}&length=${chunkSize}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Main Grid Data:', data.data);
                console.log('Summary Grid Data:', data.summary_data);

                if (data.data.length > 0) {
                    mainGridApi.applyTransaction({ add: data.data });
                    currentStart += data.data.length;
                    console.log(`Processed ${data.data.length} rows. Next chunk will start from ${currentStart}`);
                } else {
                    mainGridApi.setGridOption('loading', false); // Replaced showNoRowsOverlay
                }

                if (data.summary_data) {
                    let summaryArray = [];
                    for (let partNumber in data.summary_data) {
                        if (data.summary_data.hasOwnProperty(partNumber)) {
                            summaryArray.push({
                                "Part Number": partNumber,
                                "QTY": data.summary_data[partNumber].QTY,
                                "Description": data.summary_data[partNumber].Description
                            });
                        }
                    }
                    console.log('Processed Summary Array:', summaryArray);
                    summaryGridApi.applyTransaction({ add: summaryArray });
                    summaryGridApi.setGridOption('loading', false); // Replaced hideOverlay
                }

                if (!data.all_data_fetched) {
                    loadNextChunk();
                } else {
                    console.log("All data loaded, no more data to fetch.");
                    mainGridApi.setGridOption('loading', false); // Replaced hideOverlay
                    exportButton.disabled = false;  // Enable the export button when all data is loaded
                }
            })
            .catch(error => {
                displayNotification(`Error fetching data: ${error.message}`, false);
                console.error("Error fetching data:", error);
                mainGridApi.setGridOption('loading', false); // Replaced showNoRowsOverlay
            });
    }


    window.exportFullReport = function () {
    // 1) Notify and disable
        displayNotification('Exporting data, please wait...', false);
        exportButton.disabled = true;

        // 2) Fetch the XLSX from the server
        fetch('/sfp/export')
            .then(response => {
            if (!response.ok) {
                throw new Error(`Server error (${response.status})`);
            }
            return response.blob();
            })
            .then(blob => {
            // 3) Trigger download
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'SFP_Model_Report.xlsx';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            // 4) Success notification
            displayNotification('Export successful! Your download should start shortly.', true);
            })
            .catch(error => {
            console.error('Export failed:', error);
            displayNotification(`Export error: ${error.message}`, false);
            })
            .finally(() => {
            // 5) Re-enable the button after a short delay
            setTimeout(() => {
                exportButton.disabled = false;
                hideNotification();
            }, 3000);
            });
    };


    // Clear data on page refresh or navigation
    window.addEventListener('beforeunload', function () {
        clearGridData();
    });
});
