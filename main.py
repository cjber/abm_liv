from typing import List
import tkinter as tk  # gui
import imageio  # save images and gifs
import os  # os related functions
import matplotlib as mpl  # various plotting utilities
mpl.use('TkAgg')  # noqa, have to load before plt etc.
import matplotlib.pyplot as plt  # plots function
import matplotlib.animation as anim  # animated plots
import matplotlib.backends.backend_tkagg as mpltk  # plot backend for gui
import geopandas as gpd
import seaborn as sns
import pandas as pd
import random

# ensure that when updating my own imports they are updated here as well
import crime
import police
import api

bounds = gpd.read_file("./data/liverpool_bounds_fixed.gpkg")
#bounds = bounds.to_crs({'init': 'epsg:4326'})
environment = gpd.read_file("./data/liv_grid.shp")
#environment = environment.to_crs({'init': 'epsg:4326'})
environment['stat'] = 0


class Model_tk:
    # print some preliminary warnings to consider before running the model
    print("Select Agents and Iterations from dropdowns...")
    print("Before running select save as gif, or infinite iterations")

    def __init__(self, master: tk.Tk,
                 bounds: gpd.GeoDataFrame,
                 environment: gpd.GeoDataFrame) -> None:
        """Define the initial state of the tkinter main window.

        Defines initial variables and state for the main tkinter GUI window
        initialised by a tk.Tk() class given byt he master variable.

        Args:
            master (tk.Tk): The main GUI window.
            bounds (gpd.GeoDataFrame): A geographic dataframe showing the
                                       area of interest.
            environment (gpd.GeoDataFrame): A geographic dataframe of 
                                            multipolygons derived from the 
                                            bounds.
        """

        # variables set externally
        self.master = master
        self.bounds = bounds
        self.environment = environment

        self.bounds = self.bounds.geometry
        self.extent = self.bounds.bounds
        self.csv_data = pd.DataFrame()

        # default master variables
        self.master.title("Model GUI")
        self.police_list: List[police.Police] = []
        self.crime_list: List[crime.Crime] = []
        self.crime_api: pd.DataFrame = api.df

        bounds_gdf = gpd.GeoDataFrame(self.bounds, crs=self.bounds.crs,
                                      geometry=self.bounds.geometry)
        bg = self.bounds.buffer(100000)
        bg = gpd.GeoDataFrame(bg, crs=bg.crs, geometry=bg.geometry)
        self.bg = gpd.overlay(bg, bounds_gdf, how='difference')

        # tkinter frames
        self.frame = tk.Frame(master)
        self.frame_controls = tk.Frame(master)
        self.frame_widgets = tk.Frame(master)

        # frame positioning
        self.frame.grid(row=0, column=1, sticky="n")
        self.frame_controls.grid(row=0, column=0, sticky="nw")
        self.frame_widgets.grid(row=1, column=1, sticky="swe")

        # model plot area position and init
        self.fig = plt.figure(figsize=(7, 7))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.canvas = mpltk.FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas._tkcanvas.grid(row=0, column=1, rowspan=2, sticky="nswe")

        # variables for saving models
        self.save_img = 0
        self.filenames: List[str] = []

        # tkinter interactive buttons etc, very large section ending line 233
        # generally assigning functions to buttons, and button positioning
        self.var_crime = tk.IntVar()
        self.opts_crime = [10, 20, 30, 40, 50]
        self.var_crime.set(self.opts_crime[0])
        self.var_crime.trace("w", self.change)
        self.var_crime.trace("w", self.initial_vars)

        self.var_police = tk.IntVar()
        self.opts_police = [10, 20, 30, 40, 50]
        self.var_police.set(self.opts_police[0])
        self.var_police.trace("w", self.change)
        self.var_police.trace("w", self.initial_vars)

        self.var_iter = tk.IntVar()
        self.opts_iter = [10, 20, 30, 40, 50]
        self.var_iter.set(self.opts_iter[0])
        self.var_iter.trace("w", self.change)
        self.var_iter.trace("w", self.initial_vars)

        self.menu_crime = tk.OptionMenu(self.frame_controls, self.var_crime,
                                        *self.opts_crime)
        self.menu_crime.grid(row=10,
                             column=1,
                             padx=5,
                             pady=5)

        self.menu_police = tk.OptionMenu(self.frame_controls, self.var_police,
                                         *self.opts_police)
        self.menu_police.grid(row=11,
                              column=1,
                              padx=5,
                              pady=5)

        self.menu_iter = tk.OptionMenu(self.frame_controls, self.var_iter,
                                       *self.opts_iter)
        self.menu_iter.grid(row=12, column=1)

        self.ag_lab = tk.Label(self.frame_controls, text="Crimes")
        self.ag_lab.grid(row=10, column=0)
        self.ag_lab = tk.Label(self.frame_controls, text="Police")
        self.ag_lab.grid(row=11, column=0)
        self.it_lab = tk.Label(self.frame_controls, text="Iterations")
        self.it_lab.grid(row=12, column=0)

        self.start_btn = tk.Button(
            self.frame_controls,
            text="Run",
            command=self.run)
        self.start_btn.grid(row=0,
                            column=0,
                            sticky="we",
                            padx=5,
                            pady=2,
                            columnspan=2)

        self.stop_btn = tk.Button(
            self.frame_controls,
            text="Stop/Pause",
            command=self.stop)
        self.stop_btn.grid(row=2,
                           column=0,
                           sticky="we",
                           padx=5,
                           pady=2,
                           columnspan=2)

        self.resume_btn = tk.Button(
            self.frame_controls,
            text="Resume",
            command=self.resume)
        self.resume_btn.grid(row=1,
                             column=0,
                             sticky="we",
                             padx=5,
                             pady=2,
                             columnspan=2)

        self.inf_btn = tk.Button(
            self.frame_widgets,
            text="Infinite",
            command=self.toggle_inf)
        self.inf_btn.grid(row=0,
                          column=0,
                          padx=5,
                          pady=5)

        self.save_btn = tk.Button(
            self.frame_widgets,
            text="Save as GIF",
            command=self.toggle_save)
        self.save_btn.grid(row=0,
                           column=6,
                           padx=5,
                           pady=5)

        self.close_button = tk.Button(self.frame_widgets, text="Close",
                                      command=master.destroy)
        self.close_button.grid(row=0,
                               column=10,
                               pady=5,
                               padx=5)

        # default iteration variables
        self.carry_on: bool = True
        self.current_gen: int = 0
        self.inf: bool = False
        self.num_crime: int = self.var_crime.get()
        self.num_police: int = self.var_police.get()
        self.num_iter: int = self.var_iter.get()

    def update(self, *args: int) -> None:
        """Produce output for matplotlib animation, with agents as input.

        Takes police and crime agents from external modules, runs the local
        class functions, and produces a matplotlib figure with the updated
        agents.

        Args:
            args (int): Values derived from the GUI dropdown menus.
        """
        ax = self.ax
        plt.xlim(self.extent['minx'][0], self.extent['maxx'][0])
        plt.ylim(self.extent['miny'][0], self.extent['maxy'][0])
        plt.axis('off')
        # additional crimes
        if random.random() < 0.2:
            rand = random.randint(1, 5)
            for _ in range(rand):
                self.crime_list.append(
                    crime.Crime(self.bounds, self.crime_api))
            print(rand, "new crimes.")

        # iterate through each agent and run each class function
        for p in self.police_list:
            p.move(self.crime_list)

        for c in self.crime_list:
            c.solve(self.police_list)

        self.write_results()

        pol = pd.DataFrame()
        for p in self.police_list:
            x = p.x
            y = p.y
            df = pd.DataFrame({'x': x, 'y': y})
            pol = pol.append(df)

        geom = gpd.points_from_xy(pol['x'], pol['y'])
        pol_gdf = gpd.GeoDataFrame(pol, geometry=geom)

        within = []
        for index, row in self.environment.iterrows():
            w = sum(pol_gdf.within(row['geometry']))
            within.append(w)
        self.environment['within'] = within

        self.environment['stat'] += self.environment['within']

        cri = pd.DataFrame()
        for c in self.crime_list:
            if c.solved == 0:
                x = c.x
                y = c.y
                df = pd.DataFrame({'x': x, 'y': y})
                cri = cri.append(df)

        if len(cri) > 1:
            geom = gpd.points_from_xy(cri['x'], cri['y'])
            cri_gdf = gpd.GeoDataFrame(cri, geometry=geom)

            within = []
            for index, row in self.environment.iterrows():
                w = sum(cri_gdf.within(row['geometry']))
                within.append(w)
            self.environment['within'] = within

            self.environment['stat'] -= self.environment['within']

        # plot each agent on the input environment
        self.bounds.plot(ax=ax, facecolor="white", edgecolor="none")

        self.environment.plot(ax=ax, column='stat', cmap='RdYlGn',
                              edgecolor="white", linewidth=1,
                              vmin=-10, vmax=10)

        for p in self.police_list:
            ax.scatter(p.x, p.y, facecolor="Blue", edgecolors="Green")
        for c in self.crime_list:
            ax.scatter(c.x, c.y, facecolor=c.col, edgecolors="Red")
        ax.text(self.extent['minx'][0],
                self.extent['minx'][0], self.current_gen)
        self.bg.plot(ax=ax, facecolor='white')
        self.bounds.plot(ax=ax, facecolor="none",
                         edgecolor="black", linewidth=2)
        plt.xlim(self.extent['minx'][0], self.extent['maxx'][0])
        plt.ylim(self.extent['miny'][0], self.extent['maxy'][0])
        plt.axis('off')

        print("Current Iteration", self.current_gen + 1, "of",
              self.var_iter.get())

        # allow for saving of the current model step as an image
        if self.save_img == 1 and self.inf is False:
            savename = str(self.current_gen + 1)
            plt.savefig(savename + ".jpg")

    def initial_vars(self, *args: int) -> None:
        """Retrieves values from GUI dropdown menus.

        Function required to obtain initial values of dropdown menus.

        Args:
            args (int): Values derived from the dropdown menus.
        """
        self.num_crime = self.var_crime.get()
        self.num_police = self.var_police.get()
        self.num_iter = self.var_iter.get()

    def gen_function(self) -> None:
        """Stop iterations based on the selection.

        Iterations are determined through a dropdown GUI menu, may also be
        infinite based on a toggled button. This function also serves to
        create an ordered list of images to be converted into a gif if
        specified.

        Returns:
            self.filenames: If save_img == 1, will create a list of image 
                            filenames.
        """
        if self.inf is False:
            self.num_iter = self.num_iter
        else:
            self.num_iter = 999999999  # cannot use inf float

        # stop the function if number of iterations are exceeded
        # add one to each current gen for each iteration
        while (self.current_gen < self.num_iter) & (self.carry_on):
            yield self.current_gen
            self.current_gen = self.current_gen + 1
            # append the new image to the list of filenames
            if self.save_img == 1:
                self.filenames.append(str(self.current_gen) + ".jpg")
        # after the gen functions ends, turn images into a gif if selected
        if self.save_img == 1:
            self.create_gif()

    def run(self, *args: int) -> None:
        """Initial setup of the agents and environment. Create animation.

        Police agents are created randomly inside the polygon bounds.
        Crime agents are selected randomly from the data.police.uk api from
        within the bounds specified.

        Args:
            args (int): Values derived from the dropdown menus.
        """
        # state initial variables each time run is clicked
        self.carry_on = True
        self.current_gen = 0
        self.police_list = []
        self.crime_list = []
        self.environment = environment

        # make the agents
        for _ in range(self.num_police):
            self.police_list.append(police.Police(self.bounds))

        for _ in range(self.num_crime):
            self.crime_list.append(
                crime.Crime(self.bounds, self.crime_api))

        animation = anim.FuncAnimation(  # noqa (animation unused)
        self.fig, self.update, frames=self.gen_function, repeat=False
            )
        self.canvas.draw()

    def resume(self) -> None:
        """Allow the model to resume after being paused. Does not reset.

        Unlike run this function allows the model to resume after being
        stopped. This is useful for changing the number of agents or
        iterations without resetting the model.
        """
        if (self.current_gen < self.var_iter.get() or self.inf is True):
            self.carry_on = True
            animation = anim.FuncAnimation(  # noqa
                self.fig, self.update, frames=self.gen_function, repeat=False
            )
            self.canvas.draw()
        else:
            print("Cannot run the model! Check Parameters.")

    def stop(self) -> None:
        """Stop the model.

        This works more like a pause, the model may be resumed with "resume"
        but if "run" is clicked the model is reset.
        """
        self.carry_on = False

    def toggle_inf(self, *args: int) -> None:
        """Allow for a infinite number of iterations.

        Utilised a toggle button "hack" in tkinter to allow a button once
        pressed to stay pressed.

        The toggle inf may not be recessed at the same time as save as gif
        is selected. Infinite iterations are defined in the generation function.

        Args:
            args (int): Variables derived from the dropdowns.
        """
        if self.inf_btn.config('relief')[-1] == 'sunken':
            self.inf_btn.config(relief="raised")
            print("Running", self.var_iter.get(), "iterations.")
            self.inf = False
            self.carry_on = False

        elif self.save_btn.config("relief")[-1] == 'raised':
            self.inf_btn.config(relief="sunken")
            print("Running infinite iterations.")
            self.inf = True
            self.carry_on = True
        else:
            print("Cannot run infinite iteraions and save as GIF!")

    def toggle_save(self) -> None:
        """Allows for all frames of the model to be saved as a gif.

        Similarly uses the tkinter button "hack", prevents infinite iterations.
        Button function to allow saving as a gif.
        """
        if self.save_btn.config('relief')[-1] == 'sunken':
            self.save_btn.config(relief="raised")
            self.save_img = 0
        elif self.inf_btn.config("relief")[-1] == 'raised':
            self.save_btn.config(relief="sunken")
            self.save_img = 1
        else:
            print("Cannot save as GIF and run infinite iterations!")

    def create_gif(self) -> None:
        """Read in list of jpg files, save as a gif.

        Filenames are determined as the model is ran, to ensure they are
        ordered.
        """
        # get_write and imread allow for a very fast gif creation, despite
        # large files and number
        print("Creating GIF:", os.getcwd(), "/model.gif")
        with imageio.get_writer("model.gif", mode="I",
                                duration=0.5) as writer:
            for filename in self.filenames:
                image = imageio.imread(filename)
                writer.append_data(image)
                os.remove(filename)
        print("Finished GIF:", os.getcwd(), "/model.gif")

    def change(self, *args: int) -> None:
        """Indicates the present user selection.

        Gives the current number of crimes, police and iterations taken
        directly from the dropdown menu variables.

        Args:
            args (int): Variables derived from the dropdown menus.
        """
        print("Options changed.")
        print("Number of Crimes:", self.var_crime.get())
        print("Number of Police:", self.var_police.get())
        print("Number of Iterations:", self.var_iter.get())

    def write_results(self):
        """Takes results generated every iteration and writes to a csv.

        Results include:
            Iteration number,
            Total 'stat' value across all squares,
            Total number of police,
            Total number of crimes.
        """
        total_stat = sum(self.environment['stat'])
        total_pol = len(self.police_list)

        current_crimes = []
        for c in self.crime_list:
            if c.solved == 0:
                current_crimes.append(c)
        total_crime = len(current_crimes)

        print(total_stat)
        df = pd.DataFrame({'police': [total_pol],
                           'crime': [total_crime],
                           'area_stat': [total_stat]})
        self.csv_data = self.csv_data.append(df)

        if self.current_gen + 1 == self.num_iter:
            self.csv_data.to_csv("./data/total_data.csv", index=False)


root = tk.Tk()
gui = Model_tk(root, bounds, environment)
root.resizable(False, False)
# to write docs this cannot be uncommented
root.mainloop()
