# src/nqs_core.py
# -*- coding: utf-8 -*-
import pyperclip
from PIL import ImageGrab, Image
import io
import os
import time
import threading
import sys
import tkinter as tk # For custom transparent notifications

# Attempt to import required libraries and provide user-friendly error messages
try:
    import keyboard # For global hotkeys
except ImportError:
    print("ERROR: Library 'keyboard' not found. Please install it: pip install keyboard")
    sys.exit(1)

try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
except ImportError:
    print("ERROR: Library 'google-generativeai' not found. Please install it: pip install google-generativeai")
    sys.exit(1)

try:
    from winotify import Notification, audio # For simple, standard Windows notifications
except ImportError:
    print("ERROR: Library 'winotify' not found. Please install it: pip install winotify")
    sys.exit(1)

try:
    import win32clipboard # For copying images to clipboard on Windows
    import win32con
except ImportError:
    print("ERROR: Library 'pywin32' not found. Please install it: pip install pywin32")
    sys.exit(1)

# --- CONFIGURATION ---
API_KEY_HARDCODED = "YOUR API KEY HERE" # Replace with your actual key if needed

SUBMIT_HOTKEY = 'shift+a'           # Hotkey to process clipboard content
TOGGLE_MODEL_HOTKEY = 'shift+s'     # Hotkey to cycle through AI models
SCREENSHOT_HOTKEY = 'shift+d'       # Hotkey to take a fullscreen screenshot to clipboard
TOGGLE_INSTRUCTION_HOTKEY = 'shift+z' # Hotkey to cycle through instruction modes

# Available Gemini Models
MODEL_PRO = "gemini-2.5-pro-preview-03-25"        # More powerful model
MODEL_FLASH_PREVIEW = "gemini-2.5-flash-preview-04-17" # Faster preview model
MODEL_FLASH_STABLE = "gemini-1.5-flash-latest"       # Stable flash model (renamed from 2.0)
MODELS_AVAILABLE = [MODEL_PRO, MODEL_FLASH_PREVIEW, MODEL_FLASH_STABLE]
DEFAULT_MODEL_INDEX = 0 # Index for MODELS_AVAILABLE

# Instruction Modes for the AI
INSTRUCTION_MODE_GENERAL = "General Task"
INSTRUCTION_MODE_SCREEN_FOCUS = "Screen Focus Task" # Specifically for analyzing on-screen tasks
INSTRUCTION_MODES_AVAILABLE = [INSTRUCTION_MODE_GENERAL, INSTRUCTION_MODE_SCREEN_FOCUS]
DEFAULT_INSTRUCTION_MODE_INDEX = 0

# Prompts for different instruction modes and input types
PROMPT_GENERAL_TEMPLATE = """I will send you tasks/tests in the form of {input_type_description}.
You must:
- If it's a multiple-choice test: Write the answers in the format: 1. A; 2. B; etc.
- If it's a written assignment: Write a concise answer, covering only the most important points without using complex words.
All answers must be in English, written assignments should be at a B2 level.
Actively use Grounding to ensure your answer is accurate, truthful, and correct. The main goal is a concise, 100% correct answer. Provide your response as text.

The user has provided the following content/task:
---
{task_details}
---
"""

PROMPT_SCREEN_FOCUS = """You must answer only the tasks on the screen and not be distracted by extraneous elements not related to the test or question on the screen.
The task is in the provided image.
You must:
- If it's a multiple-choice test: Write the answers in the format: 1. A; 2. B; etc.
- If it's a written assignment: Write a concise answer, covering only the most important points without using complex words.
All answers must be in English, written assignments should be at a B2 level.
Actively use Grounding to ensure your answer is accurate, truthful, and correct. The main goal is a concise, 100% correct answer. Provide your response as text.
"""

APP_NAME_FOR_WINOTIFY = "NQS V1.5" # Application name for standard winotify notifications

# --- SETTINGS FOR CUSTOM TKINTER NOTIFICATION ---
TRANSPARENT_BG_COLOR = 'lime green'  # This color will become fully transparent
NOTIFICATION_TEXT_COLOR = 'white'
NOTIFICATION_FONT = ("Segoe UI", 14, "bold")
NOTIFICATION_DURATION_MS = 7000      # 7 seconds
NOTIFICATION_WRAP_LENGTH = 400       # Max text width before wrapping
# ---------------------------------------------------

