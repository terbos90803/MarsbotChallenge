import welcome
import planner

robot_number = welcome.get_robot_number()

planner.plan_missions(robot_number)

exit(0)
