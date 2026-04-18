import tkinter as tk
from tkinter import messagebox, ttk
import tinytuya, json, asyncio, threading, time, mss, mss.tools

SETTINGS = 'settings.json'
DEVICES = 'deviceData.json'

class mainApp:
    def __init__(self, root):
        self.started=False
        self.root = root

        root.minsize(300, 300)
        
        self.settings_parse()
        self.create_UI()
        self.initialize_device()

        self.statusbar_controller()

    def createDummyData(self):
        with open(DEVICES, 'w') as file:
            file.write(json.dumps({
                "id": 'skfmsdf123n34jnfs65l',
                'last_ip': '192.168.0.1',
                'key': 'skfmsdf123n34jnfs65l',
                'min_brightness':'255',
                'max_brightness':'0'
            }))
    
    def settings_parse(self):
        with open(DEVICES) as data:
            if data is not None: 
                try:
                    self.device = json.load(data)
                except (FileNotFoundError, json.JSONDecodeError):
                    self.createDummyData()
                    self.device = {
                        "id": 'skfmsdf123n34jnfs65l',
                        'last_ip': '192.168.0.1',
                        'key': 'skfmsdf123n34jnfs65l',
                        'min_brightness':'255',
                        'max_brightness':'0'
                    }
        with open(SETTINGS) as data:
            self.mode = tk.StringVar(value=json.load(data)['mode'])
        


    def create_UI(self):
        self.status = tk.StringVar(value='Loading...')
        self.statusbar = tk.Frame(root, relief='ridge', borderwidth=2) #bottom status bar
        self.statusbar.pack(side='bottom', fill='x')
        self.status_field = tk.Label(self.statusbar, textvariable=self.status)
        self.status_field.pack(anchor='w')

        mode_title = ttk.Label(root, text='Mode selection:')
        mode_title.pack(anchor='w')
        self.mode_selection = tk.Frame(root)#mode selector
        self.osc_button = ttk.Radiobutton(
            self.mode_selection,
            text='OSC',
            variable=self.mode,
            value = 'OSC',
            command=self.setting_change
        )
        self.sc_button = ttk.Radiobutton(
            self.mode_selection,
            text='Screen capture',
            variable=self.mode,
            value='SC',
            command=self.setting_change
        )
        self.mode_selection.pack(anchor='w')
        self.osc_button.grid(column='1', row='0');self.sc_button.grid(column='2', row='0')

        self.device_grid=ttk.Frame(root)
        id_text = ttk.Label(self.device_grid, text="Device ID:")
        self.id_field = ttk.Entry(self.device_grid)#id field
        self.id_field.insert(0, self.device['id'])
        id_text.grid(sticky='w', row=0, columnspan=2); self.id_field.grid(sticky='ew', padx=5, pady=5, row=1, columnspan=2)

        ip_text = ttk.Label(self.device_grid, text="Device IP:")
        self.ip_field = ttk.Entry(self.device_grid)#ip field
        self.ip_field.insert(0, self.device['last_ip'])
        ip_text.grid(sticky='w', row=2, columnspan=2); self.ip_field.grid(sticky='ew', padx=5, pady=5, row=3, columnspan=2)

        key_text = ttk.Label(self.device_grid, text='Device Key:')
        self.key_field = ttk.Entry(self.device_grid)#key field
        self.key_field.insert(0, self.device['key'])
        key_text.grid(sticky='w', row=4, columnspan=2); self.key_field.grid(sticky='ew', padx=5, pady=5, row=5, columnspan=2)

        max_bright_text = ttk.Label(self.device_grid, text='Maximum brightness')
        self.max_bright_field = ttk.Entry(self.device_grid)#brightness fields
        self.max_bright_field.insert(0, self.device['max_brightness'])

        min_bright_text = ttk.Label(self.device_grid, text='Minimum brightness')
        self.min_bright_field = ttk.Entry(self.device_grid)
        self.min_bright_field.insert(0, self.device['min_brightness'])

        max_bright_text.grid(sticky='w', row=6, column=0); self.max_bright_field.grid(sticky='ew', column=0, padx=5, pady=5, row=7)
        min_bright_text.grid(sticky='w', row=6, column=1); self.min_bright_field.grid(sticky='ew', column=1, padx=5, pady=5, row=7)

        self.device_grid.columnconfigure(0, weight=1)
        self.device_grid.columnconfigure(1, weight=1)
        self.device_grid.pack(fill='x', expand=True, anchor='n')

        self.buttons_grid = ttk.Frame(root)
        self.apply_button = ttk.Button(self.buttons_grid, text='Apply device settings', command=self.save_settings)
        self.apply_button.grid(row=0, column=0, padx=5)

        self.start_button = ttk.Button(self.buttons_grid, text='Start the program', command=self.start)
        self.start_button.grid(row=0, column=1, padx=5)

        self.buttons_grid.pack(pady=5)

    def setting_change(self):
        with open(SETTINGS, 'w') as file:
            new_file = json.dumps({
                "mode": self.mode.get()
            })
            file.write(new_file)
            

    def statusbar_controller(self, new_status='Loaded'): 
        self.status.set(new_status)


    def save_settings(self):
        with open(DEVICES, 'w') as file:
            file.write(json.dumps({
                "id": self.id_field.get(),
                'last_ip': self.ip_field.get(),
                'key': self.key_field.get(),
                'min_brightness':self.min_bright_field.get(),
                'max_brightness':self.max_bright_field.get()
            }))

    
    def start(self):
        if not self.started:
            thread = threading.Thread(target=self.screen_capture, daemon=True)
            thread.start()
            self.statusbar_controller('Running...')
        #else:
        #    thread.destroy()

    def screen_capture(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            
            while self.started:
                sct_img = sct.grab(monitor)
                
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                img = img.resize((1, 1), resample=Image.BILINEAR)
                color = img.getpixel((0, 0)) 
                

                self.update_tuya_device(color)
                time.sleep(0.1)
                
    def update_tuya_device(self, color):
        try:
            d.set_white(*self.process_cct(r, g, b))
        except Exception as e:
            print(f"Failed to send update: {e}")
        
    def initialize_device(self):
        d = tinytuya.BulbDevice(
        dev_id=self.device['id'],
        address=self.device['last_ip'],
        local_key=self.device['key'],
        version=3.3
        )
        d.set_socketPersistent(True)

    def process_cct(self, r, g, b):
        # 1. Calculate Perceived Brightness (Luminance)
        # Human eyes see green as brighter than blue
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        
        # 2. Map luminance to your UI Max/Min brightness settings
        # Assuming self.device['min_br'] and max_br are strings from your Entry fields
        min_b = int(self.device.get('min_br', 0))
        max_b = int(self.device.get('max_br', 255))
        
        # Simple linear scale
        brightness = int(min_b + (luminance / 255) * (max_b - min_b))

        # 3. Simple Color Temp approximation
        # If Blue > Red, it's a "Cool" screen (high temp)
        # If Red > Blue, it's a "Warm" screen (low temp)
        # Tuya 'color_temp' usually 0 (warm) to 1000 (cool)
        if (r + b) > 0:
            temp_ratio = b / (r + b + 0.1) # Avoid div by zero
        else:
            temp_ratio = 0.5
            
        color_temp = int(temp_ratio * 1000)
        
        return brightness, color_temp

root = tk.Tk()
app = mainApp(root)
root.mainloop()