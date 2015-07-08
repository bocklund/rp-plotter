#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
######## TODO ########
- add Titles to data entry and tools grid slots
- add saving of images to file
- make the plots better looking
- suggest low and high intercept values
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
	def __init__(self, path, name, area): #add more like intercept points later
		self.dir_path = path
		self.sample_name = name
		self.cathode_area = area
		self.intercept_1_list = []
		self.intercept_2_list = []
	#create variables for the intercepts. 


class NewSample(simpledialog.Dialog): #what happens when the user chooses to create a new sample

	
	def body(self, master):
		#defining options for opening a directory
		self.dir_opt = options = {}
		#options['initialdir'] = 'C:\\'
		options['initialdir'] = '~/'
		options['mustexist'] = False
		options['parent'] = master
		options['title'] = 'Select EIS Data Directory'
		
		tk.Label(master, text="Sample Name:",).grid(row=0)
		tk.Label(master, text="Cathode Area:").grid(row=1)
		tk.Label(master, text="Directory Path:").grid(row=2)
		
		self.name_entry = tk.Entry(master)
		self.area_entry = tk.Entry(master)
		self.path_entry = tk.Entry(master)


		self.name_entry.grid(row=0, column=1)
		self.area_entry.grid(row=1, column=1)
		self.path_entry.grid(row=2, column=1)
		
		self.browse_button = tk.Button(master, text="Browse", command=self.browse).grid(row=2, column = 2)
		return self.name_entry # initial focus

	def apply(self):
	
		path = str(self.path_entry.get())
		name = str(self.name_entry.get())
		area = float(self.area_entry.get())
		global sample_data
		sample_data = SampleData(path, name, area)
	
	def browse(self):
		path = filedialog.askdirectory(**self.dir_opt)
		self.path_entry.delete(0, "end")
		self.path_entry.insert(0, path)

		
	