# --- Global State Variables ---
current_model_index = DEFAULT_MODEL_INDEX
current_instruction_index = DEFAULT_INSTRUCTION_MODE_INDEX
processing_active = False   # Flag to prevent concurrent processing
processing_timer = None     # Timer to reset processing_active flag
root_tk = None              # Global root Tkinter window for custom notifications
# ---------------------------

# --- Logging Setup ---
if getattr(sys, 'frozen', False):
    base_path = Path(sys.executable).parent
else:
    base_path = Path(__file__).parent
LOG_DIRECTORY_PATH = base_path / "Logs_NQS"
try:
    LOG_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIRECTORY_PATH / "nqs_app.log"
except OSError as e:
    print(f"ERROR: Could not create log directory '{LOG_DIRECTORY_PATH}'. Error: {e}")
    log_file = base_path / "nqs_app_ERROR.log"

log_formatter = logging.Formatter('%(asctime)s:%(msecs)03d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_log_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8', delay=False)
file_log_handler.setFormatter(log_formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set to INFO for production, DEBUG for development
if not logger.hasHandlers():
    logger.addHandler(file_log_handler)
# ---------------------

# --- Core Functions ---

def show_standard_notification(title, message, sound=audio.Default):
    """Displays a standard Windows notification using winotify."""
    try:
        toast = Notification(app_id=APP_NAME_FOR_WINOTIFY, title=title, msg=message, duration="short")
        toast.set_audio(sound, loop=False)
        toast.show()
        logger.info(f"[WINOTIFY NOTIFICATION] {title}: {message[:50]}...")
    except Exception as e:
        logger.error(f"[WINOTIFY NOTIFICATION ERROR]: {e}")

def show_custom_notification(text_message):
    """Displays a custom, transparent, borderless notification using Tkinter."""
    global root_tk
    if not root_tk:
        logger.error("Tkinter root not initialized for custom notification!")
        show_standard_notification("NQS Info", text_message) # Fallback
        return

    try:
        notification_window = tk.Toplevel(root_tk)
        notification_window.withdraw() # Hide initially

        notification_window.overrideredirect(True) # Borderless
        notification_window.attributes('-transparentcolor', TRANSPARENT_BG_COLOR)
        notification_window.config(bg=TRANSPARENT_BG_COLOR)
        notification_window.attributes('-topmost', True) # Always on top

        label = tk.Label(
            notification_window,
            text=text_message,
            font=NOTIFICATION_FONT,
            fg=NOTIFICATION_TEXT_COLOR,
            bg=TRANSPARENT_BG_COLOR,
            wraplength=NOTIFICATION_WRAP_LENGTH,
            justify=tk.LEFT
        )
        label.pack(padx=15, pady=10)

        notification_window.update_idletasks() # Calculate widget sizes
        width = notification_window.winfo_width()
        height = notification_window.winfo_height()
        screen_width = notification_window.winfo_screenwidth()
        screen_height = notification_window.winfo_screenheight()
        
        x = screen_width - width - 30
        y = screen_height - height - 70 # Adjust for taskbar
        notification_window.geometry(f'{width}x{height}+{x}+{y}')

        notification_window.deiconify() # Show window
        logger.info(f"[CUSTOM NOTIFICATION] Shown: {text_message[:50]}...")
        notification_window.after(NOTIFICATION_DURATION_MS, notification_window.destroy)
    except Exception as e:
        logger.error(f"[CUSTOM NOTIFICATION ERROR]: {e}")
        show_standard_notification("NQS AI Response (Fallback)", text_message) # Fallback

def set_processing_active_flag(active, timeout_seconds=2.0):
    """Manages the processing_active flag with an optional timeout to reset it."""
    global processing_active, processing_timer
    if processing_timer:
        processing_timer.cancel()
        processing_timer = None
    processing_active = active
    if active and timeout_seconds:
        processing_timer = threading.Timer(timeout_seconds, lambda: set_processing_active_flag(False, None))
        processing_timer.start()
    logger.debug(f"Processing flag set to: {active}")

def copy_pil_image_to_windows_clipboard(pil_img):
    """Copies a PIL Image object to the Windows clipboard."""
    logger.debug("Attempting to copy PIL image to Windows clipboard...")
    try:
        output = io.BytesIO()
        # Ensure image is in RGB format if it has an alpha channel (RGBA)
        # as BMP (used for DIB) doesn't directly support alpha well for clipboard.
        if pil_img.mode == 'RGBA':
            pil_img = pil_img.convert('RGB')
        pil_img.save(output, "BMP")
        data = output.getvalue()[14:]  # DIB format starts after 14-byte BMP header
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, data)
        win32clipboard.CloseClipboard()
        logger.info("Image successfully copied to clipboard.")
        return True
    except NameError:
        logger.error("pywin32 library (win32clipboard) not found. Cannot copy image to clipboard.")
        return False
    except Exception as e:
        logger.exception("ERROR copying image to clipboard:")
        try:
            win32clipboard.CloseClipboard() # Attempt to close if left open
        except:
            pass
        return False

