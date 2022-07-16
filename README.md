# Instagramer

This is a bot that downloads everyday the top memes from the Subreddit [r/memes](https://www.reddit.com/r/memes) and reposts them on Instagram.
So far the bot can only post videos.

You can find the example account here: [@the_real_lord_of_the_memes](https://www.instagram.com/the_real_lord_of_the_memes/?igshid=YmMyMTA2M2Y%3D)

## How to setup

### Reddit requirements

In order to download memes from Reddit you need to create an account. After this you need to create an Reddit-app on this page: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).

On the bottom of the page click on "create another app...":
![image](https://user-images.githubusercontent.com/80044581/179350207-67df4943-9567-4bde-b56b-ac149aa5b03e.png)

Now create the app with the suiting parameters. Select `script`:
![image](https://user-images.githubusercontent.com/80044581/179350513-9c782455-3606-4f9e-a040-9a32c97efba5.png)

After that you should see something like this:
![image](https://user-images.githubusercontent.com/80044581/179350629-39ddaed6-680d-4552-b328-0d2c89d93129.png)

Later on we need these parameters:
- 1: `CLIENT_ID`
- 2: `SECRET_TOKEN`


**Congratulations :tada:! The first steps are done!**

### Local requirements

This bot makes use of a PostgreSQL database in order to avoid downloading the same meme again. It logs every downloaded meme and checks if it was already downloaded.
For that you need to have a local PostgreSQL installation, a database and a table called `Log`. This is a SQL statement you can use to generate the table:
```sql
CREATE TABLE public."Log" (
	"uuid" TEXT PRIMARY KEY,
	"url" TEXT NOT NULL,
	"title" TEXT,
	"startedAt" TIMESTAMP NOT NULL,
	"finishedAt" TIMESTAMP,
	"downloadStatus" TEXT NOT NULL
);
```

If this is done you have to grab the file `.env.sample` rename it to `.env` and insert your parameters. For `REDDIT_CLIENT_ID` and `REDDIT_SECRET_TOKEN` you have to insert the two values from your Reddit app as mentioned above.

Also you have to install the libaries from the `Pipfile` or `requirements.txt` file.

Are all steps completed you can now test if it works by running `python main.py` in the `src` folder.

The memes are going to be cached in the `resource` folder, so do not delete this folder! After two days every unnecessary folder in it will be deleted to keep a better overview and structure.

### Configuring

If you want to change the schedule times you can simply do that be adjusting these parameters in `main.py` on the bottom of the file:
```python
schedule.every().day.at("22:00").do(download_memes)

schedule.every().day.at("23:00").do(remove_dir)

schedule.every().day.at("06:00").do(upload_meme)
schedule.every().day.at("09:00").do(upload_meme)
schedule.every().day.at("12:00").do(upload_meme)
schedule.every().day.at("15:00").do(upload_meme)
schedule.every().day.at("18:00").do(upload_meme)
schedule.every().day.at("21:00").do(upload_meme)
```
[Here](https://schedule.readthedocs.io/en/stable/) is the documentation to the `schedule` libary.

If want to change the number of posts on Instagram you have to change following:
- Change the number of `MEMES_TO_DOWNLOAD` in the file `reddit.py` on the top of the file.
- Adapt the schedule times accordingly of `main.py` as above mentioned. (Adapt, add or remove schedule times)
