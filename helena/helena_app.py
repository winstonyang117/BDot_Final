import main
import componets.influxshake as influxshake
import componets.systemParameters as systemParameters
import reliability.deviceMonitor as deviceMonitor
import sys 

if __name__ == '__main__':
  arg = sys.argv 
  if len(arg) <2:
     print("Need at least one parameter. Exiting...")
     exit()

  if arg[1]=='main':
     main.main()

  if arg[1]=='influxshake':
     influxshake.start()

  if arg[1]=='systemParameters':
     systemParameters.start()

  if arg[1]=='deviceMonitor':
     deviceMonitor.start()

