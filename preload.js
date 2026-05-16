const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  selectFile: () => ipcRenderer.invoke('select-file'),
  analyzeCSV: (csvPath) => ipcRenderer.invoke('analyze-csv', csvPath),
  openFile: (filePath) => ipcRenderer.invoke('open-file', filePath)
});
