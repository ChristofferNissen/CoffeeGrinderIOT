
# Create new virtual environment

python3 -m virtualenv virtualenv/

source virtualenv/bin/activate   


# Create requirements.txt
python -m pip freeze > requirements.txt

# Install requirements.txt
python -m pip install -r requirements.txt


# Deactive
deactivate



# Source
https://towardsdatascience.com/virtual-environments-104c62d48c54