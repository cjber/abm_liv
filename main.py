from typing import List  # for mypy type hints
import tkinter as tk  # gui
import imageio  # save images and gifs
import os  # os related functions
import matplotlib as mpl  # various plotting utilities
mpl.use('TkAgg')  # noqa, have to load before plt etc.
import matplotlib.pyplot as plt  # plots function
import matplotlib.animation as anim  # animated plots
import matplotlib.backends.backend_tkagg as mpltk  # plot backend for gui
import geopandas as gpd  # geographic data manipulation
import pandas as pd  # data manipulation
import random  # provide pseudorandom numbers

# local imports
import crime
import police
import api

# read in bounds as a polygon
bounds = gpd.read_file("./data/bounds.gpkg")
# read in grid polygons created by data_clean.py
environment = gpd.read_file("./data/grid.shp")
# init base stat value
environment['stat'] = 0


class Model_tk:
    # print some preliminary warnings to consider before running the model
    print(
        "Select number of crimes," +
        "number of police" +
        "and number of iterations from dropdowns..."
    )
    print("Before running select save as gif, or infinite iterations")

    def __init__(self, master: tk.Tk,
                 bounds: gpd.GeoDataFrame,
                 environment: gpd.GeoDataFrame) -> None:
        """Define the initial state of the tkinter main window.

        Defines initial variables and state for the main tkinter GUI window
        initialised by a tk.Tk() class given by the master variable.

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

        # create geodataframe form given bounds (required for gpd functions)
        bounds_gdf = gpd.GeoDataFrame(self.bounds, crs=self.bounds.crs,
                                      geometry=self.bounds.geometry)
        # create large polygon outside range of bounds
        bg = self.bounds.buffer(100000)
        bg = gpd.GeoDataFrame(bg, crs=bg.crs, geometry=bg.geometry)
        # remove centre from large polygon, leaving only outside to cover
        # outside the bounds (used for plotting only)
        self.bg = gpd.overlay(bg, bounds_gdf, how='difference')

        # tkinter frames
        self.frame = tk.Frame(master)
        self.frame_controls = tk.Frame(master)
        self.frame_widgets = tk.Frame(master)

        # frame positioning
        self.frame.grid(row=0, column=1, sticky="n")
        self.frame_controls.grid(row=0, column=0, sticky="nw")
        self.frame_widgets.grid(row=1, column=1, sticky="swe")

        # model plot area position and init canvas
        self.fig = plt.figure(figsize=(7, 7))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.canvas = mpltk.FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas._tkcanvas.grid(row=0, column=1, rowspan=2, sticky="nswe")

        # variables for saving model as a gif
        self.save_img = 0
        self.filenames: List[str] = []

        # tkinter interactive buttons etc, very large section ending line 200
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

    def plot_anim(self, *args: int) -> None:
        """
        Display each iteration of the model as a matploblib plot

        Uses base polygon with overlayed grid polygons.
        Agents are plotted as a scatter plot.

        :param args: Values derived from the GUI dropdown menus.
        :type args: int

        #### BUGS

        Matplotlib when using polygon data cannot clear plot every run
        this appears to cause performance issues as >10 iterations will
        eventually stop rendering plots. I cannot find a solution to this.

        """
        # cannot have double dot operators i.e. self.ax.plot
        ax = self.ax

        # set extents based on extent of the bounds polygon
        plt.xlim(self.extent['minx'][0], self.extent['maxx'][0])
        plt.ylim(self.extent['miny'][0], self.extent['maxy'][0])
        # no axis
        plt.axis('off')

        # plot the bounds polygon defined in the init
        self.bounds.plot(ax=ax, facecolor="white", edgecolor="none")

        # plot the bounds grid
        self.environment.plot(ax=ax, column='stat', cmap='RdYlGn',
                              edgecolor="white", linewidth=1,
                              vmin=-10, vmax=10)

        # iterate through police list and plot each as a point on a scatter
        for p in self.police_list:
            ax.scatter(p.x, p.y, facecolor="Blue", edgecolors="Green")
        # iterate through crime list and plot each as a point on a scatter
        for c in self.crime_list:
            ax.scatter(c.x, c.y, facecolor=c.col, edgecolors="Red")
        # plot bg to remove grid the appear outside bounds
        self.bg.plot(ax=ax, facecolor='white')
        # create edge to bounds
        self.bounds.plot(ax=ax, facecolor="none",
                         edgecolor="black", linewidth=2)

    def update(self, *args: int) -> None:
        """Produce output for matplotlib animation, with agents as input.

        Takes police and crime agents from external modules, runs the local
        class functions, and produces a matplotlib figure with the updated
        agents.

        Args:
            args (int): Values derived from the GUI dropdown menus.

        ##### BUGS
        Memory profile reveals every iteration with default settings gives
        ~3mb increase in memory usage.

        """
        # add additional crimes randomly each iteration
        if random.random() < 0.4:
            rand = random.randint(1, 5)
            for _ in range(rand):
                self.crime_list.append(
                    crime.Crime(self.bounds, self.crime_api))
            print(rand, "new crimes.")

        # iterate through each police and run each class function
        for p in self.police_list:
            p.move(self.crime_list)

        # do the same for crimes
        for c in self.crime_list:
            c.solve(self.police_list)

        # write results to a csv file, appends each run
        self.write_results()

        # create police gdf to use gpd.within function
        pol = pd.DataFrame()
        for p in self.police_list:
            x = p.x
            y = p.y
            df = pd.DataFrame({'x': x, 'y': y})
            pol = pol.append(df)
        geom = gpd.points_from_xy(pol['x'], pol['y'])
        pol_gdf = gpd.GeoDataFrame(pol, geometry=geom)

        # for police that are geographically within a certain grid square
        # add the environment stat value (i.e. an decrease in area crime)
        within = []
        for _, row in self.environment.iterrows():
            w = sum(pol_gdf.within(row['geometry']))
            within.append(w)
        self.environment['within'] = within
        self.environment['stat'] += self.environment['within']

        # create crime gdf for same reason
        cri = pd.DataFrame()
        for c in self.crime_list:
            if c.solved == 0:
                x = c.x
                y = c.y
                df = pd.DataFrame({'x': x, 'y': y})
                cri = cri.append(df)
        if len(cri) > 1:  # ensure this isn't used if all crimes are solved
            geom = gpd.points_from_xy(cri['x'], cri['y'])
            cri_gdf = gpd.GeoDataFrame(cri, geometry=geom)

            # for crimes within a grid polygon, reduce the area stat
            within = []
            for _, row in self.environment.iterrows():
                w = sum(cri_gdf.within(row['geometry']))
                within.append(w)
            self.environment['within'] = within

            self.environment['stat'] -= self.environment['within']

        print("Current Iteration", self.current_gen + 1, "of",
              self.var_iter.get())

        self.plot_anim()

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
        self.num_iter = self.num_iter if self.inf is False else 999999999
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

        # create police agents by appending each to list of length num_police
        for _ in range(self.num_police):
            self.police_list.append(police.Police(self.bounds))

        # create crime agents by appending each to list of length num_police
        for _ in range(self.num_crime):
            self.crime_list.append(
                crime.Crime(self.bounds, self.crime_api))

        # create matplotlib animation using update function contaning
        # crime, police, and environment at each iteration
        animation = anim.FuncAnimation(  # noqa: W0612
            self.fig, self.update, frames=self.gen_function, repeat=False
        )
        self.canvas.draw()

    def resume(self) -> None:
        """Allow the model to resume after being paused. Does not reset.

        Unlike run this function allows the model to resume after being
        stopped. This is useful for changing the number of agents or
        iterations without resetting the model.
        """
        # allow resume if below max iterations or if infinite iterations
        if (self.current_gen < self.var_iter.get() or self.inf is True):
            self.carry_on = True
            animation = anim.FuncAnimation(  # noqa: W0612
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
        is selected. Infinite iterations are defined in the
        generation function.

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
        # if save button is raised the model isnt saved as a gif
        if self.save_btn.config('relief')[-1] == 'sunken':
            self.save_btn.config(relief="raised")
            self.save_img = 0
        # if inf button is pressed, cannot press save button
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
        # start "writer" set half second interval I mode is image mode
        with imageio.get_writer("model.gif", mode="I",
                                duration=0.5) as writer:
            for filename in self.filenames:
                image = imageio.imread(filename)
                # appending images to writer creates a gif
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
        # find total sum of stat across all grid polygons
        # at a certain iteration
        total_stat = sum(self.environment['stat'])
        total_pol = len(self.police_list)

        current_crimes = [c for c in self.crime_list if c.solved == 0]
        # add all non solved crimes to list
        total_crime = len(current_crimes)

        # convert to a pandas dataframe
        df = pd.DataFrame({'police': [total_pol],
                           'crime': [total_crime],
                           'area_stat': [total_stat]})
        # add to csv dataframe
        self.csv_data = self.csv_data.append(df)

        # for each iteration append data to csv
        if self.current_gen + 1 == self.num_iter:
            self.csv_data.to_csv("./data/total_data.csv", index=False)
            print("Written results to data/total_data.csv")


root = tk.Tk()
# initialise gui with root, selected bounds, and environment
gui = Model_tk(root, bounds, environment)

# ensure fixed window size
root.resizable(False, False)

# to write docs ensure this line is commented
root.mainloop()
