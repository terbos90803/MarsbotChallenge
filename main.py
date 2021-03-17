import tkinter as tk
import requests


def send():
  print("Command sent")
  try:
      response = requests.get('http://api.open-notify.org/astros.json', timeout=5)
      response.raise_for_status()
      # Code here will only run if the request is successful
      print(response)
      print(response.json())
  except requests.exceptions.HTTPError as errh:
      print(errh)
  except requests.exceptions.ConnectionError as errc:
      print(errc)
  except requests.exceptions.Timeout as errt:
      print(errt)
  except requests.exceptions.RequestException as err:
      print(err)


w = tk.Tk()
l = tk.Label(text="Mars Bot Challenge")
l.pack()
b = tk.Button(text="Send to Mars", command=send)
b.pack()
w.mainloop()
