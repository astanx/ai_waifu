const { app, BrowserWindow } = require('electron');

function createWindow() {
    const win = new BrowserWindow({
        width: 300,
        height: 400,
        frame: false, // Frameless window (no OS border or title bar)
        alwaysOnTop: true, // Keep window always on top of others
        transparent: true, // Enable transparent background
        webPreferences: { 
            nodeIntegration: true, // Allow using Node.js inside the renderer
            contextIsolation: false // Disable context isolation (simpler but less secure)
        }
    });

    // Get screen information to position the window
    const { screen } = require('electron');
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    // Position the window in the bottom-right corner
    win.setPosition(width - 300, height - 350);

    // Load the HTML file into the window
    win.loadFile('electron.html');
}

// Create the window once the app is ready
app.whenReady().then(createWindow);

// Quit the app when all windows are closed (except on macOS, where apps usually stay open)
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