def take_fullscreen_screenshot_to_clipboard():
    """Takes a fullscreen screenshot and copies it to the clipboard."""
    global processing_active
    if processing_active:
        logger.info("Processing another request, screenshot deferred.")
        return
    set_processing_active_flag(True, timeout_seconds=3.0) # Longer timeout for screenshot
    logger.info(f"[{time.strftime('%H:%M:%S')}] Hotkey '{SCREENSHOT_HOTKEY}' pressed. Taking screenshot...")
    try:
        screenshot = ImageGrab.grab(all_screens=True)
        if copy_pil_image_to_windows_clipboard(screenshot):
            logger.info("Fullscreen screenshot copied to clipboard.")
            show_custom_notification("Screenshot captured to clipboard.")
        else:
            logger.error("Failed to copy screenshot to clipboard.")
            show_standard_notification("NQS Error", "Failed to copy screenshot.", sound=audio.Caution)
    except Exception as e:
        logger.exception("ERROR taking screenshot:")
        show_standard_notification("NQS Error", f"Screenshot error: {e}", sound=audio.Caution)
    finally:
        set_processing_active_flag(False, None)

def get_clipboard_content_for_ai():
    """Reads text or image content from the clipboard for AI processing."""
    content_type = None
    content_data = None
    logger.info(f"[{time.strftime('%H:%M:%S')}] Reading clipboard content for AI...")
    try:
        # Try to get image first
        pil_image = ImageGrab.grabclipboard()
        if isinstance(pil_image, Image.Image):
            logger.info("Image found in clipboard.")
            content_type = "image"
            content_data = pil_image
        else: # If not an image, try text
            text = pyperclip.paste()
            if text and text.strip():
                logger.info("Text found in clipboard.")
                content_type = "text"
                content_data = text.strip()
            else:
                logger.info("Clipboard is empty or contains unsupported data.")
    except Exception as e:
        logger.error(f"Error reading clipboard (attempting text as fallback): {e}")
        try: # Fallback to text if ImageGrab fails for non-image content
            text = pyperclip.paste()
            if text and text.strip():
                logger.info("Text found in clipboard (after ImageGrab fallback).")
                content_type = "text"
                content_data = text.strip()
            else:
                logger.info("Clipboard still empty or unsupported after text fallback.")
        except Exception as e2:
            logger.error(f"Complete failure to read clipboard: {e2}")
    return content_type, content_data

