# POD
This code works on performing the POD analysis for the velocity components. Code is useful for data which is extracted for a particular smaller location from a huge CFD domain. The code is only tested for the .vtk/.vtu files extracted from paraview 5.6.0.


1. To run this file make sure it is placed in same folder as the time files for the snapshot data.
2. All time folder should be named as time_0, time_1......time_N. It can be done in paraview 5.6.0.
3. Thes folder will have .vtu files within itself.
4. Iterate through the time folders (line 72) : put folder range here.
5. Visualization of POD modes can be done using modes.vtu file.
6. "U.csv" saves the POD modes.
7. "S.csv" saves the singular values.
8. "VT.csv" saves the temporal coefficients of the modes.
