import welcome
import planner
import thankyou

robot_number = welcome.get_robot_number()

planner.plan_missions(robot_number)

thankyou.thanks()
