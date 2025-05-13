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

  

  // 5) Send it back to the main thread
  self.postMessage(wbout, [wbout]);
};
