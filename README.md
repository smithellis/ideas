export FLASK_APP = ideas.py 

flask run 

or 

flask run --host=0.0.0.0   -- do this if you want the thing to listen on public IP

You can now run "dev_startup.py" to start a dev server with debug on - and it handles all the exporting of paths and stuff.
