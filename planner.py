import PySimpleGUI as sg
import remote
import time


move_button = 'Move'
left_button = 'Left'
right_button = 'Right'
delete_button = u'\u232B'
send_button = 'Send Plan to Robot on Mars'

def plan_missions(robot_number):

  command_row = [

  ]
  plan_row = [ sg.Input(), sg.Button(delete_button, disabled=False, tooltip='Delete last move')]
  layout = [  [sg.Text(size=(40,1), key='-SOL-MESSAGE-')],
              command_row,
              plan_row,
              [sg.Button(send_button, disabled=False)] ]

  window = sg.Window(f'Mars Adventure - Mission Planner - Robot {robot_number}', layout)

  # Outer planning loop, once per submitted plan
  while True:
    sol_dict = remote.get_sol()
    sol_base = float(sol_dict['sol'])
    sol_total = float(sol_dict['total_sols'])
    mins_per_sol = float(sol_dict['mins_per_sol']) # minutes per sol
    if sol_base > sol_total:
      break
    sol_rt_base = time.time() # connect sol_now to the realtime clock

    # Inner planning loop, once per window event
    planning = True
    while planning:
      event, values = window.read(timeout=300)
      if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
          print('============ Event = ', event, ' ==============')
          print('-------- Values Dictionary (key=value) --------')
          for key in values:
            print(key, ' = ',values[key])

          if event == delete_button:
            pass
          elif event == send_button:
            pass

      # Update the Sol timer
      mins_planning = (time.time() - sol_rt_base) / 60.0
      sol_now = sol_base + mins_planning / mins_per_sol
      if sol_now > sol_total:
        break
      window['-SOL-MESSAGE-'].update(f'Sol {sol_now:.1f} of {sol_total:.0f}')

  window.close()
