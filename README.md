# scripts

Assorted Python scripts from my scripts folder.  Many of these may be cross platform in nature.
Does not include linux shell scripts, which I've added to a separate 'bin' repo.

# Note on environment
Pip now requires that the packages are installed in a separate environment.
This jas its own python installed.  
See:
https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
https://www.reddit.com/r/learnpython/comments/1e9xdvr/installing_an_externally_managed_package/

I have
- created an environment
	python3 -m venv .venv
- activate using 
	source .venv/bin/activate
- which python now shows .venv/bin/python
- python3 -m pip install yFinance
- deactivate command to exit virtual environment

Reddit article states that need to update shebang in script to 
!#/home/iain/.venv/bin/python



