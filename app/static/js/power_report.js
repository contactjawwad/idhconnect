// static/js/power_report.js
document.addEventListener('DOMContentLoaded', function () {
  
    let mainGridApi;
    let summaryGridApi;

    let currentStart = 0;
    const chunkSize = 10000;

    const gridOptions = {
        columnDefs: [
            { headerName: "Site Name", field: "Site Name", filter: true },
            { headerName: "Shelf Type", field: "Shelf Type", filter: true },
            { headerName: "PS-1 PN", field: "PS-1 PN", filter: true },
            { headerName: "PS-2 PN", field: "PS-2 PN", filter: true },
            { headerName: "Power Source", field: "Power Source", filter: true }
        ],
        defaultColDef: {
            flex: 1,
            minWidth: 100,
            resizable: true,
            sortable: true,
        },
        onGridReady: function (params) {
            mainGridApi = params.api;
            params.api.setGridOption('loading', true);
            params.api.autoSizeColumns(['PS-1 PN', 'PS-2 PN', 'Power Source']);
            setTimeout(() => {
                loadNextChunk();
            }, 100);
        }
    };

    const summaryGridOptions = {
        //enableRangeSelection: true,
        clipboardDelimiter: '\t',
        columnDefs: [
            { headerName: "Power Supply PN", field: "Power Supply PN", filter: true },
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
            params.api.autoSizeColumns(['Power Supply PN', 'QTY']);
            params.api.setGridOption('loading', true);
        }
    };

    const gridDiv = document.querySelector('#myGrid');
    const summaryGridDiv = document.querySelector('#summaryGrid');
    const notification = document.getElementById('notification');
    const exportButton = document.getElementById('exportFullReport');
    exportButton.disabled = true;

    agGrid.createGrid(gridDiv, gridOptions);
    agGrid.createGrid(summaryGridDiv, summaryGridOptions);

    function displayNotification(message, success = false) {
        notification.textContent = message;
        notification.style.display = 'inline';
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
        fetch(`/reports/power/data?start=${currentStart}&length=${chunkSize}`)
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
                }

                if (data.summary_data) {
                    console.log('Summary Data:', data.summary_data); // Log summary data to verify structure
                    let summaryArray = [];
                    data.summary_data.forEach(item => {
                        summaryArray.push({
                            "Power Supply PN": item["Power Supply PN"],
                            "QTY": item["QTY"],
                            "Description": item["Description"]
                        });
                    });
                    console.log('Processed Summary Array:', summaryArray); // Log processed summary array to verify correct mapping
                    summaryGridApi.applyTransaction({ add: summaryArray });
                    summaryGridApi.setGridOption('loading', false);
                }

                if (!data.all_data_fetched) {
                    loadNextChunk();
                } else {
                    console.log("All data loaded, no more data to fetch.");
                    mainGridApi.setGridOption('loading', false);
                    exportButton.disabled = false;
                }
            })
            .catch(error => {
                console.error("Error fetching data:", error);
                displayNotification(`Error fetching data: ${error.message}`, false);
                mainGridApi.setGridOption('noRowsOverlay', true);
            });
    }


    window.exportFullReport = async function () {
        displayNotification('Exporting data, please wait...', false);
        exportButton.disabled = true; // Disable the export button

        const workbook = new ExcelJS.Workbook();
        const worksheet = workbook.addWorksheet('Main Report');

        // Add headers with styling
        const headers = ["Site Name", "Shelf Type", "PS-1 PN", "PS-2 PN", "Power Source"];
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
            const row = worksheet.addRow([data["Site Name"], data["Shelf Type"], data["PS-1 PN"], data["PS-2 PN"], data["Power Source"]]);
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
        const summaryHeaders = ["Power Supply PN", "QTY", "Description"];
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
            const row = summarySheet.addRow([data["Power Supply PN"], data["QTY"], data["Description"]]);
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
        anchor.download = 'Power_Model_Report.xlsx';
        anchor.click();
        displayNotification('Successfully loaded and ready to save!', true);
        exportButton.disabled = false; // Enable the export button
        setTimeout(hideNotification, 5000); // Hide notification after 5 seconds
   
    };

    // Clear data on page refresh or navigation
    window.addEventListener('beforeunload', function () {
        clearGridData();
    });

});
