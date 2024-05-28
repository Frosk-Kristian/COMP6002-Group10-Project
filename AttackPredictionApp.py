import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import random

from main import predictionFunc

class AttackDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attack Prediction Application")

        self.data = None
        self.predictions = None

        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self.root, text="Load Dataset", command=self.load_dataset)
        self.load_button.pack()

        self.predict_button = tk.Button(self.root, text="Predict Attacks", command=self.predict_attacks)
        self.predict_button.pack()

        self.table = tk.Text(self.root, wrap="none")
        self.table.pack()

    def load_dataset(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                print("Loading Data")
                self.data = pd.read_csv(file_path)
                print("Data Loaded succesfully")
                self.display_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load dataset:\n{str(e)}")

    def display_data(self):

        self.table.delete(1.0, tk.END)
        print("inserting data in table")
        self.table.insert(tk.END, self.data.to_string(index=False))
        print("inserting successful")

    def predict_attacks(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please load a dataset first.")
            return

        # Placeholder function to predict attacks
        self.predictions = predictionFunc(self.data)
        self.highlight_predictions()

    def highlight_predictions(self):
        self.table.tag_configure("attack", background="red")

        for index, prediction in self.predictions.items():
            #if prediction in ["DrDoS_SSDP", 'Syn', 'TFTP', 'DrDos_NTP', 'UDP-lag', 'DrDoS_DNS', 'UDPLag', 'MSSQL', 'UDP', 'Portmap', 'NetBIOS', 'DrDoS_UDP', 'DrDoS_MSSQL', 'LDAP', 'WebDDoS', 'DrDoS_SNMP', 'DrDos_NetBIOS']:
            if prediction is True:
                start = f"{index + 2}.0"
                end = f"{index + 2}.end"
                self.table.tag_add("attack", start, end)

if __name__ == "__main__":
    root = tk.Tk()
    app = AttackDetectionApp(root)
    root.mainloop()
