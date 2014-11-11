# ReadMe
Kindlereader2 is a project aimed to push articles from rss reader or rss source to kindle. It is forked from work [kindlereader](https://github.com/jiedan/kindlereader/). Now the rss reader support work is based on [librssreader](https://github.com/fireinice/librssreader), and now support inoreader. More rss reader support would be added by the librssreader.

## Lisence
Licensed under the MIT license: [http://www.opensource.org/licenses/mit-license.php]()

* [kindlestrip](https://encrypted.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0CBwQFjAA&url=%68%74%74%70%3a%2f%2f%77%77%77%2e%6d%6f%62%69%6c%65%72%65%61%64%2e%63%6f%6d%2f%66%6f%72%75%6d%73%2f%73%68%6f%77%74%68%72%65%61%64%2e%70%68%70%3f%74%3d%39%36%39%30%33&ei=jM1QVMqZH8fkaLKtgvAO&usg=AFQjCNEpUD8-D-CdIAFapmdiYXjpQ0jAvw&sig2=aVM0AeUQQT0VHMpTxx_Jlw&bvm=bv.78597519,d.d2s&cad=rja) is a great work from Paul Durrant*

## Features

* Support to push inoreader articles to kindle
* Support Pocket Service Integration(need some more code to to serve as server)

## Usage

### Dependency
* python(2.7 recommanded)
* pip
* librssreader
* python-gflags
* tornado
* BeautifulSoup
* python-gflags
* kindlegen
* Pillow (Optional)

### Setup
_By now ALL feature are only tested on Linux environment_.

        $ pip install tornado

        $ pip install Pillow

	$ pip install BeautifulSoup

	$ pip install python-gflags

	$ git clone librssreader

	$ cd librssreader; python setup.py sdist

	$ pip install dist/librssreader-0.0.8.tar.gz
	
  Drop [kindlegen](http://www.amazon.com/gp/feature.html?docId=1000765211) in any dir that you can find it by `which kindlegen`
	


## Thanks

Originally created by [kindlereader](https://github.com/jiedan/kindlereader/)

[kindlestrip](https://encrypted.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0CBwQFjAA&url=%68%74%74%70%3a%2f%2f%77%77%77%2e%6d%6f%62%69%6c%65%72%65%61%64%2e%63%6f%6d%2f%66%6f%72%75%6d%73%2f%73%68%6f%77%74%68%72%65%61%64%2e%70%68%70%3f%74%3d%39%36%39%30%33&ei=jM1QVMqZH8fkaLKtgvAO&usg=AFQjCNEpUD8-D-CdIAFapmdiYXjpQ0jAvw&sig2=aVM0AeUQQT0VHMpTxx_Jlw&bvm=bv.78597519,d.d2s&cad=rja) is a great work from Paul Durrant*
