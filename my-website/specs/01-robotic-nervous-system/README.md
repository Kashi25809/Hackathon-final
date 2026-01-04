# Module 01: The Robotic Nervous System (ROS 2)

**Status:** ✅ Complete  
**Focus:** Middleware & Foundations

## 🎯 Learning Objectives

- Understand ROS 2 architecture and communication patterns (Nodes, Topics, Services, Actions).
- Create and manage ROS 2 nodes using Python (`rclpy`).
- Design robot models using URDF (Unified Robot Description Format).
- Implement basic robot control loops.

## 📚 Content Structure

The module content is located in `docs/01-robotic-nervous-system/`:

| File | Topic | Description |
|------|-------|-------------|
| `01-ros2-fundamentals.md` | Core Concepts | Nodes, DDS, and graph architecture |
| `02-nodes-topics.md` | Communication | Pub/Sub patterns and Topic tools |
| `03-services-actions.md` | Interaction | Request/Response and Long-running tasks |
| `04-python-rclpy.md` | Implementation | Writing idiomatic Python ROS 2 code |
| `05-urdf-modeling.md` | Description | Building visual and collision models |
| `06-deliverable.md` | Project | "Hello Robot" and URDF assembly |

## 🛠️ Technical Implementation

### Key Components
1. **Publisher/Subscriber**: Basic data flow.
2. **Service Client/Server**: Synchronous operations.
3. **Action Client/Server**: Asynchronous goal tracking.
4. **URDF**: XML-based robot description.

### Code Examples
- Hello World node
- Simple Bipedal Robot URDF
- Launch file configuration

## ✅ Deliverables

1. **Hello Robot Node**: A fully functional ROS 2 node that publishes status and subscribes to commands.
2. **Bipedal URDF**: A valid robot description with links (torso, legs) and joints, viewable in RViz.
3. **System Launch**: A `launch.py` script to bring up the robot state publisher and RViz.
