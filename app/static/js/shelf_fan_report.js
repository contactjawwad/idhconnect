document.addEventListener('DOMContentLoaded', function () {

    let mainGridApi;
    let summaryGridApi;

    let currentStart = 0;
    const chunkSize = 10000;

    const gridOptions = {
        columnDefs: [
            { headerName: "Site Name", field: "Site Name", filter: true },
            { headerName: "Part Number", field: "Part Number", filter: true },
            { headerName: "Serial Number", field: "Serial Number", filter: true },
            { headerName: "Shelf Type", field: "Shelf Type", filter: true },
            { headerName: "Fan P/N", field: "Fan P/N", filter: true },
            { headerName: "Fan QTY", field: "Fan QTY", filter: 'agNumberColumnFilter' }
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
            setTimeout(() => {
                loadNextChunk();
            }, 100);
            params.api.autoSizeColumns(['Serial Number', 'Fan P/N', 'Fan QTY']);
        }
    };

    const summaryGridOptions = {
        columnDefs: [
            { headerName: "Part Number", field: "Part Number", filter: true },
            { headerName: "Description", field: "Description", filter: true },
            { headerName: "QTY", field: "QTY", filter: 'agNumberColumnFilter' }
        ],
        defaultColDef: {
            flex: 1,
            minWidth: 100,
            resizable: true,
            sortable: true,
        },
        onGridReady: function (params) {
            summaryGridApi = params.api;
            params.api.autoSizeColumns(['Part Number', 'QTY']);
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
        fetch(`/reports/shelf_fan/data?start=${currentStart}&length=${chunkSize}`)
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
                    mainGridApi.setGridOption('noRowsOverlay', true);
                }

                if (data.summary_data) {
                    let summaryArray = [];
                    for (let partNumber in data.summary_data) {
                        if (data.summary_data.hasOwnProperty(partNumber)) {
                            summaryArray.push({
                                "Part Number": partNumber,
                                "QTY": data.summary_data[partNumber].QTY,
                                "Description": data.summary_data[partNumber].description
                            });
                        }
                    }
                    console.log('Processed Summary Array:', summaryArray);
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
        const headers = ["Site Name", "Part Number", "Serial Number", "Shelf Type", "Fan P/N", "Fan QTY"];
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
            const row = worksheet.addRow([data["Site Name"], data["Part Number"], data["Serial Number"], data["Shelf Type"], data["Fan P/N"], data["Fan QTY"]]);
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
        const summaryHeaders = ["Part Number", "Description", "QTY"];
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
            const row = summarySheet.addRow([data["Part Number"], data["Description"], data["QTY"]]);
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
        anchor.download = 'Shelf_Fan_Report.xlsx';
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
