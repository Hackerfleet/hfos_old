c-weatherscraper
================

This piece of script scrapes a german website to read the current weather at the base of the main antenna of c-base.
Also it scrapes the Website from TU and downloads the most current rainradar-image.

Also it provides a picture of the current solar status, to predict solar pertuberances and other space-weather relevant data.

The script generates weather.html, which can be opened in any Browser. Every re-run of the script overwrites the old weather.html with fresh new Data.

I advise that this script is used in conjunction with a cronjob, that runs it every 5-15min. If the script is run everytime the user visits the page, it might trigger flood-warnings on the website that we scrape.
