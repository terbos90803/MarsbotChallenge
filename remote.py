import requests
import json


server_address = None # offline test mode
server_address = 'http://47.147.215.195:5000/'

def _get(endpoint, attrs=dict()):
  uri = f'{server_address}{endpoint}'
  try:
    response = requests.get(uri, params=attrs, timeout=5)
    response.raise_for_status()
    # Code here will only run if the request is successful
    #print(response)
    return response.json()
  except requests.exceptions.HTTPError as err:
    return {'status': 'fail', 'reason': err}
  except requests.exceptions.ConnectionError as err:
    return {'status': 'fail', 'reason': err}
  except requests.exceptions.Timeout as err:
    return {'status': 'fail', 'reason': err}
  except requests.exceptions.RequestException as err:
    return {'status': 'fail', 'reason': err}

def _post(endpoint, body=dict(), attrs=dict()):
  uri = f'{server_address}{endpoint}'
  try:
    response = requests.post(uri, params=attrs, data=body, timeout=5)
    response.raise_for_status()
    # Code here will only run if the request is successful
    #print(response)
    return response.json()
  except requests.exceptions.HTTPError as err:
    return {'status': 'fail', 'reason': err}
  except requests.exceptions.ConnectionError as err:
    return {'status': 'fail', 'reason': err}
  except requests.exceptions.Timeout as err:
    return {'status': 'fail', 'reason': err}
  except requests.exceptions.RequestException as err:
    return {'status': 'fail', 'reason': err}


def get_robot_assignment():
  if server_address:
    return _get('robot_assignment')
  return {'status': 'ok', 'robot_number': '1'}


def get_sol():
  if server_address:
    return _get('sol')
  return {'status': 'ok', 'sol': '1.0', 'total_sols': '10.0', 'mins_per_sol': '3.0'}


def send_plan(robot, plan):
  if server_address:
    body = {
      'robot': robot,
      'plan': json.dumps(plan)
    }
    return _post('plan', body)
  return {'status': 'ok', 'delay': 10}


def send_rescue(robot):
  if server_address:
    body = {
      'robot': robot
    }
    return _post('plan', body)
  return {'status': 'ok', 'delay': 10}
