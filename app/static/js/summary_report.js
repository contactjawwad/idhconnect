document.addEventListener('DOMContentLoaded', function () {

    
    let summaryGridApi;


    // Configuration options for the AG Grid
    const summaryGridOptions = {
        columnDefs: [
            { headerName: "Part Number", field: "Part Number", headerClass: 'blue-header' },
            { headerName: "QTY", field: "QTY", headerClass: 'blue-header' },
            { headerName: "Description", field: "Description", headerClass: 'blue-header' }
        ],
        defaultColDef: {
            flex: 1,
            minWidth: 100,
            resizable: true,
            sortable: true,
            filter: true,
        },
        onGridReady: function (params) {
            summaryGridApi = params.api; // Store the API of the grid
            params.api.setGridOption('loading', true); // Show loading overlay
            loadSummaryData(); // Load the summary data when the grid is ready
        },
        rowClassRules: {
            'light-blue-row': function (params) {
                return params.data && params.data.isHeader;
            }
        }
    };

    // Create the grid with the specified options
    const summaryGridDiv = document.querySelector('#summaryGrid');
    const exportButton = document.getElementById('exportFullReport');
    exportButton.disabled = true;  // Initially disable the export button    

    agGrid.createGrid(summaryGridDiv, summaryGridOptions);
   
    // Function to display notifications
    function displayNotification(message, success = false) {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.style.display = 'block';
        if (success) {
            notification.classList.add('success');
        } else {
            notification.classList.remove('success');
        }
    }

    // Function to hide notifications
    function hideNotification(duration = 5000) {
        setTimeout(() => {
            const notification = document.getElementById('notification');
            notification.style.display = 'none';
        }, duration);
    }

    // Function to fetch summary data from the server
    async function fetchSummaryData(url, title) {
        try {
            displayNotification(`Processing ${title}`);
            // Fetch the data
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json(); // Parse the JSON data from the response

            // Log the received data to verify the structure
            console.log('Received data:', data);

            // Check if summary_data is an array or an object
            let summaryArray = [];
            if (Array.isArray(data.summary_data)) {
                summaryArray = data.summary_data.map(item => ({
                    "Part Number": item["Part Number"],
                    "QTY": item["QTY"],
                    "Description": item["Description"]
                }));
            } else if (typeof data.summary_data === 'object' && data.summary_data !== null) {
                summaryArray = Object.entries(data.summary_data).map(([partNumber, details]) => ({
                    "Part Number": partNumber,
                    "QTY": details.QTY,
                    "Description": details.Description
                }));
            } else {
                throw new Error("Unexpected data structure");
            }

            // Add the header row
            summaryGridApi.applyTransaction({
                add: [{ "Part Number": title, "QTY": '', "Description": '', isHeader: true }],
                addIndex: summaryGridApi.getDisplayedRowCount()
            });

            // Add the data rows to the grid
            summaryGridApi.applyTransaction({ add: summaryArray });

            summaryGridApi.autoSizeColumns(['QTY']);
            
            //summaryGridApi.sizeColumnsToFit();
            summaryGridApi.setGridOption('loading', false); // Hide loading overlay
        } catch (error) {
            console.error("Error fetching data:", error); // Handle any errors that occur during the fetch
            displayNotification(`Error Processing ${title}`, false);
            summaryGridApi.setGridOption('loading', false); // Hide loading overlay
        }
    }

    // Function to load summary data from multiple sources sequentially
    async function loadSummaryData() {
        // List of URLs and titles for each data source
        const urls = [
            { url: '/reports/summary/card', title: 'Summary of  Cards' },
            { url: '/reports/summary/shelf_fan', title: 'Summary of Shelf & Fans' },
            { url: '/reports/summary/power', title: 'Summary of Power Modules' },
            { url: '/reports/summary/sfp', title: 'Summary of SFP Modules' },
            { url: '/reports/summary/flash_memory', title: 'Summary of Flash Memory' }
        ];

        // Fetch and display data for each URL sequentially
        for (const { url, title } of urls) {
            await fetchSummaryData(url, title); // Wait for each fetch to complete before starting the next
        }

        // Auto-size the QTY column after all data is loaded
        summaryGridApi.autoSizeColumns(['QTY']);

        // Display final notification
        displayNotification("All Processing Completed and Ready to Export", true);
        hideNotification(5000);

        // Enable the export button after all data is loaded
        exportButton.disabled = false;
    }


    function clearGridData() {
        mainGridApi.setRowData([]);
        summaryGridApi.setRowData([]);
        currentStart = 0;
    }
    // Clear data on page refresh or navigation
    window.addEventListener('beforeunload', function () {
        clearGridData();
    });

    // Function to export the full report as an Excel file
    window.exportFullReport = async function () {
        displayNotification('Exporting data, please wait...', false);
        exportButton.disabled = true; // Disable the export button during export

        const workbook = new ExcelJS.Workbook();
        const summarySheet = workbook.addWorksheet('Summary Report');

        // Add headers with styling to the Excel sheet
        const summaryHeaders = ["Part Number", "QTY", "Description"];
        const summaryHeaderRow = summarySheet.addRow(summaryHeaders);
        summaryHeaderRow.eachCell((cell, colNumber) => {
            cell.fill = {
                type: 'pattern',
                pattern: 'solid',
                fgColor: { argb: 'FF000080' } // Dark blue color
            };
            cell.font = { bold: true, color: { argb: 'FFFFFFFF' } }; // White font color
            cell.alignment = { vertical: 'middle', horizontal: 'center' }; // Center alignment
            cell.border = {
                top: { style: 'thin' },
                left: { style: 'thin' },
                bottom: { style: 'thin' },
                right: { style: 'thin' }
            };
        });

        // Extract data from the summary grid
        const summaryGridData = [];
        summaryGridApi.forEachNodeAfterFilterAndSort((rowNode) => {
            summaryGridData.push(rowNode.data);
        });

        // Add the data rows to the Excel sheet
        summaryGridData.forEach(data => {
            const row = summarySheet.addRow([data["Part Number"], data["QTY"], data["Description"]]);
            if (data.isHeader) {
                row.eachCell((cell, colNumber) => {
                    cell.fill = {
                        type: 'pattern',
                        pattern: 'solid',
                        fgColor: { argb: 'FFD3D3D3' } // Very light grey color for headers
                    };
                    cell.font = { bold: true }; // Bold font for headers
                });
            } else {
                row.eachCell((cell, colNumber) => {
                    cell.fill = {
                        type: 'pattern',
                        pattern: 'solid',
                        fgColor: { argb: 'FFDCE6F1' } // Light blue color for data
                    };
                    cell.alignment = { vertical: 'middle', horizontal: 'center' }; // Center alignment
                    cell.border = {
                        top: { style: 'thin' },
                        left: { style: 'thin' },
                        bottom: { style: 'thin' },
                        right: { style: 'thin' }
                    };
                });
            }
        });

        // Auto-size columns for the summary sheet
        summarySheet.columns.forEach(column => {
            let maxLength = 0;
            column.eachCell({ includeEmpty: true }, cell => {
                const length = cell.value ? cell.value.toString().length : 10;
                if (length > maxLength) {
                    maxLength = length;
                }
            });
            column.width = maxLength + 2;
        });

        // Generate and download the Excel file
        const buffer = await workbook.xlsx.writeBuffer();
        const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = 'SummaryReport.xlsx';
        anchor.click();
        URL.revokeObjectURL(url);

        displayNotification('Ready to Download!', true);
        hideNotification(5000);
        exportButton.disabled = false; // Enable the export button after export
    };
});
