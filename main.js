const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');
const fs = require('fs');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile('index.html');
  mainWindow.webContents.openDevTools();

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});

// Handle file selection
ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'CSV Files', extensions: ['csv'] }]
  });
  return result.filePaths[0] || null;
});

// Handle analysis
ipcMain.handle('analyze-csv', async (event, csvPath) => {
  return new Promise((resolve) => {
    const outputDir = path.join(app.getPath('userData'), 'outputs');
    
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const pythonScript = path.join(__dirname, 'analysis.py');
    
    const options = {
      args: [csvPath, outputDir]
    };

    PythonShell.run(pythonScript, options, function (err, results) {
      if (err) {
        resolve({
          status: 'error',
          message: err.message
        });
      } else {
        try {
          const result = JSON.parse(results[results.length - 1]);
          resolve(result);
        } catch (e) {
          resolve({
            status: 'error',
            message: 'Failed to parse results'
          });
        }
      }
    });
  });
});

// Handle opening file in browser
ipcMain.handle('open-file', async (event, filePath) => {
  const { shell } = require('electron');
  await shell.openPath(filePath);
  return true;
});

// Create application menu
const template = [
  {
    label: 'File',
    submenu: [
      {
        label: 'Exit',
        accelerator: 'CmdOrCtrl+Q',
        click: () => {
          app.quit();
        }
      }
    ]
  },
  {
    label: 'Help',
    submenu: [
      {
        label: 'About',
        click: () => {
          dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'GeoScanner Pro',
            message: 'GeoScanner Pro v1.0',
            detail: 'Advanced 3D Tomography Analysis Tool'
          });
        }
      }
    ]
  }
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);
