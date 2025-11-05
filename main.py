import os
import sys
import threading as th
import code
import sv_ttk

from typing import Literal
from tkinter import ttk, Tk, BooleanVar
from tkinter import messagebox as mb
from tkinter.filedialog import askopenfilename

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False


class App(Tk):
    """Main application window for displaying 3D point clouds using Matplotlib and Plotly."""

    def __init__(self):
        """Initialize the main Tkinter window and base UI."""
        super().__init__()
        self.title("Chmura punktów 3D")
        self.data: pd.DataFrame = None
        
        # Plot-related attributes
        self.current_mask_mode: Literal["default", "mask"] = "default"
        self.plot_frame: ttk.Frame | None = None
        self.fig: Figure | None = None
        self.ax = None
        self.canvas = None
        self._mpl_initial_view = {}

        # Build the main interface
        self._build_base_ui()

        self.update_idletasks()
        self.resizable(False, False)

    # 
    # UI setup and data handling
    # 

    def _build_base_ui(self):
        """Construct the main control buttons and status label."""
        row = 0
        self.load_data_btn = ttk.Button(self, text="Wczytaj plik", command=self._on_load_data_click)
        self.load_data_btn.grid(row=row, column=0, padx=10, pady=8)
        
        self.info_lbl = ttk.Label(self, text="Brak wczytanych danych.")
        self.info_lbl.grid(row=row, column=1, padx=10, pady=8, sticky="w")

        row += 1
        self.btn_show_mpl = ttk.Button(self, text="Stwórz wykres [MPL]", command=self._draw_plot_frame)
        self.btn_show_mpl.grid(row=row, column=0, padx=10, pady=6)

        plotly_text = "Stwórz wykres w przeglądarce [Plotly]"
        if not PLOTLY_AVAILABLE:
            plotly_text += " [niedostepne]"
        self.btn_show_plotly = ttk.Button(self, text=plotly_text, command=self._open_plotly_window)
        self.btn_show_plotly.grid(row=row, column=1, padx=10, pady=6)

    @property
    def masks(self):
        """Return boolean masks for color zones based on Z coordinate."""
        return {
            'red': self.data['Z'] < -1,
            'orange': (self.data['Z'] >= -1) & (self.data['Z'] < 0.5),
            'green': self.data['Z'] >= 0.5
        }

    def _on_load_data_click(self):
        """Handle loading a dataset from file."""
        filepath = askopenfilename(initialdir="./data")
        if not filepath:
            return
        try:
            self.data = pd.read_csv(filepath, sep=r"\s+", header=None, names=['X', 'Y', 'Z'])
            self.info_lbl.config(text=f"Loaded: {os.path.basename(filepath)} [{len(self.data)} records].")
        except Exception as e:
            mb.showerror("Błąd wczytywania", f"Podczas wczytywania pliku pojawił się błąd:\n{e}")

    # 
    # MPL
    # 

    def _draw_plot_frame(self):
        """Display or refresh the embedded Matplotlib plot frame."""
        if self.data is None:
            mb.showwarning("Brak danych", "Proszę wczytać plik z danymi.")
            return

        if self.plot_frame is not None:
            self.plot_frame.lift()
            self._plot_mpl_in_frame()
            return

        self.plot_frame = ttk.Frame(self, relief="groove", borderwidth=2)
        self.plot_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Controls bar
        controls = ttk.Frame(self.plot_frame)
        controls.pack(side="top", fill="x", padx=6, pady=6)

        # Toggle color mask checkbox
        self.mask_var = BooleanVar(value=False)
        self.btn_toggle = ttk.Checkbutton(controls,
                                          text="Nałóż maskę kolorów",
                                          variable=self.mask_var,
                                          command=self._toggle_colors)
        self.btn_toggle.pack(side="left", padx=4)

        self.btn_reset = ttk.Button(controls, text="Resetuj widok", command=self._reset_view)
        self.btn_reset.pack(side="left", padx=4)

        btn_close = ttk.Button(controls, text="Zamknij wykres", command=self._destroy_plot_frame)
        btn_close.pack(side="left", padx=4)

        # Plot area
        self.canvas_container = ttk.Frame(self.plot_frame)
        self.canvas_container.pack(side="top", fill="both", expand=True, padx=6, pady=6)

        self._plot_mpl_in_frame()
        self._update_geometry()

    def _destroy_plot_frame(self):
        """Remove the Matplotlib plot frame and release resources."""
        if self.plot_frame is None:
            return
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
            self.fig = None
            self.ax = None
        self.plot_frame.destroy()
        self.plot_frame = None
        self._update_geometry()

    def _reset_view(self):
        """Reset the Matplotlib 3D view to its initial state."""
        if self.ax is None or not self._mpl_initial_view:
            return
        self.ax.view_init(elev=self._mpl_initial_view['elev'], azim=self._mpl_initial_view['azim'])
        self.ax.set_xlim(self._mpl_initial_view['xlim'])
        self.ax.set_ylim(self._mpl_initial_view['ylim'])
        self.ax.set_zlim(self._mpl_initial_view['zlim'])
        self.canvas.draw()

    def _config_tkplt(self):
        """Initialize the embedded Matplotlib figure and canvas if not yet created."""
        if self.fig is None:
            self.fig = Figure(dpi=150)
            self.ax = self.fig.add_subplot(projection='3d')
            self.ax.set_autoscale_on(False)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_container)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _plot_mpl_in_frame(self):
        """Render the current dataset in the embedded Matplotlib frame."""
        self._config_tkplt()
        self._draw_mpl(default=(self.current_mask_mode == "default"))
        self._mpl_initial_view = {'elev': self.ax.elev,
                                  'azim': self.ax.azim,
                                  'xlim': self.ax.get_xlim3d(),
                                  'ylim': self.ax.get_ylim3d(),
                                  'zlim': self.ax.get_zlim3d()}

    def _draw_mpl(self, default: bool):
        """Draw the Matplotlib 3D scatter plot, optionally with color masking."""
        self.ax.clear()
        if default:
            self.ax.plot(self.data['X'], self.data['Y'], self.data['Z'],
                         linestyle='', marker='.', markersize=1, color='blue')
        else:
            for color, mask in self.masks.items():
                self.ax.plot(self.data[mask]['X'], self.data[mask]['Y'], self.data[mask]['Z'],
                             linestyle='', marker='.', markersize=1, color=color)
        self.ax.set_xlim(self.data['X'].min(), self.data['X'].max())
        self.ax.set_ylim(self.data['Y'].min(), self.data['Y'].max())
        self.ax.set_zlim(self.data['Z'].min(), self.data['Z'].max())
        self.canvas.draw()

    def _toggle_colors(self):
        """Toggle color masking for the Matplotlib plot."""
        if self.data is None:
            return
        self.current_mask_mode = "mask" if self.mask_var.get() else "default"
        if self.ax is not None:
            self._draw_mpl(default=(self.current_mask_mode == "default"))

    # 
    # Plotly
    # 

    def _open_plotly_window(self):
        """Open a Plotly 3D scatter plot in the browser with a color toggle menu."""
        if not PLOTLY_AVAILABLE:
            mb.showerror("Nie wykryto plotly", "Nie wykryto plotly. Zainstaluj je komendą:\n pip install plotly")
            return
        if self.data is None:
            mb.showwarning("Brak danych", "Proszę wczytać plik z danymi.")
            return

        df = self.data.copy()
        def mask_conditions(z):
            if z < -1:
                return 'red' 
            elif z < 0.5:
                return 'orange'
            return 'green' 
        
        
        default_markers = ['blue'] * len(df)
        colored_markers = [mask_conditions(z) for z in df['Z']]

        fig = go.Figure(data=[go.Scatter3d(x=df['X'],
                                           y=df['Y'],
                                           z=df['Z'],
                                           mode='markers',
                                marker=dict(size=3,
                                            color=default_markers))])
        fig.update_layout(title="Chmura punktów 3D",
                          updatemenus=[dict(
                          buttons=[dict(label="Domyślne markery", method="update",
                                        args=[{"marker.color": [default_markers]}]),
                                   dict(label="Nałóż maskę kolorów", method="update",
                                        args=[{"marker.color": [colored_markers]}])],
                          direction="down",
                          showactive=True,
                          x=1.02, xanchor="left",
                          y=0.5, yanchor="middle")])
        fig.show()

    # 
    # Utility methods
    # 

    def _update_geometry(self):
        """Resize the main window to fit current layout."""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)


def devmode():
    """Start an interactive console in a background thread."""
    th.Thread(target=lambda: code.interact(local=globals()), daemon=True).start()


if __name__ == "__main__":
    if "--dev" in sys.argv:
        devmode()
    app = App()
    sv_ttk.set_theme("dark")
    app.mainloop()
