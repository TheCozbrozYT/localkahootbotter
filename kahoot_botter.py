import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import random
import string
import os

class KahootBotter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kahoot Botter")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Store active browser instances
        self.active_drivers = []
        self.custom_names = []
        
        # Style
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=5)
        style.configure('TEntry', padding=5)
        
        # Game PIN Entry
        ttk.Label(self.root, text="Game PIN:").pack(pady=5)
        self.pin_entry = ttk.Entry(self.root)
        self.pin_entry.pack(pady=5)
        
        # Number of Bots Entry
        ttk.Label(self.root, text="Number of Bots:").pack(pady=5)
        self.bots_entry = ttk.Entry(self.root)
        self.bots_entry.pack(pady=5)
        
        # Names File Frame
        names_frame = ttk.Frame(self.root)
        names_frame.pack(pady=5, fill='x', padx=20)
        
        self.names_path = tk.StringVar()
        ttk.Label(names_frame, text="Custom Names File (Optional):").pack(side='top', pady=2)
        names_entry = ttk.Entry(names_frame, textvariable=self.names_path)
        names_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        browse_btn = ttk.Button(names_frame, text="Browse", command=self.browse_names_file)
        browse_btn.pack(side='right')
        
        # Start Button
        self.start_button = ttk.Button(self.root, text="Start Botting", command=self.start_botting)
        self.start_button.pack(pady=20)
        
        # Stop Button
        self.stop_button = ttk.Button(self.root, text="Stop & Exit", command=self.stop_botting, state='disabled')
        self.stop_button.pack(pady=5)
        
        # Status Label
        self.status_label = ttk.Label(self.root, text="Status: Ready")
        self.status_label.pack(pady=10)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.root, length=300, mode='determinate')
        self.progress.pack(pady=10)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def browse_names_file(self):
        filename = filedialog.askopenfilename(
            title="Select Names File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filename:
            self.names_path.set(filename)
    
    def load_custom_names(self):
        """Load custom names from file if provided"""
        path = self.names_path.get().strip()
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.custom_names = [line.strip() for line in f if line.strip()]
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load names file: {e}")
                return False
        return True
    
    def generate_name(self):
        """Generate a random bot name or pick from custom names"""
        if self.custom_names:
            return random.choice(self.custom_names)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    def join_game(self, pin, bot_number):
        """Join a Kahoot game with the given PIN"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Run in headless mode
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            
            # Store driver instance
            self.active_drivers.append(driver)
            
            # Navigate to Kahoot
            driver.get('https://kahoot.it')
            time.sleep(2)  # Wait for page to fully load
            
            # Wait for and enter game PIN
            try:
                pin_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "gameId"))
                )
            except:
                pin_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "game-input"))
                )
            pin_input.send_keys(pin)
            
            # Click join button - try multiple possible selectors
            try:
                join_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-functional-selector='join-game-pin']"))
                )
            except:
                try:
                    join_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                    )
                except:
                    join_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".enter-pin__form-button"))
                    )
            join_button.click()
            
            time.sleep(2)  # Wait for transition
            
            # Wait for and enter nickname
            try:
                nickname_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "nickname"))
                )
            except:
                nickname_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "nickname"))
                )
            
            bot_name = f"{self.generate_name()}_{bot_number}"
            nickname_input.send_keys(bot_name)
            
            # Click final join button - try multiple possible selectors
            try:
                join_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )
            except:
                try:
                    join_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".join-button__button"))
                    )
                except:
                    join_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-functional-selector='join-button-game']"))
                    )
            join_button.click()
            
            time.sleep(2)  # Wait to ensure join is complete
            return True
            
        except Exception as e:
            print(f"Error joining game: {e}")
            if driver in self.active_drivers:
                self.active_drivers.remove(driver)
            driver.quit()
            return False
    
    def stop_botting(self):
        """Stop all bots and close the program"""
        self.status_label.config(text="Status: Stopping bots...")
        self.root.update()
        
        # Close all browser instances
        for driver in self.active_drivers:
            try:
                driver.quit()
            except:
                pass
        self.active_drivers.clear()
        
        self.root.quit()
    
    def on_closing(self):
        """Handle window close event"""
        self.stop_botting()
    
    def start_botting(self):
        """Start the botting process"""
        try:
            pin = self.pin_entry.get().strip()
            num_bots = int(self.bots_entry.get().strip())
            
            if not pin or not num_bots:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            if num_bots <= 0 or num_bots > 100:
                messagebox.showerror("Error", "Number of bots must be between 1 and 100")
                return
            
            # Load custom names if provided
            if not self.load_custom_names():
                return
            
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.progress['maximum'] = num_bots
            self.progress['value'] = 0
            
            def bot_thread():
                success_count = 0
                for i in range(num_bots):
                    self.status_label.config(text=f"Status: Adding bot {i+1}/{num_bots}")
                    if self.join_game(pin, i+1):
                        success_count += 1
                    self.progress['value'] = i + 1
                    self.root.update()
                    time.sleep(1.5)  # Delay between bots to avoid detection
                
                self.status_label.config(text=f"Status: Running! Added {success_count}/{num_bots} bots")
            
            threading.Thread(target=bot_thread, daemon=True).start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    botter = KahootBotter()
    botter.run()
