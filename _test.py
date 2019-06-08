import re

test_msg = 'BlaBla shared by soundcloud https://soundcloud.com/spazewindu/suser-geschmack-w-luk-the-dude appendix'

url_schema = '(?P<url>https?://[^\s]+)'

match = re.search(url_schema, test_msg)

if match:
    print(match.group('url'))
else:
    print('no url found')