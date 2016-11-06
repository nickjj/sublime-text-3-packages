## Sublime Text 3 Packages

This repository contains all of my Sublime Text 3 packages and settings. There
are over 30 different packages catered towards web development with Rails, Flask,
Elixir and Docker.

A number of screenshots and a full write up can be found at:  
https://nickjanetakis.com/blog/25-sublime-text-3-packages-for-polyglot-programmers

## Installation instructions

Keep in mind if you follow these instructions exactly your personal Sublime Text 3
settings and / or packages will be overwritten. You've been warned!

The steps are the same for all operating systems but the location of your Sublime
Text 3 config folder will be OS specific.

**First make sure Sublime Text 3 is closed.**

Then, clone this repository to your ST3 config folder:

- **Linux** distributions will have it located in `~/.config/sublime-text-3`.
- **OSX** users can find it in `~/Library/Application Support/Sublime Text 3`.
- **Windows** users will be able to find it in `%APPDATA%\Sublime Text 3`.

For example, on Linux you would run:  
`git clone https://github.com/nickjj/sublime-text-3-packages.git ~/.config/sublime-text-3`

### Posting Gists with your GitHub account

There is one piece of sensitive information that I omit from this repository
because it includes a private GitHub token tied into my account.

This is for the Gist package that allows you to publish and manage gists directly
from Sublime. To configure that, read the
[Gist package's documentation](https://github.com/condemil/Gist#generating-access-token)
for generating your own personal access token.

### Various linters won't work out of the box

I have a number of packages that perform real time linting on various files.
They require that you have Python, Ruby, Elixir and so on installed on your machine.

[This blog post](https://nickjanetakis.com/blog/25-sublime-text-3-packages-for-polyglot-programmers)
links to each package's README which shows instructions on how to do that for
each linker you want.

If you omit this step, things should still run fine except you won't get the
linter support.