class Application:
	def __init__(self, parent):
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
		
		
		###### set up data panel ######
		
		#labels in column 0
		tk.Label(self.data_panel, text="Temp.", anchor=tk.W).grid(row=0, column=0)
		tk.Label(self.data_panel, text="400°C", anchor=tk.W).grid(row=1, column=0)
		tk.Label(self.data_panel, text="450°C", anchor=tk.W).grid(row=2, column=0)
		tk.Label(self.data_panel, text="500°C", anchor=tk.W).grid(row=3, column=0)
		tk.Label(self.data_panel, text="550°C", anchor=tk.W).grid(row=4, column=0)
		tk.Label(self.data_panel, text="600°C", anchor=tk.W).grid(row=5, column=0)
		tk.Label(self.data_panel, text="650°C", anchor=tk.W).grid(row=6, column=0)
		tk.Label(self.data_panel, text="700°C", anchor=tk.W).grid(row=7, column=0)
		
		
		
		#low intercepts in column 1 and high intercepts in column 2 
		tk.Label(self.data_panel, text="Low Intercept", anchor=tk.N).grid(row=0, column=1)
		tk.Label(self.data_panel, text="High Intercept", anchor=tk.N).grid(row=0, column=2)
		self.intercept_1_400 = tk.Entry(self.data_panel, width=6)
		self.intercept_1_400.grid(row = 1, column = 1)
		self.intercept_2_400 = tk.Entry(self.data_panel, width=6)
		self.intercept_2_400.grid(row = 1, column = 2)
		self.intercept_1_450 = tk.Entry(self.data_panel, width=6)
		self.intercept_1_450.grid(row = 2, column = 1)        
		self.intercept_2_450 = tk.Entry(self.data_panel, width=6)
		self.intercept_2_450.grid(row = 2, column = 2)  
		self.intercept_1_500 = tk.Entry(self.data_panel, width=6)
		self.intercept_1_500.grid(row = 3, column = 1)
		self.intercept_2_500 = tk.Entry(self.data_panel, width=6)
		self.intercept_2_500.grid(row = 3, column = 2)
		self.intercept_1_550 = tk.Entry(self.data_panel, width=6)
		self.intercept_1_550.grid(row = 4, column = 1)
		self.intercept_2_550 = tk.Entry(self.data_panel, width=6)
		self.intercept_2_550.grid(row = 4, column = 2)
		self.intercept_1_600 = tk.Entry(self.data_panel, width=6)
		self.intercept_1_600.grid(row = 5, column = 1)
		self.intercept_2_600 = tk.Entry(self.data_panel, width=6)
		self.intercept_2_600.grid(row = 5, column = 2)
		self.intercept_1_650 = tk.Entry(self.data_panel, width=6)
		self.intercept_1_650.grid(row = 6, column = 1)
		self.intercept_2_650 = tk.Entry(self.data_panel, width=6)
		self.intercept_2_650.grid(row = 6, column = 2)
		self.intercept_1_700 = tk.Entry(self.data_panel, width=6)
		self.intercept_1_700.grid(row = 7, column = 1)
		self.intercept_2_700 = tk.Entry(self.data_panel, width=6)
		self.intercept_2_700.grid(row = 7, column = 2)  

		
		#plot buttons for each temperature in column 3
		tk.Label(self.data_panel, text="High Intercept", anchor=tk.N).grid(row=0, column=2)        
		self.plot_400_button = tk.Button(self.data_panel, text='Plot', command=lambda: self.plot_isotherm(1)) #plot command    
		self.plot_400_button.grid(row=1, column=3)
		self.plot_450_button = tk.Button(self.data_panel, text='Plot', command=lambda: self.plot_isotherm(2)) #plot command    
		self.plot_450_button.grid(row=2, column=3)
		self.plot_500_button = tk.Button(self.data_panel, text='Plot', command=lambda: self.plot_isotherm(3)) #plot command    
		self.plot_500_button.grid(row=3, column=3)
		self.plot_550_button = tk.Button(self.data_panel, text='Plot', command=lambda: self.plot_isotherm(button_number=4)) #plot command    
		self.plot_550_button.grid(row=4, column=3)
		self.plot_600_button = tk.Button(self.data_panel, text='Plot', command=lambda: self.plot_isotherm(button_number=5)) #plot command    
		self.plot_600_button.grid(row=5, column=3)
		self.plot_650_button = tk.Button(self.data_panel, text='Plot', command=lambda: self.plot_isotherm(button_number=6)) #plot command    
		self.plot_650_button.grid(row=6, column=3)
		self.plot_700_button = tk.Button(self.data_panel, text='Plot', command=lambda: self.plot_isotherm(button_number=7)) #plot command    
		self.plot_700_button.grid(row=7, column=3)
		
		
		###### buttons to plot rp ######
		
		#generate some labels
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
		
		#make a new plot checkbox
		self.new_plot = tk.IntVar()
		self.new_plot_checkbox = tk.Checkbutton(self.tools_panel, text="Plot Rp on new plot?", variable = self.new_plot).grid(row=3, column = 0, columnspan = 3, sticky = tk.W)
		self.new_plot.set(1)
			
		#finally, make the button
		self.plot_rp_button = tk.Button(self.tools_panel, text="Plot Rp", command=self.plot_rp, padx='3m', pady='3m').grid(row=4, column = 0, columnspan=3, pady='3m')
		
		
		###### set up isotherm figure ######
		self.isotherm_figure = Figure(figsize=(6,4), facecolor='w')
		self.isotherm_axes = self.isotherm_figure.add_subplot(111)
		self.isotherm_figure.tight_layout(pad = 4) #possibly change to set_tight_layout and repeat below
		self.isotherm_canvas = FigureCanvasTkAgg(self.isotherm_figure, self.isotherm_plot)
		self.isotherm_canvas.show()
		self.isotherm_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		
		###### set up rp figure ######
		self.rp_figure = Figure(figsize=(7,5), facecolor='w')
		self.rp_axes = self.rp_figure.add_subplot(111)
		self.rp_axes_twin = self.rp_axes.twiny()
		self.rp_figure.tight_layout(pad = 3.5)
		self.rp_canvas = FigureCanvasTkAgg(self.rp_figure, self.rp_plot)
		self.rp_canvas.show()
		self.rp_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
	
		
	def plot_rp(self):
		self.get_entries()
		temperatures, recip_temperatures, asr = get_rp_plot_data()
		
		if self.new_plot.get():
			#clear plot
			self.rp_axes.clear()
			self.rp_axes_twin.clear()
			#draw plot
		
		#self.rp_axes.set_title(r"R$\mathregular{_p}$ of " + sample_data.sample_name, y=1.16)
		self.rp_axes.set_xlabel(r"Temperature $\mathregular{(1000/T)\ (K}^{-1}\mathregular{)}$")
		self.rp_axes.set_ylabel(r"R$\mathregular{_p}$ $\mathregular{(\Omega cm^2)}$")
		self.rp_axes.set_yscale('log')
		self.rp_axes.yaxis.set_major_formatter(ScalarFormatter()) 
		self.rp_axes.ticklabel_format(axis='y', style='plain')
		self.rp_axes.axis([1, 1.55, 0.011, 15])
		self.rp_axes.tick_params(direction='out', which='both')
		self.rp_axes.axhline(y=0.1, linestyle='--', color='0.6')
		#plot
		self.rp_axes.plot(recip_temperatures, asr, marker=self.marker_style.get(), markersize=6, color=self.marker_color.get(), linestyle="None", label=sample_data.sample_name)
		self.rp_axes.legend(loc='upper left', numpoints = 1, fontsize='small',)
		
		#twin axes to go to celsius
		celsius_tick_locations = recip_temperatures
		self.rp_axes_twin.axis([1, 1.55, 0.011, 15])
		self.rp_axes_twin.tick_params(direction='out', which='both')
		self.rp_axes_twin.set_xticks(celsius_tick_locations)
		self.rp_axes_twin.set_xticklabels(temperatures)
		self.rp_axes_twin.set_xlabel(r'Temperature (°C)')
		
		
		
		
		
		self.rp_canvas.show()
		self.rp_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)					
	
	def plot_isotherm(self, button_number):
		#pass if sample_data is 0
		if sample_data : 
			
			self.isotherm_axes.clear() #clean up last plot
			
			#get new data
			file_path, temperature = self.eis_file_path(button_number, sample_data.dir_path)
			raw_data = get_isotherm_plot_data(file_path, temperature)
			
			self.active_isotherm_temperature = temperature
			#plot new plot

			self.isotherm_axes.set_title(sample_data.sample_name + " at " + temperature, y=1.08)
			self.isotherm_axes.set_xlabel("Z\' ($\mathregular{\Omega cm^2}$)")
			self.isotherm_axes.set_ylabel("-Z\'\' ($\mathregular{\Omega cm^2}$)")
			self.isotherm_axes.set_aspect('equal',)# adjustable='box')
			self.isotherm_axes.plot(raw_data.iloc[:,1], raw_data.iloc[:,2], marker='.', markersize=9, color='black', linestyle="None")
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
		#pass if sample_data is 0
		

		if sample_data : 			
			#get new data
			file_path, temperature = self.eis_file_path(3, sample_data.dir_path)
			raw_data = get_isotherm_plot_data(file_path, temperature)
			self.active_isotherm_temperature = temperature
			#plot new plot
			self.nyquist_stack_500_axes.set_aspect('equal',)# adjustable='box')
			self.nyquist_stack_500_axes.plot(raw_data.iloc[:,1], raw_data.iloc[:,2], marker='.', markersize=9, color='black', linestyle="None")
			#square the axes
			xmin, xmax, ymin, ymax = self.nyquist_stack_500_axes.axis()
			#print('nyquist stack 500: xmin, xmax, ymin, ymax', xmin, xmax, ymin, ymax)
			if (ymax-ymin) > (xmax-xmin):
				xmax = xmin + (ymax-ymin)
			else:
				ymax = ymin + (xmax-xmin)
			self.nyquist_stack_500_axes.axis([xmin, xmax, ymin, ymax])	
			self.nyquist_stack_500_axes.tick_params(direction='out')
			#label peaks		
		if sample_data : 			
			#get new data
			file_path, temperature = self.eis_file_path(5, sample_data.dir_path)
			raw_data = get_isotherm_plot_data(file_path, temperature)
			self.active_isotherm_temperature = temperature
			#plot new plot
			self.nyquist_stack_600_axes.set_aspect('equal',)# adjustable='box')
			self.nyquist_stack_600_axes.plot(raw_data.iloc[:,1], raw_data.iloc[:,2], marker='.', markersize=9, color='black', linestyle="None")
			#square the axes
			#print('nyquist stack 700: xmin, xmax, ymin, ymax', xmin, xmax, ymin, ymax)	
			xmin, xmax, ymin, ymax = self.nyquist_stack_600_axes.axis()
			if (ymax-ymin) > (xmax-xmin):
				xmax = xmin + (ymax-ymin)
			else:
				ymax = ymin + (xmax-xmin)
			self.nyquist_stack_600_axes.axis([xmin, xmax, ymin, ymax])	
			self.nyquist_stack_600_axes.tick_params(direction='out')	
			#label peaks

		if sample_data : 			
			#get new data
			file_path, temperature = self.eis_file_path(7, sample_data.dir_path)
			raw_data = get_isotherm_plot_data(file_path, temperature)
			self.active_isotherm_temperature = temperature
			#plot new plot
			self.nyquist_stack_700_axes.set_aspect('equal',)# adjustable='box')
			self.nyquist_stack_700_axes.plot(raw_data.iloc[:,1], raw_data.iloc[:,2], marker='.', markersize=9, color='black', linestyle="None")
			#square the axes
			xmin, xmax, ymin, ymax = self.nyquist_stack_700_axes.axis()
			#print('nyquist stack 700: xmin, xmax, ymin, ymax', xmin, xmax, ymin, ymax)
			if (ymax-ymin) > (xmax-xmin):
				xmax = xmin + (ymax-ymin)
			else:
				ymax = ymin + (xmax-xmin)
			self.nyquist_stack_700_axes.axis([xmin, xmax, ymin, ymax])	
			self.nyquist_stack_700_axes.tick_params(direction='out')
		
			#label peaks


			
	def new_sample(self):
		NewSample(self.parent)
			
	def eis_file_path(self, button_number, dir_path):
	
		#print(os.path.join(dir_path, os.listdir(dir_path)[button_number-1]))
		file_path = os.path.join(dir_path, os.listdir(dir_path)[button_number-1])
		temp_range = ['400°C', '450°C', '500°C', '550°C', '600°C', '650°C', '700°C']
		temperature = temp_range[button_number-1]
		
		return file_path, temperature
	
	def get_entries(self):
		
		intercept_1_entries = [self.intercept_1_400,
		self.intercept_1_450,
		self.intercept_1_500,
		self.intercept_1_550,
		self.intercept_1_600,
		self.intercept_1_650,
		self.intercept_1_700]
		
		intercept_2_entries = [self.intercept_2_400,
		self.intercept_2_450,
		self.intercept_2_500,
		self.intercept_2_550,
		self.intercept_2_600,
		self.intercept_2_650,
		self.intercept_2_700]
		
		sample_data.intercept_1_list = []
		sample_data.intercept_2_list = []
		
		for intercept_1_entry, intercept_2_entry in zip(intercept_1_entries, intercept_2_entries):
			sample_data.intercept_1_list.append(float(intercept_1_entry.get()))
			sample_data.intercept_2_list.append(float(intercept_2_entry.get()))
	
	def set_entries(self):
		intercept_1_entries = [self.intercept_1_400,
		self.intercept_1_450,
		self.intercept_1_500,
		self.intercept_1_550,
		self.intercept_1_600,
		self.intercept_1_650,
		self.intercept_1_700]
		
		intercept_2_entries = [self.intercept_2_400,
		self.intercept_2_450,
		self.intercept_2_500,
		self.intercept_2_550,
		self.intercept_2_600,
		self.intercept_2_650,
		self.intercept_2_700]
		
		
		for intercept_1_entry, intercept_2_entry, intercept_1_value, intercept_2_value in zip(intercept_1_entries, intercept_2_entries, sample_data.intercept_1_list, sample_data.intercept_2_list):
			intercept_1_entry.delete(0,"end")
			intercept_2_entry.delete(0,"end")
			
			intercept_1_entry.insert(0,str(intercept_1_value))
			intercept_2_entry.insert(0,str(intercept_2_value))
		
	def save_sample(self):
		#run a dialog to choose the sample save location
		
		#defining options for saving a file
		self.file_opt = options = {}
		options['defaultextension'] = '.p'
		options['filetypes'] = [('Resistance Plotter Files', '.p')]
		#options['initialdir'] = 'C:\\'
		options['initialdir'] = '~/'
		options['initialfile'] = sample_data.sample_name + '.p'
		options['parent'] = root
		options['title'] = 'Save Resistance Plotter File'
		
		try:
			file, filename = self.ask_save_filename()		
			
			#set the sample data variable one last time
			self.get_entries()
			global sample_data
			
			#save data
			pickle.dump(sample_data, file)#set save name to be sample name later
			file.close()
		except TypeError:
			pass
		
		
	def save_rp(self):
		#run a dialog to choose the sample save location
		
		#defining options for saving a file
		self.file_opt = options = {}
		options['defaultextension'] = '.png'
		options['filetypes'] = [('Portable Network Graphics', '.png'), ('Portable Document Format','.pdf'), ('Encapsulated PostScript','.eps')]
		#options['initialdir'] = 'C:\\'
		options['initialdir'] = '~/'
		options['initialfile'] = sample_data.sample_name + "_rp" + '.png'
		options['parent'] = root
		options['title'] = 'Save Rp Plot'
		try:
			#get file
			#maybe later make a dialog to set the settings
			file, filename = self.ask_save_filename()			
			#detect file type
			ext = filename.rsplit('.',1)[1]
			#save data
			self.rp_canvas.print_figure(file, dpi=200, format=ext)
			file.close()
		except TypeError:
			pass
			
			
	def save_isotherm(self):
		#run a dialog to choose the sample save location
		
		#defining options for saving a file
		self.file_opt = options = {}
		options['defaultextension'] = '.png'
		options['filetypes'] = [('Portable Network Graphics', '.png'), ('Portable Document Format','.pdf'), ('Encapsulated PostScript','.eps')]
		options['initialdir'] = '~/'
		#options['initialdir'] = 'C:\\'
		options['initialfile'] = sample_data.sample_name + "_nyquist_" + self.active_isotherm_temperature +'.png'
		options['parent'] = root
		options['title'] = 'Save Nyquist Plot'
		

		try:
			#get file
			#maybe later make a dialog to set the settings
			file, filename = self.ask_save_filename()		
			#detect file type
			ext = filename.rsplit('.',1)[1]		
			#save data			
			self.isotherm_canvas.print_figure(file, dpi=200, format=ext)
			file.close()
		except TypeError:
			pass
		
		
		
		
	def save_nyquist_stack(self):
		#grid the figure
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
		
		self.nyquist_stack_500_axes.set_xlabel("Z\' ($\mathregular{\Omega cm^2}$)")
		self.nyquist_stack_500_axes.set_ylabel("-Z\'\' ($\mathregular{\Omega cm^2}$)")
		
		self.plot_nyquist_stack()
		
		#run a dialog to choose the sample save location
		
		#defining options for saving a file
		self.file_opt = options = {}
		options['defaultextension'] = '.png'
		options['filetypes'] = [('Portable Network Graphics', '.png'), ('Portable Document Format','.pdf'), ('Encapsulated PostScript','.eps')]
		#options['initialdir'] = 'C:\\'
		options['initialdir'] = '~/'
		options['initialfile'] = sample_data.sample_name + "_nyquist_stack" +'.png'
		options['parent'] = root
		options['title'] = 'Save Nyquist Stack Plot'
		

		try:
			#get file
			#maybe later make a dialog to set the settings
			file, filename = self.ask_save_filename()		
			#detect file type
			ext = filename.rsplit('.',1)[1]
			#save data		
			self.nyquist_stack_canvas.print_figure(file, dpi=200, format=ext)
			file.close()
		except TypeError:
			pass
		self.nyquist_stack_plot.grid_forget()
		self.nyquist_stack_plot.destroy()
	def open_sample(self):
			
		#defining options for opening a file
		self.file_opt = options = {}
		options['defaultextension'] = '.p'
		options['filetypes'] = [('Resistance Plotter Files', '.p')]
		#options['initialdir'] = 'C:\\'
		options['initialdir'] = '~/'
		options['initialfile'] = ''
		options['parent'] = root
		options['title'] = 'Open Resistance Plotter File'
		
		try:
			#open the file
			file = self.ask_open_filename()
			
			global sample_data
			sample_data = pickle.load(file)
			file.close()
			#print("sample name:",sample_data.sample_name)
			#print("int 1 list:",sample_data.intercept_1_list)
			#print("int 2 list:",sample_data.intercept_2_list)
			self.set_entries()
			#use an open dialog in the future or display a list of all the sample files and let the user choose one
		except TypeError:
			pass
		
		
	def ask_save_filename(self):
		#get filename
		filename = filedialog.asksaveasfilename(**self.file_opt)
		
		if filename:
			return open(filename, 'wb'), filename
	
	
	def ask_open_filename(self):
		#select a file
		filename = filedialog.askopenfilename(**self.file_opt)
		
		if filename:
			return open(filename, 'rb') #returns the opened file
		


