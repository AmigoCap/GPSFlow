# GPSFlow

## How to use

1. Download the project

```
git clone https://github.com/AmigoCap/GPSFlow
```

2. Download your Google Takout Location History [here](https://takeout.google.com/settings/takeout)

Deselect everything but 'Location History' and click download. Google may ask for your password and you will download a `.zip`. Unzipp it and find the `.json` file, which contains all the GPS data collected by Google Maps.

3. Rename it to `takout.json` and place it into the `cli` folder of the project

4. Using your terminal, navigate to the `cli` folder and run the command `python main.py takout.json`

5. Your GPS data will be parsed, filtered and analysed. It can take a while (up to 15min). Let it run until everything is done.

6. Once the programm is finished, if everything went well, you should have a file called `output.json` inside the `cli` folder.

7. Use the vizualisation tool to display the output in your navigator.