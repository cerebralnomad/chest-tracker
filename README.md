# Total Battle Clan Chest Tracker

A Python application with PyQt6 GUI to track clan chest contributions in the Total Battle online game. Automatically extracts player names and chest types using OCR, maintains daily/weekly/monthly databases, and generates beautiful HTML reports for sharing with clan members.

This program was developed for and tested on Linux only. Specifically Kubuntu 24.04, but it should run on most any Linux distribution.
It should in theory run on Windows, as it is written in Python, but some changes may be required. 
I offer no support whatsoever to running on Windows, as I do not have a Windows machine, nor do I have any experience with Windows
beyond Windows 7.


## Features

- 🎯 **Automated OCR Processing**: Captures screen region and extracts player names and chest types
- 📊 **Multi-Period Tracking**: Separate daily, weekly, and monthly databases
- 🏆 **Leaderboards & Rankings**: Sort by chest count, type, or point value
- 📈 **Interactive Charts**: Beautiful HTML reports with Chart.js visualizations
- ⚙️ **Configurable Points**: Set custom point values for each chest type
- 🌐 **Web-Ready Reports**: Self-contained HTML files ready for upload to your server
- 🗑️ **Auto-Cleanup**: Databases older than 30 days are automatically deleted (HTML preserved)

## Requirements

- Linux (tested on Ubuntu 24.04)
- Python 3.8+
- X11 or XWayland (for screen capture)
- Display server running

## Installation

### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pyqt6 python3-xlib scrot

# Fedora
sudo dnf install python3-pyqt6 python3-xlib scrot

# Arch
sudo pacman -S python-pyqt6 python-xlib scrot
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv chest_tracker_env
source chest_tracker_env/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note**: PaddleOCR installation may take several minutes as it downloads the OCR models.

## Configuration

### First Time Setup

1. **Launch the application**:
   ```bash
   python3 chest_tracker.py
   ```

2. **Set up capture coordinates**:
   - Go to the "Coordinates" tab
   - Open Total Battle and navigate to the clan chest screen
   - Use a screenshot tool to find the coordinates of the chest list area
   - Enter the X, Y position of the top-left corner
   - Enter the width and height of the capture area
   - Click "Test Capture" to verify
   - Click "Save Coordinates"

3. **Configure point values**:
   - Go to the "Point Values" tab
   - Set points for each chest type
   - Add new chest types if needed
   - Click "Save Point Values"

## Usage

### Processing Chests

1. Open Total Battle and navigate to clan chests screen
2. Make sure the chest list is visible in the configured capture area
3. Go to the "Capture" tab
4. Click "Start Processing"
5. The application will:
   - Capture the screen region
   - Run OCR to extract player names and chest types
   - Save data to databases
   - Click the "Open" button automatically
   - Repeat until no more chests are found

### Viewing Statistics

1. Go to the "Statistics" tab
2. Click "Refresh Statistics" to see today's data
3. Export reports:
   - **Daily Report**: Current day's statistics
   - **Weekly Report**: Monday 12am - Sunday 12pm
   - **Monthly Report**: Full calendar month

### HTML Reports

Generated reports are saved in the `html_reports/` directory. These files are:
- **Self-contained**: All CSS and JavaScript included
- **No external dependencies**: Can be uploaded anywhere
- **Responsive**: Works on desktop and mobile
- **Interactive**: Tabbed interface with multiple chart views

#### Uploading to Your Server

```bash
# Example: Upload to your subdomain
scp html_reports/weekly_report_*.html user@yourserver.com:/var/www/clanchests/

# Or use FTP/SFTP client of your choice
```

The HTML files can be accessed directly via:
```
https://yoursubdomain.yourdomain.com/weekly_report_2024-W10.html
```

## Database Structure

### Daily Databases
- Location: `databases/daily_YYYY-MM-DD.db`
- Period: 12:00 AM to 11:59 PM

### Weekly Databases
- Location: `databases/weekly_YYYY-WXX.db`
- Period: Monday 12:00 AM to Sunday 12:00 PM

### Monthly Databases
- Location: `databases/monthly_YYYY-MM.db`
- Period: First to last day of month

### Auto-Cleanup
- Databases older than 30 days are automatically deleted
- HTML reports are never deleted (preserve forever)

## Troubleshooting

### "OCR model not ready yet"
Wait a few seconds after launching the app. OCR initialization takes time on first run.

### "Screen capture failed"
- Ensure X11/XWayland is running
- Install `python3-xlib`: `sudo apt install python3-xlib`
- Test with: `python3 -c "import pyautogui; print(pyautogui.position())"`

### "No chests found"
- Verify capture coordinates are correct
- Ensure chest list is visible and not obscured
- Check that game text is clear and readable
- Try adjusting screen resolution or zoom level

### OCR extracts wrong text
- Increase game resolution for clearer text
- Ensure good lighting/contrast
- Verify the capture area includes only the chest list
- English text works best (uncomment `lang='en'` in OCR init if needed)

### Database corruption
Delete the affected database file. It will be recreated on next run:
```bash
rm databases/daily_2024-03-15.db
```

## File Structure

```
chest_tracker/
├── chest_tracker.py          # Main PyQt6 application
├── database_manager.py       # Database operations
├── html_generator.py         # HTML report generation
├── requirements.txt          # Python dependencies
├── config.json              # Application configuration (auto-created)
├── databases/               # SQLite databases (auto-created)
│   ├── daily_*.db
│   ├── weekly_*.db
│   └── monthly_*.db
└── html_reports/            # Generated HTML files (auto-created)
    ├── daily_report_*.html
    ├── weekly_report_*.html
    └── monthly_report_*.html
```

## Customization

### Adding New Chest Types

1. Go to "Point Values" tab
2. Enter new chest type name
3. Click "Add"
4. Restart application
5. Set point value for new type

### Modifying Report Style

Edit `html_generator.py` and modify the `_get_css()` method to change colors, fonts, or layout.

### Changing Time Periods

Edit `database_manager.py`:
- Modify `_get_daily_db()`, `_get_weekly_db()`, or `_get_monthly_db()` methods
- Adjust time calculations as needed

## Tips for Best Results

1. **Use consistent screen resolution** - OCR works best with stable layout
2. **Clear game graphics** - Higher quality = better OCR accuracy
3. **Test coordinates first** - Always use "Test Capture" before processing
4. **Regular exports** - Export weekly reports for clan members
5. **Backup HTML files** - Keep historical reports for comparison

## Contributing

Found a bug or have a feature request? Please let us know!

## License

This project is provided as-is for personal and clan use.

## Credits

- **PaddleOCR**: OCR engine for text extraction
- **PyQt6**: GUI framework
- **Chart.js**: Interactive charts in HTML reports
- **pyautogui**: Screen capture and automation

---

**Note**: This tool is for tracking clan participation and is not affiliated with or endorsed by Total Battle or any game developer.
