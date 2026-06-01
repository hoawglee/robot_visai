import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    package_dir = get_package_share_directory('robot_navigation')
    map_file = os.path.join(package_dir, 'maps', 'warehouse.yaml') #lay file map 
    params_file = os.path.join(package_dir, 'config', 'nav2_params.yaml')
    rviz_config = os.path.join(package_dir, 'rviz', 'nav2_default_view.rviz')

    # MAP SERVER 
    map_server = Node(
        package='nav2_map_server',  
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': map_file},
                    {'use_sim_time': True}]
    )
    #load ban do da save
    #map_server có nhiệm vụ đọc file bản đồ dạng YAML/PGM đã được lưu từ SLAM, 
    #sau đó publish bản đồ tĩnh lên topic /map để các node định vị và điều hướng sử dụng.

    # MAP SERVER UPDATE
    map_saver = Node(
        package='nav2_map_server',
        executable='map_saver_server',
        name='map_saver',
        output='screen',
        parameters=[params_file]
    )
    #Node này dùng để lưu map.

    # AMCL
    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[params_file]
    )
    #AMCL dùng để định vị robot trên bản đồ đã có sẵn.
    #Nếu không có AMCL thì Nav2 không biết robot đang ở vị trí nào để lập đường đi.
    #AMCL là node định vị Monte Carlo. Nó sử dụng bản đồ tĩnh, dữ liệu LiDAR, odometry và TF để ước lượng pose của robot trong hệ tọa độ map.
    #Khi bạn dùng RViz bấm: 2D Pose estimate

    # PLANNER
    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[params_file]
    )
    #Node này dùng để lập đường đi toàn cục.
    #Khi bạn chọn điểm đích bằng: Nav goas
    #thì planner_server sẽ tìm đường từ vị trí robot hiện tại đến điểm đích.
    #planner_server có nhiệm vụ tạo đường đi toàn cục từ vị trí hiện tại của robot đến goal dựa trên bản đồ

    # CONTROLLER
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[params_file]
    )
    #controller_server là bộ điều khiển cục bộ, có nhiệm vụ bám theo global path và xuất lệnh vận tốc /cmd_vel cho robot.


    # SMOOTHER SERVER (bắt buộc)
    smoother_server = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        parameters=[params_file]
    )
    #Node này dùng để làm mượt đường đi.
    #Đường do planner tạo ra đôi khi bị gấp khúc. smoother_server giúp đường đi mềm hơn, robot chạy tự nhiên hơn.

    # BEHAVIOR TREE NAVIGATOR
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[params_file]
    )
    #Đây là node điều phối nhiệm vụ navigation.
    #Sau đó bt_navigator sẽ gọi các node khác theo thứ tự: gọi planner_server để lập đường
    # gọi controller_server để đi theo đường, nếu lỗi thì gọi behavior_server để xử lý, đến goal thì dừng
    #bt_navigator là node trung tâm nhận goal từ người dùng, sau đó điều phối planner, 
    # controller và behavior server thông qua Behavior Tree để robot di chuyển đến đích.
    

    # RECOVERY SERVER (bắt buộc)
    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[params_file]
    )
    #Node này xử lý các hành vi khi robot gặp vấn đề. robot bị kẹt ,không tìm được đường
    #behavior_server cung cấp các hành vi phục hồi như quay tại chỗ, lùi lại hoặc chờ khi robot gặp lỗi trong quá trình điều hướng.


    # VELOCITY SMOOTHER (tùy nhưng nên có)
    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=[params_file]
    )
    #Node này dùng để làm mượt vận tốc.
    #velocity_smoother giúp vận tốc tăng/giảm từ từ hơn.
    
    lifecycle_manager_loc = Node(
    package='nav2_lifecycle_manager',
    executable='lifecycle_manager',
    name='lifecycle_manager_localization',
    output='screen',
    parameters=[{
            'use_sim_time': True,
            'autostart': True, #Nó cho phép tự động activate node.
            'node_names': [
                'map_server',
                'map_saver',
                'amcl'
            ]
        }]
    )
    #nhiều node Nav2 khi bật lên chưa chạy ngay. Nó có các trạng thái:unconfigured → inactive → active
    #lifecycle_manager có nhiệm vụ tự động kích hoạt chúng.
    #Nếu không có lifecycle manager, nhiều node Nav2 sẽ bật lên nhưng chưa hoạt động.

    # LIFECYCLE MANAGER
    lifecycle_manager_nav = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'planner_server',
                'controller_server',
                'smoother_server',
                'bt_navigator',
                'behavior_server',
                'velocity_smoother'
            ]
        }]
    )
    #Node này kích hoạt nhóm navigation: o ben tren vi du planner_server controller_server
    #Tên trong node_names phải trùng chính xác với name= của từng node.

    # RVIZ
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config] #-d nghĩa là dùng file display config:
    )
    #Node này mở RViz với file cấu hình có sẵn.

    return LaunchDescription([
        map_server,
        map_saver,
        amcl,
        planner_server,
        controller_server,
        smoother_server,
        bt_navigator,
        behavior_server,
        velocity_smoother,
        lifecycle_manager_loc,
        lifecycle_manager_nav,
        rviz_node
    ])
#navigation.launch.py = file bật map + định vị AMCL + lập đường + điều khiển robot + RViz
#File navigation.launch.py dùng để khởi động hệ thống điều hướng Nav2. Trong đó map_server
#load bản đồ đã lưu, amcl định vị robot trên bản đồ, planner_server lập đường đi toàn cục,
#controller_server điều khiển robot bám theo đường, bt_navigator nhận goal và điều phối toàn bộ
#quá trình navigation. Ngoài ra còn có behavior_server để xử lý khi robot gặp lỗi, velocity_smoother
#để làm mượt vận tốc và lifecycle_manager để tự động kích hoạt các node Nav2.
