from datetime import datetime
from dateutil import tz
import pytz

format = '%Y-%m-%dT%H:%M:%S.%fZ'

time2 = "2019-05-30T18:20:46.995Z"
d = datetime.strptime(time2, format)
print(d.strftime("%m-%d %I:%M %p"))


from_zone = tz.tzutc()
to_zone = pytz.timezone("America/New_York")

# utc = datetime.utcnow()
utc = datetime.strptime(time2, '%Y-%m-%dT%H:%M:%S.%fZ')

# Tell the datetime object that it's in UTC time zone since 
# datetime objects are 'naive' by default
utc = utc.replace(tzinfo=from_zone)

# Convert time zone
central = utc.astimezone(to_zone)

d = central.strftime("%m-%d %I:%M %p")

print(d)
