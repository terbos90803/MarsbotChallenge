import PySimpleGUI as sg
import remote
import time


forward_button = u'\u2191' # 'Forward'
reverse_button = u'\u2193' # 'Reverse'
left_button = u'\u2190' # 'Left'
right_button = u'\u2192' # 'Right'
grab_button = 'Grab'
release_button = 'Release'
delete_button = u'\u232B'
send_button = 'Send Plan to Robot on Mars'
rescue_button = 'Rescue'

sol_key = '-SOL-MESSAGE-'
move_key = '-MOVE-'
turn_key = '-TURN-'
plan_key = '-PLAN-'
progress_key = '-PROGRESS-'

progress_template = '----------------------------------------'

def plan_missions(robot_number):

  sol_row = [
    sg.Column( [[sg.Text(size=(30,1), key=sol_key, font=('Sans', 24), justification='center')]], justification='c')
  ]
  move_row = [
    sg.Text('Move:', size=(6,1)), 
    sg.Input(size=(3,1), key=move_key, tooltip='How far to move.  Decimals are ok.'), 
    sg.Button(forward_button, size=(5,1), tooltip='Straight Forward'), 
    sg.Button(reverse_button, size=(5,1), tooltip='Straight Reverse')
  ]
  turn_row = [
    sg.Text('Turn:', size=(6,1)), 
    sg.Input(size=(3,1), key=turn_key, tooltip='How far to turn. '), 
    sg.Button(left_button, size=(5,1), tooltip='Turn Left'), 
    sg.Button(right_button, size=(5,1), tooltip='Turn Right')
  ]
  grab_row = [
    sg.Text('Grab:', size=(6,1)), 
    sg.Button(grab_button, size=(10,1)), 
    sg.Button(release_button, size=(10,1))
  ]
  plan_row = [
    sg.Button(delete_button, disabled=True, tooltip='Delete last move'),
    sg.Text(size=(40,1), key=plan_key, font=('Sans',10))
  ]
  send_row = [
    sg.Button(send_button, disabled=True),
    sg.Button(rescue_button)
  ]
  controls_row = [
    sg.Column( [
      move_row,
      turn_row,
      grab_row,
      plan_row,
      send_row
    ], justification='c')
  ]
  progress_row = [
    sg.Column( [[
      sg.Text('Earth'), 
      sg.Text(progress_template, key=progress_key), 
      sg.Text('Mars')
      ]], justification='c')
  ]

  layout = [
    sol_row,
    controls_row,
    progress_row
  ]

  window = sg.Window(f'Mars Adventure - Mission Planner - Robot {robot_number}', layout, font=('Sans', 14), finalize=True)

  window[move_key].update(value='1')
  window[turn_key].update(value='1')

  plan = []

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
      # Update the Sol timer
      mins_planning = (time.time() - sol_rt_base) / 60.0
      sol_now = sol_base + mins_planning / mins_per_sol
      if sol_now > sol_total:
        break
      window['-SOL-MESSAGE-'].update(f'Sol {sol_now:.1f} of {sol_total:.0f}')

      # Display the current plan
      plan_text = ''
      for step in plan:
        if len(step) == 1:
          plan_text += f'{step[0]}, '
        else:
          plan_text += f'{step[0]} {step[1]}, '
      window[plan_key].update(plan_text)

      # Enable the correct buttons
      empty_plan = len(plan) == 0
      window[delete_button].update(disabled=empty_plan)
      window[send_button].update(disabled=empty_plan)

      # Wait for window events
      # timeout allows the Sol timer to update like a clock
      event, values = window.read(timeout=500)

      # Process any other events
      if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
          #print('============ Event = ', event, ' ==============')
          #print('-------- Values Dictionary (key=value) --------')
          #for key in values:
          #  print(key, ' = ',values[key])

          if event == delete_button:
            plan.pop()
          elif event == forward_button:
            plan.append([event, float(values[move_key])])
          elif event == reverse_button:
            plan.append([event, float(values[move_key])])
          elif event == left_button:
            plan.append([event, float(values[turn_key])])
          elif event == right_button:
            plan.append([event, float(values[turn_key])])
          elif event == grab_button:
            plan.append([event])
          elif event == release_button:
            plan.append([event])
          elif event == send_button:
            send(window, plan)
            plan = []
            planning = False
          elif event == rescue_button:
            clicked = sg.popup_ok_cancel('Are you sure you want a rescue?', keep_on_top=True)
            if clicked == 'OK':
              send_rescue(window)

  window.close()


def send(window, plan):
  animate_transmission(window, 10)


def send_rescue(window):
  animate_transmission(window, 10)


def animate_transmission(window, duration):
  progress_bar = window[progress_key]
  length = len(progress_template)
  step_time = float(duration) / (length * 2)

  #Outbound
  for i in range(0, length):
    bar = progress_template[:i] + '*' + progress_template[i+1:]
    progress_bar.update(value=bar)
    window.refresh()
    time.sleep(step_time)

  #Inbound
  for i in range(length-1, -1, -1):
    bar = progress_template[:i] + '*' + progress_template[i+1:]
    progress_bar.update(value=bar)
    window.refresh()
    time.sleep(step_time)

  progress_bar.update(value=progress_template)
  