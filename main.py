import tkinter as tk
from tkinter import messagebox, ttk
import tinytuya, json, asyncio, threading
from PIL import ImageGrab

SETTINGS = 'settings.json'
DEVICES = 'deviceData.json'

class mainApp:
    def __init__(self, root):
        self.root = root

        self.load_config()
        self.create_UI()
        #self.initialize_vars()

        self.running = False
        self.root.title('Main App')
        #root.geometry('800x600')

        #UI Elements
        self.label = tk.Label(root, text="Use the button below to start capture", fg="red")
        self.label.pack(pady=10)
        
        self.btn = tk.Button(root, text="Start Sync")
        self.btn.pack(pady=10)
        root.minsize('320', '200')

        self.status.set('Loaded.')
    
    def load_config(self):
        with open(DEVICES) as data: 
            self.devices = json.load(data)
        with open(SETTINGS) as data:
            self.mode = tk.StringVar(value=json.load(data)['mode'])
        
    
    def create_UI(self):
        self.status = tk.StringVar(value='Loading...')
        self.statusbar = tk.Frame(root, relief='ridge', borderwidth=2) #bottom status bar
        self.statusbar.pack(side='bottom', fill='x')
        self.status_field = tk.Label(self.statusbar, textvariable=self.status)
        self.status_field.pack(anchor='w')

        self.mode_selection = tk.Frame(root)#mode selector
        self.osc_button = tk.Radiobutton(
            self.mode_selection,
            text='OSC',
            variable=self.mode,
            value = 'OSC',
            command=self.setting_change
        )
        self.sc_button = tk.Radiobutton(
            self.mode_selection,
            text='Screen capture',
            variable=self.mode,
            value='SC',
            command=self.setting_change
        )
        self.mode_selection.pack()
        self.osc_button.grid(column='1', row='0');self.sc_button.grid(column='2', row='0')

        self.settings_button=tk.Button(root, text="Settings", command=self.device_setup)
        self.settings_button.pack()

    def setting_change(self):
        with open(SETTINGS, 'w') as file:
            new_file = json.dumps({
                "mode": self.mode.get()
            })
            file.write(new_file)

    def device_setup(self):
        self.status.set('Opening settings window...')
        self.device_setup_screen()

    def device_setup_screen(self):
        if self.settings is not None and self.settings.winfo_exists():
            self.settings.lift() 
            self.settings.focus_force() 
        else:
            self.settings = tk.Toplevel(self.root)
            self.settings.title("Add New Device")
            self.settings.minsize(200, 100)

        device_data = tk.Frame(self.settings)
        id_text=tk.Label(device_data, text='Device ID:')
        id_text.pack(anchor='w')
        id_entry = tk.Entry(device_data)
        id_entry.pack()
        
        device_data.pack()

        self.status.set('Starting device scan...')

        def scan_for_devices():
            self.scan = True
            self.scan_results = tinytuya.deviceScan()

        self.scan_results = None
        if messagebox.askyesno(title='Start device scan?', message='Do you want to automatically scan for the devices on the network?'):
            threading.Thread(target=scan_for_devices, daemon=True).start()
            self.check_scan_status()
            self.wait=tk.Toplevel()
            self.wait.title("Please wait...")
            pb = ttk.Progressbar(self.wait,mode="indeterminate",length=250)
            self.wait.protocol("WM_DELETE_WINDOW", self.abort_scan)
            pb.pack(); pb.start()

    def check_scan_status(self):
        if self.scan_results is not None:
            if scan:
                self.status.set("Scan complete.")
                self.scan = False 
                self.scan_completed(self)
        else:
            self.root.after(100, self.check_scan_status)

    def scan_completed(self):
        print('heh')

    def abort_scan(self):
        if self.scan:
            if messagebox.askyesno(title='Cancel scan?', message='Do you want to cancel device scan?'):
                self.wait.destroy()
                self.scan = False
                self.status.set("Scan aborted.")
            else: self.wait.destroy()
        else: self.wait.destroy()

root = tk.Tk()
app = mainApp(root)
root.mainloop()