def get_isotherm_plot_data(dir_location, temperature ):
	raw_impedance_data = pd.read_csv(filepath_or_buffer=dir_location ,delim_whitespace=True, index_col=0,header=None, skiprows=19, names=['Number',
		'Frequency/Hz',
		'impedance R/Ohm',
		'impedance I/Ohm',
		'Significance',
		'Time/s'])
	#raw_impedance_data.info() #check info for debugging
	raw_impedance_data.iloc[:,2] *= -1.0 #change Z'' to -Z'' for plot readability
	return raw_impedance_data
	

	
def get_rp_plot_data():
	
	raw_rp = np.array(sample_data.intercept_2_list) - np.array(sample_data.intercept_1_list)
	
	asr = raw_rp/2*sample_data.cathode_area
	
	temperatures = np.array([400, 450, 500, 550, 600, 650, 700])
	temperatures_kelvin = temperatures + 273.15
	recip_temperatures = 1000/temperatures_kelvin
	#print("1/Temperatures: ", recip_temperatures)
	#print("asrs: ", asr)
	return temperatures, recip_temperatures, asr
	
def initialize():
	#choose MIEC and Electrolyte
	#choose ohmic offset and/or rp using 0,1,2 or radio buttons in tkinter
	#name of sample that is being analyzed
	dir_location = input('What is the path of the folder with raw data files?') #validate to check for valid path, or graphically
	#get low, high, temperature increment. Later, just implement use of logic in the files
	temp_range_low = int(input('What is the low impedance temperature?'))
	temp_range_high = int(input('What is the high impedance temperature?'))
	temp_range_increment = int(input('What is the temperature increment?'))
	temp_range = range(temp_range_low, temp_range_high+temp_range_increment, temp_range_increment)
	return sample_name, analysis_type, dir_location, temp_range
	


	
#main	
	
#create initial data, will be moved to the "New" menu item later
sample_data = 0 


root = tk.Tk()
root.title("Polarization Resistance Plotter")
app = Application(root)
root.mainloop()

