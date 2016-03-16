#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
######## TODO ########
- add Titles to data entry and tools grid slots
- make the plots better looking
- suggest low and high intercept values (fit a high order polynomial)
- programatically set the width of the rp plot based on the input recip values
- add choice of MIEC and Electrolyte
- set program up to work cross platform with file handling. 'initialdir' option.
- fix twin axis for Rp plot
- rework Nyquist stack plot
- Add peak labeling for isotherms and nyquist stack
- handle hidden files
"""

import pandas as pd
import numpy as np
import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import pickle
from matplotlib.ticker import ScalarFormatter  #needed to format y axis log to scalar

#class Electrolyte:

#class Miec:

class SampleData:
    """ Describes a sample that has been test with EIS.

    SampleData objects that are saved and operated on by the application.

    Public variables:
    dir_path -- directory where the EIS files are saved
    sample_name -- name given to the sample by the user
    cathode_area -- Geometric area of the cathode (in cm^2)
    intercept_1_list -- list of lower intercepts calculated from Nyquist plots
    intercept_2_list -- list of higher intercepts calculated from Nyquist plots
    temperature_range -- list of temperatures the sample was tested at
    temperature_range_text -- list of testing temperatures as strings with units
    low_intercept_entries -- list of Tkinter entery fields for low intercepts
    high_intercept_entries -- list of Tkinter entry fields for high intercepts
    """

    def __init__(self, path, name, area, temp_range, auto_generated_file): #add more like intercept points later
        """ Set variables from new or opened sample. """
        self.dir_path = path
        self.sample_name = name
        self.cathode_area = area
        self.auto_generated = auto_generated_file
        self.intercept_1_list = []
        self.intercept_2_list = []
        self.temperature_range = temp_range
        self.temperature_range_text = []
        self.low_intercept_entries = []
        self.high_intercept_entries = []
        for temperature in self.temperature_range:
            self.temperature_range_text.append(str(temperature) + "°C")


class NewSample(simpledialog.Dialog):
    """ Display a dialog window to create a new sample. """

    def body(self, master):
        """ Set up sample dialog window visuals and entries. """
        #defining options for opening a directory
        self.dir_opt = options = {}
        #options['initialdir'] = 'C:\\' #Windows
        options['initialdir'] = '~/'
        options['mustexist'] = False
        options['parent'] = master
        options['title'] = 'Select EIS Data Directory'

        tk.Label(master, text="Sample Name:",).grid(row=0)
        tk.Label(master, text="Cathode Area:").grid(row=1)
        tk.Label(master, text="Minimum Temperature:",).grid(row=2)
        tk.Label(master, text="Maximum Temperature:",).grid(row=3)
        tk.Label(master, text="Temperature Step Size:",).grid(row=4)
        tk.Label(master, text="Automatically Collected File? ").grid(row=5)
        tk.Label(master, text="Directory Path:").grid(row=6)

        self.name_entry = tk.Entry(master)
        self.area_entry = tk.Entry(master)
        self.temp_min_entry = tk.Entry(master)
        self.temp_max_entry = tk.Entry(master)
        self.temp_step_entry = tk.Entry(master)
        self.path_entry = tk.Entry(master)


        self.name_entry.grid(row=0, column=1)
        self.area_entry.grid(row=1, column=1)
        self.temp_min_entry.grid(row=2, column=1)
        self.temp_max_entry.grid(row=3, column=1)
        self.temp_step_entry.grid(row=4, column=1)
        self.path_entry.grid(row=6, column=1)
        self.browse_button = tk.Button(master, text="Browse", command=self.browse).grid(row=6, column = 2)

        self.auto_generated_file = tk.IntVar()
        self.auto_generated_checkbox = tk.Checkbutton(
            master,
            variable = self.auto_generated_file,)
        self.auto_generated_checkbox.grid(row=5, column=1)

        return self.name_entry # initial focus

    def apply(self):
        """ Accept the entered values and initialize a sample."""
        path = str(self.path_entry.get())
        name = str(self.name_entry.get())
        area = float(self.area_entry.get())
        t_min = int(self.temp_min_entry.get())
        t_max = int(self.temp_max_entry.get())
        t_step = int(self.temp_step_entry.get())
        temperatures = list(range(t_min, t_max+1, t_step))
        auto_gen = self.auto_generated_file.get()
        if sample_data: app.tear_down_data_panel()
        global sample_data
        sample_data = SampleData(path, name, area, temperatures,auto_gen)
        app.set_up_data_panel()

    def browse(self):
        """ Select a director with EIS files and output to entry"""
        path = filedialog.askdirectory(**self.dir_opt)
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, path)


class Application:
    """ Main Tkinter Application

    Parent application that contains the main windows and menu bar.
    """

    def __init__(self, parent):
        """ Set up menu bar, grid in main window, and placeholders. """
        #set up parent variable
        self.parent = parent

        #set up menubar
        self.menu_bar = tk.Menu(self.parent)
        #file menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New...", command=self.new_sample)
        self.file_menu.add_command(label="Open...", command=self.open_sample)
        self.file_menu.add_command(label="Save", command=self.save_sample)
        self.file_menu.add_separator()

        self.parent.bind("<Command-o>", self.open_sample)
        self.parent.bind("<Command-n>", self.new_sample)

        #save image menu
        self.save_image_menu = tk.Menu(self.file_menu, tearoff=0)
        self.save_image_menu.add_command(label="Save Nyquist Plot", command=self.save_isotherm)
        self.save_image_menu.add_command(label="Save Nyquist Stack", command=self.save_nyquist_stack)
        self.save_image_menu.add_command(label="Save Rp Plot", command=self.save_rp)
        self.file_menu.add_cascade(label="Save Image", menu = self.save_image_menu)

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.parent.destroy)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.parent.config(menu=self.menu_bar)

        #set up top level panels
        self.grid_padx = '10m'
        self.grid_pady = '1m'

        self.data_panel = tk.Frame(self.parent)
        self.data_panel.grid(row=0, column = 0, padx=self.grid_padx)

        self.isotherm_plot = tk.Frame(self.parent)
        self.isotherm_plot.grid(row=0, column = 1, padx=self.grid_padx)

        self.tools_panel = tk.Frame(self.parent)
        self.tools_panel.grid(row = 1, column = 0, padx=self.grid_padx)

        self.rp_plot = tk.Frame(self.parent)
        self.rp_plot.grid(row = 1, column = 1, padx=self.grid_padx, pady=self.grid_pady)

        #initialize and set up data panel if possible

        self.label_list = []
        self.low_intercept_entry_list = []
        self.high_intercept_entry_list = []
        self.plot_button_list = []

        if sample_data:
            self.set_up_data_panel()

        #set up tools panel
        tk.Label(self.tools_panel, text="Plot Rp", anchor=tk.N).grid(row=0, column=0, columnspan = 3)
        tk.Label(self.tools_panel, text="Select Marker Color: ", anchor=tk.N).grid(row=1, column=0)
        tk.Label(self.tools_panel, text="Select Marker Style: ", anchor=tk.N).grid(row=2, column=0)

        #drop downs for color and symbol
        self.marker_color = tk.StringVar()
        self.marker_color.set("black") #initialize
        self.marker_style = tk.StringVar()
        self.marker_style.set("o") #initialize
        self.marker_color_selector = tk.OptionMenu(self.tools_panel, self.marker_color, "black", "red", "blue", "green", "yellow", "magenta", "cyan").grid(row=1, column = 1, columnspan = 2, sticky = tk.W)
        self.marker_style_selector = tk.OptionMenu(self.tools_panel, self.marker_style, "o", "^", "s", "+", "x", "d", ".").grid(row=2, column = 1, columnspan = 2, sticky = tk.W)

        #checkbox to make a new plot
        self.new_plot = tk.IntVar()
        self.new_plot_checkbox = tk.Checkbutton(self.tools_panel, text="Plot Rp on new plot?", variable = self.new_plot).grid(row=3, column = 0, columnspan = 3, sticky = tk.W)
        self.new_plot.set(1)

        self.plot_rp_button = tk.Button(self.tools_panel, text="Plot Rp", command=self.plot_rp, padx='3m', pady='3m').grid(row=4, column = 0, columnspan=3, pady='3m')

        #set up isotherm figure
        self.isotherm_figure = Figure(figsize=(6,4), facecolor='w')
        self.isotherm_axes = self.isotherm_figure.add_subplot(111)
        self.isotherm_figure.tight_layout(pad = 4) #possibly change to set_tight_layout and repeat below
        self.isotherm_canvas = FigureCanvasTkAgg(self.isotherm_figure, self.isotherm_plot)
        self.isotherm_canvas.show()
        self.isotherm_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        #set up Rp figure
        self.rp_figure = Figure(figsize=(7,5), facecolor='w')
        self.rp_axes = self.rp_figure.add_subplot(111)
        self.rp_axes_twin = self.rp_axes.twiny()
        self.rp_figure.tight_layout(pad = 3.5)
        self.rp_canvas = FigureCanvasTkAgg(self.rp_figure, self.rp_plot)
        self.rp_canvas.show()
        self.rp_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def set_up_data_panel(self):
        """ Set up the data panel for a sample.

        Create four columns iteratively over the temperature range:
        1) temperature label
        2) low intercept input
        3) high temperature input
        4) plot button to plot nyquist plot
        """

        #set up the row of labels
        tk.Label(self.data_panel, text="Temp.", anchor=tk.W).grid(row=0, column=0)
        tk.Label(self.data_panel, text="Low Intercept", anchor=tk.N).grid(row=0, column=1)
        tk.Label(self.data_panel, text="High Intercept", anchor=tk.N).grid(row=0, column=2)

        row = 1
        for temperature in sample_data.temperature_range_text:
            label = tk.Label(self.data_panel, text=temperature, anchor=tk.W)
            label.grid(row=row, column=0)
            low_intercept = tk.Entry(self.data_panel, width=6)
            high_intercept = tk.Entry(self.data_panel, width=6)
            low_intercept.grid(row=row, column = 1)
            high_intercept.grid(row=row, column = 2)

            #set the plot button lambda 'manually'
            if row == 1: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(1))
            elif row == 2: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(2))
            elif row == 3: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(3))
            elif row == 4: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(4))
            elif row == 5: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(5))
            elif row == 6: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(6))
            elif row == 7: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(7))
            elif row == 8: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(8))
            elif row == 9: plot_button = tk.Button(self.data_panel,
                                                   text='Plot', takefocus=0,
                                                   command=lambda:
                                                   self.plot_isotherm(9))
            elif row ==10: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(10))
            elif row ==11: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(11))
            elif row ==12: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(12))
            elif row ==13: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(13))
            elif row ==14: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(14))
            elif row ==15: plot_button = tk.Button(self.data_panel, text='Plot', takefocus=0, command=lambda: self.plot_isotherm(15))

            plot_button.grid(row=row, column =3)

            self.label_list.append(label)
            self.low_intercept_entry_list.append(low_intercept)
            self.high_intercept_entry_list.append(high_intercept)
            self.plot_button_list.append(plot_button)

            row = row + 1

    def tear_down_data_panel(self):
        """ Remove the data panel items for Nyquist plot data.

        First, iteratively destroy all of the widgets in the list.
        Second, clear the lists.
        """
        for label, low_int, high_int, button in zip(self.label_list, self.low_intercept_entry_list, self.high_intercept_entry_list, self.plot_button_list):
            label.grid_forget()
            low_int.grid_forget()
            high_int.grid_forget()
            button.grid_forget()
            label.destroy()
            low_int.destroy()
            high_int.destroy()
            button.destroy()

        self.label_list = []
        self.low_intercept_entry_list = []
        self.high_intercept_entry_list = []
        self.plot_button_list = []

    def plot_rp(self):
        """Plot the Rp in the figure panel.

        Get the resistance entries from Nyquist plots,
        calculate recriprocal temperatures and Rp,
        setup and plot the values nicely with twin axes
        """

        self.get_entries()
        recip_temperatures, asr = get_rp_plot_data()
        if self.new_plot.get():
            self.rp_axes.clear()
            self.rp_axes_twin.clear()

        #self.rp_axes.set_title(r"R$\mathregular{_p}$ of " + sample_data.sample_name, y=1.16)
        self.rp_axes.set_xlabel(r"Temperature $\mathregular{(1000/T)\ (K}^{-1}\mathregular{)}$")
        self.rp_axes.set_ylabel(r"$\mathregular{R_p}$ $\mathregular{(\Omega cm^2\!)}$")
        self.rp_axes.set_yscale('log')
        self.rp_axes.yaxis.set_major_formatter(ScalarFormatter())
        self.rp_axes.ticklabel_format(axis='y', style='plain')
        x_min = np.around(np.amin(recip_temperatures),decimals=2) - 0.02
        x_max = np.around(np.amax(recip_temperatures),decimals=2) + 0.02
        self.rp_axes.axis([x_min, x_max, 0.011, 15])
        self.rp_axes.tick_params(direction='out', which='both')
        self.rp_axes.axhline(y=0.1, linestyle='--', color='0.6')
        #plot
        self.rp_axes.plot(recip_temperatures, asr, marker=self.marker_style.get(), markersize=6, color=self.marker_color.get(), linestyle="None", label=sample_data.sample_name)
        self.rp_axes.legend(loc='upper left', numpoints = 1, fontsize='small',)

        #twin axes to go to celsius
        celsius_tick_locations = recip_temperatures
        self.rp_axes_twin.axis([x_min, x_max, 0.011, 15])
        self.rp_axes_twin.tick_params(direction='out', which='both')
        self.rp_axes_twin.set_xticks(celsius_tick_locations)
        self.rp_axes_twin.set_xticklabels([400,'',450,'',500,'',550,'',600,'',650,'',700])
        self.rp_axes_twin.set_xlabel(r'Temperature (°C)')


        self.rp_canvas.show()
        self.rp_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def plot_isotherm(self, button_number):
        """ Draw a Nyquist plot for the isotherm chosen. """
        if sample_data :
            self.isotherm_axes.clear()

            #get new data
            file_path, temperature = self.eis_file_path(button_number, sample_data.dir_path)
            raw_data = get_isotherm_plot_data(file_path)

            self.active_isotherm_temperature = temperature
            self.isotherm_axes.set_title(sample_data.sample_name + " at " + temperature, y=1.08)
            self.isotherm_axes.set_xlabel("Z\' $\mathregular{(\Omega cm^2\!)}$")
            self.isotherm_axes.set_ylabel("-Z\'\' $\mathregular{(\Omega cm^2\!)}$")
            self.isotherm_axes.set_aspect('equal',)# adjustable='box')
            self.isotherm_axes.plot(raw_data.iloc[:,0], raw_data.iloc[:,1], marker='.', markersize=9, color='black', linestyle="None")
            #square the axes
            xmin, xmax, ymin, ymax = self.isotherm_axes.axis()
            if (ymax-ymin) > (xmax-xmin):
                xmax = xmin + (ymax-ymin)
            else:
                ymax = ymin + (xmax-xmin)
            self.isotherm_axes.axis([xmin, xmax, ymin, ymax])
            self.isotherm_axes.tick_params(direction='out')

            #label peaks

            self.isotherm_canvas.show()
            self.isotherm_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def plot_nyquist_stack(self):
        """ Make three Nyquist plots from chosen temperatures. """
        #change the button numbers passed to EIS data to correspond to the desired nyquist stack temperatures + 1.
        #.e.g.: find that 600˚C is index '2' in sample_data.temperature_range, pass 2+1
        #allow for selectable temperatures?
        if sample_data :
            #Set 1
            #get new data
            file_path, temperature = self.eis_file_path(1, sample_data.dir_path)
            raw_data = get_isotherm_plot_data(file_path)
            self.active_isotherm_temperature = temperature
            #plot new plot
            self.nyquist_stack_500_axes.set_aspect('equal',)# adjustable='box')
            self.nyquist_stack_500_axes.plot(raw_data.iloc[:,0], raw_data.iloc[:,1], marker='.', markersize=9, color='black', linestyle="None")
            #square the axes
            xmin, xmax, ymin, ymax = self.nyquist_stack_500_axes.axis()
            if (ymax-ymin) > (xmax-xmin):
                xmax = xmin + (ymax-ymin)
            else:
                ymax = ymin + (xmax-xmin)
            self.nyquist_stack_500_axes.axis([xmin, xmax, ymin, ymax])
            self.nyquist_stack_500_axes.tick_params(direction='out')

            #Set 2
            file_path, temperature = self.eis_file_path(5, sample_data.dir_path)
            raw_data = get_isotherm_plot_data(file_path)
            self.active_isotherm_temperature = temperature
            self.nyquist_stack_600_axes.set_aspect('equal',)# adjustable='box')
            self.nyquist_stack_600_axes.plot(raw_data.iloc[:,0], raw_data.iloc[:,1], marker='.', markersize=9, color='black', linestyle="None")
            xmin, xmax, ymin, ymax = self.nyquist_stack_600_axes.axis()
            if (ymax-ymin) > (xmax-xmin):
                xmax = xmin + (ymax-ymin)
            else:
                ymax = ymin + (xmax-xmin)
            self.nyquist_stack_600_axes.axis([xmin, xmax, ymin, ymax])
            self.nyquist_stack_600_axes.tick_params(direction='out')

            #Set 3
            file_path, temperature = self.eis_file_path(9, sample_data.dir_path)
            raw_data = get_isotherm_plot_data(file_path)
            self.active_isotherm_temperature = temperature
            self.nyquist_stack_700_axes.set_aspect('equal',)# adjustable='box')
            self.nyquist_stack_700_axes.plot(raw_data.iloc[:,0], raw_data.iloc[:,1], marker='.', markersize=9, color='black', linestyle="None")
            xmin, xmax, ymin, ymax = self.nyquist_stack_700_axes.axis()
            if (ymax-ymin) > (xmax-xmin):
                xmax = xmin + (ymax-ymin)
            else:
                ymax = ymin + (xmax-xmin)
            self.nyquist_stack_700_axes.axis([xmin, xmax, ymin, ymax])
            self.nyquist_stack_700_axes.tick_params(direction='out')

    def new_sample(self, event=None):
        """ Open the dialog to create a new sample. """
        NewSample(self.parent)

    def eis_file_path(self, button_number, dir_path):
        """Return EIS file path and the temperature for the button pressed. """
        #print(os.path.join(dir_path, os.listdir(dir_path)[button_number-1])) #debug file location
        file_path = os.path.join(dir_path, os.listdir(dir_path)[button_number-1])
        temperature = sample_data.temperature_range_text[button_number-1]

        return file_path, temperature

    def get_entries(self):
        """Set the values of the sample's intercepts by reading the entries."""
        intercept_1_entries = self.low_intercept_entry_list
        intercept_2_entries = self.high_intercept_entry_list
        sample_data.intercept_1_list = []
        sample_data.intercept_2_list = []

        for intercept_1_entry, intercept_2_entry in zip(intercept_1_entries, intercept_2_entries):
            if intercept_1_entry.get() is "":
                sample_data.intercept_1_list.append(0.0)
            else:
                sample_data.intercept_1_list.append(float(intercept_1_entry.get()))
            if intercept_2_entry.get() is "":
                sample_data.intercept_2_list.append(0.0)
            else:
                sample_data.intercept_2_list.append(float(intercept_2_entry.get()))

    def set_entries(self):
        """ Set the entry fields from the saved sample values. """
        intercept_1_entries = self.low_intercept_entry_list
        intercept_2_entries = self.high_intercept_entry_list

        for intercept_1_entry, intercept_2_entry, intercept_1_value, intercept_2_value in zip(intercept_1_entries, intercept_2_entries, sample_data.intercept_1_list, sample_data.intercept_2_list):
            intercept_1_entry.delete(0,"end")
            intercept_2_entry.delete(0,"end")
            intercept_1_entry.insert(0,str(intercept_1_value))
            intercept_2_entry.insert(0,str(intercept_2_value))

    def save_sample(self):
        """ Run a dialog to write sample data to the disk. """
        self.file_opt = options = {}
        options['defaultextension'] = '.p'
        options['filetypes'] = [('Resistance Plotter Files', '.p')]
        #options['initialdir'] = 'C:\\' #Windows
        options['initialdir'] = '~/'
        options['initialfile'] = sample_data.sample_name + '.p'
        options['parent'] = root
        options['title'] = 'Save Resistance Plotter File'

        try:
            file, filename = self.ask_save_filename()
            self.get_entries()
            global sample_data
            pickle.dump(sample_data, file)
            file.close()
        except TypeError:
            pass

    def save_rp(self):
        """ Run a dialog to write an image of the Rp plot to the disk. """
        self.file_opt = options = {}
        options['defaultextension'] = '.png'
        options['filetypes'] = [('Portable Network Graphics', '.png'), ('Portable Document Format','.pdf'), ('Encapsulated PostScript','.eps')]
        #options['initialdir'] = 'C:\\' #Windows
        options['initialdir'] = '~/'
        options['initialfile'] = sample_data.sample_name + "_rp" + '.png'
        options['parent'] = root
        options['title'] = 'Save Rp Plot'
        try:
            file, filename = self.ask_save_filename()
            ext = filename.rsplit('.',1)[1] #detect file type
            self.rp_canvas.print_figure(file, dpi=200, format=ext)
            file.close()
        except TypeError:
            pass

    def save_isotherm(self):
        """ Run a dialog to write a Nyquist isotherm to disk. """
        self.file_opt = options = {}
        options['defaultextension'] = '.png'
        options['filetypes'] = [('Portable Network Graphics', '.png'), ('Portable Document Format','.pdf'), ('Encapsulated PostScript','.eps')]
        options['initialdir'] = '~/'
        #options['initialdir'] = 'C:\\' #Windows
        options['initialfile'] = sample_data.sample_name + "_nyquist_" + self.active_isotherm_temperature +'.png'
        options['parent'] = root
        options['title'] = 'Save Nyquist Plot'
        try:
            file, filename = self.ask_save_filename()
            ext = filename.rsplit('.',1)[1]  #detect file type
            self.isotherm_canvas.print_figure(file, dpi=200, format=ext)
            file.close()
        except TypeError:
            pass

    def save_nyquist_stack(self):
        """ Configure, display, and write the Nyquist plot stack to disk. """
        self.nyquist_stack_plot = tk.Frame(self.parent)
        #self.nyquist_stack_plot.grid(row=0, column = 2, padx=self.grid_padx, pady=self.grid_pady)
        #set up nyquist stack figure
        self.nyquist_stack_figure = Figure(figsize=(6,6), facecolor='w')
        self.nyquist_stack_500_axes = self.nyquist_stack_figure.add_axes([.14, .15, .8, .8])
        self.nyquist_stack_600_axes = self.nyquist_stack_figure.add_axes([.46, .46, .45, .45])
        self.nyquist_stack_700_axes = self.nyquist_stack_figure.add_axes([.65, .65, .23, .23])
        self.nyquist_stack_figure.text(.15, .905, r"500°C", size = 12)
        self.nyquist_stack_figure.text(.47, .87, r"600°C", size = 12)
        self.nyquist_stack_figure.text(.665, .84, r"700°C", size = 12)
        self.nyquist_stack_canvas = FigureCanvasTkAgg(self.nyquist_stack_figure, self.nyquist_stack_plot)
        self.nyquist_stack_canvas.show()
        self.nyquist_stack_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.nyquist_stack_500_axes.set_xlabel("Z\' $\mathregular{(\Omega cm^2\!)}$")
        self.nyquist_stack_500_axes.set_ylabel("-Z\'\' $\mathregular{(\Omega cm^2\!)}$")

        self.plot_nyquist_stack()

        self.file_opt = options = {}
        options['defaultextension'] = '.png'
        options['filetypes'] = [('Portable Network Graphics', '.png'), ('Portable Document Format','.pdf'), ('Encapsulated PostScript','.eps')]
        #options['initialdir'] = 'C:\\' #Windows
        options['initialdir'] = '~/'
        options['initialfile'] = sample_data.sample_name + "_nyquist_stack" +'.png'
        options['parent'] = root
        options['title'] = 'Save Nyquist Stack Plot'
        try:
            file, filename = self.ask_save_filename()
            ext = filename.rsplit('.',1)[1] #detect file type
            self.nyquist_stack_canvas.print_figure(file, dpi=200, format=ext)
            file.close()
        except TypeError:
            pass
        self.nyquist_stack_plot.grid_forget()
        self.nyquist_stack_plot.destroy()

    def open_sample(self, event=None):
        """ Open and set up a sample that was saved to the disk. """
        self.file_opt = options = {}
        options['defaultextension'] = '.p'
        options['filetypes'] = [('Resistance Plotter Files', '.p')]
        #options['initialdir'] = 'C:\\' #windows
        options['initialdir'] = '~/'
        options['initialfile'] = ''
        options['parent'] = root
        options['title'] = 'Open Resistance Plotter File'
        try:
            file = self.ask_open_filename()
            global sample_data
            sample_data = pickle.load(file)
            file.close()
            if sample_data: self.tear_down_data_panel()
            self.set_up_data_panel()
            self.set_entries()
        except TypeError:
            pass

    def ask_save_filename(self):
        """ Ask for and return a file to save"""
        filename = filedialog.asksaveasfilename(**self.file_opt)
        if filename:
            return open(filename, 'wb'), filename

    def ask_open_filename(self):
        """Ask for and return a file to open"""
        filename = filedialog.askopenfilename(**self.file_opt)
        if filename:
            return open(filename, 'rb')


