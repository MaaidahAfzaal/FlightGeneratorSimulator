# import pandas as pd
from itertools import zip_longest


def path_generator(lon1: float, lon2: float, lat1: float, lat2: float, lon_steps: int,
                   lat_steps: int):

    def path_iterator(start_coord: float, end_coord: float, steps: int):

        step_size = (end_coord - start_coord) / steps
        trace_path = []
        if start_coord > end_coord:
            val = start_coord

            while val > end_coord + step_size:
                trace_path.append(val)
                val += step_size

        else:
            val = start_coord

            while val < end_coord + step_size:
                trace_path.append(val)
                val += step_size

        return trace_path[:-1]

    lon_steps = path_iterator(lon1, lon2, lon_steps)
    lat_steps = path_iterator(lat1, lat2, lat_steps)

    if not lon_steps: lon_steps = lat_steps
    if not lat_steps: lat_steps = lon_steps 

    # Join lat long values in single list
    path_trace = list(zip_longest(lon_steps, lat_steps))

    if lon_steps != lat_steps:
        # Get the last item of the smallest list
        place_holder = lon_steps[-1] if len(lon_steps) < len(lat_steps) else lat_steps[-1]

        # Replace None with place_holder value
        path_trace = [[v if v is not None else place_holder for v in nested] for nested in path_trace]

    return path_trace
