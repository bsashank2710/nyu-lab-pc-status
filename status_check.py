import subprocess
from app import db, pc_names
from app.models import Status
import time

def status_check():
    for name in pc_names.keys():
        ping = subprocess.Popen(
            'ping -n 1 {}'.format(name),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=True)

        (ping_output, ping_err) = ping.communicate()

        status = subprocess.Popen(
            'query user /server:{}'.format(name),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=True)

        if ping.returncode == 1:
            #msg = 'NO COMM'
            stat = Status(
                domain_name = name,
                ip_address = pc_names[name],
                state = "System Down")
        else:
            (output, err) = status.communicate()
            msg = output.decode('utf-8')
            #print(name, msg)

            if len(msg) > 0:
                msg = msg.split('\n')[1].split()
                if len(msg[1]) < 2:
                    msg.insert(1, None)

                stat = Status(
                    domain_name = name,
                    ip_address = pc_names[name],
                    username = msg[0],
                    session_name = msg[1],
                    session_id = msg[2],
                    state = msg[3],
                    idle_time = msg[4],
                    logon_time = msg[5] + ' ' + msg[6] + ' ' + msg[7])
            else:
                #msg = 'NO USER'
                stat = Status(
                    domain_name = name,
                    ip_address = pc_names[name],
                    state = "Available")

        db.session.add(stat)
        db.session.commit()


if __name__ == '__main__':
    i = 1
    while True:
        print('--> Check No. {}'.format(i))
        status_check()
        i += 1
        time.sleep(60)