def ask_gemini_ai(content_type, content_data):
    """Sends content to Gemini AI and returns the response."""
    global current_model_index, current_instruction_index
    if not content_type or not content_data:
        logger.warning("No content to send to AI.")
        return None

    selected_model_name = MODELS_AVAILABLE[current_model_index]
    selected_instruction_mode = INSTRUCTION_MODES_AVAILABLE[current_instruction_index]
    
    logger.info(f"Preparing to send to {selected_model_name} (Mode: {selected_instruction_mode})...")
    
    prompt_parts = []
    try:
        model_for_request = genai.GenerativeModel(selected_model_name)
        
        if content_type == "text":
            formatted_prompt = PROMPT_GENERAL_TEMPLATE.format(
                input_type_description="a text-based task/question", 
                task_details=content_data
            )
            prompt_parts.append(formatted_prompt)
            logger.debug("Text prompt prepared.")
        elif content_type == "image":
            if selected_instruction_mode == INSTRUCTION_MODE_SCREEN_FOCUS:
                prompt_parts.append(PROMPT_SCREEN_FOCUS)
                logger.debug("Screen Focus prompt prepared for image.")
            else: # General Task for image
                formatted_prompt = PROMPT_GENERAL_TEMPLATE.format(
                    input_type_description="an image-based task/question", 
                    task_details="[The task or question is based on the provided image]"
                )
                prompt_parts.append(formatted_prompt)
                logger.debug("General prompt prepared for image.")
            prompt_parts.append(content_data) # Append PIL image object
        
        if not prompt_parts:
            logger.error("Prompt parts are empty, cannot send request.")
            return None
            
        generation_config = genai.types.GenerationConfig(response_mime_type="text/plain")
        
        logger.info(f"Sending request to {selected_model_name}...")
        start_time = time.time()
        response = model_for_request.generate_content(prompt_parts, generation_config=generation_config)
        duration = time.time() - start_time
        logger.info(f"AI response received from {selected_model_name} in {duration:.2f}s.")
        
        ai_response_text = response.text.strip()
        logger.debug(f"Raw AI Response (first 100 chars): {ai_response_text[:100]}")
        return ai_response_text

    except Exception as e:
        logger.exception(f"ERROR during Gemini API call with {selected_model_name}:")
        if isinstance(e, google_exceptions.NotFound):
            return f"ERROR: Model '{selected_model_name}' not found or access denied."
        return f"API Error ({selected_model_name}): {type(e).__name__}"

def process_clipboard_and_submit_to_ai():
    """Main function triggered by SUBMIT_HOTKEY."""
    global processing_active
    if processing_active:
        logger.info("Another request is already processing.")
        return
    
    set_processing_active_flag(True, timeout_seconds=30.0) # Longer timeout for AI calls
    logger.info(f"\n[{time.strftime('%H:%M:%S')}] Hotkey '{SUBMIT_HOTKEY}' pressed!")
    
    try:
        content_type, content_data = get_clipboard_content_for_ai()
        if content_type and content_data:
            show_custom_notification(f"Processing with {MODELS_AVAILABLE[current_model_index].split('/')[-1]}...")
            ai_result = ask_gemini_ai(content_type, content_data)
            if ai_result:
                logger.info(f"\n--- AI Response ({MODELS_AVAILABLE[current_model_index]}) ---\n{ai_result}\n--- End of Response ---")
                try:
                    pyperclip.copy(ai_result)
                    logger.info("(AI Response copied to clipboard)")
                except Exception as e_clip:
                    logger.error(f"(Failed to copy AI response to clipboard: {e_clip})")
                
                show_custom_notification(ai_result) # Show AI result in custom notification
            else:
                logger.warning("Failed to get a valid response from AI.")
                show_custom_notification("AI: Failed to get response.")
        else:
            logger.info("Clipboard empty or content not supported for AI processing.")
            show_custom_notification("Clipboard is empty or content not supported.")
            
    except Exception as e:
        logger.exception("CRITICAL ERROR during clipboard processing and AI submission:")
        show_custom_notification(f"Critical Error: {e}")
    finally:
        set_processing_active_flag(False, None)
        logger.info(f"Processing finished. Ready for new '{SUBMIT_HOTKEY}' request.")

def cycle_ai_model():
    """Cycles through the available AI models."""
    global current_model_index, processing_active
    if processing_active:
        logger.info("Processing active, model change deferred.")
        return
    set_processing_active_flag(True, timeout_seconds=0.5)
    current_model_index = (current_model_index + 1) % len(MODELS_AVAILABLE)
    model_name_short = MODELS_AVAILABLE[current_model_index].split('/')[-1] # Get last part of model name
    msg = f"AI Model: {model_name_short}"
    logger.info(f"\n*** {msg} ***")
    show_standard_notification("NQS: Model Changed", msg, sound=audio.Reminder)
    set_processing_active_flag(False, None)

def cycle_instruction_mode():
    """Cycles through the available instruction modes."""
    global current_instruction_index, processing_active
    if processing_active:
        logger.info("Processing active, instruction mode change deferred.")
        return
    set_processing_active_flag(True, timeout_seconds=0.5)
    current_instruction_index = (current_instruction_index + 1) % len(INSTRUCTION_MODES_AVAILABLE)
    mode_name = INSTRUCTION_MODES_AVAILABLE[current_instruction_index]
    msg = f"Instruction Mode: {mode_name}"
    logger.info(f"\n*** {msg} ***")
    show_standard_notification("NQS: Instruction Mode Changed", msg, sound=audio.Reminder)
    set_processing_active_flag(False, None)

