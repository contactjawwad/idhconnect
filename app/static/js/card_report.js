///home/jawwad/InventoryDataHub/app/static/js/card_report.js
document.addEventListener('DOMContentLoaded', function () {

    let mainGridApi;
    let summaryGridApi;

    let currentStart = 0;
    const chunkSize = 10000;

    const gridOptions = {
        columnDefs: [
            { headerName: "Site Name", field: "Site Name",filter: true },
            { headerName: "Part Number", field: "Part Number", filter: true },
            { headerName: "Serial Number", field: "Serial Number", filter: true },
            { headerName: "Shelf Type", field: "Shelf Type", filter: true },
            { headerName: "Card Description", field: "Card Description", filter: true }
        ],
        defaultColDef: {
            flex: 1,
            minWidth: 100,
            resizable: true,
            sortable: true,  // Adding sorting functionality
        },
        onGridReady: function (params) {
            mainGridApi = params.api;
            // Commenting out autoSizeColumns temporarily
            params.api.autoSizeColumns(['Part Number', 'Serial Number', 'Shelf Type']);
            loadNextChunk();
        }
    };

    const summaryGridOptions = {
        columnDefs: [
            { headerName: "Part Number", field: "Part Number", filter: true },
            { headerName: "QTY", field: "QTY", filter: 'agNumberColumnFilter' },
            { headerName: "Card Description", field: "Card Description", filter: true }
        ],
        defaultColDef: {
            flex: 1,
            minWidth: 100,
            resizable: true,
            sortable: true,  // Adding sorting functionality
        },
        onGridReady: function (params) {
            summaryGridApi = params.api;
            params.api.autoSizeColumns(['Part Number', 'QTY']);
        }
    };

    const gridDiv = document.querySelector('#myGrid');
    const summaryGridDiv = document.querySelector('#summaryGrid');
    const notification = document.getElementById('notification');
    const exportButton = document.getElementById('exportFullReport');

    exportButton.disabled = true;  // Initially disable the export button
// Old code
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
        fetch(`/reports/card/data?start=${currentStart}&length=${chunkSize}`)
            .then(response => response.json())
            .then(data => {
                if (data.data.length > 0) {
                    mainGridApi.applyTransaction({ add: data.data });
                    currentStart += data.data.length;
                }
    
                if (!data.all_data_fetched) {
                    loadNextChunk();
                } else {
                    // Old code
                    mainGridApi.hideOverlay();  // Hide loading overlay
                    loadSummaryData(data.summary_data);
                    exportButton.disabled = false;
                }
            })
            .catch(error => {
                displayNotification(`Error fetching data: ${error.message}`, false);
                // Old code
                mainGridApi.showNoRowsOverlay();  // Show no rows overlay on error
                
            });
    }
    gridOptions.onRowDataChanged = function(params) {
        params.api.hideOverlay();
    };
    function loadSummaryData(summaryData) {
        const summaryRows = [];
        for (const partNumber in summaryData) {
            if (summaryData.hasOwnProperty(partNumber)) {
                summaryRows.push({
                    'Part Number': partNumber,
                    'Card Description': summaryData[partNumber].description,
                    'QTY': summaryData[partNumber].QTY
                });
            }
        }
        // Old code
        summaryGridApi.updateGridOptions({ rowData: summaryRows });
        //summaryGridApi.setRowData(summaryRows);
    }

    window.exportFullReport = async function () {
        displayNotification('Exporting data, please wait...', false);
        exportButton.disabled = true; // Disable the export button

        const workbook = new ExcelJS.Workbook();
        const worksheet = workbook.addWorksheet('Main Report');

        // Add headers with styling
        const headers = ["Site Name", "Part Number", "Serial Number", "Shelf Type", "Card Description"];
        const headerRow = worksheet.addRow(headers);
        headerRow.eachCell((cell, colNumber) => {
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

        // Extract data from main grid
        const mainGridData = [];
        mainGridApi.forEachNodeAfterFilterAndSort((rowNode) => {
            mainGridData.push(rowNode.data);
        });

        mainGridData.forEach(data => {
            const row = worksheet.addRow([data["Site Name"], data["Part Number"], data["Serial Number"], data["Shelf Type"], data["Card Description"]]);
            row.eachCell((cell, colNumber) => {
                cell.fill = {
                    type: 'pattern',
                    pattern: 'solid',
                    fgColor: { argb: 'FFDCE6F1' } // Light blue color
                };
                cell.alignment = { vertical: 'middle', horizontal: 'center' }; // Center alignment
                cell.border = {
                    top: { style: 'thin' },
                    left: { style: 'thin' },
                    bottom: { style: 'thin' },
                    right: { style: 'thin' }
                };
            });
        });

        // Auto-size columns
        worksheet.columns.forEach(column => {
            let maxLength = 0;
            column.eachCell({ includeEmpty: true }, cell => {
                const length = cell.value ? cell.value.toString().length : 10;
                if (length > maxLength) {
                    maxLength = length;
                }
            });
            column.width = maxLength + 2;
        });

        // Add summary data to a new sheet
        const summarySheet = workbook.addWorksheet('Summary Report');
        const summaryHeaders = ["Part Number", "Card Description", "QTY"];
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

        // Extract data from summary grid
        const summaryGridData = [];
        summaryGridApi.forEachNodeAfterFilterAndSort((rowNode) => {
            summaryGridData.push(rowNode.data);
        });

        summaryGridData.forEach(data => {
            const row = summarySheet.addRow([data["Part Number"], data["Card Description"], data["QTY"]]);
            row.eachCell((cell, colNumber) => {
                cell.fill = {
                    type: 'pattern',
                    pattern: 'solid',
                    fgColor: { argb: 'FFDCE6F1' } // Light blue color
                };
                cell.alignment = { vertical: 'middle', horizontal: 'center' }; // Center alignment
                cell.border = {
                    top: { style: 'thin' },
                    left: { style: 'thin' },
                    bottom: { style: 'thin' },
                    right: { style: 'thin' }
                };
            });
        });

        // Auto-size columns for summary sheet
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

        // Generate and download the file
        const buffer = await workbook.xlsx.writeBuffer();
        const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = 'Cards_Report.xlsx';
        anchor.click();
        URL.revokeObjectURL(url);

        displayNotification('Successfully loaded and ready to save!', true);
        exportButton.disabled = false; // Enable the export button
        setTimeout(hideNotification, 5000); // Hide notification after 5 seconds
    };

    // Clear data on page refresh or navigation
    window.addEventListener('beforeunload', function () {
        clearGridData();
    });


});
