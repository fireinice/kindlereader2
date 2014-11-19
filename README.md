# ReadMe
Kindlereader2 is a project aimed to push articles from rss reader or rss source to kindle. It is forked from work [kindlereader](https://github.com/jiedan/kindlereader/). Now the rss reader support work is based on [librssreader](https://github.com/fireinice/librssreader), and now support inoreader. More rss reader support would be added by the librssreader.

## Lisence
Licensed under the MIT license: [http://www.opensource.org/licenses/mit-license.php]()

## Features

* Support to push inoreader articles to kindle

## Usage
### Dependency
* python(2.7 recommanded)
* pip


### Setup
  _By now ALL feature are only tested on Linux environment_.
  Drop [kindlegen](http://www.amazon.com/gp/feature.html?docId=1000765211) in any dir that you can find it by `which kindlegen`

  $ kindlereader.pyt --generate_config # a config.ini would be generated in the dir

  Fill Infos into the config.ini and then

  $ kindlereader.py
  

## Thanks

Originally created by [kindlereader](https://github.com/jiedan/kindlereader/)

