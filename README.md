# NQS (Nimble Query Snapshot) 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

NQS is a Windows utility designed for quick analysis of selected screen regions or clipboard content using Google's Gemini AI. The analysis result is automatically copied back to the clipboard for immediate use.

This project aims to integrate powerful language models directly into the workflow for rapid information retrieval and on-the-fly data processing.

## 🌟 Core Features (Implemented/Planned)

*   **Screen Region Analysis:**
    *   Activated by a hotkey sequence (`Alt+Q` + Left Click, then `Alt+W` + Left Click).
    *   "Silent" selection without screen dimming.
    *   Sends a screenshot of the selected region to Gemini AI for analysis.
*   **Clipboard Content Analysis:** (Future integration, based on previous helper script)
    *   Hotkey activated.
    *   Sends text or images from the clipboard to Gemini AI.
*   **Powered by Google Gemini AI:** Utilizes Gemini models (e.g., Pro/Flash) for analysis.
*   **Clipboard Output:** AI response is ready to be pasted immediately.
*   **System Notifications:** (If implemented in the final version) Alerts for mode changes or operation completion.
*   **Background Operation:** Designed to run unobtrusively.
*   **Logging:** Actions and errors are logged for debugging purposes.

## 🛠 Technologies Used

*   Python 3
*   Google Gemini API (`google-generativeai`)
*   Pynput (for global hotkeys and mouse event monitoring)
*   Pillow (PIL Fork) (for screen capture)
*   PyWin32 (for copying images to the Windows clipboard)
*   Winotify (for system notifications - if used)
*   PyInstaller (for packaging into an `.exe`)

## 🚀 Installation

### For Users (via `.exe`):

1.  Navigate to the [**Releases**](https://github.com/YOUR_GITHUB_USERNAME/NimbleQuerySnapshot/releases) section of this repository.
2.  Download the latest `NQS.exe` (or a setup file/archive).
3.  **Important:** For global hotkeys and screen capture to function correctly, the `.exe` file **must be run as administrator**. It's recommended to set up auto-start via Windows Task Scheduler with elevated privileges.
4.  On first launch, you might need to provide your Google API Key for Gemini (or it might be pre-configured, depending on the release version).

### For Developers (from source code):

1.  Clone the repository:
    ```bash
    git clone https://github.com/YOUR_GITHUB_USERNAME/NimbleQuerySnapshot.git
    cd NimbleQuerySnapshot
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate 
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  You will need a **Google API Key** for Gemini. Store it as an environment variable `GOOGLE_API_KEY` or follow instructions within the code if an alternative configuration method (like a `.env` file or hardcoding for testing) is used.
5.  Run the main script (e.g., `src/nqs_core.py`):
    ```bash
    python src/nqs_core.py
    ```
    *(Debugging might require running from an administrator console).*

## 📋 How to Use (Example for "Silent Snipper" mode)

1.  Ensure the NQS application (`.exe` or script) is **running with administrator privileges**.
2.  To capture a screen region:
    *   Press **`Alt+Q`**. The script will enter the mode for selecting the first point.
    *   **Left-click** on one corner of the desired screen area (this is the first point).
    *   Press **`Alt+W`**. The script will enter the mode for selecting the second point.
    *   **Left-click** on the opposite corner of the desired screen area (this is the second point).
3.  The screen region between these two points will be captured and (if AI analysis is implemented) sent to Gemini.
4.  After a few seconds, the result (e.g., image description or analysis) will be copied to your clipboard.
5.  Paste (`Ctrl+V`) the result into your desired application.
6.  Check the `Logs_NQS` folder (or the configured log folder name) next to the executable for operation details and potential errors.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🙏 Acknowledgements

*   The Python community for excellent libraries.
*   Google for providing access to Gemini models.

