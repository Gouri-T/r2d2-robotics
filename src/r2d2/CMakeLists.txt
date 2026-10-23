cmake_minimum_required(VERSION 3.8)
project(r2d2)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf meshes launch worlds rviz
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS scripts/teleop_keyboard.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
