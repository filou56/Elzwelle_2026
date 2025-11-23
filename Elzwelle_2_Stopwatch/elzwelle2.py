import warnings
import ttkbootstrap as ttk

with warnings.catch_warnings():
    # filter DeprecationWarning
    warnings.simplefilter("ignore", category=DeprecationWarning)
    from ttkbootstrap.tableview import Tableview
    
from ttkbootstrap.constants import SUCCESS    

# Create main window
my_w = ttk.Window()
my_w.geometry("400x300")  # Set window size




# Run the Tkinter application
my_w.mainloop()