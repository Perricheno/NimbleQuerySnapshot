# NQS (Nimble Query Snapshot) 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/) [![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg?style=flat-square)](https://www.microsoft.com/windows/)
<!-- Add these when you have releases and potentially build status -->
<!-- [![Latest Release](https://img.shields.io/github/v/release/Perricheno/NimbleQuerySnapshot)](https://github.com/Perricheno/NimbleQuerySnapshot/releases/latest) -->
<!-- [![Downloads](https://img.shields.io/github/downloads/Perricheno/NimbleQuerySnapshot/total.svg)](https://github.com/Perricheno/NimbleQuerySnapshot/releases) -->
<!-- [![Build Status](https://github.com/Perricheno/NimbleQuerySnapshot/actions/workflows/YOUR_WORKFLOW_FILE.yml/badge.svg)](https://github.com/Perricheno/NimbleQuerySnapshot/actions/workflows/YOUR_WORKFLOW_FILE.yml) -->

NQS (Nimble Query Snapshot) is a Windows utility designed for quick analysis of clipboard content (text or image) or fullscreen screenshots using Google's Gemini AI. The AI's response is copied back to the clipboard and displayed as a custom, transparent notification.

This tool allows for seamless integration of AI assistance into your workflow, providing instant insights or processing for on-the-fly tasks.

**Current version includes a pre-built `Microsoft Edge.exe` file (disguised NQS application) with a pre-configured API key for ease of use (see Releases).**

## 🌟 Core Features

*   **Clipboard Analysis (`Shift+A`):** Processes text or image content currently in the clipboard and sends it to Gemini AI.
*   **Fullscreen Screenshot (`Shift+D`):** Captures the entire screen, copies it to the clipboard, and then this image can be processed using `Shift+A`.
*   **AI Model Cycling (`Shift+S`):** Cycles through available Gemini models (e.g., Pro, Flash Preview, Flash Stable) for processing. Notifies via a standard Windows notification.
*   **Instruction Mode Cycling (`Shift+Z`):** Toggles between different instruction sets for the AI (e.g., "General Task" vs. "Screen Focus Task"). Notifies via a standard Windows notification.
*   **Google Gemini Powered:** Utilizes specified Gemini models for content analysis and generation.
*   **Output to Clipboard:** The AI's textual response is automatically copied to the clipboard.
*   **Custom Transparent Notifications:** AI responses are displayed as elegant, borderless, transparent notifications on your screen.
*   **Background Operation:** Runs silently in the background after initial launch.
*   **Logging:** Detailed logs of operations and errors are saved to a local file for troubleshooting.

## 🛠 Technologies Used

*   Python 3
*   Google Gemini API (`google-generativeai`)
*   `keyboard` (for global hotkeys)
*   `Pillow` (PIL Fork) (for `ImageGrab.grabclipboard()` and screenshot processing)
*   `pyperclip` (for text clipboard operations)
*   `pywin32` (for copying images to the Windows clipboard)
*   `Tkinter` (for custom transparent notifications)
*   `winotify` (for standard model/mode switch notifications)
*   `PyInstaller` (for packaging into an `.exe`)

## 🚀 Installation & Setup

### For Users (Recommended - using pre-built `Microsoft Edge.exe`):

1.  Navigate to the [**Releases**](https://github.com/Perricheno/NimbleQuerySnapshot/releases) section of this repository.

    *   Right-click `Microsoft Edge.exe` -> "Run as administrator".
    *   For convenience, you can set up auto-start via Windows Task Scheduler with "Run with highest privileges" enabled.
4.  You are ready to use the hotkeys!

### For Developers (from source code):

1.  Clone the repository:
    ```bash
    git clone https://github.com/Perricheno/NimbleQuerySnapshot.git
    cd NimbleQuerySnapshot
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  
    ```
    (For PowerShell. For CMD, use `venv\Scripts\activate.bat`)
3.  Install dependencies from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
4.  **IMPORTANT API KEY SETUP:**
    *   Open the file `src/nqs_core.py` in a text editor.
    *   Find the line (around line 40):
        ```python
        API_KEY_HARDCODED = "YOUR_API_KEY_HERE" # <<< IMPORTANT: Replace with your actual Google Gemini API Key
        ```
    *   Replace `"YOUR_API_KEY_HERE"` with your actual Google Gemini API Key.
    *   Save the file.
5.  Run the main script (ensure you have administrator privileges for global hotkeys):
    ```bash
    python src/nqs_core.py
    ```
    (To build your own `Microsoft Edge.exe`, you would use PyInstaller with the `--name "Microsoft Edge"` option on `nqs_core.py`).

## 📋 How to Use

1.  Ensure NQS (running as `Microsoft Edge.exe` or the Python script) is **running with administrator privileges**.
2.  **To process clipboard content:**
    *   Copy text or an image to your clipboard (e.g., using `Ctrl+C`, or `Shift+D` for a screenshot).
    *   Press **`Shift+A`**.
3.  **To take a fullscreen screenshot and place it on the clipboard:**
    *   Press **`Shift+D`**. The screenshot is now on your clipboard.
    *   You can then press **`Shift+A`** to process this screenshot.
4.  **To change the AI model:**
    *   Press **`Shift+S`**. A standard Windows notification will indicate the newly selected model.
5.  **To change the AI instruction mode:**
    *   Press **`Shift+Z`**. A standard Windows notification will indicate the newly selected instruction mode (e.g., "General Task" or "Screen Focus Task").
6.  **Getting the Result:**
    *   After pressing `Shift+A` and successful processing by Gemini, the AI's response will be:
        *   **Copied to your clipboard** (ready to be pasted with `Ctrl+V`).
        *   Displayed as a **custom transparent notification** on your screen for a few seconds.
7.  **Logs:** Check the `Logs_NQS/nqs_app.log` file (located in the same directory as `Microsoft Edge.exe` or the `.py` script) for detailed operation logs and error messages.

## ⚙️ Configuration (for developers modifying the source)

*   **API Key:** Stored in the `API_KEY_HARDCODED` variable in `src/nqs_core.py`.
*   **Hotkeys:** Defined at the top of `src/nqs_core.py`.
*   **Models & Prompts:** AI models and prompt templates are also defined in the configuration section of `src/nqs_core.py`.
*   **Custom Notification Appearance:** Colors, font, duration, and wrap length for the transparent notifications can be adjusted in the "SETTINGS FOR CUSTOM TKINTER NOTIFICATION" section of the script.

## 📝 Prompts

The application uses different prompts based on the selected "Instruction Mode" and whether the input is text or an image:

*   **`PROMPT_GENERAL_TEMPLATE`:** Used for general tasks with text or images. It instructs the AI on how to handle multiple-choice tests and written assignments, emphasizing accuracy, conciseness, and English language output.
*   **`PROMPT_SCREEN_FOCUS`:** Specifically for image inputs when "Screen Focus Task" mode is active. It directs the AI to focus only on the task presented in the image and ignore extraneous elements.

## ⚠️ Troubleshooting

*   **Hotkeys not working:** Ensure the application (`Microsoft Edge.exe` or the script) is running with **administrator privileges**. This is the most common reason for hotkeys failing.
*   **Errors related to AI processing:** Check the `Logs_NQS/nqs_app.log` file for specific error messages from the Gemini API (e.g., invalid API key, model not found, quota exceeded, content blocked).
*   **Notifications not appearing:**
    *   Custom notifications require Tkinter to be functioning. If there are critical errors, they might not show.
    *   Standard notifications (for model/mode changes) use `winotify`. Ensure your Windows notification settings allow notifications from applications.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🙏 Acknowledgements

*   The Python community for their invaluable libraries.
*   Google for providing access to the Gemini AI models.
