## xyz.userbyte.flatpak-profiles
## a tool to help manage your flatpak container data
## 07/08/2024

version = '0.2.1'

import argparse, sys, os, toml, shutil

wrk_dir = ''
cfg_dir = ''

HOME = os.environ['HOME']
try:
    XDG_DATA_HOME = os.environ['XDG_DATA_HOME']
    wrk_dir = XDG_DATA_HOME+'/flatpak-profiles'
except KeyError:
    print('$XDG_DATA_HOME not set')
    wrk_dir = os.path.dirname(os.path.realpath(__file__))

try:
    cfg_dir = os.environ['XDG_CONFIG_HOME']
except KeyError:
    print('$XDG_CONFIG_HOME not set')
    cfg_dir = os.path.dirname(os.path.realpath(__file__))

fppdata = None
try:
    fppdata = toml.load(f'{wrk_dir}/data.toml')
except FileNotFoundError:
    print('Data files missing! Please refer to CONFIG.MD for info on how to create them.')

def setup_data_dir():
    print('running initial data dir setup...')
    os.mkdir(f'{XDG_DATA_HOME}/flatpak-profiles')
    os.mkdir(f'{XDG_DATA_HOME}/flatpak-profiles/profiles')
    # os.mkdir(f'{XDG_DATA_HOME}/flatpak-profiles/data')

def setup_flatpak(app_id):
    # check db
    try:
        fppdata[app_id]
    except KeyError:
        # not in db, this likely means its not setup yet so we'll go with that
        print('running initial flatpak setup...')
        print('moving current data (if any) to a default profile...')
        try:
            try:
                shutil.move(f'{HOME}/.var/app/{app_id}', f'{wrk_dir}/profiles/{app_id}+default')
            except FileNotFoundError:
                # flatpak doesnt have data yet, whatever just make a folder for it
                os.mkdir(f'{wrk_dir}/profiles/{app_id}+default')
        except FileExistsError:
            print('file exists')
        # set default profile as the active one
        os.symlink(f'{wrk_dir}/profiles/{app_id}+default', f'{HOME}/.var/app/{app_id}')
        fppdata[app_id] = {}
        fppdata[app_id]['profiles'] = ['default']
        fppdata[app_id]['active'] = 'default'
        with open(f'{wrk_dir}/data.toml', 'w') as f:
            s = toml.dump(fppdata, f)
    else:
        # print('ERROR: flatpak already setup? requires manual inspection as to not break shit')
        pass

def create_profile(app_id, profile_name):
    setup_flatpak(app_id)
    try:
        os.mkdir(f'{wrk_dir}/profiles/{app_id}+{profile_name}')
    except FileExistsError:
        print(f'Profile "{profile_name}" already exists!')
        return False
    else:
        fppdata[app_id]['profiles'].append(profile_name)
        with open(f'{wrk_dir}/data.toml', 'w') as f:
            s = toml.dump(fppdata, f)
        return True

def delete_profile(app_id, profile_name):
    setup_flatpak(app_id)
    try:
        os.rmdir(f'{wrk_dir}/profiles/{app_id}+{profile_name}')
    except FileNotFoundError:
        print(f'Profile "{profile_name}" does not exist')
        # we count this as a success because the profile doesnt exist
        return True
    except Exception as e:
        # unknown error
        print(f'ERROR: unknown error "{e}"')
        return False
    else:
        fppdata[app_id]['profiles'].remove(profile_name)
        with open(f'{wrk_dir}/data.toml', 'w') as f:
            s = toml.dump(fppdata, f)
        return True

def set_active_profile(app_id, profile_name):
    if os.path.exists(f'{wrk_dir}/profiles/{app_id}+{profile_name}'):
        # remove existing symlink
        os.remove(f'{HOME}/.var/app/{app_id}')

        # set a new one
        os.symlink(f'{wrk_dir}/profiles/{app_id}+{profile_name}', f'{HOME}/.var/app/{app_id}')

        return True
    else:
        print(f'Profile "{profile_name}" does not exist!')
        return False


# TODO: might want in the future
# try:
#     if cfg['enable_linux_notifs']:
#         import gi
#         gi.require_version('Notify', '0.7')
#         from gi.repository import Notify
# except KeyError:
#     pass

# def send_desktop_notif(icon, content):
#     if cfg['enable_linux_notifs']:
#         Notify.init("flatpak-profiles")
#         Notify.Notification.new(
#             "flatpak-profiles",
#             content,
#             icon
#         ).show()

# -- ugly but required argparse stuff --

class ap(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f'error: {message}\n')
        self.print_help()
        sys.exit(2)

def argument(*name_or_flags, **kwargs):
    return (list(name_or_flags), kwargs)

parser = ap()
subparsers = parser.add_subparsers(dest="subcommand")
def subcommand(name, args=[], parent=subparsers):
    def decorator(func):
        parser = parent.add_parser(name, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator

# -- ugly but required argparse stuff --

# -- commands --

@subcommand("list", [argument("app_id", help="(OPTIONAL) Flatpak app identifier (ex. com.example.ExampleApp)", nargs='?')])
def c_list(args):
    """Lists all profiles"""
    appsummary = ''
    if args.app_id == None:
        for app_id in fppdata:
            appsummary = appsummary+f'{app_id}'
            for profile in fppdata[app_id]['profiles']:
                appsummary = appsummary+f'\n - {profile}'
            appsummary = appsummary+'\n'
    else:
        app_id = args.app_id
        appsummary = appsummary+f'{app_id}'
        for profile in fppdata[app_id]['profiles']:
            appsummary = appsummary+f'\n - {profile}'
    print(appsummary)

@subcommand("create", [argument("app_id", help="Flatpak app identifier (ex. com.example.ExampleApp)"), argument("profile_name", help="Name of profile to create")])
def c_create(args):
    """Create a new profile"""
    create_profile(args.app_id, args.profile_name)

@subcommand("delete", [argument("app_id", help="Flatpak app identifier (ex. com.example.ExampleApp)"), argument("profile_name", help="Name of profile to delete")])
def c_delete(args):
    """Delete a profile"""
    yn = input('⚠  WARNING: This action is irreversible! Are you absolutely sure you want to delete this profile? [y/N]: ')
    if yn.lower() == 'y':
        x = delete_profile(args.app_id, args.profile_name)
        if x:
            print(f'🗑️  Deleted profile "{args.profile_name}" from {args.app_id}')
    else:
        return

@subcommand("use", [argument("app_id", help="Flatpak app identifier (ex. com.example.ExampleApp)"), argument("profile_name", help="Name of profile to set as the active one")])
def c_use(args):
    """Sets the active profile"""
    x = set_active_profile(args.app_id, args.profile_name)
    if x:
        print(f'✔  Set profile of {args.app_id} to "{args.profile_name}"')
    else:
        yn = input(f'Would you like to create and switch to it? [y/N]: ')
        if yn.lower() == 'y':
            print('Creating...')
            create_profile(args.app_id, args.profile_name)
            print('Switching...')
            set_active_profile(args.app_id, args.profile_name)
            print(f'✔  Set profile of {args.app_id} to "{args.profile_name}"')
        else:
            return

@subcommand("test")
def c_test(args):
    """DEBUG: test command"""
    print('Test!')

# -- commands --

if __name__ == "__main__":

    if not os.path.exists(f'{XDG_DATA_HOME}/flatpak-profiles'):
        setup_data_dir()

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)