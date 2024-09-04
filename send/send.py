#!/usr/bin/env python3

# Copyright 2024 Mihail Demyanovich.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

# send - simple terminal frontend for scp.

from argparse import ArgumentParser
from os import remove, system
from os.path import exists, expanduser

try:
    try_file_path = expanduser('~/try')
    try_file = open(try_file_path, 'a')
    try_file.close()
    remove(try_file_path)

except:
    print('send: Permission error.')
    exit()

send_conf_path = expanduser('~/.send.conf')

if exists(send_conf_path):
    # Start the parser.
    parser = ArgumentParser(description='send - simple terminal frontend for scp.')
    parser.add_argument('server_nickname', type=str, help='Server nickname.')
    parser.add_argument('source_plus_destination', type=str, nargs='+', help="Source file(s), divided by ' ' plus destination directory, starting with ':'.")
    args = parser.parse_args()

    # Get source_split, destination from the source_plus_destination argument.
    try:
        source_plus_destination = args.source_plus_destination
        last_element_split = source_plus_destination[-1].split(':')
        last_source = last_element_split[0]
        destination = last_element_split[1]
        source_split = source_plus_destination[:-1]
        if last_source != '':
            source_split.append(last_source)

    except (IndexError, ValueError):
        print("send: Wrong syntax of the source_plus_destination argument.")
        exit()

    # Read .send.conf to send_conf_split.
    with open(send_conf_path, 'r') as send_conf:
        send_conf_split = tuple([line.rstrip('\n').split(' ') for line in send_conf if not line.startswith(('#', '\n'))])

    # Get user, ip_or_domain, port from the line of .send.conf
    # that refers to server_nickname; build the command.
    server_nickname = args.server_nickname
    done = False
    for line in send_conf_split:
        if line[0] == server_nickname:
            try:
                user = line[1]
                ip_or_domain = line[2]
                port = line[3]
                command = f"""scp -P {port} {' '.join(["'" + item + "'" for item in source_split])} {user}@{ip_or_domain}:'{destination}'"""
                done = True
                break

            except IndexError:
                break

    # Execute the command.
    if done:
        system(command)
    else:
        print('send: Wrong configuration.')

else:
    # Create .send.conf optionally if it doesnt exist.
    decision = input("send: .send.conf doesn't exist. Do you want to create it? y/n ")
    while decision not in ('y', 'n'):
        decision = input('send: Wrong input. Do you want to create .send.conf? y/n ')
    if decision == 'y':
        with open(send_conf_path, 'w') as send_conf:
            send_conf.write('''#send - simple terminal frontend for scp.
#Add information about servers:
#Syntax:
#server_nickname user ip_or_domain port
#The default port is 22.
#For the next server add new line.
''')
        print('send: Created .send.conf in home directory. It contains an instruction to configure it manually!')
