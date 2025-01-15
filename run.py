import os
import vtk
import numpy as np
from scipy.linalg import svd
import csv

# Function to read a .vtu file and extract point-centered velocity vectors
def read_vtu(file_path):
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_path)
    reader.Update()  # Reads the file
    output = reader.GetOutput()
    
    # Get the velocity array (ensure the name matches your data)
    velocity_array = output.GetPointData().GetArray("U")
    
    if velocity_array is None:
        raise ValueError(f"Velocity data not found in file: {file_path}")
    
    num_points = velocity_array.GetNumberOfTuples()
    
    # Extract velocity components
    velocities = np.zeros((num_points, 3))
    for i in range(num_points):
        velocities[i, :] = velocity_array.GetTuple3(i)
        
    return velocities, output

# Function to write modes to a .vtu file
def write_modes_vtu(file_path, modes, template):
    # Create a new VTK unstructured grid
    grid = vtk.vtkUnstructuredGrid()
    grid.DeepCopy(template)

    # Remove all existing point data arrays
    grid.GetPointData().Initialize()

    # Create and add mode arrays to the grid
    for mode_index, mode in enumerate(modes):
        mode_array = vtk.vtkFloatArray()
        mode_array.SetNumberOfComponents(1)  # Only one component since it's just u, v, or w
        mode_array.SetName(f"Mode{mode_index + 1}")
        
        # Fill the VTK array with the mode data
        for i in range(mode.shape[0]):
            mode_array.InsertNextTuple1(mode[i])  # Only one value per point
        
        # Add the mode array to the grid
        grid.GetPointData().AddArray(mode_array)

    # Write the grid to a .vtu file
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(file_path)
    writer.SetInputData(grid)
    writer.SetDataModeToAscii()  # Save as ASCII
    writer.Write()

# Function to save a numpy array to a CSV file
def save_csv(file_path, array):
    np.savetxt(file_path, array, delimiter=",")

# Path to the main directory (current directory)
main_directory = os.getcwd()

# List to store velocity matrices for each time step
velocity_matrices = []
templates = []

# Specify the velocity component (0 for u, 1 for v, 2 for w)
velocity_component = int(input("Enter the velocity component to analyze (0 for u, 1 for v, 2 for w): "))

# Iterate through the time folders
for i in range(1441):
    time_folder = os.path.join(main_directory, f"time_{i}")
    
    # Check if the directory exists
    if os.path.isdir(time_folder):
        # Construct the .vtu file name
        vtu_file = os.path.join(time_folder, f"time_{i}_0_0.vtu")
        
        # Check if the file exists
        if os.path.isfile(vtu_file):
            try:
                print(f"Reading file: {vtu_file}")
                velocities, template = read_vtu(vtu_file)
                # Append only the specified velocity component
                velocity_matrices.append(velocities[:, velocity_component])
                templates.append(template)
                print(f"Successfully read: {vtu_file}")
            except ValueError as e:
                print(e)
        else:
            print(f"File not found: {vtu_file}")
    else:
        print(f"Folder not found: {time_folder}")

# Stack velocity matrices into a single 2D array where each column is a time step
if velocity_matrices:
    num_points = len(velocity_matrices[0])  # Number of points from the first time step
    combined_velocity_matrix = np.zeros((num_points, len(velocity_matrices)))

    # Populate the combined matrix with the chosen component
    for t, velocities in enumerate(velocity_matrices):
        combined_velocity_matrix[:, t] = velocities

    # Perform SVD on the combined velocity matrix
    U, S, VT = svd(combined_velocity_matrix, full_matrices=False)

    # Display the singular values
    print("Singular values:")
    print(S)

    # Ask the user how many modes they want to save
    num_modes = int(input("Enter the number of modes to save: "))
    
    # Save each spatial mode separately
    modes = []
    for mode_index in range(num_modes):
        mode = U[:, mode_index]
        modes.append(mode)
    
    # Write all modes to a single .vtu file
    output_file_path = os.path.join(main_directory, "modes.vtu")
    write_modes_vtu(output_file_path, modes, templates[0])
    print(f"All modes saved to {output_file_path}")

    # Save U, S, and VT to CSV files
    save_csv(os.path.join(main_directory, "U.csv"), U)
    save_csv(os.path.join(main_directory, "S.csv"), S)
    save_csv(os.path.join(main_directory, "VT.csv"), VT)
    print("U, S, and VT matrices saved to CSV files.")
else:
    print("No velocity data found.")

