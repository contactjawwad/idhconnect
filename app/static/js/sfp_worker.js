importScripts('https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.2.1/exceljs.min.js');

self.onmessage = async function (e) {
  const { mainGridData, summaryGridData } = e.data;
  const workbook = new ExcelJS.Workbook();

  // --- Main Report sheet ---
  const mainSheet   = workbook.addWorksheet('Main Report');
  // 1) include Shelf Type in the headers
  const mainHeaders = [
    'Site Name',
    'Connector Type',
    'Part Number',
    'Vendor Serial Number',
    'Description',
    'Shelf Type'
  ];
  const mainHeaderRow = mainSheet.addRow(mainHeaders);

  // 2) style *only* the header
  mainHeaderRow.eachCell(cell => {
    cell.fill      = { type:'pattern', pattern:'solid', fgColor:{ argb:'FF000080' } };
    cell.font      = { bold:true, color:{ argb:'FFFFFFFF' } };
    cell.alignment = { vertical:'middle', horizontal:'center' };
    cell.border    = {
      top:{style:'thin'}, left:{style:'thin'},
      bottom:{style:'thin'}, right:{style:'thin'}
    };
  });

  // 3) bulk‐add your data rows, including shelf type
  const mainRows = mainGridData.map(d => [
    d['Site Name'],
    d['Connector Type'],
    d['Part Number'],
    d['Vendor Serial Number'],
    d['Description'],
    d['Shelf Type'] || ''       // fallback empty string
  ]);
  mainSheet.addRows(mainRows);

  // 4) assign fixed or header‐based widths instead of scanning all cells
  //    you can tune these numbers to fit your longest expected content
  const mainColWidths = [30, 25, 20, 28, 40, 22];
  mainSheet.columns.forEach((col, i) => {
    col.width = mainColWidths[i] || 15;
  });


  // --- Summary Report sheet (unchanged) ---
  const summarySheet   = workbook.addWorksheet('Summary Report');
  const summaryHeaders = ['Part Number','QTY','Description'];
  const summaryHeaderRow = summarySheet.addRow(summaryHeaders);
  summaryHeaderRow.eachCell(cell => {
    cell.fill      = { type:'pattern', pattern:'solid', fgColor:{ argb:'FF000080' } };
    cell.font      = { bold:true, color:{ argb:'FFFFFFFF' } };
    cell.alignment = { vertical:'middle', horizontal:'center' };
    cell.border    = {
      top:{style:'thin'}, left:{style:'thin'},
      bottom:{style:'thin'}, right:{style:'thin'}
    };
  });
  const summaryRows = summaryGridData.map(d => [
    d['Part Number'], d['QTY'], d['Description']
  ]);
  summarySheet.addRows(summaryRows);
  const summaryColWidths = [20, 8, 40];
  summarySheet.columns.forEach((col, i) => {
    col.width = summaryColWidths[i] || 15;
  });


  // --- send it back ---
  const buffer = await workbook.xlsx.writeBuffer();
  self.postMessage(buffer);
};
