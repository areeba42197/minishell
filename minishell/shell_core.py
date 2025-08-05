import os
import shlex
import subprocess
import threading
import requests    
import time
import psutil 

class ShellCore:
    def __init__(self):
        self.history = []
        self.index = -1
        self.path = os.getcwd()

    def display_prompt(self):
        return "IIUI-Shell> "

    def process(self, cmd, cb=None):
        if not cmd.strip():
            return ""

        bg = cmd.strip().endswith("&")
        if bg:
            cmd = cmd.strip()[:-1].strip()

        self.history.append(cmd)
        self.index = len(self.history)

        if cmd == "exit":
            quit()
        elif cmd == "clear":
            return "\n" * 80
        elif cmd == "help":
            return "Commands: clear, exit, help, about, cd, mkdir, rmdir, touch, ls, echo, history, head, grep, pwd, date, whoami, cat, rm ,timeit ,mood , weather"
        elif cmd == "about":
            return "IIUI-Shell - Enhanced Custom Shell"
        elif cmd.startswith("cd"):
            return self._change_dir(cmd)
        elif cmd.startswith("mkdir"):
            return self._mkdir(cmd)
        elif cmd.startswith("rmdir"):
            return self._rmdir(cmd)
        elif cmd.startswith("touch"):
            return self._touch(cmd)
        elif cmd.strip() == "ls":
            return self._ls()
        elif cmd.strip() == "pwd":
            return self.path
        elif cmd.startswith("timeit"):
            return self._timeit(cmd)

        elif cmd.startswith("echo"):
            if ">>" in cmd or ">" in cmd:
                return self._echo_redirect(cmd)
            else:
                return self._echo(cmd)
        elif cmd == "history":
            return self._history()
        

        elif cmd.startswith("head"):
            return self._head(cmd)
        elif cmd.startswith("grep"):
            return self._grep(cmd)
        elif cmd.strip() == "date":
            return self._run_simple("date")
        elif cmd.strip() == "whoami":
            return self._run_simple("whoami")
        elif cmd.startswith("cat"):
            return self._cat(cmd)
        elif cmd.startswith("rm"):
            return self._rm(cmd)
        elif cmd.startswith("weather"):
           return self._weather(cmd)
        elif cmd.strip() == "mood":
           return self._mood()
       


        


        def execute():
            try:
                is_windows = os.name == 'nt'
                use_shell = is_windows or any(op in cmd for op in ['|', '>', '<'])

                if use_shell:
                    proc = subprocess.Popen(cmd, cwd=self.path, shell=True, text=True,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    args = shlex.split(cmd)
                    
                    # If .exe file is specified directly
                    if args[0].endswith(".exe") or os.path.exists(os.path.join(self.path, args[0])):
                        full_path = os.path.join(self.path, args[0])
                        if os.path.isfile(full_path) and full_path.endswith(".exe"):
                            proc = subprocess.Popen([full_path] + args[1:], cwd=self.path, shell=False, text=True,
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        else:
                            proc = subprocess.Popen(args, cwd=self.path, shell=False, text=True,
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        proc = subprocess.Popen(args, cwd=self.path, shell=False, text=True,
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                out, err = proc.communicate()

                if cb:
                    cb((out or "") + (err or ""))
            except FileNotFoundError:
                if cb:
                    cb(f"{cmd.split()[0]}: not found")
            except Exception as e:
                if cb:
                    cb(str(e))


        if bg:
            threading.Thread(target=execute).start()
            return f"[Running in background] {cmd}"
        else:
            holder = []
            def capture(o):
                holder.append(o)
            execute()
            return holder[0] if holder else ""

    def _change_dir(self, cmd):
        try:
            args = shlex.split(cmd)
            target = args[1] if len(args) > 1 else os.path.expanduser("~")
            new_path = os.path.abspath(os.path.join(self.path, target))
            os.chdir(new_path)
            self.path = new_path
            return f"Moved to: {self.path}"
        except Exception as err:
            return f"cd failed: {err}"

    def _mkdir(self, cmd):
        try:
            args = shlex.split(cmd)
            os.mkdir(os.path.join(self.path, args[1]))
            return f"Directory '{args[1]}' created"
        except Exception as err:
            return f"mkdir failed: {err}"

    def _rmdir(self, cmd):
        try:
            args = shlex.split(cmd)
            os.rmdir(os.path.join(self.path, args[1]))
            return f"Directory '{args[1]}' removed"
        except Exception as err:
            return f"rmdir failed: {err}"

    def _touch(self, cmd):
        try:
            args = shlex.split(cmd)
            path = os.path.join(self.path, args[1])
            with open(path, 'a'):
                os.utime(path, None)
            return f"File '{args[1]}' created"
        except Exception as err:
            return f"touch failed: {err}"

    def _ls(self):
        try:
            return "\n".join(os.listdir(self.path))
        except Exception as err:
            return f"ls failed: {err}"

    def _echo(self, cmd):
        try:
            args = shlex.split(cmd)
            return " ".join(args[1:])
        except Exception as err:
            return f"echo failed: {err}"

    def _echo_redirect(self, cmd):
        try:
            append = ">>" in cmd
            parts = cmd.split(">>" if append else ">")
            if len(parts) != 2:
                return "Syntax error: expected format `echo message > filename`"

            message = parts[0].strip()[5:].strip()
            filename = parts[1].strip()
            file_path = os.path.join(self.path, filename)

            with open(file_path, 'a' if append else 'w') as f:
                f.write(message + "\n")

            return f"Written to '{filename}'"
        except Exception as err:
            return f"echo redirection failed: {err}"

    def _history(self):
        try:
            return "\n".join(f"{i+1}: {cmd}" for i, cmd in enumerate(self.history))
        except Exception as err:
            return f"history failed: {err}"

    def _head(self, cmd):
        try:
            args = shlex.split(cmd)
            file_path = os.path.join(self.path, args[1])
            with open(file_path, 'r') as f:
                return "".join([next(f) for _ in range(10)])
        except Exception as err:
            return f"head failed: {err}"

    def _grep(self, cmd):
        try:
            args = shlex.split(cmd)
            pattern, filename = args[1], args[2]
            file_path = os.path.join(self.path, filename)
            with open(file_path, 'r') as f:
                return "\n".join([line.strip() for line in f if pattern in line])
        except Exception as err:
            return f"grep failed: {err}"

    def _run_simple(self, cmd):
        try:
            result = subprocess.run(cmd, cwd=self.path, text=True, shell=True, capture_output=True)
            return result.stdout.strip() or result.stderr.strip()
        except Exception as err:
            return f"{cmd} failed: {err}"

    def _cat(self, cmd):
        try:
            args = shlex.split(cmd)
            file_path = os.path.join(self.path, args[1])
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as err:
            return f"cat failed: {err}"

    def _rm(self, cmd):
        try:
            args = shlex.split(cmd)
            file_path = os.path.join(self.path, args[1])
            os.remove(file_path)
            return f"File '{args[1]}' removed"
        except Exception as err:
            return f"rm failed: {err}"
        
  
    def _timeit(self, cmd):
        try:
           command = cmd[len("timeit"):].strip()
           if not command:
            return "Usage: timeit [command]"
           start = time.time()
           output = self.process(command)
           end = time.time()
           duration = end - start
           return f"{output}\n\n[Execution Time: {duration:.4f} seconds]"
        except Exception as e:
           return f"timeit error: {e}"
        
    def _weather(self, cmd):
      city = cmd[len("weather"):].strip()
      if not city:
        return "Usage: weather <city>"

      api_key = ""
  
      url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

      try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("cod") != 200:
            return f"Error: {data.get('message', 'City not found')}"

        weather_desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return (f"Weather for {city.title()}:\n"
                f"  Condition: {weather_desc}\n"
                f"  Temperature: {temp}°C\n"
                f"  Humidity: {humidity}%\n"
                f"  Wind speed: {wind_speed} m/s")

      except requests.RequestException as e:
        return f"Failed to get weather data: {e}"
      
    def _mood(self):
     try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage(self.path).percent

        if cpu < 30 and ram < 50:
            mood = "🟢 System is Happy"
        elif cpu < 60 and ram < 75:
            mood = "🟡 System is Fine"
        else:
            mood = "🔴 System is Struggling"

        return (
            f"{mood}\n"
            f"CPU Usage: {cpu:.1f}%\n"
            f"RAM Usage: {ram:.1f}%\n"
            f"Disk Usage: {disk:.1f}%"
        )
     except Exception as e:
        return f"mood check failed: {e}"
     
  
