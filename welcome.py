import PySimpleGUI as sg
import remote
import time

def get_robot_number():
  # Wait for server connection
  layout = [
    [sg.Text('Waiting to connect...', size=(30,1), justification='center')],
    [sg.Text(' ', size=(30,1), key='-MESSAGE-', justification='center')]
  ]
  window = sg.Window(
    'Connecting to the Mars Adventure', layout, font=('Sans', 14),
    disable_close=True, finalize=True)
  while True:
    try:
      resp = remote.get_robot_assignment()
      if resp['status'] == 'ok':
        robot_number = int(resp['robot_number'])
        break
      #print(resp['reason'])
      msg = resp.get('message')
      window['-MESSAGE-'].update(msg if msg else 'Server not ready')
      window.refresh()
    except:
      pass
    time.sleep(1)
  window.close()

  # Wait for game to start
  layout = [
    [sg.Text(f'You will be driving robot number {robot_number}')],
    [sg.Text('Waiting for the game to start', key='-WAIT-')],
    [sg.Button('Ok', key='-OK-', disabled=True, bind_return_key=True)]
  ]
  window = sg.Window(
    'Waiting to start Mars Adventure', layout, font=('Sans', 14),
    disable_close=True, finalize=True)
  flash = False
  while True:
    try:
      resp = remote.get_sol()
      status = resp.get('status')
      waiting = status != 'ok'

      window['-WAIT-'].update(visible=waiting)

      flash = not flash
      light = flash and not waiting
      color = ('white', 'green') if light else None
      window['-OK-'].update(button_color=color, disabled=waiting)
      
      event, values = window.read(timeout=500)
      if event == '-OK-':
        break
    except:
      time.sleep(1)
  window.close()

  return robot_number