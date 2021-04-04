import PySimpleGUI as sg
import remote
import time


forward_button = u'\u2191' # up-arrow glyph
reverse_button = u'\u2193' # down-arrow glyph
left_button = u'\u2190' # left-arrow glyph
right_button = u'\u2192' # right-arrow glyph
grab_button = 'Grab'
release_button = 'Release'
delete_button = u'\u232B' # Delete-left glyph
send_button = 'Send Plan to Robot on Mars'
rescue_button = 'Rescue'

sol_key = '-SOL-MESSAGE-'
move_key = '-MOVE-'
turn_key = '-TURN-'
plan_key = '-PLAN-'
progress_key = '-PROGRESS-'

progress_template = '----------------------------------------'

def plan_missions(robot_number):

  window = sg.Window(
    f'Mars Adventure - Mission Planner - Robot {robot_number}', 
    build_layout(), 
    disable_close=True,
    font=('Sans', 14), 
    finalize=True)

  # Outer planning loop, once per submitted plan
  while True:
    window[move_key].update(value='1')
    window[turn_key].update(value='1')

    plan = []

    # Get the current Sol time
    # A status other than ok means the game ended
    sol_dict = remote.get_sol()
    if sol_dict['status'] != 'ok':
      break

    sol_base = float(sol_dict['sol'])
    sol_total = float(sol_dict['total_sols'])
    mins_per_sol = float(sol_dict['mins_per_sol']) # minutes per sol
    sol_rt_base = time.time() # connect sol_now to the realtime clock

    # Inner planning loop, once per window event
    planning = True
    while planning:
      # Update the Sol timer
      mins_planning = (time.time() - sol_rt_base) / 60.0
      sol_now = sol_base + mins_planning / mins_per_sol
      if sol_now > sol_total + 1:
        planning = False # game probably over, check with server
      window['-SOL-MESSAGE-'].update(f'Sol {sol_now:.1f} of {sol_total:.0f}')

      # Display the current plan
      plan_text = ''
      for step in plan:
        if len(step) == 1:
          plan_text += f'{step[0]}, '
        else:
          plan_text += f'{step[0]} {step[1]}, '
      window[plan_key].update(plan_text)
      window[plan_key].set_size((len(plan_text),None))

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

          move_val = 0
          turn_val = 0
          try:
            move_val = float(values[move_key])
            turn_val = float(values[turn_key])
          except:
            window[move_key].update(value='1')
            window[turn_key].update(value='1')
            move_val = 1.0
            turn_val = 1.0

          if event == delete_button:
            plan.pop()
          elif event == forward_button:
            plan.append((event, move_val))
          elif event == reverse_button:
            plan.append((event, move_val))
          elif event == left_button:
            plan.append((event, turn_val))
          elif event == right_button:
            plan.append((event, turn_val))
          elif event == grab_button:
            plan.append((event,))
          elif event == release_button:
            plan.append((event,))
          elif event == send_button:
            window.hide()
            send(robot_number, plan)
            window.un_hide()
            planning = False
          elif event == rescue_button:
            clicked = sg.popup_ok_cancel('Are you sure you want a rescue?', 
              keep_on_top=True,
              font=('Sans', 20))
            if clicked == 'OK':
              window.hide()
              send_rescue(robot_number)
              window.un_hide()
              planning = False

  window.close()


def build_layout():
  sol_row = [
    sg.Column( [[sg.Text(size=(20,1), key=sol_key, font=('Sans', 24), justification='center')]], justification='c')
  ]
  move_row = [
    sg.Text('Move:', size=(6,1)), 
    sg.Input(size=(3,1), key=move_key, tooltip='How far to move. Decimals are ok.'), 
    sg.Button(forward_button, size=(5,1), tooltip='Straight Forward'), 
    sg.Button(reverse_button, size=(5,1), tooltip='Straight Reverse')
  ]
  turn_row = [
    sg.Text('Turn:', size=(6,1)), 
    sg.Input(size=(3,1), key=turn_key, tooltip='How far to turn. Decimals are ok.'), 
    sg.Button(left_button, size=(5,1), tooltip='Turn Left'), 
    sg.Button(right_button, size=(5,1), tooltip='Turn Right')
  ]
  grab_row = [
    sg.Text('Grab:', size=(6,1)), 
    sg.Button(grab_button, size=(10,1)), 
    sg.Button(release_button, size=(10,1))
  ]
  plan_row = [
    sg.Column( [[
      sg.Button(delete_button, disabled=True, font=('Sans',10), tooltip='Delete last move'),
      sg.Text(size=(1,1), key=plan_key, font=('Sans',10))
    ]], justification='left')
  ]
  send_row = [
    sg.Column( [[
      sg.Button(send_button, disabled=True),
      sg.Button(rescue_button)
    ]], justification='left')
  ]
  controls_row = [
    sg.Column( [
      move_row,
      turn_row,
      grab_row
    ], justification='left')
  ]

  layout = [
    sol_row,
    controls_row,
    plan_row,
    send_row
  ]
  return layout


def send(robot_number, plan):
  process_plan_response(remote.send_plan(robot_number, plan))


def send_rescue(robot_number):
  process_plan_response(remote.send_rescue(robot_number))


def process_plan_response(resp):
  status = resp.get('status')
  if status == 'ok':
    animate_transmission(resp.get('delay'))
  else:
    print(f'Problem with plan: {resp}')


def animate_transmission(duration):
  if duration is None:
    print('Plan submission:')
    duration = '10' # safety default

  progress_layout = [[
    sg.Text('Earth'), 
    sg.Text(progress_template, key=progress_key), 
    sg.Text('Mars')
  ]]
  window = sg.Window(
    'Transmitting Plan to Mars', 
    progress_layout, 
    font=('Sans', 30),
    disable_close=True,
    #disable_minimize=True, # doesn't work in repl.it
    keep_on_top=True,
    modal=True,
    finalize=True,
    element_justification='center')

  progress_bar = window[progress_key]
  length = len(progress_template)
  step_time = float(duration) / (length * 2)

  def animate_progress(start, end, inc=1):
    for i in range(start, end, inc):
      bar = progress_template[:i] + '*' + progress_template[i+1:]
      progress_bar.update(value=bar)
      window.refresh()
      time.sleep(step_time)

  #Outbound
  animate_progress(0, length)

  #Inbound
  animate_progress(length-1, -1, -1)

  window.close()
  