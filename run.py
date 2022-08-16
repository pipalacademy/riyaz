import sys
from riyaz.app import app
from riyaz.migrate import migrate
from riyaz.sample_data import load_sample_data

def main():
    migrate()

    if "--load-sample-data" in sys.argv:
        load_sample_data("sample_data")
    else:
        app.run()

if __name__ == "__main__":
    main()