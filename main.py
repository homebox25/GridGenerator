import math
import random
from pyproj import Proj, transform
import svgwrite


class HexTile:
    def __init__(self, q, r):
        """
        Initialize a hex tile with cube coordinates (q, r, s).

        :param q: Cube coordinate q
        :param r: Cube coordinate r
        """
        self.q = q
        self.r = r
        self.s = -q - r
        self.elevation = random.uniform(0, 100)  # Elevation in meters
        self.temperature = random.uniform(-30, 50)  # Temperature in Celsius
        self.natural_resources = random.choice(['None', 'Iron', 'Gold', 'Coal', 'Oil'])
        self.agriculture = random.choice(['None', 'Low', 'Medium', 'High'])

    def __repr__(self):
        return f"HexTile(q={self.q}, r={self.r}, elevation={self.elevation:.1f}, " \
               f"temperature={self.temperature:.1f}, natural_resources={self.natural_resources}, " \
               f"agriculture={self.agriculture})"


class HexGrid:
    def __init__(self, radius):
        """
        Initialize a hexagonal grid with a given radius.

        :param radius: The radius of the hexagonal grid (number of rings).
        """
        self.radius = radius
        self.grid = self.generate_grid()

    def generate_grid(self):
        """
        Generate a hexagonal grid based on the radius.

        :return: A dictionary of hex tiles with (q, r) as keys.
        """
        grid = {}
        for q in range(-self.radius, self.radius + 1):
            for r in range(max(-self.radius, -q - self.radius), min(self.radius, -q + self.radius) + 1):
                grid[(q, r)] = HexTile(q, r)
        return grid

    def get_tile(self, q, r):
        """
        Retrieve a tile from the grid based on its cube coordinates.

        :param q: Cube coordinate q
        :param r: Cube coordinate r
        :return: The HexTile object if it exists, otherwise None.
        """
        return self.grid.get((q, r))

    def simulate_tectonics(self):
        """
        Simulate tectonics using pyproj for coordinate transformations.
        """
        # Define projections (example: WGS84 to a flat Cartesian system)
        proj_wgs84 = Proj(proj='latlong', datum='WGS84')
        proj_cartesian = Proj(proj='aeqd', datum='WGS84')  # Azimuthal Equidistant Projection

        for (q, r), tile in self.grid.items():
            # Convert hex coordinates to approximate lat/lon for simulation
            lon, lat = self.hex_to_latlon(q, r)

            # Transform lat/lon to Cartesian coordinates
            x, y = transform(proj_wgs84, proj_cartesian, lon, lat)

            # Simple elevation simulation based on Cartesian coordinates
            # Peaks in the center, lowering outward
            tile.elevation = 1000 - (math.sqrt(x ** 2 + y ** 2) / 10)

            # Ensure elevation stays non-negative
            tile.elevation = max(0, tile.elevation)

    def hex_to_latlon(self, q, r):
        """
        Convert hex coordinates to approximate latitude and longitude.

        :param q: Cube coordinate q
        :param r: Cube coordinate r
        :return: Tuple of (longitude, latitude).
        """
        scale = 10  # Scaling factor for lat/lon spread
        lon = q * scale
        lat = r * scale
        return lon, lat

    def display_grid(self):
        """
        Print a summary of all hex tiles in the grid.
        """
        for key, tile in self.grid.items():
            print(tile)

    def visual_grid(self):
        """
        Print a visual representation of the hexagonal grid.
        """
        min_q = -self.radius
        max_q = self.radius

        for r in range(-self.radius, self.radius + 1):
            # Print spaces for alignment
            print(" " * (self.radius - r), end="")
            for q in range(max(-self.radius, -r - self.radius), min(self.radius, -r + self.radius) + 1):
                if (q, r) in self.grid:
                    print("o ", end="")  # 'o' represents a hex tile
                else:
                    print("  ", end="")
            print()

    def export_to_svg(self, filename="hexmap.svg"):
        """
        Export the hexagonal grid to an SVG file.

        :param filename: Name of the SVG file to save.
        """
        hex_size = 20  # Size of each hexagon
        dwg = svgwrite.Drawing(filename, profile='tiny')

        for (q, r), tile in self.grid.items():
            x, y = self.hex_to_pixel(q, r, hex_size)
            hex_points = self.calculate_hex_points(x, y, hex_size)
            color = self.get_color_by_elevation(tile.elevation)
            dwg.add(dwg.polygon(points=hex_points, fill=color, stroke="black"))

        dwg.save()

    def hex_to_pixel(self, q, r, size):
        """
        Convert hex coordinates to pixel coordinates for rendering.

        :param q: Cube coordinate q
        :param r: Cube coordinate r
        :param size: Size of the hexagon.
        :return: Tuple of (x, y) pixel coordinates.
        """
        x = size * (3 / 2 * q)
        y = size * (math.sqrt(3) * (r + q / 2))
        return x, y

    def calculate_hex_points(self, x, y, size):
        """
        Calculate the vertices of a hexagon at a given position.

        :param x: X-coordinate of the hexagon center.
        :param y: Y-coordinate of the hexagon center.
        :param size: Size of the hexagon.
        :return: List of (x, y) tuples for the hexagon vertices.
        """
        points = []
        for i in range(6):
            angle = 2 * math.pi / 6 * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.append((px, py))
        return points

    def get_color_by_elevation(self, elevation):
        """
        Get a color based on elevation.

        :param elevation: Elevation value.
        :return: Hex color string.
        """
        if elevation > 800:
            return "#8B0000"  # High elevation: Dark Red
        elif elevation > 400:
            return "#FFA500"  # Medium elevation: Orange
        else:
            return "#00FF00"  # Low elevation: Green


if __name__ == "__main__":
    # Create a hexagonal grid with radius 3
    radius = 3
    hex_grid = HexGrid(radius)

    # Simulate tectonics
    hex_grid.simulate_tectonics()

    # Display all tiles in the grid
    hex_grid.display_grid()

    # Display a visual representation of the grid
    print("\nVisual Representation of the Grid:")
    hex_grid.visual_grid()

    # Export to SVG
    hex_grid.export_to_svg("hexmap.svg")

    # Example: Get a specific tile's data
    tile = hex_grid.get_tile(0, 0)
    print("\nSpecific Tile:", tile)
