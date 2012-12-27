from contextlib import closing

from sh import launchctl

LAUNCHD_RUN_ONCE_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{label}</string>
  <key>ProgramArguments</key>
  <array>
    {args}
  </array>
  <key>UserName</key>
  <string>root</string>
  <key>UserGroup</key>
  <string>wheel</string>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
"""


def generate_launchd_label(name):
    return "com.hubspot.moxie.{0}".format(name)


def generate_launchd_filename(name):
    return "/Library/LaunchDaemons/{0}.plist".format(generate_launchd_label(name))


def add_run_once(name, args):
    filename = generate_launchd_filename(name)
    contents = LAUNCHD_RUN_ONCE_TEMPLATE.format(
      label=generate_launchd_label(name),
      args='\n    '.join(['<string>%s</string>' % arg for arg in args])
    )

    with closing(open(filename, 'w')) as fp:
        fp.write(contents)

    launchctl.load(filename)


def remove_run_once(name):
    filename = generate_launchd_filename(name)

    launchctl.unload(filename)
