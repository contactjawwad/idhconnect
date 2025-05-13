importScripts('https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.2.1/exceljs.min.js');

self.onmessage = async function (e) {
    const { mainGridData, summaryGridData } = e.data;

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Main Report');

    const headers = ["Site Name", "Connector Type", "Part Number", "Vendor Serial Number", "Description","Shelf Type"];
    const headerRow = worksheet.addRow(headers);
    headerRow.eachCell((cell, colNumber) => {
        cell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FF000080' }
        };
        cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
        cell.border = {
            top: { style: 'thin' },
            left: { style: 'thin' },
            bottom: { style: 'thin' },
            right: { style: 'thin' }
        };
    });

    mainGridData.forEach(data => {
        const row = worksheet.addRow([
            data["Site Name"],
            data["Connector Type"],
            data["Part Number"],
            data["Vendor Serial Number"],
            data["Description"],
            data["Shelf Type"]
          ]);
          

                row.eachCell((cell, colNumber) => {
            cell.fill = {
                type: 'pattern',
                pattern: 'solid',
                fgColor: { argb: 'FFDCE6F1' }
            };
            cell.alignment = { vertical: 'middle', horizontal: 'center' };
            cell.border = {
                top: { style: 'thin' },
                left: { style: 'thin' },
                bottom: { style: 'thin' },
                right: { style: 'thin' }
            };
        });
    });

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

    const summarySheet = workbook.addWorksheet('Summary Report');
    const summaryHeaders = ["Part Number", "QTY", "Description"];
    const summaryHeaderRow = summarySheet.addRow(summaryHeaders);
    summaryHeaderRow.eachCell((cell, colNumber) => {
        cell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FF000080' }
        };
        cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
        cell.border = {
            top: { style: 'thin' },
            left: { style: 'thin' },
            bottom: { style: 'thin' },
            right: { style: 'thin' }
        };
    });

    summaryGridData.forEach(data => {
        const row = summarySheet.addRow([data["Part Number"], data["QTY"], data["Description"]]);
        row.eachCell((cell, colNumber) => {
            cell.fill = {
                type: 'pattern',
                pattern: 'solid',
                fgColor: { argb: 'FFDCE6F1' }
            };
            cell.alignment = { vertical: 'middle', horizontal: 'center' };
            cell.border = {
                top: { style: 'thin' },
                left: { style: 'thin' },
                bottom: { style: 'thin' },
                right: { style: 'thin' }
            };
        });
    });

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

// …after you’ve written Main Report and Summary Report…

// 1) Create the pivot sheet and write its header
const pivotSheet = workbook.addWorksheet('SFPPivot');
const pivotHeaders = ['Shelf Type','Part Number','Description','QTY'];
const pivotHeaderRow = pivotSheet.addRow(pivotHeaders);

// style only the header row
pivotHeaderRow.eachCell(cell => {
  cell.fill      = { type:'pattern', pattern:'solid', fgColor:{ argb:'FF000080' } };
  cell.font      = { bold:true, color:{ argb:'FFFFFFFF' } };
  cell.alignment = { vertical:'middle', horizontal:'center' };
  cell.border    = {
    top:{style:'thin'}, left:{style:'thin'},
    bottom:{style:'thin'}, right:{style:'thin'}
  };
});

    // 2) Build a simple map: Shelf Type → Part Number → {QTY, Description}
    const pivotMap = {};
    mainGridData.forEach(d => {
    const shelf = d['Shelf Type'] || 'Unknown';
    const part  = d['Part Number'];
    const desc  = d['Description'];

    if (!pivotMap[shelf])           pivotMap[shelf] = {};
    if (!pivotMap[shelf][part]) {
        pivotMap[shelf][part] = { QTY:0, Description: desc };
    }
    pivotMap[shelf][part].QTY++;
    });

    // 3) Flatten into an array of rows
    const pivotRows = [];
    Object.entries(pivotMap).forEach(([shelf, parts]) => {
    Object.entries(parts).forEach(([part, info]) => {
        pivotRows.push([ shelf, part, info.Description, info.QTY ]);
    });
    });

    // 4) Add them all at once (no per-cell loops)
    pivotSheet.addRows(pivotRows);

    // 5) Auto-size columns
    pivotSheet.columns.forEach(col => {
    let maxLength = 0;
    col.eachCell({ includeEmpty:true }, cell => {
        const len = cell.value ? cell.value.toString().length : 10;
        if (len > maxLength) maxLength = len;
    });
    col.width = maxLength + 2;
    });

// …then write out the buffer as before…


    const buffer = await workbook.xlsx.writeBuffer();
    self.postMessage(buffer);
};
