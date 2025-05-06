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
        displayNotification('Exporting data, please wait...', false);
        exportButton.disabled = true;  // Disable the export button
        const mainGridData = [];
        mainGridApi.forEachNodeAfterFilterAndSort((rowNode) => {
            mainGridData.push(rowNode.data);
        });

        const summaryGridData = [];
        summaryGridApi.forEachNodeAfterFilterAndSort((rowNode) => {
            summaryGridData.push(rowNode.data);
        });

        const worker = new Worker('/static/js/sfp_worker.js');
        worker.postMessage({ mainGridData, summaryGridData });

        worker.onmessage = function (e) {
            const buffer = e.data;
            const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement('a');
            anchor.href = url;
            anchor.download = 'SFP_Model_Report.xlsx';
            anchor.click();
            URL.revokeObjectURL(url);
            displayNotification('Successfully loaded and ready to save!', true);
            exportButton.disabled = false;  // Enable the export button
            setTimeout(hideNotification, 5000); // Hide notification after 5 seconds

            // No need to clear grid data here, just clean up variables
            mainGridData.length = 0;
            summaryGridData.length = 0;
        };

        worker.onerror = function (error) {
            displayNotification(`Export error: ${error.message}`, false);
            console.error("Worker error:", error);
            exportButton.disabled = false;  // Enable the export button on error
        };
    };

    // Clear data on page refresh or navigation
    window.addEventListener('beforeunload', function () {
        clearGridData();
    });
});
