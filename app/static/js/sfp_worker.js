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

    // Pivot sheet: Node Type (Shelf Type) vs Part Number with Description and count
    const pivotSheet = workbook.addWorksheet('SFPPivot');
    const pivotHeaders = ["Shelf Type", "Part Number", "Description", "QTY"];
    const pivotHeaderRow = pivotSheet.addRow(pivotHeaders);
    pivotHeaderRow.eachCell((cell) => {
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF000080' } };
        cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
        cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
    });
    // Build pivot mapping with description
    const pivotMap = {};
    mainGridData.forEach(data => {
        const shelf = data["Shelf Type"] || 'Unknown';
        const part = data["Part Number"];
        const desc = data["Description"];
        if (!pivotMap[shelf]) pivotMap[shelf] = {};
        if (!pivotMap[shelf][part]) pivotMap[shelf][part] = { QTY: 0, Description: desc };
        pivotMap[shelf][part].QTY += 1;
    });
    // Write pivot rows
    Object.entries(pivotMap).forEach(([shelf, parts]) => {
        Object.entries(parts).forEach(([part, info]) => {
            const row = pivotSheet.addRow([shelf, part, info.Description, info.QTY]);
            row.eachCell((cell) => {
                cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFDCE6F1' } };
                cell.alignment = { vertical: 'middle', horizontal: 'center' };
                cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
            });
        });
    });
    pivotSheet.columns.forEach(column => {
        let maxLength = 0;
        column.eachCell({ includeEmpty: true }, cell => {
            const length = cell.value ? cell.value.toString().length : 10;
            if (length > maxLength) maxLength = length;
        });
        column.width = maxLength + 2;
    });



    const buffer = await workbook.xlsx.writeBuffer();
    self.postMessage(buffer);
};
