from .ChernCharacter import ChernCharacter
import matplotlib.pyplot as plt
import math
import numpy as np
import plotly.graph_objects as go
from plotly.graph_objs import *
import plotly.utils
import json
import cmath
from mpl_toolkits.mplot3d import Axes3D  
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import cm


class LePotier():
    """
    Class which encodes a significant porition of the mathematical information about the Drézet-Le Potier
    curve embedded in the ch1/ch0, ch2/ch0 plane. An algorithmic description of how to obtain the 
    coordinates of exceptional vector bundles is described in 

    https://link.springer.com/article/10.1007/s00029-017-0352-4

    Attributes:
    ----------------
    granularity (int): The number of bits of precision to use in the calculation of the curve
    width (int): The width of the curve in terms of the number of dyadic characters
    boundary_points (list): A list of tuples containing the coordinates of the boundary points of the curve

    """

    def __init__(self, granularity=5, width=5):
        """
        Constructor for the LePotier class. Initializes the curve with the given granularity
        and width.

        Args:
        ----------------
        granularity (int): The number of bits of precision to use in the calculation of the curve
        width (int): The width of the curve in terms of the number of dyadic characters
        """
        self.granularity = granularity
        self.width = width

        lower_bound = -1*self.width * 2**self.granularity
        upper_bound = self.width * 2**(self.granularity ) + 1

        self.boundary_points = []

        for i in range(lower_bound, upper_bound):

            self.boundary_points.append(self._e_plus(i, granularity))
            self.boundary_points.append(self._e_left(i, granularity))
            self.boundary_points.append(self._e_right(i, granularity))
        
        self.boundary_points = sorted(self.boundary_points, key=lambda x: x[0])
        


    def _get_dyadic_character(self, p, m):
        """
        Helper function to calculate the chern characer corresponding to a dyadic number p/2^m
        
        Args:
        ----------------
        p (int): The index of the dyadic character
        m (int): the exponent of the denominator of the dyadic character, e.g. p/2^m

        Returns:
        ----------------
        ChernCharacter: The Chern character of the dyadic character

        Raises:
        ----------------
        ValueError: If the input data is not valid
        """

        if not isinstance(p, int) or not isinstance(m, int) or not m >= 0:
            raise ValueError("Input data must be integers, with m >= 0")

        
        if p % int(2**m) == 0:
            d = p // int(2**m)
            return ChernCharacter(1, int(d), float( d**2 ) / 2)
        elif p % 4 == 3:
            return 3 * self._get_dyadic_character(p+1, m).ch0 * self._get_dyadic_character(p-1, m) - self._get_dyadic_character(p-3, m)
        elif p % 4 == 1:
            return 3 * self._get_dyadic_character(p-1, m).ch0 * self._get_dyadic_character(p+1, m) - self._get_dyadic_character(p+3, m)
        elif p % 4 == 2:
            new_p = p // 2
            return self._get_dyadic_character(new_p, m-1)
        else:
            new_p = p // 4
            return self._get_dyadic_character(new_p, m-2)
        
    def _e_reg(self, p, m):
        """
        Helper function to calculate the regular part of the exceptional vector bundle

        Args:
        ----------------
        p (int): The index of the dyadic character
        m (int): the exponent of the denominator of the dyadic character, e.g. p/2^m

        Returns:
        ----------------
        tuple: A tuple containing the coordinates of the regular part of the exceptional vector bundle
        """
        chern = self._get_dyadic_character(p, m)
        return ( float(chern.ch1) / chern.ch0, chern.ch2 / chern.ch0 )
        
    def _e_plus(self, p, m):
        """
        Helper function to calculate the right-side part of the exceptional vector bundle

        Args:
        ----------------
        p (int): The index of the dyadic character
        m (int): the exponent of the denominator of the dyadic character, e.g. p/2^m

        Returns:
        ----------------
        tuple: A tuple containing the coordinates of the right-side part of the exceptional vector bundle

        
        """
        chern = self._get_dyadic_character(p, m)
        return ( float(chern.ch1) / chern.ch0, chern.ch2 / chern.ch0 - float(1 / (chern.ch0)**2) )
    
    def _e_left(self, p, m):
        """
        
        Helper function to calculate the left-side part of the exceptional vector bundle

        Args:
        ----------------
        p (int): The index of the dyadic character
        m (int): the exponent of the denominator of the dyadic character, e.g. p/2^m

        Returns:
        ----------------

        tuple: A tuple containing the coordinates of the left-side part of the exceptional vector bundle

        """
        x_1, y_1 = self._e_plus(p, m)
        x_2, y_2 = self._e_reg(p-1, m)

        m = float(y_2 - y_1) / (x_2 - x_1) #slope 

        x_3 = m + math.sqrt( m**2 - 2*m*x_1 + 2*y_1 + 1 )
        if x_1 <= x_3 <= x_2 or x_2 <= x_3 <= x_1:
            y_3 = m * x_3 + (y_1 - m * x_1)
            return (x_3, y_3)
        else:
            x_3 = m - math.sqrt( m**2 - 2*m*x_1 + 2*y_1 + 1 )
            y_3 = m * x_3 + (y_1 - m * x_1)
            return (x_3, y_3)
    
    def _e_right(self, p, m):
        """

        Helper function to calculate the right-side part of the exceptional vector bundle

        Args:
        ----------------
        p (int): The index of the dyadic character
        m (int): the exponent of the denominator of the dyadic character, e.g. p/2^m

        Returns:
        ----------------
        tuple: A tuple containing the coordinates of the right-side part of the exceptional vector bundle

        """

        x_1, y_1 = self._e_plus(p, m)
        x_2, y_2 = self._e_reg(p+1, m)

        m = float(y_2 - y_1) / (x_2 - x_1)

        x_3 = m + math.sqrt( m**2 - 2*m*x_1 + 2*y_1 + 1 )
        if x_1 <= x_3 <= x_2 or x_2 <= x_3 <= x_1:
            y_3 = m * x_3 + (y_1 - m * x_1)
            return (x_3, y_3)
        else:
            x_3 = m - math.sqrt( m**2 - 2*m*x_1 + 2*y_1 + 1 )
            y_3 = m * x_3 + (y_1 - m * x_1)
            return (x_3, y_3)
        


    def is_above_curve(self, x, y):
        """
        Function which indicates whether a coordinate (s,q) is above the set of (ch1/ch0, ch2/ch0) for which vector bundles of given charge are stable

        Args:
        ----------------
        x (float): The x-coordinate of the point
        y (float): The y-coordinate of the point

        Returns:
        ----------------
        bool: True if the point is above the curve, False otherwise
        """
        return y > self.curve_estimate(x)
    
    def curve_estimate(self, x):

        """
        Function which estimates the value of y for a given x using linear interpolation between the boundary points

        Args:
        ----------------
        x (float): The x-coordinate of the point

        Returns:
        ----------------
        float: The estimated y-coordinate of the point
        """

        x_values = [p[0] for p in self.boundary_points]

        # Check if x is within the range of the curve
        if x < x_values[0] or x > x_values[-1]:
            raise ValueError("x is outside the range of the curve")

        # Find the segment containing x
        for i in range(len(self.boundary_points) - 1):
            x1, y1 = self.boundary_points[i]
            x2, y2 = self.boundary_points[i + 1]

            if x1 <= x <= x2:
                # Perform linear interpolation to find y-interp at x
                y_interp = y1 + (y2 - y1) * ((x - x1) / (x2 - x1))
                
                return y_interp

        raise ValueError("x is outside the range of the curve")


        
    def plot_drezet_le_potier(self, plot_3d=False, return_json=False, show_walls=False):
        """
        Utility function to plot the Drézet-Le Potier curve in the ch1/ch0, ch2/ch0 plane

        Args:
        ----------------
        plot_3d (bool): Whether to plot the curve in 3D
        return_json (bool): Whether to return the plot as a JSON string
        show_walls (bool): Whether to show the walls of the chambers

        Returns:
        ----------------
        str: A JSON string containing the plot

        Or

        None: If return_json is False


        

        """

        lower_bound = -1*self.width * 2**self.granularity
        upper_bound = self.width * 2**(self.granularity ) + 1

        # Create figure
        fig = go.Figure()   

        if plot_3d:
            for i in range(lower_bound, upper_bound):
                x1, y1 = self._e_plus(i, self.granularity)
                x2, y2 = self._e_left(i, self.granularity)
                x3, y3 = self._e_right(i, self.granularity)

                fig.add_trace(go.Scatter3d(
                    x=[x1, x2], 
                    y=[y1, y2], 
                    z=[0,0],
                    mode='lines+markers',
                    line=dict(color='blue', width=5),
                    marker=dict(size=6),
                    showlegend=False  # Hide legend for individual line segments
                ))

                fig.add_trace(go.Scatter3d
                (
                    x=[x1, x3], 
                    y=[y1, y3], 
                    z=[0,0],
                    mode='lines+markers',
                    line=dict(color='blue', width=5),
                    marker=dict(size=6),
                    showlegend=False  # Hide legend for individual line segments
                ))

                if show_walls:
                    x_4, y_4 = self._e_reg(i, self.granularity)

                    fig.add_trace(go.Scatter3d
                    (
                        x=[x1, x_4], 
                        y=[y1, y_4], 
                        z=[0,0],
                        mode='lines+markers',
                        line=dict(color='gray', width=5),
                        marker=dict(size=6, color='black'),
                        showlegend=False  # Hide legend for individual line segments
                    ))
                    

        else:
            for i in range(lower_bound, upper_bound):

                x1, y1 = self._e_plus(i, self.granularity)
                x2, y2 = self._e_left(i, self.granularity)
                x3, y3 = self._e_right(i, self.granularity)

                fig.add_trace(go.Scatter(
                    x=[x1, x2], 
                    y=[y1, y2], 
                    mode='lines+markers',
                    line=dict(color='blue', width=4),
                    marker=dict(size=6),
                    showlegend=False  # Hide legend for individual line segments
                ))

                fig.add_trace(go.Scatter
                (
                    x=[x1, x3], 
                    y=[y1, y3], 
                    mode='lines+markers',
                    line=dict(color='blue', width=4),
                    marker=dict(size=6),
                    showlegend=False  # Hide legend for individual line segments
                ))


                if show_walls:
                    x_4, y_4 = self._e_reg(i, self.granularity)

                    fig.add_trace(go.Scatter
                    (
                        x=[x1, x_4], 
                        y=[y1, y_4], 
                        mode='lines+markers',
                        line=dict(color='gray', width=5),
                        marker=dict(size=6, color='black'),
                        showlegend=False  # Hide legend for individual line segments
                    ))

            # Ensure equal scaling of x and y axes
            fig.update_layout(
                xaxis=dict(scaleanchor="y"),  # Locks the aspect ratio
                yaxis=dict(scaleanchor="x")   # Ensures square grid
            )    

        if not return_json:
            config = dict({'scrollZoom': True})
            # Show plot
            fig.show(config=config)
        else:
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)




    def plot_stability_chambers(self):


        #################################################
        #             GEOMETRIC CHAMBER                 #
        #################################################

        # Define x values (spread around a region)
        x_vals = np.linspace(-5, 5, 200)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for x in x_vals:
            y_min = float(self.curve_estimate(x)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 150)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array

        # Repeat x values to match the shape of y
        x_vals = np.repeat(x_vals, 150)  # Each x value repeats 10 times

        z_vals = [0] * len(x_vals)

        # Plot the surface
        fig = go.Figure(data=[go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis'))])
        


       

        lower_bound = -1*self.width * 2**self.granularity
        upper_bound = self.width * 2**(self.granularity ) + 1

        for i in range(lower_bound,upper_bound):

            if i % 11 == 0:

                ##############################
                #          ADD WALL          #
                ##############################
                x1, y1 = self._e_plus(i, self.granularity)
                x2, y2 = self._e_reg(i, self.granularity)
                fig.add_trace(go.Scatter3d(
                    x=[x1, x2], 
                    y=[y1, y2], 
                    z=[0,0],
                    mode='lines+markers',
                    line=dict(color='blue', width=9),
                    marker=dict(size=9),
                    showlegend=False  # Hide legend for individual line segments
                ))

                #####################################
                #          ADD NEW CHAMBER          #
                #####################################

                # Define x values (spread around a region)
                z_vals = np.linspace(-5, 5, 200)  # X values from -2 to 2

                # Generate y values satisfying y > x^2
                y_vals = []
                for z in z_vals:
                    y_min = float(self.curve_estimate(z)) # Slightly above x^2
                    y_max = 11.5  # Arbitrary upper bound
                    y_range = np.linspace(y_min, y_max, 150)  # 50 points per x value
                    y_vals.append(y_range)

                # Convert to numpy array
                y_vals = np.array(y_vals).flatten()  # Flatten the y array
                y_vals = -1*y_vals

                z_vals = z_vals / 2
                y_vals = y_vals / 2

                y_vals = y_vals + (1.5 * float(self.curve_estimate(x1)) + y2 -y1)

                # Repeat x values to match the shape of y
                z_vals = np.repeat(z_vals, 150)  # Each x value repeats 10 times

                z_vals = z_vals - x1/2

                x_vals = [x1] * len(x_vals)  


                # Plot the surface
                fig.add_trace(go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                                mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis')))
                


        fig.show()








    def plot_continuing_chamber(self, plot_walls=False, return_json=False):


        #################################################
        #             GEOMETRIC CHAMBER                 #
        #################################################

        # Define x values (spread around a region)
        x_vals = np.linspace(-5, 5, 200)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for x in x_vals:
            y_min = float(self.curve_estimate(x)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 150)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array

        # Repeat x values to match the shape of y
        x_vals = np.repeat(x_vals, 150)  # Each x value repeats 10 times

        z_vals = [0] * len(x_vals)

        # Plot the surface
        fig = go.Figure(data=[go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis'))])
        


       

        lower_bound = -1*self.width * 2**self.granularity
        upper_bound = self.width * 2**(self.granularity ) + 1

        i_sp = range(lower_bound,upper_bound)[ len(range(lower_bound,upper_bound)) // 3 ]

        

        ##############################
        #          ADD WALL          #
        ##############################
        x1, y1 = self._e_plus(i_sp, self.granularity)
        x2, y2 = self._e_reg(i_sp, self.granularity)
        fig.add_trace(go.Scatter3d(
            x=[x1, x2], 
            y=[y1, y2], 
            z=[0,0],
            mode='lines+markers',
            line=dict(color='blue', width=9),
            marker=dict(size=9),
            showlegend=False  # Hide legend for individual line segments
        ))

        #####################################
        #          ADD 2nd CHAMBER          #
        #####################################

        # Define x values (spread around a region)
        z_vals = np.linspace(-5, 5, 180)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for z in z_vals:
            y_min = float(self.curve_estimate(z)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 130)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array
        y_vals = -1*y_vals

        z_vals = z_vals / 2
        y_vals = y_vals / 2

        y_vals = y_vals + (1.5 * float(self.curve_estimate(x1)) + y2 -y1)

        # Repeat x values to match the shape of y
        z_vals = np.repeat(z_vals, 130)  # Each x value repeats 10 times

        z_vals = z_vals - x1/2

        x_vals = [x1] * len(z_vals)  


        # Plot the surface
        fig.add_trace(go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis')))


        #####################################
        #          ADD 3rd CHAMBER          #
        #####################################

        # Define x values (spread around a region)
        x_vals = np.linspace(-5, 5, 150)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for x in x_vals:
            y_min = float(self.curve_estimate(x)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 110)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array

        # Repeat x values to match the shape of y
        x_vals = np.repeat(x_vals, 110)  # Each x value repeats 10 times

        z_vals = np.array([0] * len(x_vals))

        x_vals = x_vals / 4
        y_vals = y_vals / 4

        z_shift = 1.082048
        y_shift = 1.309
        x_shift = -1.686207

        z_vals = z_vals + z_shift
        y_vals = y_vals + y_shift
        x_vals = x_vals + x_shift

        # Plot the surface
        fig.add_trace(go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis')))


        #####################################
        #          ADD 4th CHAMBER          #
        #####################################
        
        # Define x values (spread around a region)
        z_vals = np.linspace(-5, 5, 110)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for z in z_vals:
            y_min = float(self.curve_estimate(z)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 70)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array
        y_vals = -1*y_vals

        # Repeat x values to match the shape of y
        z_vals = np.repeat(z_vals, 70)  # Each x value repeats 10 times

        x_vals = np.array([0] * len(z_vals))

        z_vals = z_vals / 8
        y_vals = y_vals / 8

        z_shift = 1.572048
        y_shift = 3.869
        x_shift = -2.646207

        z_vals = z_vals + z_shift
        y_vals = y_vals + y_shift
        x_vals = x_vals + x_shift

        # Plot the surface
        fig.add_trace(go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis')))


        #####################################
        #          ADD 5th CHAMBER          #
        #####################################

        # Define x values (spread around a region)
        x_vals = np.linspace(-5, 5, 100)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for x in x_vals:
            y_min = float(self.curve_estimate(x)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 50)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array

        # Repeat x values to match the shape of y
        x_vals = np.repeat(x_vals, 50)  # Each x value repeats 10 times

        z_vals = np.array([0] * len(x_vals))

        x_vals = x_vals / 16
        y_vals = y_vals / 16

        z_shift = 1.45
        y_shift = 3.93
        x_shift = -2.586207

        z_vals = z_vals + z_shift
        y_vals = y_vals + y_shift
        x_vals = x_vals + x_shift

        # Plot the surface
        fig.add_trace(go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis')))

        #####################################
        #          ADD 6th CHAMBER          #
        #####################################
        
        # Define x values (spread around a region)
        z_vals = np.linspace(-5, 5, 80)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for z in z_vals:
            y_min = float(self.curve_estimate(z)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 50)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array
        y_vals = -1*y_vals

        # Repeat x values to match the shape of y
        z_vals = np.repeat(z_vals, 50)  # Each x value repeats 10 times

        x_vals = np.array([0] * len(z_vals))

        z_vals = z_vals / 32
        y_vals = y_vals / 32

        z_shift = 1.43
        y_shift = 3.905
        x_shift = -2.52

        z_vals = z_vals + z_shift
        y_vals = y_vals + y_shift
        x_vals = x_vals + x_shift

        # Plot the surface
        fig.add_trace(go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis')))



        #####################################
        #          ADD 7th CHAMBER          #
        #####################################

        # Define x values (spread around a region)
        x_vals = np.linspace(-5, 5, 70)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for x in x_vals:
            y_min = float(self.curve_estimate(x)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 40)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array

        # Repeat x values to match the shape of y
        x_vals = np.repeat(x_vals, 40)  # Each x value repeats 10 times

        z_vals = np.array([0] * len(x_vals))

        x_vals = x_vals / 64
        y_vals = y_vals / 64

        z_shift = 1.399
        y_shift = 3.91
        x_shift = -2.502

        z_vals = z_vals + z_shift
        y_vals = y_vals + y_shift
        x_vals = x_vals + x_shift

        # Plot the surface
        fig.add_trace(go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis')))


        #####################################
        #          ADD 8th CHAMBER          #
        #####################################

        # Define x values (spread around a region)
        z_vals = np.linspace(-5, 5, 60)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for z in z_vals:
            y_min = float(self.curve_estimate(z)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 40)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array
        y_vals = -1*y_vals

        # Repeat x values to match the shape of y
        z_vals = np.repeat(z_vals, 40)  # Each x value repeats 10 times

        x_vals = np.array([0] * len(z_vals))

        z_vals = z_vals / 128
        y_vals = y_vals / 128

        z_shift = 1.399
        y_shift = 3.91
        x_shift = -2.48

        z_vals = z_vals + z_shift
        y_vals = y_vals + y_shift
        x_vals = x_vals + x_shift

        # Plot the surface
        fig.add_trace(go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis')))

        #####################################
        #          ADD 9th CHAMBER          #
        #####################################

        # Define x values (spread around a region)
        x_vals = np.linspace(-5, 5, 70)  # X values from -2 to 2

        # Generate y values satisfying y > x^2
        y_vals = []
        for x in x_vals:
            y_min = float(self.curve_estimate(x)) # Slightly above x^2
            y_max = 11.5  # Arbitrary upper bound
            y_range = np.linspace(y_min, y_max, 40)  # 50 points per x value
            y_vals.append(y_range)

        # Convert to numpy array
        y_vals = np.array(y_vals).flatten()  # Flatten the y array

        # Repeat x values to match the shape of y
        x_vals = np.repeat(x_vals, 40)  # Each x value repeats 10 times

        z_vals = np.array([0] * len(x_vals))

        x_vals = x_vals / 256
        y_vals = y_vals / 256

        z_shift = 1.407
        y_shift = 3.913
        x_shift = -2.482

        z_vals = z_vals + z_shift
        y_vals = y_vals + y_shift
        x_vals = x_vals + x_shift

        # Plot the surface
        fig.add_trace(go.Scatter3d(z=z_vals, x=x_vals, y=y_vals,
                                        mode='markers', marker=dict(size=3, color=y_vals, colorscale='viridis')))


        if plot_walls:
            lower_bound = -1*self.width * 2**self.granularity
            upper_bound = self.width * 2**(self.granularity ) + 1

            for i in range(lower_bound+1, upper_bound-1):
                x1, y1 = self._e_plus(i, self.granularity)
                x_2, y_2 = self._e_reg(i, self.granularity)

                fig.add_trace(go.Scatter3d
                    (
                        x=[x1, x_2], 
                        y=[y1, y_2], 
                        z=[0.03,0.03],
                        mode='lines+markers',
                        line=dict(color='blue', width=9),
                        marker=dict(size=3, color='blue'),
                        showlegend=False  # Hide legend for individual line segments
                    ))
                
        fig.update_layout(showlegend=False)


        if not return_json:
            fig.show()
        else:
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)





def calcZ1(x, y, k, n):
    return cmath.exp(1j*(2*cmath.pi*k/n)) * (cmath.cos(x+y*1j)**(2/n))

def calcZ2(x, y, k, n):
    return cmath.exp(1j*(2*cmath.pi*k/n)) * (cmath.sin(x+y*1j)**(2/n))

def calcZ1Real(x, y, k, n):
    return (calcZ1(x, y, k, n)).real

def calcZ2Real(x, y, k, n):
    return (calcZ2(x, y, k, n)).real

def calcZ(x, y, k1_, k2_, n, a_):
    z1 = calcZ1(x, y, k1_, n)
    z2 = calcZ2(x, y, k2_, n)
    return z1.imag * math.cos(a_) + z2.imag*math.sin(a_)
         
        


if __name__ == "__main__":

    n=3
    a = 0.4
    row, col = 30, 30


    # set param range
    x = np.linspace(0, math.pi/2, col)
    y = np.linspace(-math.pi/2, math.pi/2, row)
    x, y = np.meshgrid(x, y)

    fig = plt.figure(dpi=100)

    ax = fig.add_subplot(projection='3d')
    



    # frames = []

    # fig = go.Figure()





    def update(t):
        ax.cla()

        X1 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 0, 3).astype('float32')
        Y1 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 0, 3).astype('float32')
        Z1 = np.frompyfunc(calcZ, 6, 1)(x, y, 0, 0, 3, math.exp(t)).astype('float32')

        X2 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 0, 3).astype('float32')
        Y2 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 1, 3).astype('float32')
        Z2 = np.frompyfunc(calcZ, 6, 1)(x, y, 0, 1, 3, math.exp(t)).astype('float32')

        X3 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 0, 3).astype('float32')
        Y3 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 2, 3).astype('float32')
        Z3 = np.frompyfunc(calcZ, 6, 1)(x, y, 0, 2, 3, math.exp(t)).astype('float32')
        
        X4 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 1, 3).astype('float32')
        Y4 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 0, 3).astype('float32')
        Z4 = np.frompyfunc(calcZ, 6, 1)(x, y, 1, 0, 3, math.exp(t)).astype('float32')

        X5 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 1, 3).astype('float32')
        Y5 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 1, 3).astype('float32')
        Z5 = np.frompyfunc(calcZ, 6, 1)(x, y, 1, 1, 3, math.exp(t)).astype('float32')

        X6 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 1, 3).astype('float32')
        Y6 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 2, 3).astype('float32')
        Z6 = np.frompyfunc(calcZ, 6, 1)(x, y, 1, 2, 3, math.exp(t)).astype('float32')
        
        X7 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 2, 3).astype('float32')
        Y7 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 0, 3).astype('float32')
        Z7 = np.frompyfunc(calcZ, 6, 1)(x, y, 2, 0, 3, math.exp(t)).astype('float32')

        X8 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 2, 3).astype('float32')
        Y8 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 1, 3).astype('float32')
        Z8 = np.frompyfunc(calcZ, 6, 1)(x, y, 2, 1, 3, math.exp(t)).astype('float32')

        X9 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 2, 3).astype('float32')
        Y9 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 2, 3).astype('float32')
        Z9 = np.frompyfunc(calcZ, 6, 1)(x, y, 2, 2, 3, math.exp(t)).astype('float32')

        ax.plot_surface(X1, Y1, Z1, alpha=0.8, cmap=cm.afmhot)
        ax.plot_surface(X2, Y2, Z2, alpha=0.8, cmap=cm.afmhot)
        ax.plot_surface(X3, Y3, Z3, alpha=0.8, cmap=cm.afmhot)
        ax.plot_surface(X4, Y4, Z4, alpha=0.8, cmap=cm.afmhot)
        ax.plot_surface(X5, Y5, Z5, alpha=0.8, cmap=cm.afmhot)
        ax.plot_surface(X6, Y6, Z6, alpha=0.8, cmap=cm.afmhot)
        ax.plot_surface(X7, Y7, Z7, alpha=0.8, cmap=cm.afmhot)
        ax.plot_surface(X8, Y8, Z8, alpha=0.8, cmap=cm.afmhot)
        ax.plot_surface(X9, Y9, Z9, alpha=0.8, cmap=cm.afmhot)

        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_zlim(-2, 2)




    ani = FuncAnimation(fig = fig, func = update, frames = 100, interval = 175)
    
    
    with open("myvideo.html", "w") as f:
        print(ani.to_html5_video(), file=f)




    # fig.add_trace(go.Surface(x=X1, y=Y1, z=Z1))
    # fig.add_trace(go.Surface(x=X2, y=Y2, z=Z2))
    # fig.add_trace(go.Surface(x=X3, y=Y3, z=Z3))
    # fig.add_trace(go.Surface(x=X4, y=Y4, z=Z4))
    # fig.add_trace(go.Surface(x=X5, y=Y5, z=Z5))
    # fig.add_trace(go.Surface(x=X6, y=Y6, z=Z6))
    # fig.add_trace(go.Surface(x=X7, y=Y7, z=Z7))
    # fig.add_trace(go.Surface(x=X8, y=Y8, z=Z8))
    # fig.add_trace(go.Surface(x=X9, y=Y9, z=Z9))


    # for alpha in range(1, 50):
    #     X1 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 0, 3).astype('float32')
    #     Y1 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 0, 3).astype('float32')
    #     Z1 = np.frompyfunc(calcZ, 6, 1)(x, y, 0, 0, 3, alpha).astype('float32')

    #     X2 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 0, 3).astype('float32')
    #     Y2 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 1, 3).astype('float32')
    #     Z2 = np.frompyfunc(calcZ, 6, 1)(x, y, 0, 1, 3, alpha).astype('float32')

    #     X3 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 0, 3).astype('float32')
    #     Y3 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 2, 3).astype('float32')
    #     Z3 = np.frompyfunc(calcZ, 6, 1)(x, y, 0, 2, 3, alpha).astype('float32')
        
    #     X4 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 1, 3).astype('float32')
    #     Y4 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 0, 3).astype('float32')
    #     Z4 = np.frompyfunc(calcZ, 6, 1)(x, y, 1, 0, 3, alpha).astype('float32')

    #     X5 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 1, 3).astype('float32')
    #     Y5 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 1, 3).astype('float32')
    #     Z5 = np.frompyfunc(calcZ, 6, 1)(x, y, 1, 1, 3, alpha).astype('float32')

    #     X6 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 1, 3).astype('float32')
    #     Y6 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 2, 3).astype('float32')
    #     Z6 = np.frompyfunc(calcZ, 6, 1)(x, y, 1, 2, 3, alpha).astype('float32')
        
    #     X7 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 2, 3).astype('float32')
    #     Y7 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 0, 3).astype('float32')
    #     Z7 = np.frompyfunc(calcZ, 6, 1)(x, y, 2, 0, 3, alpha).astype('float32')

    #     X8 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 2, 3).astype('float32')
    #     Y8 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 1, 3).astype('float32')
    #     Z8 = np.frompyfunc(calcZ, 6, 1)(x, y, 2, 1, 3, alpha).astype('float32')

    #     X9 = np.frompyfunc(calcZ1Real, 4, 1)(x, y, 2, 3).astype('float32')
    #     Y9 = np.frompyfunc(calcZ2Real, 4, 1)(x, y, 2, 3).astype('float32')
    #     Z9 = np.frompyfunc(calcZ, 6, 1)(x, y, 2, 2, 3, alpha).astype('float32')

        

    #     frame = go.Frame(data =[go.Surface(x=X1, y=Y1, z=Z1),
    #                             go.Surface(x=X2, y=Y2, z=Z2),
    #                             go.Surface(x=X3, y=Y3, z=Z3),
    #                             go.Surface(x=X4, y=Y4, z=Z4),
    #                             go.Surface(x=X5, y=Y5, z=Z5),
    #                             go.Surface(x=X6, y=Y6, z=Z6),
    #                             go.Surface(x=X7, y=Y7, z=Z7),
    #                             go.Surface(x=X8, y=Y8, z=Z8),
    #                             go.Surface(x=X9, y=Y9, z=Z9)
    #                             ])
    #     frames.append(frame)


    # fig.update(frames=frames)
    # fig.update_layout(
    #     updatemenus=[dict(
    #         type="buttons",
    #         showactive=False,
    #         buttons=[dict(label="Play",
    #                       method="animate",
    #                       args=[None, dict(frame=dict(duration=20, redraw=True),
    #                                         fromcurrent=True)]),

    #                 dict(label="Pause",
    #                       method="animate",
    #                         args=[[None],
    #                                dict(frame=dict(duration=0, redraw=False),
    #                                      mode="immediate",
    #                                      transition=dict(duration=0))])]
    #     )]
    # )

    # fig.update_layout(showlegend=False)

    # fig.show()






    

    
    




