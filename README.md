# GPSFlow

## How to run gpsflow with python

1. Download the project

```
git clone https://github.com/AmigoCap/GPSFlow
```

2. Install all modules listed in `requirements.txt`

3. Download your Google Takout Location History [here](https://takeout.google.com/settings/takeout)

- Deselect everything but 'Location History' and click download. 
- Google may ask for your password and you will download a `.zip`. 
- Unzipp it and find the `.json` file, which contains all the GPS data collected by Google Maps.

4. Rename it to `takout.json` and place it into the `pipelien/src/` folder of the project

5. Using your terminal, navigate to the `pipelien/src/` folder and run the following command :

```
python main.py takout.json
```

6. Your GPS data will be parsed, filtered and analysed. It can take a while (up to 15min). Let it run until everything is done.

7. Once the programm is finished, if everything went well, you should have a file called `output.json` inside the `cli` folder.

8. Use the vizualisation tool to display the output in your navigator.

## How to recompile gpsflow from source

1. Install pyinstaller

```
pip install pyinstaller
```

2. cd into the `pipeline/build-<YOUR_OS>/` folder

3. delete `dist/`,  `build/` and `gpsflow.spec`

4. From inside `build-<YOUR_OS>/`, run the following command

```
pyinstaller --onefile --additional-hooks-dir=hooks --name=gpsflow ../src/main.py
```

5. The compiled file is inside `dist/`

6. To execute it

```
cd dist
```

And then

```
gpsflow <path_to_takout.json>
```