# --- Main Application Logic ---
def initialize_app():
    """Initializes the application components."""
    global root_tk # Make root_tk accessible globally for notifications
    
    logger.info("--- NQS (Nimble Query Snapshot) Initializing ---")
    if not API_KEY_HARDCODED or "AIzaS" not in API_KEY_HARDCODED: # Basic check for placeholder
        logger.critical("CRITICAL ERROR: API KEY IS NOT SET or is a placeholder!")
        # Attempt to show a Tkinter error if possible, then exit
        try:
            temp_root = tk.Tk(); temp_root.withdraw()
            messagebox.showerror("NQS Critical Error", "API Key is not configured in the script!")
            temp_root.destroy()
        except:
            print("CRITICAL ERROR: API KEY IS NOT SET or is a placeholder in the script!")
        sys.exit(1)
        
    try:
        genai.configure(api_key=API_KEY_HARDCODED)
        logger.info("Google AI SDK configured successfully.")
    except Exception as e:
        logger.critical(f"CRITICAL ERROR configuring Gemini SDK: {e}")
        try:
            temp_root = tk.Tk(); temp_root.withdraw()
            messagebox.showerror("NQS SDK Error", f"Error configuring Gemini SDK: {e}")
            temp_root.destroy()
        except:
            print(f"CRITICAL ERROR configuring Gemini SDK: {e}")
        sys.exit(1)

    logger.info(f"Default Model: {MODELS_AVAILABLE[current_model_index]}")
    logger.info(f"Default Instruction Mode: {INSTRUCTION_MODES_AVAILABLE[current_instruction_index]}")
    logger.info(f"Submit Hotkey: '{SUBMIT_HOTKEY}'")
    logger.info(f"Toggle Model Hotkey: '{TOGGLE_MODEL_HOTKEY}'")
    logger.info(f"Screenshot Hotkey: '{SCREENSHOT_HOTKEY}'")
    logger.info(f"Toggle Instruction Hotkey: '{TOGGLE_INSTRUCTION_HOTKEY}'")
    logger.warning("--- IMPORTANT: Ensure this application is run with Administrator privileges for global hotkeys to work! ---")

    # Initialize Tkinter root window (hidden) for custom notifications
    root_tk = tk.Tk()
    root_tk.withdraw() # Keep it hidden

    try:
        keyboard.add_hotkey(SUBMIT_HOTKEY, process_clipboard_and_submit_to_ai, suppress=False)
        keyboard.add_hotkey(TOGGLE_MODEL_HOTKEY, cycle_ai_model, suppress=False)
        keyboard.add_hotkey(SCREENSHOT_HOTKEY, take_fullscreen_screenshot_to_clipboard, suppress=False)
        keyboard.add_hotkey(TOGGLE_INSTRUCTION_HOTKEY, cycle_instruction_mode, suppress=False)
        logger.info("Global hotkeys registered successfully.")
        
        # Start the Tkinter main loop in the main thread.
        # This is necessary for `notification_window.after()` to work.
        # Hotkeys registered with `keyboard` library run in their own thread
        # and should continue to function.
        logger.info("NQS is active. Starting Tkinter main loop for notification handling...")
        root_tk.mainloop() 

    except Exception as e:
        logger.exception("CRITICAL ERROR during hotkey setup or Tkinter main loop:")
        try:
            if root_tk: root_tk.destroy() # Attempt to close Tkinter if it was created
            # Show error via simple notification if possible, as Tkinter might be problematic
            show_standard_notification("NQS Critical Error", f"Error: {e}. See log.", sound=audio.Error)
        except: pass # If even notifications fail, error is already logged
    finally:
        logger.info("NQS shutting down. Removing hotkeys...")
        try:
            keyboard.remove_all_hotkeys()
            logger.info("Hotkeys removed.")
        except Exception as e_hk:
            logger.error(f"Error removing hotkeys: {e_hk}")
        
        global processing_timer
        if processing_timer:
            processing_timer.cancel()
        
        if root_tk: # Ensure Tkinter is properly quit
            try:
                root_tk.quit()
            except:
                pass # If already destroyed or errored
        logger.info("NQS shutdown complete.")

if __name__ == "__main__":
    initialize_app()