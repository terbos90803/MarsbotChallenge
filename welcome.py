import PySimpleGUI as sg
import remote

def get_robot_number():
  robots_dict = remote.get_valid_robots();
  first_robot = int(robots_dict['first_robot'])
  last_robot = int(robots_dict['last_robot'])

  layout = [  [sg.Text("What is your robot number?")],
              [sg.Input()],
              [sg.Text(size=(40,1), key='-OUTPUT-')],
              [sg.Button('Ok', bind_return_key=True)] ]

  window = sg.Window('Welcome to the Mars Adventure', layout)
  number = -1
  valid_range = range(first_robot, last_robot + 1)
  while number not in valid_range:
    event, values = window.read()
    number = int(values[0])
    if number not in valid_range:
      window['-OUTPUT-'].update(f'Please enter a robot number between {first_robot} and {last_robot}')
    else:
      resp = remote.register_robot_number(number)
      if resp['status'] == 'fail':
        window['-OUTPUT-'].update(f'Error: {resp["reason"]}')
        number = -1

  window.close()
  return number