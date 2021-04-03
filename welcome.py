import PySimpleGUI as sg
import remote
import time

def get_robot_number():
  # Wait for server connection
  layout = [[sg.Text('Waiting to connect...', size=(30,1), justification='center')]]
  window = sg.Window(
    'Connecting to the Mars Adventure', layout, font=('Sans', 14),
    disable_close=True, finalize=True)
  while True:
    try:
      resp = remote.get_robot_assignment()
      robot_number = int(resp['robot_number'])
      break
    except:
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
  while True:
    try:
      resp = remote.get_sol()
      status = resp['status']
      waiting = status != 'ok'
      window['-WAIT-'].update(visible=waiting)
      window['-OK-'].update(disabled=waiting)
      event, values = window.read(timeout=1000)
      if event == '-OK-':
        break
    except:
      time.sleep(1)
  window.close()

  return robot_number