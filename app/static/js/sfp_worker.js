// sfp_worker.js
importScripts('https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js');

self.onmessage = function(e) {
  const { mainGridData, summaryGridData } = e.data;

  // 1) Create a new workbook
  const wb = XLSX.utils.book_new();

  // 2) Main Report sheet (including Shelf Type)
  const mainHeaders = [
    'Site Name',
    'Connector Type',
    'Part Number',
    'Vendor Serial Number',
    'Description',
    'Shelf Type'
  ];
  // Convert your array of objects into a sheet, forcing the header order
  const wsMain = XLSX.utils.json_to_sheet(mainGridData, {
    header: mainHeaders,
    skipHeader: false
  });
  XLSX.utils.book_append_sheet(wb, wsMain, 'Main Report');

  // 3) Summary Report sheet
  const summaryHeaders = ['Part Number','QTY','Description'];
  const wsSummary = XLSX.utils.json_to_sheet(summaryGridData, {
    header: summaryHeaders,
    skipHeader: false
  });
  XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary Report');

  // 4) Write out the XLSX as an ArrayBuffer (transferable)
  const wbout = XLSX.write(wb, {
    bookType: 'xlsx',
    type: 'array'
  });

  // 5) Send it back to the main thread
  self.postMessage(wbout, [wbout]);
};
