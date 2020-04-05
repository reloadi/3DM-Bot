from check import Check

import configparser
config = configparser.ConfigParser()
config.read('config.cfg')


MY_SERVER_NAME  = "3DMeltdown 3D Printing"
INTERVAL_MSG    = 8
DISCORD_HOOK    = config['disboard']['hook']

check = Check(MY_SERVER_NAME, DISCORD_HOOK)
check.check()

# if first place is us
if check.is_us() or check.is_ok_second():
    print("we are first or second")
#if check.is_us():
    # it's the first time
    if check.count() == 1 and check.is_us():
        check.notify('**3DMeltdown is back to #1**')
# it's not us
else:
    print("we are not first or second ({0})".format(check.count()))

    # send notification every INTERVAL_MSG check
    if check.count() % INTERVAL_MSG == 1:
        msg = '**3DMeltdown is currently NOT in first position on dishboard**\n'
        for i in range(5):
            msg += "{0} - {1} ({2})\n".format(i+1, check.index_list[i], check.index_time[i])
        msg += '\nPlease bump the server using: `!d bump` (last bump: {0})\n'.format(check.my_last_bump)
        check.notify(msg)
