# flatpak-profiles

a flatpak container data manager

allows you to setup multiple profiles for a single flatpak and switch between them, useful if you have multiple accounts for a single app, but don't wanna log in and out every time

inspired by a jailbreak tweak called [Crane](https://havoc.app/package/crane) whose functionality i really wanted on the desktop

## usage

**Create a new profile**

`$ fpp create com.example.ExampleApp profile1`

*note: if this is the first profile, your current data will be moved into a profile called "default" which you can go back to at any time*

**List all apps and their profiles**

`$ fpp list`

**Switch profiles**

`$ fpp use com.example.ExampleApp profile1`

**Delete a profile**

`$ fpp use com.example.ExampleApp profile1`