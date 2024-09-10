if [ -e "env" ]; then
    source env/bin/activate;
else
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
fi

python main.py
