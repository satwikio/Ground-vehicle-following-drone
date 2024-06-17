# IBVS for Drone operations

This is a simulation project in which we are simulating basic drone operations in Gazebo using IBVS.

## Authors

- Satwik Jaiswal B21263
- Jagadeesh Rachapudi S23096

## Installation and Running

1. Navigate to the `ros2_ws` directory.
2. Open a terminal.
3. Build the workspace by running the following command:
   ```bash
   colcon build
   ```
4. Source the environment by running:
   ```bash
   source install/setup.bash
   ```
5. Launch the required launch file by running:
   ```bash
   ros2 launch drive_drone p1_a_something
   ```
   Replace `something` with the name of the launch file that is specified in the video. This will open an environment with a drone and a ground vehicle.
6. Run the `img_sub` node by executing:
   ```bash
   ros2 run drone_controller img_sub
   ```
   This command will run the image subscriber node, which fetches the image data from the bottom camera of the drone and publishes the velocity of the drone after processing the image.

## Credits

This project utilizes code from the following repositories:

- [SJTU_DRONE](https://github.com/NovoG93/sjtu_drone): Our code is made upon this repo.

## Contributing

Provide guidelines for contributing to the project. Include information on how to report bugs, suggest enhancements, and submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

