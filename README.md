# Polygon to TIOJ #

## How to use ##

1. `git clone https://github.com/oToToT/Polygon2TIOJ`
2. `cd Polygon2TIOJ`
3. `pip install -r requirements.txt`
4. `./main.py filename [filename] --url=URL`


* `filename` is the path to zip downloaded from polygon, notice that you should download Full Package of Linux.
* `URL` is the url to TIOJ.
* if `--update` is being set, you could update problem with its problem id by `./main.py filename ID --url=URL`.
* if `--remove_tests` is being set, you could remove tests with its problem id by `./main.py ID [ID] --url=URL`.

## How to import contest to TIOJ ##

1. `git clone https://github.com/oToToT/Polygon2TIOJ`
2. `cd Polygon2TIOJ`
3. `./download.sh [username] [cid]`
4. Input your password
5. `./main.py *.zip --url=URL`
6. `rm *.zip`

## Special Thanks ##

Thanks @WillyPillow for an easy tool to download contest packages from Polygon

## TODO ##

- [ ] check is user admin
