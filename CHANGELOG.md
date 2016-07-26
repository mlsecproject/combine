CHANGE LOG
==========

#### 0.1.3.9000 Delayed Capybara - WIP
Bugfix release

* Updating `requirements.txt` and issue with authenticated site ([#162](https://github.com/mlsecproject/combine/pull/162)) - thanks to [@Darkan](https://github.com/Darkan)

#### 0.1.3 Captivating Capybara
Bugfix release, and also making it easier to install and use the system with Venv and Docker procedures. Special thanks to [@krmaxwell](https://github.com/krmaxwell) who seems to have done all the work

* Updating the regex used for hostname capture on Thresher. Will be further updated on v0.2 ([#131](https://github.com/mlsecproject/combine/issues/131))
* Sources update:
    * Updating PalevoTracker location and removing Spyeye tracker ([#123](https://github.com/mlsecproject/combine/issues/123))
    * Updating MaxMind local dataset to March 2015
    * Adding Feodo Abuse.ch tracker
    * Ajusted Wiki to current Threat Intelligence feeds ([#71](https://github.com/mlsecproject/combine/issues/71))
* Docker file and usage guide ([#117](https://github.com/mlsecproject/combine/issues/117))
* Instalation documentation using Python venv ([#115](https://github.com/mlsecproject/combine/issues/115))
* Minor cleanup on gitignore and other files ([#109](https://github.com/mlsecproject/combine/issues/109))
* Correct enrichment of FQDN indicators - it extracts all the related IPv4s and enriches them further ([#36](https://github.com/mlsecproject/combine/issues/36))
* Added contributing document to repository ([#127](https://github.com/mlsecproject/combine/issues/127))

#### 0.1.2 Bouncing Capybara
This is a bugfix release with several stability and performance improvements

* Multiple Enrichment Speedups:
  * Rewrite of ASN enrichment code
  ([#42](https://github.com/mlsecproject/combine/issues/42),
  [#104](https://github.com/mlsecproject/combine/issues/104))
  * Speedup of GeoIP code - thanks to [@jeffbryner](https://github.com/jeffbryner)
* Better csv-based extraction on packetmail - thanks to [@btv](https://github.com/btv)
* Exporting extracted data to CRITs ([#84](https://github.com/mlsecproject/combine/issues/84), [#91](https://github.com/mlsecproject/combine/issues/91), [#94](https://github.com/mlsecproject/combine/issues/94)) - thanks to [@paulpc](https://github.com/paulpc)
* Better Logging Facility ([#34](https://github.com/mlsecproject/combine/issues/34))
* Updated grequests and Exception Handling ([#78](https://github.com/mlsecproject/combine/issues/78),
[#32](https://github.com/mlsecproject/combine/issues/32))

#### 0.1.1 Ascending Capybara
This is a bugfix release to improve the stability of "tiq-test" enriched data generation

* Enriched IP generation should work fine in this release. ([#58](https://github.com/mlsecproject/combine/issues/58), [#67](https://github.com/mlsecproject/combine/issues/67), [#76](https://github.com/mlsecproject/combine/issues/76))
* Supports simple lists of IP addresses and domain names as local file importing ([#48](https://github.com/mlsecproject/combine/issues/48))

Revision of enriched DNS data generation is on track for v0.1.2

#### 0.1 Capybara
* First release of combine, for the talks in BSidesLV 2014 and DEF CON 22.
