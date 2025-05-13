importScripts('https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.2.1/exceljs.min.js');

self.onmessage = async function (e) {
  const { mainGridData, summaryGridData } = e.data;
  const workbook = new ExcelJS.Workbook();

  // --- Main Report sheet ---
  const mainSheet   = workbook.addWorksheet('Main Report');
  const mainHeaders = ['Site Name','Connector Type','Part Number','Vendor Serial Number','Description'];
  const mainHeaderRow = mainSheet.addRow(mainHeaders);
  // Style header row only
  mainHeaderRow.eachCell(cell => {
    cell.fill      = { type:'pattern', pattern:'solid', fgColor:{ argb:'FF000080' } };
    cell.font      = { bold:true, color:{ argb:'FFFFFFFF' } };
    cell.alignment = { vertical:'middle', horizontal:'center' };
    cell.border    = { top:{style:'thin'}, left:{style:'thin'}, bottom:{style:'thin'}, right:{style:'thin'} };
  });
  // Bulk add data rows
  const mainRows = mainGridData.map(d => [
    d['Site Name'], d['Connector Type'], d['Part Number'],
    d['Vendor Serial Number'], d['Description'], 
  ]);
  mainSheet.addRows(mainRows);
  // Compute column widths from header + data
  const mainAll = [mainHeaders].concat(mainRows);
  mainSheet.columns.forEach((col, idx) => {
    let maxLen = 0;
    mainAll.forEach(r => {
      const v = r[idx] != null ? r[idx].toString().length : 0;
      if (v > maxLen) maxLen = v;
    });
    col.width = maxLen + 2;
  });

  // --- Summary Report sheet ---
  const summarySheet   = workbook.addWorksheet('Summary Report');
  const summaryHeaders = ['Part Number','QTY','Description'];
  const summaryHeaderRow = summarySheet.addRow(summaryHeaders);
  summaryHeaderRow.eachCell(cell => {
    cell.fill      = { type:'pattern', pattern:'solid', fgColor:{ argb:'FF000080' } };
    cell.font      = { bold:true, color:{ argb:'FFFFFFFF' } };
    cell.alignment = { vertical:'middle', horizontal:'center' };
    cell.border    = { top:{style:'thin'}, left:{style:'thin'}, bottom:{style:'thin'}, right:{style:'thin'} };
  });
  const summaryRows = summaryGridData.map(d => [d['Part Number'], d['QTY'], d['Description']]);
  summarySheet.addRows(summaryRows);
  const summaryAll = [summaryHeaders].concat(summaryRows);
  summarySheet.columns.forEach((col, idx) => {
    let maxLen = 0;
    summaryAll.forEach(r => {
      const v = r[idx] != null ? r[idx].toString().length : 0;
      if (v > maxLen) maxLen = v;
    });
    col.width = maxLen + 2;
  });

  // Finalize and send back
  const buffer = await workbook.xlsx.writeBuffer();
  self.postMessage(buffer);
};