def get_isotherm_plot_data(file_location):
    """ Return impedance data read from file on disk. Positive imaginary Z. """

    if sample_data.auto_generated:
        raw_impedance_data = pd.read_csv(filepath_or_buffer=file_location ,delim_whitespace=True, index_col=0,header=None, skiprows=0, names=[
            'Frequency/Hz',
            'impedance R/Ohm',
            'impedance I/Ohm',])
        raw_impedance_data.iloc[:,1] *= -1.0 #change Z'' to -Z'' for plot readability
    else:
        raw_impedance_data = pd.read_csv(filepath_or_buffer=file_location ,delim_whitespace=True, index_col=0,header=None, skiprows=19, names=['Number',
		    'Frequency/Hz',
	    	'impedance R/Ohm',
	    	'impedance I/Ohm',
	    	'Significance',
	    	'Time/s'])
        raw_impedance_data.iloc[:,2] *= -1.0 #change Z'' to -Z'' for plot readability
        raw_impedance_data.iloc[:,0] = raw_impedance_data.iloc[:,1]
        raw_impedance_data.iloc[:,1] = raw_impedance_data.iloc[:,2]

    #raw_impedance_data.info() #use to debug if no data is being read


    return raw_impedance_data


def get_rp_plot_data():
    """ Calculate and return Rp and the reciprocal temperatures. """
    raw_rp = np.array(sample_data.intercept_2_list) - np.array(sample_data.intercept_1_list)
    asr = raw_rp/2*sample_data.cathode_area
    temperatures = np.array(sample_data.temperature_range)
    temperatures_kelvin = temperatures + 273.15
    recip_temperatures = 1000/temperatures_kelvin
    return recip_temperatures, asr


### Main ###

sample_data = 0

root = tk.Tk()
root.title("Polarization Resistance Plotter")
app = Application(root)
root.mainloop()
